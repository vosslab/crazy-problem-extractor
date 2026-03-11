# Swarm strategies

Best practices for the chaotic competitive pipeline for PGML question generation.

## Overview

The chaotic pipeline dispatches multiple independent AI coders to the same chapter simultaneously, with no coordination between them. Each coder reads the textbook source directly, identifies problems, and generates PGML files using their own widget type and approach. Batch validation filters the output afterward.

## Anti-pattern: deterministic parsing and scaffolding

Do not use deterministic Python scripts to pre-parse textbook content, build manifests, or create staging directories. Earlier iterations of this project used `parse_textbook.py`, `parse_biology2e.py`, and `multi_agent_folder_setup.py` to extract problems into structured JSON and then feed those to coders. This approach is wrong for several reasons:

- **It removes intelligence from the coder.** The whole point of using AI coders is that they can read the textbook, understand the problems, and generate creative PGML questions. A deterministic parser strips out the understanding step and reduces coders to template-fillers.
- **Parsed output is lossy.** OCR artifacts, garbled text, and context loss in the structured JSON caused coders to produce verbatim copies instead of transformed questions.
- **Scaffolding scripts duplicate what agents do naturally.** Directory creation, manifest building, and problem assignment are trivial tasks that a team lead agent handles inline. They do not need dedicated scripts.
- **It creates a false sense of progress.** Running a parser and seeing 1,515 problems extracted feels productive, but the quality bottleneck is in the PGML generation, not the parsing.

The correct approach: give each coder the raw textbook chapter (or a PDF page range) and let them extract, understand, and transform the problems themselves.

## Dispatch strategies

### Fewer coders per chapter

- 2 coders per chapter guarantees competition on every assigned problem
- 4 coders adds widget diversity
- 8 coders is overkill for most chapters (heavy overlap, diminishing returns)

### Two-wave dispatch

- **Wave 1**: coders with full creative freedom (broad coverage)
- **Wave 2**: targeted coders dispatched to fill gaps from Wave 1

## Agent spawning

### Direct spawning (required)

Always spawn coders directly from the team lead via the `Agent` tool. Never use orchestrator intermediaries -- the `orchestrator` agent type does not have access to the `Agent` tool and cannot spawn sub-agents. Use `parallelizer` if an intermediary is needed.

### bypassPermissions mode

Mandatory for all coder agents. Without it, every file write and bash command prompts the user for approval, making the swarm unusable.

Alternatives to explore: `mode: "auto"` (untested at swarm scale) and `mode: "acceptEdits"` (auto-approves file edits only).

### Coder deny list

Coders must be explicitly told what NOT to do in the prompt:

```
- DO NOT run validate_pgml.py
- DO NOT use for loops in Bash
- DO NOT run claude commands
- DO NOT run any validation scripts
- Use .pgml extension ONLY (never .pg)
```

### Self-validation over tool-based validation

Instruct coders to re-read files after writing instead of running `validate_pgml.py`. Batch validation should be a separate post-generation step run by a tester agent.

## Model tiers

| Role | Recommended model | Rationale |
| --- | --- | --- |
| Team lead / orchestrator | Opus or Sonnet | Needs complex coordination, error recovery |
| Coder agents | Haiku or Sonnet | Template-following, well-defined output format |
| Referee / reviewer | Sonnet | Quality judgment, comparative scoring |
| Tester / validator | Haiku | Mechanical validation, pass/fail checks |

Custom agent definitions in `~/.claude/agents/` support a `model` field in YAML frontmatter. The `CLAUDE_CODE_SUBAGENT_MODEL` env var provides a global override.

## Transformation requirements

Coders must reword stems, replace distractors, add meaningful `$rng->random()` randomization, vary difficulty, and mix widget types. Without explicit anti-copying instructions, coders produce verbatim copies of textbook questions. See [docs/SWARM_TEST4_REPORT.md](SWARM_TEST4_REPORT.md) for the failure analysis.

## Recommended production pipeline

1. **Assign chapters**: team lead assigns chapter ranges to coders (e.g., "generate PGML questions for chapter 3")
2. **Spawn coders**: directly from team lead, `bypassPermissions` mode, explicit deny list in prompt; each coder reads the textbook source directly
3. **Monitor**: check file counts periodically. Shut down completed coders immediately.
4. **Validate**: batch run `validate_pgml.py` on all generated files (tester agent)
5. **Curate**: manually review and move best files to `output/`

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

## Quality selection

No automated referee has proven effective yet. `validate_pgml.py` catches structural errors but cannot judge pedagogical quality. Manual review or a future AI referee step is needed to select the best version when multiple coders produce competing files for the same problem.

## File organization

```
_staging/
  coder_1/ch03_amino_acids/       # coder 1 output
    ch03_p01.pgml
    ...
  coder_2/ch03_amino_acids/       # coder 2 output (overlapping problems)
    ch03_p01.pgml
    ...

output/ch03_amino_acids/          # curated final files
  ch03_p01.pgml
  ...
```

## Open questions

- Should the referee keep multiple "best" versions for the same problem as separate question variants?
- Should Tier 3 (calculation) problems get a specialized prompt with formula examples?
- Can we detect herding early (after 2-3 coders finish) and redirect remaining coders to gaps?
- Should each problem be assigned to 2 coders (not 1) to guarantee competition on every problem?
- Should coder agents be given a strict time limit to prevent indefinite in_progress states?
- Should file extension (.pgml vs .pg) be validated at write time by the coder, or only by the batch validator?

## Test reports

- [docs/SWARM_TEST1_REPORT.md](SWARM_TEST1_REPORT.md) -- ch03 free-choice baseline (8 coders, 37% coverage)
- [docs/SWARM_TEST2_REPORT.md](SWARM_TEST2_REPORT.md) -- ch03 modular assignment (8 coders, 100% coverage)
- [docs/SWARM_TEST3_REPORT.md](SWARM_TEST3_REPORT.md) -- Biology 2e full-scale (47 chapters, 1,151+ files)
- [docs/SWARM_TEST4_REPORT.md](SWARM_TEST4_REPORT.md) -- Biology 2e re-dispatch and quality findings
