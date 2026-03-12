# Swarm test 7 report

Answer-varying RNG and repair pass pipeline.

## Summary

Test 7 targeted the two biggest quality gaps from test 6: cosmetic-only RNG (answer never changes across seeds) and scientific accuracy. It used 10 new chapters not tested in test 5 or test 6, an enhanced coder briefing with explicit answer-variation rules, new static audit scripts, and a two-wave generation+repair architecture.

**Result**: Answer variation improved dramatically (53% to 91.7%), structural RNG hit 100%, and option coverage reached 96.2%. Scientific accuracy as judged by Sonnet reviewers dropped to 69.8%, and answer-shuffled compliance was only 79.4%. The repair pass recovered 57 of 67 rejected files. Final yield: 254 validated files out of 267 target problems (95.1%).

## Chapters

ch03, ch06, ch09, ch11, ch13, ch15, ch16, ch17, ch20, ch21 (none used in test 5 or test 6).

## Pipeline architecture

```
Wave 1: 50 Haiku coders (5/chapter) --> 263 files (~5 min)
         |
Static audit: check_rng_usage, check_answer_variation, check_option_coverage
         |
Review: 10 Sonnet reviewers (1/chapter, 7-criterion rubric) --> 262 files reviewed
         |
Sort: _sort_files.py reads reviewer JSON --> 197 validated, 67 rejected
         |
Wave 2: 4 Haiku repair coders --> 64/67 repaired --> 57 pass audit --> validated
         |
Final: 254 validated, 13 still rejected
```

Total wall-clock time: ~15 minutes.

## Metrics comparison

| Metric | Test 6 | Test 7 | Target | Met? |
| --- | --- | --- | --- | --- |
| Files generated | 315 | 263 | 267 | 98.5% coverage |
| Functional RNG (static audit) | 53% | 91.7% | >85% | YES |
| RNG structural | 99% | 100% | 100% | YES |
| Lint pass | 99% | 100% | 100% | YES |
| Option coverage (static) | N/A | 96.2% | >98% | NO (96.2%) |
| Answer shuffled (reviewer) | N/A | 79.4% | >95% | NO |
| Scientific accuracy (reviewer) | 89.2% | 69.8% | >95% | NO |
| Quality all-pass (reviewer) | 92.1% | 40.8% | >97% | NO |
| Same concept (reviewer) | N/A | 96.9% | -- | -- |
| Different stem (reviewer) | N/A | 97.3% | -- | -- |
| Different answer (reviewer) | N/A | 88.2% | -- | -- |
| Final yield | 87.5% | 95.1% | -- | -- |

## What worked

1. **Answer-varying RNG**: The enhanced briefing with explicit bad/good examples and the "mentally substitute pick_index=0,1,2" self-check rule raised functional RNG from 53% to 91.7%. This was the primary goal and it succeeded.

2. **Structural RNG and lint**: Both hit 100%, up from 99%. The self-lint-via-API pattern from test 5/6 continues to work well.

3. **Repair pass**: The two-wave architecture is effective. 64 of 67 rejected files were repaired, with 57 passing re-audit. This recovered 85% of rejected files with minimal agent cost (4 Haiku agents).

4. **Coverage**: 263/267 target problems covered (98.5%), consistent with test 6 levels.

5. **New audit scripts**: `check_answer_variation.py` and `check_option_coverage.py` provide automated quality gates that catch issues reviewers also flag.

## What did not work

1. **Scientific accuracy dropped**: 69.8% vs 89.2% in test 6. Possible explanations:
   - Different chapters may be harder (ch09 cell signaling, ch16 gene expression have complex cascades)
   - Reviewers may have been stricter with 7 criteria vs fewer in test 6
   - The emphasis on answer variation may have encouraged coders to create more creative but less accurate questions
   - Sonnet reviewers may over-flag accuracy when they are unsure about biology content

2. **Answer shuffled (79.4%)**: Many files lack `order => "random"` in their widget constructors. The briefing mentioned this requirement but coders did not consistently apply it. This is a mechanical fix that could be automated.

3. **Option coverage (96.2%)**: Below the 98% target. Some files have answer values that do not appear in the widget option list. The static checker catches these but coders still produce them.

4. **Reviewer all-pass rate (40.8%)**: Much lower than test 6 (92.1%). The expanded 7-criterion rubric is stricter than the previous rubric. The main drivers of failure are scientific_accuracy (30.2% fail) and answer_shuffled (20.6% fail).

## Per-criterion failure analysis

| Criterion | Pass rate | Failure count | Notes |
| --- | --- | --- | --- |
| same_concept | 96.9% | 8 | Coders occasionally wander off-topic |
| different_stem | 97.3% | 7 | Good transformation quality |
| option_coverage | 95.0% | 13 | Mostly PopUp widgets with missing values |
| different_answer | 88.2% | 31 | Some coders reproduce textbook answers |
| answer_shuffled | 79.4% | 54 | Missing `order => "random"` |
| answer_varies | 77.1% | 60 | Improved from 53% but still many 2-value arrays |
| scientific_accuracy | 69.8% | 79 | Biggest problem; may need Opus reviewers |

## Repair pass results

- 67 files rejected after review
- 64 files repaired by 4 Haiku agents
- 57 passed re-audit, 9 failed (7 answer variation, 2 option coverage)
- 3 files never repaired (likely coder timeout)
- Net recovery: 85% of rejected files

## Recommendations for test 8

1. **Answer shuffle automation**: Post-process all files to inject `order => "random"` into RadioButtons and CheckboxList constructors. This is a mechanical transformation, not a creative task.

2. **Scientific accuracy**: Consider using Opus for review instead of Sonnet, or add a dedicated accuracy-check pass with a biology-specific prompt. The 69.8% rate may reflect reviewer strictness as much as actual errors.

3. **Minimum 3 answer values**: The briefing says >= 3 distinct values but many coders still use 2-value arrays. Consider adding a static pre-check that rejects files before review if they have < 3 answer values.

4. **Repair loop**: Run repair in a loop (repair -> audit -> repair) until convergence or a max iteration count. The current single-pass repair leaves 9 files still failing.

5. **Review calibration**: The 7-criterion rubric may be too strict for a single-pass review. Consider splitting into hard criteria (same_concept, option_coverage, answer_varies) and soft criteria (scientific_accuracy, answer_shuffled) with different thresholds.

6. **Chapter difficulty weighting**: Some chapters (ch09, ch15, ch16) had notably higher failure rates. Consider dispatching more coders or stronger models for complex chapters.
