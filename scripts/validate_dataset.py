"""Validate the supplied dataset without changing questions or split assignments."""

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
from itertools import combinations
import json
from pathlib import Path
import posixpath
import random
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZipFile


INTENTS = ("Hours", "Fees", "Location", "Registration", "Contact")
PREFIXES = ("HOU", "FEE", "LOC", "REG", "CON")
COLUMNS = ("question_id", "question", "intent", "style", "split")
FILES = {
    "all": "CampusAsk_100_Questions.csv",
    "train": "CampusAsk_Train_80.csv",
    "test": "CampusAsk_Test_20.csv",
}
BASE_SEED = 42
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
STOP_WORDS = set(
    "a an the is are was were do does did can could i me my you your to of for in "
    "on at and or it there this that what which how where when with from have has "
    "be get students student university campus".split()
)


def normalize(text):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold()))


def duplicate_groups(rows, field, normalized=False):
    groups = defaultdict(list)
    for row in rows:
        key = normalize(row[field]) if normalized else row[field]
        groups[key].append(row["question_id"])
    return [ids for ids in groups.values() if len(ids) > 1]


def workbook_tables(path):
    with ZipFile(path) as archive:
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {rel.attrib["Id"]: rel.attrib["Target"] for rel in relationships}
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared = ["".join(node.itertext()) for node in
                      ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        result = {}
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        for sheet in workbook.findall("s:sheets/s:sheet", NS):
            relationship = sheet.attrib[
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
            ]
            target = targets[relationship]
            target = target.lstrip("/") if target.startswith("/") else posixpath.normpath(
                posixpath.join("xl", target))
            rows = []
            for row in ET.fromstring(archive.read(target)).findall("s:sheetData/s:row", NS):
                cells = {}
                for cell in row.findall("s:c", NS):
                    column = re.match(r"[A-Z]+", cell.attrib["r"])[0]
                    value = cell.find("s:v", NS)
                    inline = cell.find("s:is", NS)
                    text = value.text or "" if value is not None else ""
                    if cell.attrib.get("t") == "s":
                        text = shared[int(text)]
                    elif inline is not None:
                        text = "".join(inline.itertext())
                    cells[column] = text
                rows.append(cells)
            result[sheet.attrib["name"]] = rows
        return result


def validate(project):
    checks = []
    datasets = {}

    def check(name, passed, details):
        checks.append({"name": name, "status": "PASS" if passed else "FAIL",
                       "details": details})

    for subset, filename in FILES.items():
        path = project / "data" / filename
        try:
            with path.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream, strict=True)
                headers = reader.fieldnames
                raw_rows = list(reader)
            check(f"{subset}.schema", headers == list(COLUMNS), {"headers": headers})
            malformed = [index for index, row in enumerate(raw_rows, 2)
                         if None in row or any(row.get(column) is None for column in COLUMNS)]
            check(f"{subset}.row_shape", not malformed, {"invalid_lines": malformed})
            rows = [{column: row.get(column) or "" for column in COLUMNS} for row in raw_rows]
            datasets[subset] = rows
        except (OSError, UnicodeError, csv.Error) as error:
            check(f"{subset}.read", False, {"error": str(error)})
            continue

        expected_size = {"all": 100, "train": 80, "test": 20}[subset]
        check(f"{subset}.count", len(rows) == expected_size, {"count": len(rows)})
        counts = Counter(row["intent"] for row in rows)
        expected_counts = {intent: expected_size // 5 for intent in INTENTS}
        check(f"{subset}.intent_balance", dict(counts) == expected_counts, dict(counts))
        missing = [{"line": index, "column": column} for index, row in enumerate(rows, 2)
                   for column in COLUMNS if not row[column].strip()]
        check(f"{subset}.missing_values", not missing, {"cells": missing})
        invalid_values = [row["question_id"] for row in rows
                          if row["style"] not in {"standard", "short", "long", "informal"}
                          or row["split"] not in {"train", "test"}]
        check(f"{subset}.allowed_values", not invalid_values, {"ids": invalid_values})
        for field, normalized in (("question_id", False), ("question", False), ("question", True)):
            duplicates = duplicate_groups(rows, field, normalized)
            name = f"{subset}.duplicate_{field}" + ("_normalized" if normalized else "")
            check(name, not duplicates, {"groups": duplicates})
        if subset != "all":
            wrong_split = [row["question_id"] for row in rows if row["split"] != subset]
            check(f"{subset}.split_tags", not wrong_split, {"ids": wrong_split})

    if len(datasets) == 3:
        master, train, test = (datasets[key] for key in ("all", "train", "test"))
        expected_ids = {f"{prefix}-{index:03}" for prefix in PREFIXES for index in range(1, 21)}
        actual_ids = {row["question_id"] for row in master}
        check("all.id_coverage", actual_ids == expected_ids,
              {"missing": sorted(expected_ids - actual_ids), "extra": sorted(actual_ids - expected_ids)})
        prefix_map = dict(zip(INTENTS, PREFIXES))
        invalid_ids = [row["question_id"] for row in master
                       if not re.fullmatch(rf"{prefix_map.get(row['intent'], 'INVALID')}-\d{{3}}",
                                           row["question_id"])]
        check("all.id_intent_alignment", not invalid_ids, {"ids": invalid_ids})

        as_records = lambda rows: Counter(tuple(row[column] for column in COLUMNS) for row in rows)
        check("all.subset_union", as_records(master) == as_records(train + test),
              {"master_rows": len(master), "combined_subset_rows": len(train) + len(test)})
        for subset, rows in (("train", train), ("test", test)):
            matches = as_records(rows) == as_records([r for r in master if r["split"] == subset])
            check(f"{subset}.matches_master", matches, {"all_columns_compared": list(COLUMNS)})

        for field, normalized in (("question_id", False), ("question", False), ("question", True)):
            values = lambda rows: {normalize(r[field]) if normalized else r[field] for r in rows}
            overlap = sorted(values(train) & values(test))
            name = "split.overlap_" + field + ("_normalized" if normalized else "")
            check(name, not overlap, {"count": len(overlap), "values": overlap})

        seeds = []
        for index, intent in enumerate(INTENTS):
            group = sorted((r for r in master if r["intent"] == intent),
                           key=lambda row: row["question_id"])
            expected = sorted(r["question_id"] for r in random.Random(BASE_SEED + index).sample(
                group, min(4, len(group))))
            actual = sorted(r["question_id"] for r in group if r["split"] == "test")
            seeds.append({"intent": intent, "seed": BASE_SEED + index,
                          "expected_test_ids": expected, "actual_test_ids": actual})
        check("split.seed_42_reproduction", all(item["expected_test_ids"] == item["actual_test_ids"]
                                                for item in seeds), seeds)

    required = ("docs/CampusAsk_Review.xlsx", "docs/CampusAsk_Data_Guide.txt")
    for relative in required:
        check(f"file.{relative}", (project / relative).is_file(), {"path": relative})
    try:
        manifest = json.loads((project / "docs/dataset_manifest.json").read_text(encoding="utf-8"))
        check("provenance.split_configuration",
              manifest.get("base_seed") == BASE_SEED and manifest.get("category_order") == list(INTENTS),
              {"base_seed": manifest.get("base_seed"), "category_order": manifest.get("category_order")})
        expected_paths = {"data/" + name for name in FILES.values()} | set(required)
        check("provenance.manifest_coverage", set(manifest["files"]) == expected_paths,
              {"file_count": len(manifest["files"])})
        for relative, original_hash in manifest["files"].items():
            actual_hash = hashlib.sha256((project / relative).read_bytes()).hexdigest()
            check(f"provenance.{relative}", actual_hash == original_hash,
                  {"sha256": actual_hash, "matches_original": actual_hash == original_hash})
    except (OSError, ValueError, KeyError, TypeError) as error:
        check("provenance.manifest", False, {"error": str(error)})

    try:
        sheets = workbook_tables(project / "docs/CampusAsk_Review.xlsx")
        expected_header = ["Question ID", "English Question", "Intent", "Style", "Split"]
        for sheet, subset in (("All Questions", "all"), ("Train 80", "train"), ("Test 20", "test")):
            table = [[row.get(column, "") for column in "ABCDE"] for row in sheets[sheet]]
            expected = [[r[column] for column in COLUMNS] for r in datasets[subset]]
            matches = table[0] == expected_header and table[1:] == expected
            check(f"workbook.{subset}.matches_csv", matches, {"data_rows": len(table) - 1})
        summary = {row.get("A"): row for row in sheets["Summary"]}
        summary_ok = all([summary[intent].get(c) for c in "CDE"] == ["20", "16", "4"]
                         for intent in INTENTS)
        summary_ok = summary_ok and [summary["TOTAL"].get(c) for c in "CDE"] == ["100", "80", "20"]
        check("workbook.summary_counts", summary_ok, {"expected_total_train_test": [100, 80, 20]})
    except (OSError, BadZipFile, ET.ParseError, KeyError, IndexError, ValueError) as error:
        check("workbook.read", False, {"error": str(error)})

    candidates = []
    for left, right in combinations(datasets.get("all", []), 2):
        a = set(normalize(left["question"]).split()) - STOP_WORDS
        b = set(normalize(right["question"]).split()) - STOP_WORDS
        score = len(a & b) / len(a | b) if a | b else 0
        if score >= 0.5:
            candidates.append({"ids": [left["question_id"], right["question_id"]],
                               "token_jaccard": round(score, 3),
                               "cross_split": left["split"] != right["split"]})
    passed = all(item["status"] == "PASS" for item in checks)
    return {"status": "PASS" if passed else "FAIL", "base_seed": BASE_SEED,
            "python_version": sys.version.split()[0], "checks": checks,
            "similarity_candidates": candidates,
            "semantic_review": "Human approval pending; see docs/data_review.md. Lexical similarity "
                               "does not establish or exclude semantic leakage.",
            "seed_provenance": "Saved assignments match the documented compatible reproduction. "
                               "The original generation script was not supplied."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json-output", type=Path, help="Save the actual validation results as JSON")
    args = parser.parse_args()
    result = validate(args.project_dir.resolve())
    for item in result["checks"]:
        print(f"{item['status']}: {item['name']} {json.dumps(item['details'], ensure_ascii=True)}")
    print(f"Overall structural validation: {result['status']}")
    print(f"Lexical similarity candidates: {len(result['similarity_candidates'])}")
    print(result["semantic_review"])
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
