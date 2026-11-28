# CampusAsk – Error Analysis (20 error instances)

## Scope and selection

This analysis contains 20 model-error instances drawn from the actual 20-question test set and the saved predictions.
It includes all 12 errors made by the three non-baseline systems (Keyword Rules and both Naive Bayes variants),
plus 8 representative Majority Baseline errors. Some question IDs appear more than once because different models
made an error on the same test question. Therefore, 20 means 20 model-error instances, not 20 unique questions.

## Important interpretation

The explanations below are qualitative interpretations of the wording and model behavior; they are not experimentally
proven causes. The test set is small (4 examples per intent), so results should be interpreted cautiously.

## Main findings

- The Majority Baseline predicts Hours for every test question. The training classes are balanced, so the tie is
  resolved by the first class encountered (Hours); its 20% accuracy is therefore a tie-breaking outcome.
- Keyword Rules reaches 80% accuracy but misses some paraphrases that do not contain its listed keywords.
- Naive Bayes with lowercasing enabled reaches 85% and makes 3 errors; lowercasing disabled reaches 75% and makes 5.
- The remaining errors are concentrated in Fees and Contact for the lowercased Naive Bayes model.
- The training set has only 16 examples per intent, which limits coverage of synonyms, informal expressions, and ambiguous wording.

## Twenty analyzed error instances

| Model | ID | True → Predicted | Error category |
|---|---|---|---|
| keyword_rules | LOC-014 | Location → Hours | Missing location cue |
| keyword_rules | REG-014 | Registration → Hours | Weak registration wording |
| keyword_rules | REG-016 | Registration → Hours | Ambiguous application wording |
| keyword_rules | CON-008 | Contact → Hours | Contact synonym not covered |
| nb_lowercase_on | FEE-015 | Fees → Contact | Overlapping payment/contact vocabulary |
| nb_lowercase_on | CON-003 | Contact → Fees | Sparse contact examples / payment-word overlap |
| nb_lowercase_on | CON-008 | Contact → Fees | Contact synonym not covered |
| nb_lowercase_off | HOU-004 | Hours → Contact | Capitalization sensitivity |
| nb_lowercase_off | FEE-002 | Fees → Contact | Short question / capitalization sensitivity |
| nb_lowercase_off | FEE-015 | Fees → Contact | Overlapping payment/contact vocabulary |
| nb_lowercase_off | LOC-018 | Location → Hours | Limited training vocabulary |
| nb_lowercase_off | CON-003 | Contact → Fees | Sparse contact examples / payment-word overlap |
| majority_baseline | FEE-002 | Fees → Hours | Majority-class bias |
| majority_baseline | FEE-005 | Fees → Hours | Majority-class bias |
| majority_baseline | FEE-010 | Fees → Hours | Majority-class bias |
| majority_baseline | LOC-004 | Location → Hours | Majority-class bias |
| majority_baseline | LOC-014 | Location → Hours | Majority-class bias |
| majority_baseline | REG-009 | Registration → Hours | Majority-class bias |
| majority_baseline | CON-002 | Contact → Hours | Majority-class bias |
| majority_baseline | CON-008 | Contact → Hours | Majority-class bias |

## Detailed case notes

### 1. keyword_rules – LOC-014
- **Question:** How can I walk from the library to the language center without leaving campus?
- **Actual intent:** Location
- **Predicted intent:** Hours
- **Category:** Missing location cue
- **Analysis:** The question asks for a route between two campus places, but it does not use a strong location keyword such as 'where' or 'located'.

### 2. keyword_rules – REG-014
- **Question:** How can I join the waiting list for a course that has no seats left?
- **Actual intent:** Registration
- **Predicted intent:** Hours
- **Category:** Weak registration wording
- **Analysis:** The phrase 'waiting list' is not enough for the rule list to identify the registration intent; the rule list contains 'waitlist' as one word.

### 3. keyword_rules – REG-016
- **Question:** Can I cancel an application after I submit it?
- **Actual intent:** Registration
- **Predicted intent:** Hours
- **Category:** Ambiguous application wording
- **Analysis:** The word 'application' can refer to admission or another process, and the question does not contain a strong registration keyword.

### 4. keyword_rules – CON-008
- **Question:** Student customer service hotline?
- **Actual intent:** Contact
- **Predicted intent:** Hours
- **Category:** Contact synonym not covered
- **Analysis:** The phrase 'customer service hotline' expresses a contact request, but the keyword rules and the small training set do not represent this wording strongly.

### 5. nb_lowercase_on – FEE-015
- **Question:** Hey, do I pay extra to retake an exam?
- **Actual intent:** Fees
- **Predicted intent:** Contact
- **Category:** Overlapping payment/contact vocabulary
- **Analysis:** The phrase 'pay extra' signals Fees, while the learned vocabulary can associate the short informal wording with Contact-related examples.

### 6. nb_lowercase_on – CON-003
- **Question:** Is there a WhatsApp number for student support?
- **Actual intent:** Contact
- **Predicted intent:** Fees
- **Category:** Sparse contact examples / payment-word overlap
- **Analysis:** The phrase 'WhatsApp number' is a contact request, but 'number' and short support wording can overlap with fee-related vocabulary in this small dataset.

