# Swarm strategies

Lessons learned from the chaotic competitive pipeline for PGML question generation.

## Overview

The chaotic pipeline dispatches multiple independent AI coders to the same chapter simultaneously, with no coordination between them. Each coder reads the problem manifest, picks problems that interest them, chooses their own widget type and approach, and generates PGML files. A referee then evaluates the organic overlap and selects winners.

This document captures what we learned from the ch03 swarm test (8 coders, 19 problems, 42 files generated) and strategies for production runs.

## What worked

### Parallel execution
- 8 coder agents ran simultaneously with zero file conflicts
- Each coder wrote to its own staging directory (`_staging/coder_{N}/`)
- Total wall-clock time: ~2 minutes for all 8 coders (vs ~16 min sequential)
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

## Strategies for production

### Strategy 1: Assigned problem ranges to fix herding

Split the problem manifest into overlapping ranges so each coder has a "home turf" but can also roam:

```
Coder 1: problems 1-5 (required: pick at least 2) + any others
Coder 2: problems 3-8 (required: pick at least 2) + any others
Coder 3: problems 6-10 (required: pick at least 2) + any others
...
```

This guarantees breadth while preserving creative freedom and natural overlap.

### Strategy 2: Curate the manifest

Clean up problem text before dispatching:
- Fix OCR artifacts and run-on text
- Flag image-dependent problems as "needs adaptation" with a text description of what the image shows
- Separate problems that got merged during OCR (e.g., p02 contains p03 text)
- Mark calculation problems with explicit formulas and expected numeric answers

### Strategy 3: Reduce warning noise

Update `validate_pgml.py` or `pgml_checks.py` to suppress false positives:
- Skip passthrough warnings for lines inside setup blocks (between `Context()` and `BEGIN_PGML`)
- Or scope the check to only fire inside `BEGIN_PGML`...`END_PGML` blocks

### Strategy 4: Deterministic problem assignment

Instead of letting coders self-select (which causes herding), assign problems mechanically:

- **Parity split**: odd-numbered coders get odd-numbered problems, even coders get even problems. Each coder must attempt at least 2 from their assigned set plus may pick freely from the other set.
- **Modular assignment**: coder N gets problems where `(problem_number % num_coders) == (N - 1)`. With 8 coders and 19 problems, each coder gets 2-3 assigned problems plus free picks.
- **Random seed assignment**: shuffle the problem list with a per-coder seed and assign the first 3-4 to each coder as required, rest as optional. Different seeds produce different orderings, guaranteeing spread.
- **Hash assignment**: `hash(problem_number + coder_number) % 3 == 0` assigns roughly 1/3 of problems to each coder as required. Simple, deterministic, no coordination needed.

The key insight: coders still have creative freedom on widget type, framing, and difficulty. Only the problem selection is constrained to prevent herding. Each coder's required set overlaps with 1-2 other coders, preserving competition on every problem.

Example for 8 coders, 19 problems (modular):

```
Coder 1: required p01, p09, p17   + pick 2-3 freely
Coder 2: required p02, p10, p18   + pick 2-3 freely
Coder 3: required p03, p11, p19   + pick 2-3 freely
Coder 4: required p04, p12        + pick 3-4 freely
Coder 5: required p05, p13        + pick 3-4 freely
Coder 6: required p06, p14        + pick 3-4 freely
Coder 7: required p07, p15        + pick 3-4 freely
Coder 8: required p08, p16        + pick 3-4 freely
```

Every problem has at least 1 assigned coder. Free picks produce natural overlap on popular problems. Gap rate drops from 63% to near 0%.

### Strategy 5: Fewer coders per chapter, more chapters in parallel

The ch03 test showed 8 coders produces heavy overlap on popular problems but leaves gaps. Consider:
- 4-5 coders per chapter (still plenty of competition)
- Run 3-4 chapters simultaneously (20 coders total, better breadth)
- Reserve 2-3 "gap filler" coder slots dispatched after the first wave to specifically target uncovered problems

### Strategy 6: Two-wave dispatch

- **Wave A**: 5 coders with full creative freedom (like the test)
- **Wave B**: 3 coders dispatched after Wave A completes, explicitly assigned to gap problems
- This combines organic diversity with guaranteed coverage

### Strategy 7: Problem difficulty tiers

Tag problems in the manifest with difficulty estimates:
- Tier 1: straightforward identification/classification (most coders will attempt)
- Tier 2: application/comparison (moderate coverage expected)
- Tier 3: calculations, multi-step reasoning, image-dependent (likely gaps)

Instruct coders: "attempt at least 1 Tier 3 problem" to push coverage upward.

## Metrics to track

### Per chapter
- **Coverage**: problems with at least 1 version / total problems
- **Overlap depth**: mean and max competing versions per covered problem
- **Widget diversity**: unique widget types across all versions of a problem
- **Validation pass rate**: files with 0 errors / total files generated
- **Gap rate**: problems with 0 versions / total problems

### Across chapters
- **Herding index**: standard deviation of problem selection frequency (lower = more herding)
- **Widget entropy**: Shannon entropy of widget type distribution (higher = more diverse)
- **Coder throughput**: files per coder per chapter (target: 4-6)

## Referee evaluation insights

