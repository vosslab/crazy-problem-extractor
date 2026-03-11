# Swarm test 1: free-choice baseline (ch03)

## Test design

First swarm test using ch03 (Amino Acids) from Tymoczko "Biochemistry: A Short Course" (3rd ed.). 8 coders dispatched with full creative freedom -- no assigned problems, each coder picks whatever interests them from the 19-problem manifest.

## Results

| Metric | Value |
| --- | --- |
| Total files generated | 42 |
| Unique problems covered | 7 / 19 (37%) |
| Gap count | 12 |
| Competition count | 7 |
| Single count | 0 |
| Validation errors | 0 |
| Widget types used | 4 (PopUp, RadioButtons, String, CheckboxList) |
| Wall time (8 coders parallel) | ~2 minutes |
| Sequential estimate | ~16 minutes |

## What worked

### Parallel execution
- 8 coder agents ran simultaneously with zero file conflicts
- Each coder wrote to its own staging directory (`_staging/coder_{N}/`)
- All 42 generated files passed validation with 0 errors

### Natural overlap creates competition
- Every covered problem had multiple competing versions (2-8 per problem)
- Zero "single" entries -- coders naturally gravitate to the same interesting problems
- This gives the referee real choices for quality selection

### Widget diversity emerges organically
- Problem 01 (translate codes): PopUp, RadioButtons, String input, text input
- Problem 06 (solubility): RadioButtons, PopUp
- Problems 09/11 (select-all): CheckboxList consensus -- coders independently agree on the right widget
- No forced widget constraints needed; creative freedom produces variety on ambiguous problems and consensus on clear ones

### Validation as quality gate
- The `validate_pgml.py` static checker caught issues before they reached the referee
- Coders self-corrected during generation (validate, fix, re-validate)
- Zero errors across all 42 files shows the briefing doc is effective

## What did not work

### Herding: coders pick the same problems
- 7 of 19 problems covered (37%) -- 12 gaps
- All 8 coders picked p01, p06, p11 (the clearest, most self-contained problems)
- Problems requiring images (p03, p13), complex calculations (p16-19), or garbled text (p02) got zero attempts
- The "pick whatever interests you" strategy produces great depth but poor breadth

### Garbled problem text reduces coverage
- Textbook OCR artifacts make some problems unreadable (p02 text runs into p03)
- Coders cannot interpret problems they cannot read
- The manifest should include cleaned/curated problem text, not raw OCR output

### Warning false positives
- Perl array index syntax (`$array[$index]`) triggers PGML passthrough warnings
- These are false positives from the setup section, not actual PGML blocks
- Warning noise ranges from 0-20 per file, making it harder to spot real issues

## Conclusions

1. **Free choice causes severe herding.** Only 37% coverage with 8 coders is unacceptable for production.
2. **Widget diversity is a strength.** Coders naturally explore different approaches when given creative freedom.
3. **Parallel execution works.** Zero file conflicts with the `_staging/coder_{N}/` directory structure.
4. **Problem assignment is needed.** The next test (test 2) will use modular assignment to fix herding while preserving creative freedom.

## Pipeline timing

| Step | Wall time | Agent count |
| --- | --- | --- |
| Dispatch (manifest + dirs) | 2 seconds | 1 |
| Coder generation | ~2 minutes | 8 parallel |
| Referee evaluation | 1 second | 1 |
| Total | ~2.5 minutes | -- |