### 7. nb_lowercase_on – CON-008
- **Question:** Student customer service hotline?
- **Actual intent:** Contact
- **Predicted intent:** Fees
- **Category:** Contact synonym not covered
- **Analysis:** The phrase 'customer service hotline' expresses a contact request, but the keyword rules and the small training set do not represent this wording strongly.

### 8. nb_lowercase_off – HOU-004
- **Question:** What are the working hours of the student affairs office?
- **Actual intent:** Hours
- **Predicted intent:** Contact
- **Category:** Capitalization sensitivity
- **Analysis:** With lowercasing disabled, capitalized words may be treated as distinct tokens from their lowercase training forms, reducing useful word matches.

### 9. nb_lowercase_off – FEE-002
- **Question:** Fee for an official transcript?
- **Actual intent:** Fees
- **Predicted intent:** Contact
- **Category:** Short question / capitalization sensitivity
- **Analysis:** The very short phrase provides few tokens; without lowercasing, capitalization differences can further reduce overlap with training examples.

### 10. nb_lowercase_off – FEE-015
- **Question:** Hey, do I pay extra to retake an exam?
- **Actual intent:** Fees
- **Predicted intent:** Contact
- **Category:** Overlapping payment/contact vocabulary
- **Analysis:** The phrase 'pay extra' signals Fees, while the learned vocabulary can associate the short informal wording with Contact-related examples.

### 11. nb_lowercase_off – LOC-018
- **Question:** Is the postgraduate studies office in the north wing of the building?
- **Actual intent:** Location
- **Predicted intent:** Hours
- **Category:** Limited training vocabulary
- **Analysis:** The model may not have enough representative examples for this wording in an 80-question training set.

### 12. nb_lowercase_off – CON-003
- **Question:** Is there a WhatsApp number for student support?
- **Actual intent:** Contact
- **Predicted intent:** Fees
- **Category:** Sparse contact examples / payment-word overlap
- **Analysis:** The phrase 'WhatsApp number' is a contact request, but 'number' and short support wording can overlap with fee-related vocabulary in this small dataset.

### 13. majority_baseline – FEE-002
- **Question:** Fee for an official transcript?
- **Actual intent:** Fees
- **Predicted intent:** Hours
- **Category:** Majority-class bias
- **Analysis:** The baseline predicts Hours for every question because all training classes are tied and Hours is encountered first. It ignores the question meaning.

### 14. majority_baseline – FEE-005
- **Question:** How much does a parking permit cost for one semester?
- **Actual intent:** Fees
- **Predicted intent:** Hours
- **Category:** Majority-class bias
- **Analysis:** The baseline predicts Hours for every question because all training classes are tied and Hours is encountered first. It ignores the question meaning.

### 15. majority_baseline – FEE-010
- **Question:** Are there additional charges for courses that include laboratory sessions?
- **Actual intent:** Fees
- **Predicted intent:** Hours
- **Category:** Majority-class bias
- **Analysis:** The baseline predicts Hours for every question because all training classes are tied and Hours is encountered first. It ignores the question meaning.

### 16. majority_baseline – LOC-004
- **Question:** Is the student affairs office on the first floor?
- **Actual intent:** Location
- **Predicted intent:** Hours
- **Category:** Majority-class bias
- **Analysis:** The baseline predicts Hours for every question because all training classes are tied and Hours is encountered first. It ignores the question meaning.

### 17. majority_baseline – LOC-014
- **Question:** How can I walk from the library to the language center without leaving campus?
- **Actual intent:** Location
- **Predicted intent:** Hours
- **Category:** Majority-class bias
- **Analysis:** The baseline predicts Hours for every question because all training classes are tied and Hours is encountered first. It ignores the question meaning.

### 18. majority_baseline – REG-009
- **Question:** Can transfer students register directly for second-year courses?
- **Actual intent:** Registration
- **Predicted intent:** Hours
- **Category:** Majority-class bias
- **Analysis:** The baseline predicts Hours for every question because all training classes are tied and Hours is encountered first. It ignores the question meaning.

### 19. majority_baseline – CON-002
- **Question:** Academic advising email address?
- **Actual intent:** Contact
- **Predicted intent:** Hours
- **Category:** Majority-class bias
- **Analysis:** The baseline predicts Hours for every question because all training classes are tied and Hours is encountered first. It ignores the question meaning.

### 20. majority_baseline – CON-008
- **Question:** Student customer service hotline?
- **Actual intent:** Contact
- **Predicted intent:** Hours
- **Category:** Majority-class bias
- **Analysis:** The baseline predicts Hours for every question because all training classes are tied and Hours is encountered first. It ignores the question meaning.

## Suggested improvements

1. Expand the training data with paraphrases, especially for Fees and Contact, while keeping the class balance.
2. Add multi-word variants such as 'waiting list' and 'customer service hotline' to the keyword rules.
3. Add route/direction expressions (e.g., 'how can I walk', 'which entrance', 'how do I get to') to Location rules.
4. Keep lowercasing enabled for this baseline Naive Bayes comparison.
5. Evaluate improvements on a new or repeated stratified split; do not tune repeatedly against the same held-out test set.

## Reporting note

Report these as 20 error instances across model runs. Do not describe them as 20 distinct test questions.