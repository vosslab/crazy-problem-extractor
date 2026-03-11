# Changelog

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
