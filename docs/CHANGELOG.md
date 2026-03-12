# Changelog

## 2026-03-10

### Additions and New Features

- Completed quality review of ch03 (32 files) and ch06 (21 files) from test7 swarm run
  - ch03: 32 files reviewed; 11 files with scientific_accuracy=false, 9 files with answer_varies=false; major errors include: @byproducts array assigning ammonia/CO2/methane as dehydration synthesis byproducts (c1_p01), glycosidic bond mapped to hydrolysis (c1_p06), identical @roles and @correct_answers arrays making any option "correct" (c1_p11, c1_p21, c1_p26), glycogen incorrectly assigned "structural support" role (c3_p08), and pick_index 2 in c3_p23 mapping polar-to-nonpolar surface swap to secondary structure change
  - ch06: 21 files reviewed; 7 files with scientific_accuracy=false, 1 file with answer_varies=false; major errors include: photosynthesis listed as requiring ATP as input (c2_p17), injury recovery classified as primarily catabolic (c1_p16), Km used as proxy for activation energy (c3_p08), ice melting classified as not an energy transformation (c4_p09), GTP/ADP/NADH incorrectly listed as immediate energy currencies for lipids/proteins/nucleic acids (c4_p04), and enzyme properties incorrectly labeled as false statements (c3_p13)
  - Created `test7/reports/ch03_quality.json` (32 entries) and `test7/reports/ch06_quality.json` (21 entries)

- Completed quality review of ch09 (32 files) and ch11 (28 files) from test7 swarm run
  - ch09: 32 files reviewed; 15 files with answer_varies=false (hardcoded indices or single-answer arrays), 3 scientific accuracy failures including fabricated PIP2 percentages (ch09_c5_p10), IkB dephosphorylation logic reversal (ch09_c4_p14), incorrect ECM growth factor storage claim (ch09_c2_p32), and PKC immune suppression error (ch09_c3_p18)
  - ch11: 28 files reviewed; 7 files with answer_varies=false, 8 scientific accuracy failures including horse gamete calculation error (ch11_c1_p11), fungal/animal life cycle array errors (ch11_c1_p16), telophase I ploidy contradiction (ch11_c2_p12), and incorrect meiosis-in-gametophyte claim (ch11_c3_p28)
  - Created `test7/reports/ch09_quality.json` (32 entries) and `test7/reports/ch11_quality.json` (28 entries)

- Completed quality review of ch13 (12 files) and ch15 (25 files) from test7 swarm run
  - ch13: 3/12 pass all 7 criteria; failures in scientific_accuracy (7 files), answer_varies (3 files); ch13_c3_p08 critically broken (all four location codes marked correct for every pick_index); ch13_c4_p04 assigns wrong sex-linked distributions to hemophilia and fragile X
  - ch15: 5/25 pass all 7 criteria; failures in scientific_accuracy (13 files), answer_varies (9 files), option_coverage (5 files); ch15_c4_p24 mRNA sequences do not correctly derive from template strands; ch15_c5_p10 uses randomized historical year as correct answer with no biological basis
  - Created `test7/reports/ch13_quality.json` (12 entries) and `test7/reports/ch15_quality.json` (25 entries)