### Automated scoring is necessary but not sufficient
- The current `_referee_evaluate.py` does validation-only scoring (errors/warnings)
- Qualitative scoring (accuracy, distractors, pedagogy) requires the referee agent
- Files with 0 errors and 0 warnings are not necessarily better than files with warnings

### Competition tiebreakers
- When all versions pass validation equally, the referee needs the rubric criteria:
  - Accuracy (3x weight) -- is the answer correct?
  - Distractors (2x) -- do wrong answers test real misconceptions?
  - Widget fit (2x) -- is the widget appropriate?
  - Randomization (2x) -- how many meaningful variants?
  - Pedagogy (1x) -- does the solution teach?

### Merge opportunities
- Problem p01 had versions using PopUp (interactive per-residue), RadioButtons (pick the hidden word), and String input (type the answer)
- These are fundamentally different question designs, not just variations
- The referee could keep multiple versions as separate problems rather than merge

## Pipeline timing

From the ch03 test (8 coders, 19 problems):

| Step | Wall time | Agent count |
| --- | --- | --- |
| Dispatch (manifest + dirs) | 2 seconds | 1 |
| Coder generation | ~2 minutes | 8 parallel |
| Referee evaluation | 1 second | 1 |
| Total | ~2.5 minutes | -- |

Projected for 10 chapters at 5 coders each:
- 2-3 chapters in parallel = ~8 minutes per wave
- 4 waves = ~32 minutes total generation time
- Plus referee + merge + promote per chapter

## File organization

```
_staging/
  ch03_manifest.yaml              # problem manifest
  coder_1/ch03_amino_acids/       # coder 1 output
    ch03_p01.pgml
    ch03_p06.pgml
    ...
  coder_2/ch03_amino_acids/       # coder 2 output (overlapping problems)
    ch03_p01.pgml
    ch03_p06.pgml
    ...
  merged/ch03_amino_acids/        # referee-selected winners
    ch03_p01.pgml
    ch03_p06.pgml
    ...

reports/referee/
  ch03_referee_report.yaml        # competition results + scores

output/ch03_amino_acids/          # promoted final files
  ch03_p01.pgml
  ...
```

## Swarm test 2: modular assignment (ch03)

### Test design

Re-ran ch03 with the same 8 coders but using **Strategy 4 (modular assignment)** instead of free choice. Each coder received 2-3 required problems assigned via `(index % 8) + 1` on the sorted problem list, plus creative freedom to pick 2-3 optional problems.

Assignment table (18 problems after deduplication, 8 coders):

```
Coder 1: required p01, p10, p18   + free picks
Coder 2: required p02, p11, p19   + free picks
Coder 3: required p03, p12        + free picks
Coder 4: required p04, p13        + free picks
Coder 5: required p05, p14        + free picks
Coder 6: required p06, p15        + free picks
Coder 7: required p07, p16        + free picks
Coder 8: required p09, p17        + free picks
```

### Results comparison

| Metric | Test 1 (free choice) | Test 2 (modular) |
| --- | --- | --- |
| Total files | 42 | 43 |
| Unique problems covered | 7 / 19 | 18 / 18 |
| Coverage % | 37% | 100% |
| Gap count | 12 | 0 |
| Competition count | 7 | 6 |
| Single count | 0 | 12 |
| Validation errors | 0 | 0 |
| Widget types used | 4 | 4 (RadioButtons, CheckboxList, PopUp, Numeric) |

### What changed

- **Coverage jumped from 37% to 100%.** Every problem now has at least one version. The 12 gaps from test 1 are all filled.
- **Herding reduced but not eliminated.** p11 (aromatic amino acids) and p14 (phenol-like R group) still attracted all 8 coders as optional picks. These are simple, self-contained problems that coders gravitate to regardless of assignment.
- **Competition preserved where it matters.** 6 problems have competing versions (p01=5, p06=4, p09=4, p11=8, p14=8, p18=2). The referee still has real choices for quality selection on popular problems.
- **Difficult problems now covered.** Challenge problems p16 (minor species ratio), p17 (titration pKa), p18 (lysine protonation), p19 (glutamic acid Henderson-Hasselbalch) all have at least 1 version. Test 1 had zero coverage on these.
- **OCR-garbled problems handled.** p02 (uncommon amino acids) and p03 (identify from structures) were adapted to text-based questions by their assigned coders. Test 1 coders skipped these entirely.
- **File count nearly identical** (43 vs 42). Modular assignment did not reduce coder throughput.

### Conclusions

1. **Modular assignment solves herding.** The strategy delivers near-perfect coverage without reducing creative freedom or output volume.
2. **Free picks still herd.** Even with required assignments, optional picks cluster on easy problems (p11, p14). This is acceptable because the required assignments guarantee breadth.
3. **Single-coverage problems are the tradeoff.** 12 of 18 problems have only 1 version (no competition). For production, consider assigning each problem to 2 coders or using a second wave to add competition on singles.
4. **Strategy 4 is validated for production use.** Recommend modular assignment as the default dispatch mode for all chapters.

## Open questions

- Should the referee keep multiple "best" versions for the same problem as separate question variants?
- How many coders is the sweet spot? The 8-coder test suggests 5-6 is sufficient for strong competition.
- Should Tier 3 (calculation) problems get a specialized prompt with formula examples?
- Can we detect herding early (after 2-3 coders finish) and redirect remaining coders to gaps?
- Should each problem be assigned to 2 coders (not 1) to guarantee competition on every problem?
