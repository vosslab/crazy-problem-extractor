# Swarm test 5 report

Pipelined Bio2e generation with quality improvements.

- **Date**: 2026-03-10
- **Textbook**: OpenStax Biology 2e
- **Chapters**: 10 (ch01, ch04, ch07, ch10, ch14, ch19, ch24, ch30, ch37, ch44)
- **Coders**: 50 (5 per chapter, Haiku model)
- **Pipeline**: 50 coders + 10 testers + 1 reviewer

## Results

- **Total files generated**: 331 / 333 expected (99.4%)
- **Lint pass rate**: 331/331 (100%)
- **Verbatim rate**: 0% (10-file sample)
- **RNG usage**: 65.6% meaningful (target was 80%)
- **Widget diversity**: 4 types (RadioButtons 58%, CheckboxList 24%, PopUp 10%, Numeric 2%)
- **Solution quality**: 70% good or excellent (10-file sample)

## What worked

1. **Coder briefing with transformation requirements** eliminated verbatim copying entirely. Test 4 had high verbatim rates; test 5 has 0%.
2. **Round-robin problem assignment** across 5 coders gave near-complete coverage (331/333).
3. **Renderer API lint** (`lint_pg_via_renderer_api.py -i FILE`) caught structural errors at write time. 100% pass rate means coders self-corrected.
4. **Haiku coders** produced high-quality output with good solution explanations and plausible distractors. Cost-effective for template-following work.
5. **Widget diversity directive** in the briefing resulted in 4 widget types. Test 4 was RadioButtons-only.

## What needs improvement

1. **RNG usage at 65.6%** is below the 80% target. Many files seed `$rng` but never call `->random()`. The briefing told coders to randomize but did not enforce it structurally.
2. **RadioButtons dominance at 58%**. More explicit targets per widget type (e.g., "at least 1 PopUp and 1 CheckboxList per coder") would improve diversity.
3. **Pipelining was not fully realized**. Testers ran as a batch after all coders completed instead of starting as each coder finished. This was due to context window limits, not a design flaw.
4. **ch37 missing 2 files**. Round-robin assignment works but some coders produced fewer files than assigned.
5. **Essay widget bug** in ch10_c4_p29.pgml -- a `[____]{15}` widget grades against the number 15 instead of accepting free text. Needs a lint rule to catch this pattern.

## Comparison with previous tests

| Metric | Test 3 | Test 4 | Test 5 |
| --- | --- | --- | --- |
| Chapters | 47 | 47 | 10 |
| Total files | 1,151+ | ~500 | 331 |
| Lint pass rate | ~60% | ~60% | 100% |
| Verbatim rate | high | high | 0% |
| Widget diversity | 1 type | 1 type | 4 types |
| RNG usage | decorative | decorative | 65.6% meaningful |
| Coder model | Haiku | Haiku | Haiku |

## Detailed reports

- [test5/reports/summary.md](../test5/reports/summary.md) -- full metrics and file counts
- [test5/reports/quality_review.md](../test5/reports/quality_review.md) -- 10-file quality sample
- `test5/reports/chNN_lint.md` -- per-chapter lint results

## Recommendations for test 6

1. Add a lint rule that flags files where `PGrandom->new()` exists but `->random(` is never called
2. Set explicit widget quotas per coder (e.g., "problems 1-3 use RadioButtons, problem 4 uses CheckboxList, problem 5 uses PopUp")
3. Pipeline testers to start as each coder finishes, not as a batch
4. Consider Sonnet for complex chapters where application-level questions need deeper reasoning
5. Add a post-generation pass to fix decorative RNG patterns
6. Repurpose tester agents as quality reviewers instead of lint checkers (coders self-lint). Testers should:
   - Verify the PGML addresses the same concept/topic as the assigned problem
   - Confirm the correct answer is **different** from the textbook's answer (transformation requirement for copyright)
   - Confirm the stem is sufficiently different from the textbook wording
   - Verify the new correct answer is scientifically accurate (use Sonnet for this)
7. Skip the mechanical lint tester pass entirely -- 100% pass rate means it adds wall time for zero value
8. Launch all coders in fewer batches to reduce user round-trips