- Completed quality review of ch20 (20 files) and ch21 (30 files) from test7 swarm run
  - ch20: 20 files reviewed; 4 files with answer_varies=false (hardcoded correct indices), 1 file with answer_shuffled forced to index 0 always, 1 scientific accuracy failure (crocodile four-chambered heart), 1 stem leaks answer via template variable in question text
  - ch21: 30 files reviewed; 3 files with critical CheckboxList bugs (barrier label strings don't match option strings, making answers unmarkable), 1 scientific error (measles receptor wrongly identified as CD4 instead of CD46/SLAM), 1 same_concept=false (replication timeline vs replication truth statement), 1 bacteriophage lytic cycle time wrong by orders of magnitude (20 hours vs ~20 minutes)
  - Created `test7/reports/ch20_quality.json` (20 entries) and `test7/reports/ch21_quality.json` (30 entries)

- Completed quality review of ch16 (35 files) and ch17 (28 files) from test7 swarm run
  - ch16: 35 files reviewed; 9 files with answer_varies=false (mostly hardcoded $answer = $answers[0] or fixed index patterns in coder 4 files), 10 files with scientific_accuracy=false; major errors: ch16_c4_p09 hardcodes 'activator' but LacI pick describes repressor behavior, ch16_c3_p18 pick_index=2 marks 'alternative splicing requires different genes' as correct (factually false), ch16_c5_p15 lists 'translation initiation' as posttranscriptional control, ch16_c2_p22 targets patients with high ER in normal cells instead of tumor cells
  - ch17: 28 files reviewed; 2 files with answer_varies=false (ch17_c2_p02 correct_indices always [0,1,2]), 9 files with scientific_accuracy=false; major errors: ch17_c2_p22 pick_index=2 marks Southern blotting as detecting gene expression (should be Northern blotting), ch17_c4_p09 question stem describes cDNA library clones but labels them 'SNP markers', ch17_c1_p21 pick_index=1 defines protein signature as amino acid sequence (wrong), ch17_c4_p24 pick_index=1 describes Bt bacterium as a gene delivery method rather than source of the gene
  - Created `test7/reports/ch16_quality.json` (35 entries) and `test7/reports/ch17_quality.json` (28 entries)

- Completed test7 pipeline: Wave 2 repair pass and final reporting
  - Repair coders produced 64/67 files; 57 passed re-audit, moved to validated
  - Final yield: 254 validated files out of 267 target problems (95.1%)
  - Answer variation improved from 53% (test 6) to 91.7% (test 7 validated)
  - RNG structural and lint both hit 100%
  - Scientific accuracy dropped to 69.8% (reviewer); answer shuffled at 79.4%
  - Created [docs/SWARM_TEST7_REPORT.md](SWARM_TEST7_REPORT.md) with full metrics comparison
  - Created `test7/reports/timing.md` with phase timestamps
  - New scripts: `test7/check_answer_variation.py`, `test7/check_option_coverage.py`, `test7/_sort_files.py`

### Decisions and Failures

- ch21_c5_p15 and ch21_c5_p25: parallel arrays use short label strings as correct answers but CheckboxList options use full sentences; WeBWorK string matching will fail to mark any answer correct -- these files must be regenerated
- ch21_c5_p10: bacteriophage lytic cycle time listed as 20 hours is scientifically wrong (actual ~20-30 minutes for T4); numeric answer files require domain expert verification
- ch20_c4_p19: template variable $answer appears verbatim in the question stem, telegraphing the correct answer before students select

- Completed swarm test 6: Bio2e PGML generation with quality gates
  - 315/315 files generated across 10 chapters (100% coverage)
  - Widget distribution: RadioButtons 41.3%, CheckboxList 30.5%, PopUp 19.7%, Numeric 8.6% (all targets met)
  - RNG audit: 99.0% structural pass (vs 65.6% in test 5)
  - Quality review: 290/315 validated (92.1%), 25 rejected
  - 8 critical bugs found (unanswerable questions, scientifically false correct answers)
  - ~100 files with cosmetic-only RNG (answer never changes across seeds)
- Created `test6/generate_assignments.py` with global widget assignment cycle
- Created `test6/check_rng_usage.py` for structural RNG auditing
- Created `test6/prompts/coder_briefing.md` with mandatory RNG and widget quota enforcement
- Created [docs/SWARM_TEST6_REPORT.md](SWARM_TEST6_REPORT.md): full metrics comparison and recommendations
- Added test 6 entry to test reports list in [docs/SWARM_STRATEGIES.md](SWARM_STRATEGIES.md)
- Completed swarm test 5: pipelined Bio2e generation with quality improvements
  - 50 Haiku coder agents across 10 chapters, 331 PGML files generated
  - 100% lint pass rate via renderer API (`lint_pg_via_renderer_api.py`)
  - 0% verbatim copying rate (vs high rate in tests 3-4)
  - 4 widget types used (RadioButtons, CheckboxList, PopUp, Numeric)
  - 65.6% meaningful RNG usage (below 80% target)
- Created `test5/` directory structure with staging, validated, rejected, reports, and prompts subdirectories
- Created `test5/prompts/coder_briefing.md` with transformation requirements, widget diversity expectations, deny list, and full example
- Created `test5/prompts/assignments.json` with round-robin problem assignments for 5 coders x 10 chapters
- Created `test5/prompts/Biology2e-WEB.txt` from pdftotext conversion of Biology 2e PDF
- Created [docs/SWARM_TEST5_REPORT.md](SWARM_TEST5_REPORT.md): test 5 results, comparison with previous tests, recommendations for test 6
- Added test directory convention section to [docs/SWARM_STRATEGIES.md](SWARM_STRATEGIES.md)
- Added test 5 entry to test reports list in [docs/SWARM_STRATEGIES.md](SWARM_STRATEGIES.md)

### Developer Tests and Notes

- Quality review of 53 PGML files across ch02 (19 files) and ch05 (34 files) written to [test6/reports/ch02_ch05_quality.md](../test6/reports/ch02_ch05_quality.md)
  - 51 of 53 files pass all 5 criteria (96%)
  - ch02_c4_p19: concept mismatch -- saturated/unsaturated triglyceride content belongs in ch03 (biological macromolecules), not ch02 section 2.3 (carbon chemistry)
  - ch05_c3_p13: accuracy failure at 2 of 4 random paths -- fabricated Na-K pump mechanisms paired with wrong correct answers; pick_index 1 and 2 present incorrect biology
- Quality review of 65 PGML files across ch40 (23 files) and ch45 (42 files) written to [test6/reports/ch40_ch45_quality.md](../test6/reports/ch40_ch45_quality.md)
  - 4 critical bugs: ch45_c4_p29 unanswerable (answer string not in options), ch45_c2_p17 popup ignores pick_index, ch45_c4_p39 scientifically false claim as correct answer, ch40_c3_p13 cardiac muscle called voluntary
  - 16 files with cosmetic-only RNG (context changes, correct answer fixed); 2 ch40 files reproduce exact textbook answer
- Quality review of 67 PGML files across ch18 (25 files) and ch22 (42 files) written to [test6/reports/ch18_ch22_quality.md](../test6/reports/ch18_ch22_quality.md)
  - 58 of 67 files pass all 5 criteria (87%); 9 files have at least one FAIL
  - ch18_c1_p01: both RNG branches overwrite correct answer with identical string; answer never varies
  - ch18_c4_p14: all four `@classifications` entries are "prezygotic"; correct answer invariant across seeds
  - ch22_c1_p06: `$rng->random(0, 0, 1)` locks pick_index to 0; RNG is called but produces zero variation
  - ch22_c1_p16: scenario pool affects only solution text; question stem and correct answer "Calcium" are constant across seeds
  - ch22_c3_p03: `$reason_idx` picked independently from scenario; indices 1, 3, and 4 in `@reasons` are scientifically incorrect; students can be graded correct for a false statement depending on seed
  - ch22_c3_p23: marked correct answer limits antibiotic producers to prokaryotes, contradicting the textbook definition and the fungal examples (penicillin, cephalosporin) cited in the stem
  - ch22_c5_p20: at index 2, `answer => 2` points to "photoautotroph" in the numbered list but `$class_bold` displays "photolithotroph" in the solution; direct label mismatch

### Decisions and Failures

- RNG usage at 65.6% is below the 80% target; many Haiku coders seed `$rng` but never call `->random()`. Need structural enforcement or a lint rule.
- ch37 produced 33/35 files (2 short). Round-robin assignment works but some coders produce fewer files than assigned.
- ch10_c4_p29.pgml has a functional bug: numeric widget graded against value 15 instead of essay format.
- Testers ran as batch after all coders completed instead of pipelined per the plan (context window limitation).

## 2026-03-10 (continued)

### Developer Tests and Notes

- Completed quality review of 53 PGML files from test6 ch02 and ch05 staging directories
  - 100% pass on Concept, Diff-ans, and Diff-stem criteria
  - Sci-acc: 48 PASS, 3 FAIL, 2 WARN (91%)
  - Funct-RNG: 49 PASS, 4 FAIL (92%)
  - 7 files flagged for rejection or repair
- Key defects found: hemolysis/hypertonic mismatch in ch05_c1_p01; Na-K pump mechanism errors in ch05_c3_p13; unused RNG calls in ch02_c3_p08 and ch02_c3_p18; always-True answer in ch02_c1_p11; false statement is actually true in ch02_c3_p03
- Report written to [test6/reports/ch02_ch05_quality.md](../test6/reports/ch02_ch05_quality.md)
- Completed quality review of 63 PGML files from test6 ch28 and ch31 staging directories
  - Concept: 63/63 PASS (100%)
  - Answer differs: 53/63 PASS (84%); 10 files share same correct answer as textbook
  - Stem differs: 63/63 PASS (100%)
  - Scientific accuracy: 62/63 PASS (98%); ch28_c1_p21 misstates echinoderm circulatory fluid
  - Functional RNG: 43/63 PASS (68%); 18 files hardcode answer label while varying only scenario text
  - 1 critical bug: ch31_c4_p24 popup widget mismatch makes 3 of 4 seeds unanswerable
  - Report written to test6/reports/ch28_ch31_quality.md
- Completed quality review of 67 PGML files from test6 ch08 (photosynthesis) and ch12 (Mendel's heredity)
  - 100% pass on Concept, Diff-ans, Diff-stem criteria across all 67 files
  - Sci-acc: 53 PASS, 9 WARN, 5 FAIL (79% clean pass)
  - Funct-RNG: 32 PASS, 31 WARN, 4 FAIL (48% full variation; 46% cosmetic-only)
  - 7 files flagged for correction before production use
  - Key defects: antenna molecule oxygen production error (ch08_c2_p07); answer text in choice label (ch08_c3_p08); wrong photon count (ch08_c5_p10); incorrect Mendelian trait (ch12_c1_p06); contradictory carrier-male statements (ch12_c3_p28); wrong chocolate lab probability (ch12_c5_p20)
  - Report written to [test6/reports/ch08_ch12_quality.md](../test6/reports/ch08_ch12_quality.md)

## 2026-03-12

### Additions and New Features

- Created [docs/SWARM_TEST1_REPORT.md](SWARM_TEST1_REPORT.md): ch03 free-choice baseline report (8 coders, 37% coverage, extracted from SWARM_STRATEGIES.md)
- Created [docs/SWARM_TEST2_REPORT.md](SWARM_TEST2_REPORT.md): ch03 modular assignment report (8 coders, 100% coverage, extracted from SWARM_STRATEGIES.md)
- Created [docs/SWARM_TEST3_REPORT.md](SWARM_TEST3_REPORT.md): Biology 2e full-scale production report (47 chapters, 1,151+ files, extracted from SWARM_STRATEGIES.md)
- Created [docs/AGENT_SETUP.md](AGENT_SETUP.md): documents agent roles, relevant skills (webwork-writer, python-code-review, gas-town-workflow, etc.), escalation paths, and configuration tips
- Moved `chaotic_dispatch.py` to `scripts/multi_agent_folder_setup.py` (honest name: sets up folders and manifests for multi-agent work)

### Behavior or Interface Changes

- Restructured [docs/SWARM_STRATEGIES.md](SWARM_STRATEGIES.md): now contains only best practices and forward-looking recommendations; test results moved to individual `SWARM_TEST{N}_REPORT.md` files
- Removed automated referee/promote pipeline (scripts `referee_evaluate.py` and `promote_winners.py` deleted): validation-only scoring was not an effective quality gate, and promotion was just file copying
- Created `scripts/` directory for general-purpose utility scripts

### Removals and Deprecations

- Deleted `referee_evaluate.py`: validation-only scoring did not compare quality between competing versions
- Deleted `promote_winners.py`: trivial `shutil.copy2()` wrapper, manual curation is more appropriate
- Deleted `tests/test_referee_evaluate.py` and `tests/test_promote_winners.py`
- Deleted `tests/test_multi_agent_folder_setup.py` (script is a minor utility, tests not needed)
- Deleted unvetted test files: `tests/test_build_index.py`, `tests/test_pgml_checks.py`, `tests/test_pgml_macros.py`, `tests/test_pgml_template.py`, `tests/test_validate_pgml.py`

### Additions and New Features (continued)

- Added "Transformation requirements" section to `_prompts/_coder_briefing.md`: explicitly requires reworded stems, replaced distractors, meaningful `$rng->random()` randomization, varied difficulty, and mixed widget types -- prevents verbatim textbook copying
- Added verbatim-copy failure analysis section to [docs/SWARM_STRATEGIES.md](docs/SWARM_STRATEGIES.md): documents root cause (no anti-copying instruction), evidence (100% sampled files are word-for-word copies), impact (1,482 unusable files), fix, and prevention steps
- Added quality findings section to [docs/SWARM_TEST4_REPORT.md](docs/SWARM_TEST4_REPORT.md): documents verbatim content, decorative RNG, lack of widget diversity, and transformation requirements

### Behavior or Interface Changes

- Renamed pipeline scripts: `_chaotic_dispatch.py` to `chaotic_dispatch.py`, `_referee_evaluate.py` to `referee_evaluate.py`, `_promote_winners.py` to `promote_winners.py` (underscore prefix conflicts with temp-file convention)
- Updated all test imports and doc references to use new non-underscore script names

### Fixes and Maintenance

- Renamed 4 `.pg` files in `_staging/coder_2/bio2e_ch26_seed_plants/` to `.pgml` extension
- Recreated `referee_evaluate.py`, `promote_winners.py`, and `chaotic_dispatch.py` from test specifications (scripts were lost in worktree cleanup)
- All 36 tests pass (7 referee, 8 promote, 21 dispatch)

### Developer Tests and Notes

- Batch validation of 1,586 staging files: 34 errors, 1,093 warnings (mostly false-positive passthrough warnings from setup-block array syntax)

## 2026-03-11

### Additions and New Features

- Created [docs/SWARM_TEST4_REPORT.md](docs/SWARM_TEST4_REPORT.md): comprehensive report from Biology 2e swarm tests 3 and 4, including re-dispatch results, orphaned task analysis, cost estimates, model tier recommendations, and `bypassPermissions` alternatives

### Developer Tests and Notes

- Wave 3 re-dispatch: 12 coders (2 per chapter) generated ~293 PGML files for 6 previously zero-output chapters (ch01, ch14, ch16, ch19, ch21, ch24), bringing total to 1,479 files across all 47 chapters
- Swarm totals: 145 unique agents spawned (137 coders + 8 orchestrators), 318 tasks created, 55 orphaned pending tasks, ~3.9 MB of PGML output (129,408 lines)
- Cleaned up ~100 stale `in_progress` tasks from Waves 1-2 by marking them `completed`

### Decisions and Failures

- **Estimated swarm cost with all-Opus: ~$557.** Haiku coders would reduce to ~$137 (75% savings). Custom agent definitions in `~/.claude/agents/` support a `model` frontmatter field (`opus`, `sonnet`, `haiku`, `inherit`). The `CLAUDE_CODE_SUBAGENT_MODEL` env var provides a global override. No CLI workarounds needed.
- **`bypassPermissions` alternatives:** `mode: "auto"` and `mode: "acceptEdits"` are untested at swarm scale but could provide safer alternatives. `acceptEdits` auto-approves file writes but still prompts for Bash commands.
- **Optimal coders per chapter: 2** (not 8). Wave 3 re-dispatch with 2 coders per chapter achieved near-complete coverage. 8 coders per chapter creates task sprawl and orphaned work without proportional quality benefit.
- **No validation, referee, or promotion run.** All 1,479 PGML files remain in `_staging/coder_*/` directories unvalidated. Next session must run `validate_pgml.py`, `referee_evaluate.py`, and `promote_winners.py` before files are production-ready.

## 2026-03-10

### Additions and New Features

- Added `--include-all` flag to `chaotic_dispatch.py` to include problems without answers (required for textbooks like Biology 2e that have no answer key)
- Created `parse_biology2e.py` parser: extracts 1,515 problems across 47 chapters from OpenStax Biology 2e PDF text (146 visual connection, 804 review MC, 565 critical thinking)
- Created `tests/test_parse_biology2e.py` test suite for the Biology 2e parser

### Behavior or Interface Changes

- `build_manifest()` in `chaotic_dispatch.py` now accepts `include_all` parameter; when True, includes all problems regardless of answer availability

### Decisions and Failures

- **Orchestrator agent type cannot spawn sub-agents**: the `orchestrator` agent type does not have the `Agent` tool, making it unable to spawn coder sub-agents. Batch orchestrators (ch25-30-batch, ch31-36-batch, ch37-42-batch, ch43-47-batch) all failed to spawn coders. Some worked around this via `claude` CLI commands in Bash, which was unreliable. Use `parallelizer` or spawn coders directly from the team lead instead.
- **6 chapters produced zero PGML output** (ch01, ch14, ch16, ch19, ch21, ch24): root causes include empty assignments from pre-fix dispatch, failed orchestrator intermediaries, and coders that stalled silently. All need re-dispatch with direct coder spawning.
- **bypassPermissions mode is mandatory** for coder agents in swarms. Without it, every file write and bash command prompts the user for approval, making the swarm unusable.
- **Self-validation beats tool-based validation** during generation. Coders running `validate_pgml.py` caused permission prompts and for-loop complaints. Instruct coders to re-read files instead; batch validation as a separate post-step.
- **Coder deny-list required**: coders must be explicitly told "DO NOT run validate_pgml.py, for loops, or claude commands" to prevent permission prompt interruptions.
- **4 files used wrong .pg extension** instead of .pgml (ch26 coder_2). File naming conventions need enforcement via validation.
- **Task list sprawl**: 305+ tasks created across the swarm, many orphaned. Use coarser per-chapter tasks instead of per-coder tasks in future runs.

### Developer Tests and Notes

- Swarm test 3 (Biology 2e, 47 chapters): 1,151+ PGML files generated across 41/47 chapters, 8 coders per chapter (Wave 1) + coder_2 wave for ch25-47, ~5 min generation time, 0 file conflicts
- Peak output: ch11 (113 files), ch07 (112 files), ch10 (88 files)
- Updated [docs/SWARM_STRATEGIES.md](docs/SWARM_STRATEGIES.md) with full test 3 results, failure analysis, and production pipeline recommendations

## 2026-03-09

### Additions and New Features

- Added `--prefix` argument to `chaotic_dispatch.py` (default: `ch`); all functions (`find_chapter_json`, `extract_slug`, `create_staging_dirs`, `write_manifest`, `write_assignments`) now accept a `prefix` parameter, enabling `bio2e_ch` prefix for Biology 2e chapters while preserving existing Tymoczko behavior unchanged

### Developer Tests and Notes

- Added 6 prefix tests to `tests/test_chaotic_dispatch.py`: `test_extract_slug_bio2e_prefix`, `test_find_chapter_json_bio2e_prefix`, `test_create_staging_dirs_bio2e_prefix`, `test_write_manifest_bio2e_prefix`, `test_write_assignments_bio2e_prefix`, `test_default_prefix_unchanged` (21 total tests, all passing)

## 2026-03-07

### Additions and New Features

- Added modular problem assignment to `chaotic_dispatch.py`: new `assign_problems_modular()` function distributes problems across coders via `(index % num_coders) + 1`, new `write_assignments()` writes per-coder `assignments.yaml` files, new `--assign` flag (choices: `none`, `modular`), and `print_assignment_summary()` for human-readable output
- Added deduplication to `build_manifest()` in `chaotic_dispatch.py`: keeps only the first entry per problem number, fixing duplicate problem 4 in ch03

### Developer Tests and Notes

- Added 6 new tests to `tests/test_chaotic_dispatch.py`: `test_build_manifest_deduplicates`, `test_assign_problems_modular_basic`, `test_assign_problems_modular_optional`, `test_assign_problems_modular_uneven`, `test_assign_problems_modular_ch03`, `test_write_assignments` (15 total tests, all passing)
- Swarm test 2 (ch03, modular assignment): 8 coders, 43 files generated, 0 validation errors, 18/18 problems covered (100%), 6 competitions, 12 singles, 0 gaps -- vs test 1 which had 42 files, 7/19 coverage (37%), 12 gaps
- Updated [docs/SWARM_STRATEGIES.md](SWARM_STRATEGIES.md) with test 2 results, comparison table, and conclusions; modular assignment validated as default dispatch strategy

### Decisions and Failures

- Modular assignment uses positional index (not problem number) for coder assignment, producing even distribution even when problem numbers have gaps (e.g., no problem 8 in ch03)
- Free picks still herd on easy problems (p11 and p14 attracted all 8 coders), but required assignments guarantee breadth; this tradeoff is acceptable
- 12 of 18 problems have only 1 version (no competition); future improvement could assign each problem to 2 coders

## 2026-03-06

### Additions and New Features

- Added `chaotic_dispatch.py`: reads a chapter JSON file and builds a problem manifest (YAML) plus staging directories (`_staging/coder_{1..N}/`, `_staging/merged/`) for the chaotic PGML generation pipeline; accepts `--chapter` and `--coders` arguments
- Added `promote_winners.py`: promotes referee-selected PGML winners from `_staging/merged/` to `output/`; accepts `--chapter N` (required) and `--dry-run`; loads referee report from `reports/referee/ch{NN}_referee_report.yaml`, skips `gap` and `needs_revision` problems, validates each merged file via `validate_pgml.validate_file()`, copies passing files to `output/ch{NN}_{slug}/`, and prints a promotion summary
- Added `referee_evaluate.py`: staging scanner and referee report generator; accepts `--chapter N`, loads `_staging/ch{NN}_manifest.yaml`, scans `_staging/coder_*/` for competing PGML files, validates each via `validate_pgml.validate_file()`, groups by problem number, and writes a YAML referee report skeleton to `reports/referee/ch{NN}_referee_report.yaml` with per-problem action classification (gap/single/competition) and summary statistics
- Created [docs/SWARM_STRATEGIES.md](SWARM_STRATEGIES.md): comprehensive lessons learned from the ch03 swarm test (8 coders, 19 problems, 42 files); covers herding behavior, widget diversity emergence, coverage gaps, deterministic problem assignment, two-wave dispatch, and metrics to track
- Created `_prompts/_coder_briefing.md`: guidance document for AI coder agents generating WeBWorK PGML question files; covers file structure, widget types, RNG patterns, PGML formatting rules, validation workflow, file naming, and quality guidelines with condensed examples for RadioButtons, PopUp, and CheckboxList widgets
- Created `_prompts/_referee_rubric.md`: scoring rubric for referee agents evaluating competing PGML question files; covers accuracy (3x), distractors (2x), widget fit (2x), randomization (2x), pedagogy (1x) with 50-point max, merge guidelines, gap handling, and YAML report format
- Created repo scaffolding: `VERSION` (26.03), `pyproject.toml`, `pip_requirements.txt`
- Added [docs/INSTALL.md](INSTALL.md), [docs/USAGE.md](USAGE.md), [docs/CODE_ARCHITECTURE.md](CODE_ARCHITECTURE.md), [docs/FILE_STRUCTURE.md](FILE_STRUCTURE.md)
- Updated [README.md](../README.md) with project description, quick start, and doc links
- Updated `.gitignore` for `structured/`, `reports/`, `output_smoke/`, `output/`, `concepts/`, `__pycache__/`
- Updated `.gitignore` to exclude `_staging/` and `_prompts/` directories (chaotic pipeline working data)
- Added `textbook_clean.py`: text cleaning utilities with `clean_text()`, `remove_page_headers()`, `join_split_lines()`, `normalize_whitespace()`
- Added `pgml_template.py`: reusable template builder for WeBWorK PGML files with `build_header_block()`, `build_preamble()`, `build_solution_block()`, `build_footer()`
- Added `textbook_problems.py`: problem extraction from chapter text with `extract_problems()`, `extract_challenge_problems()`, `extract_data_interpretation_problems()`
- Added `pgml_checks.py`: PGML source lint checks (HTML whitelist, raw passthrough, color usage, variable scoping, structure matching, inline graders, beginproblem detection) with `run_all_checks()` convenience function
- Added `build_index.py`: concept index builder and coverage reporter with `load_concepts()`, `scan_pgml_files()`, `build_concept_index()`, `generate_coverage_report()`; produces `output/concept_index.yaml` and `reports/coverage_report.txt`
- Added `textbook_answers.py`: answer key parser with `detect_answer_section_boundaries()` and `extract_answer_key()` for extracting per-chapter numbered answers from the textbook's "Answers to Problems" section
- Added `validate_pgml.py`: unified PGML file validator combining `pgml_checks` and `pgml_macros` checks with ASCII compliance, Context() call, loadMacros() presence, and PGML_SOLUTION detection; supports file or directory input with rich colored output fallback to plain text
- Added `textbook_chapters.py`: chapter boundary detection, section extraction, and key terms parsing with `detect_chapter_boundaries()`, `extract_sections()`, `extract_key_terms()`; identifies all 41 chapters in the Tymoczko 3rd edition textbook body text, filtering out TOC and section intro headings
- Added `parse_textbook.py`: integration script that reads the raw textbook, splits into chapters, and writes per-chapter JSON files to `structured/chapters/`; extracts sections, key terms, problems (standard + challenge + data interpretation), and answers for all 41 chapters (730 problems, 781 key terms total)
- Added `pgml_macros.py`: widget-to-macro mapping with `macro_for_widget()`, `detect_widgets_used()`, `extract_loaded_macros()`, `validate_macro_widget_pairing()`
- Added `validate_pgml_render.py`: renderer API validator with `render_pgml()`, `check_render_result()`, `validate_file()`; sends PGML to local renderer and checks for errors
- Created `concepts/ch03_concepts.yaml`: concept map for ch03 (Amino Acids) with 6 concepts covering structure, codes, stereochemistry, side chains, ionization, and essential amino acids
- Created proof-of-concept PGML: `output/ch03_amino_acids/ch03_side_chain_classification.pgml` -- Level 2 RadioButtons question on amino acid side chain classification with randomized amino acid selection, validated via renderer
- Created `output/ch03_amino_acids/ch03_amino_acid_structure.pgml`: Level 1 RadioButtons question on alpha carbon components with randomized component selection
- Created `output/ch03_amino_acids/ch03_one_letter_codes.pgml`: Level 1 RadioButtons question on amino acid one-letter codes with randomized amino acid and distractor selection
- Created `output/ch03_amino_acids/ch03_stereochemistry.pgml`: Level 2 RadioButtons question on L/D amino acids, chirality, and glycine achirality with 3 randomized question variants
- Created `output/ch03_amino_acids/ch03_ionization_and_charge.pgml`: Level 3 RadioButtons question on amino acid net charge at different pH values using pKa data for 8 simple amino acids
- Created `output/ch03_amino_acids/ch03_essential_amino_acids.pgml`: Level 1 RadioButtons question on essential vs nonessential amino acid classification with all 20 standard amino acids
- Created concept YAMLs for chapters 17-24: `concepts/ch17_concepts.yaml` through `concepts/ch24_concepts.yaml` (33 concepts total covering gluconeogenesis, PDH complex, citric acid cycle, electron transport, proton-motive force, light reactions, Calvin cycle, glycogen degradation)
- Created 33 PGML files across 8 chapters (ch17-24): 5 for ch17 (bypass reactions, energy cost, reciprocal regulation, Cori cycle, precursors), 3 for ch18 (PDH complex, coenzymes, regulation), 4 for ch19 (cycle overview, enzymes, regulation, glyoxylate), 4 for ch20 (redox potentials, ETC complexes, inhibitors, ROS), 5 for ch21 (ATP synthase, PMF, shuttles, ATP yield, uncoupling), 4 for ch22 (chloroplast structure, photosystems, Z scheme, photosynthetic ATP), 4 for ch23 (Calvin stages, rubisco, C4/CAM, regulation), 4 for ch24 (breakdown steps, phosphorylase regulation, signal cascade, tissue differences)
- M3 full generation: created concept YAMLs and PGML questions for all 41 chapters (181 concepts, 181 PGML files, 100% coverage)
  - ch01-02, ch04-08: 26 PGML files covering biochemistry unity, water/weak bonds, protein structure, protein techniques, enzyme action, kinetics/regulation, mechanisms/inhibitors
  - ch09-16: 37 PGML files covering hemoglobin, carbohydrates, lipids, membranes, signal transduction, digestion, metabolism basics, glycolysis
  - ch25-33: 39 PGML files covering glycogen synthesis, pentose phosphate pathway, fatty acid degradation/synthesis, lipid synthesis, amino acid degradation/synthesis, nucleotide metabolism, DNA/RNA structure
  - ch34-41: 38 PGML files covering DNA replication, DNA repair, bacterial RNA synthesis, eukaryotic gene expression, RNA processing, genetic code, protein synthesis, recombinant DNA
- Regenerated `output/concept_index.yaml` and `reports/coverage_report.txt` with all 181 concepts and 181 PGML files

### Developer Tests and Notes

- Added `tests/test_chaotic_dispatch.py`: 9 pytest tests for `chaotic_dispatch.py` pure functions (`extract_slug`, `build_manifest`, `create_staging_dirs`, `write_manifest`, `find_chapter_json`)
- Added `tests/test_promote_winners.py`: 8 pytest tests for `promote_winners.py` pure functions (`find_merged_file`, `build_dest_path`, `load_referee_report`, `promote_file`) covering path construction, zero-padding, YAML loading, missing report error, wet/dry run copy behavior, and directory creation
- Added `tests/test_referee_evaluate.py`: 7 pytest tests for `referee_evaluate.py` pure functions (`load_manifest`, `scan_staging_files`, `build_report`, `write_report`) covering YAML manifest loading, missing manifest error, PGML file grouping by problem number, empty staging scan, all-gaps report, mixed gap/single/competition report, and YAML report serialization

### Fixes and Maintenance

- Fixed `referee_evaluate.py` `build_report()`: replaced undefined `problem_list` with `problem_numbers` on line 191 (NameError crash when assembling the summary dict)
- Fixed PGML bold rendering in 12 files (ch01, ch02, ch04, ch05, ch08): replaced `*[$var]*` with HTML bold passthrough pattern (`$var_bold = "<b>$var</b>"` plus `[$var_bold]*` in PGML blocks)
- Fixed PGML solution text in `ch02_ph_and_pka.pgml`: removed square brackets from `[H+]` and `[OH-]` in BEGIN_PGML_SOLUTION to prevent PGML parser from treating them as blocks

### Decisions and Failures

- PG safe compartment blocks `sort()` -- use pre-sorted arrays instead of `sort keys %hash`
- PGML `*bold*` does not work reliably with variable interpolation; use HTML `<b>` tags via `[$var]*` passthrough instead

- Chose CalVer 26.03 for initial version
- PGML square brackets in solution text (e.g. `[A-]/[HA]`) get parsed as PGML blocks; avoid raw brackets in BEGIN_PGML_SOLUTION and use plain text equivalents instead
- Pipeline architecture: 5 layers (ingestion, concepts, questions, validation, index)
- Deterministic Python for parsing/validation; Claude agents for concept extraction and question generation
- Chaotic pipeline design: 8 independent coders per chapter with full creative freedom, referee scoring/selection, staged promotion; produces widget diversity through organic overlap rather than rigid persona assignment
