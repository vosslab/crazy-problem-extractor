# Swarm test 6 report

Date: 2026-03-10
Chapters: 10 (ch02, ch05, ch08, ch12, ch18, ch22, ch28, ch31, ch40, ch45)
Coders: 50 Haiku agents (5 per chapter)
Reviewers: 5 Sonnet agents (2 chapters each)

## Results vs targets

| Metric | Test 5 | Test 6 target | Test 6 actual | Status |
| --- | --- | --- | --- | --- |
| File coverage | 99.4% (331/333) | 100% | 100% (315/315) | OK |
| Lint pass (structural) | 100% | 100% | 99.0% (312/315) | OK |
| RNG audit pass | 65.6% | >90% | 99.0% (312/315) | OK |
| Meaningful RNG (reviewer) | -- | >90% | ~53% | MISS |
| RadioButtons share | 58% | <45% | 41.3% (130) | OK |
| CheckboxList share | 24% | >25% | 30.5% (96) | OK |
| PopUp share | 10% | >15% | 19.7% (62) | OK |
| Numeric share | 2% | >8% | 8.6% (27) | OK |
| Scientific accuracy | -- | >95% | 89.2% | MISS |
| Quality review pass | -- | >85% | 92.1% (290/315) | OK |

## Key improvements over test 5

1. **Widget distribution**: Explicit per-problem widget quotas in `assignments.json` achieved target distribution. Global assignment (not per-coder) was needed because per-coder chunks were too small to reach Numeric in the 10-element cycle.

2. **RNG audit pass rate**: 99.0% vs 65.6%. Mandatory briefing language ("every file MUST call `$rng->random()` at least once") and deny list rule ("DO NOT write files where `$rng->srand` appears but `$rng->random` does not") drove near-universal structural compliance.

3. **File coverage**: 100% (315/315) vs 99.4% (331/333). All assigned problems produced files.

## New findings from quality review

### Cosmetic-only RNG (~100 files, ~32%)

The biggest quality gap. Many files call `->random()` but use it only to vary scenario text (organism name, location, etc.) while the correct answer never changes. This passes the structural RNG audit but provides minimal pedagogical variation. The briefing said RNG "must select content that changes the correct answer" but coders often satisfied this loosely.

### Hardcoded answer labels (~18 files)

Mostly from ch28 coder 1. The correct answer is always at position "A" or "B" regardless of seed. Students who notice the pattern can exploit it. Fix: shuffle the options array.

### Scientific accuracy errors (34 files flagged)

8 critical bugs where the PGML presents a factually wrong statement as the correct answer or generates unanswerable questions. The most common patterns:

- Parallel arrays where some entries contain incorrect biology
- PopUp/RadioButton options that don't include all possible `$answer` values
- Mismatched scenario/answer pairings across random indices

### Files sorted

- Validated: 290 (92.1%)
- Rejected: 25 (7.9%)
- Rejected files copied to `test6/rejected/` for repair

## Architecture

### Pipeline

1. `generate_assignments.py` creates `assignments.json` with per-problem widget quotas
2. 50 Haiku coders dispatched in a single batch, `bypassPermissions` mode
3. Coders self-lint via `lint_pg_via_renderer_api.py`
4. `check_rng_usage.py` audits structural RNG compliance
5. 5 Sonnet reviewers evaluate 5-point quality rubric per file
6. `_sort_files.py` sorts into `validated/` and `rejected/`

### Reviewer rubric (5 criteria)

1. Same concept as assigned problem
2. Different correct answer from textbook
3. Different question stem from textbook
4. Scientific accuracy
5. Functional RNG (different indices produce different answers)

### Timing

- Coder phase: ~35 minutes wall time (50 parallel Haiku agents)
- Reviewer phase: ~4 minutes wall time (5 parallel Sonnet agents)
- Total: ~40 minutes

## Recommendations for test 7

1. **Enforce answer-varying RNG**: Add a reviewer criterion that checks whether the correct answer string or index actually changes across at least 2 pick_index values. Flag cosmetic-only RNG.

2. **Validate PopUp/RadioButton option coverage**: Add a lint rule that checks every possible `$answer` value appears in the widget option list.

3. **Shuffle answer positions**: Add briefing instruction to randomize the position of the correct answer in RadioButtons and CheckboxList widgets.

4. **Two-pass generation**: Run a quick Haiku repair pass on the 25 rejected files rather than full re-generation.

5. **Track wall time formally**: See wall time measurement notes below.

## Wall time measurement plan

Test 6 had no formal timing. The team lead should capture timestamps at each pipeline phase boundary. All timing lives in the team lead's logic -- no changes to coder or reviewer agents are needed.

### Where to capture timestamps

| Event | How to measure | Variable name |
| --- | --- | --- |
| Pipeline start | `time.time()` before any agent spawning | `t_start` |
| All coders launched | `time.time()` after the last `Agent` tool call returns | `t_coders_launched` |
| Each coder completes | Parse `duration_ms` from task notification | per-coder duration |
| Last coder completes | `time.time()` when the final coder notification arrives | `t_coders_done` |
| Post-coder audit done | `time.time()` after `check_rng_usage.py` finishes | `t_audit_done` |
| All reviewers launched | `time.time()` after the last reviewer `Agent` call | `t_reviewers_launched` |
| Last reviewer completes | `time.time()` when the final reviewer notification arrives | `t_reviewers_done` |
| Post-processing done | `time.time()` after file sorting and report writing | `t_done` |

### How to implement

The team lead agent cannot run `time.time()` directly (it is an LLM, not a Python process). Instead:

1. **Use Bash `date +%s`** at each phase boundary to capture Unix timestamps. Store in shell variables or a temp file.

2. **Parse `duration_ms` from task notifications.** Every background agent completion notification includes `<duration_ms>`. Record these per agent.

3. **Write a timing log.** After each phase, append a line to `testN/reports/timing.md`:

```markdown
| Phase | Start | End | Wall time |
| --- | --- | --- | --- |
| Coder dispatch | 14:00:00 | 14:00:45 | 45s |
| Coder execution | 14:00:45 | 14:35:12 | 34m 27s |
| RNG audit | 14:35:12 | 14:35:30 | 18s |
| Reviewer dispatch | 14:35:30 | 14:35:55 | 25s |
| Reviewer execution | 14:35:55 | 14:40:42 | 4m 47s |
| Post-processing | 14:40:42 | 14:42:10 | 1m 28s |
| **Total** | **14:00:00** | **14:42:10** | **42m 10s** |
```

4. **Per-agent stats.** Record each agent's `duration_ms` and `total_tokens` from the task notification. Compute min/max/median coder duration to identify stragglers.

### What to report

- Total wall time (pipeline start to post-processing done)
- Coder phase wall time (launch to last completion)
- Reviewer phase wall time (launch to last completion)
- Slowest coder duration and identity (straggler detection)
- Median coder duration
- Total tokens consumed (sum of all agent `total_tokens`)

### Practical pattern

```bash
# at each phase boundary, run:
date +%s > /tmp/t_phase_name
```

Then at the end, read all timestamps and compute deltas. Or simpler: just note the clock time in a running markdown log as each phase completes.

## File inventory

```
test6/
  staging/       315 PGML files (10 chapter directories)
  validated/     290 files passing all quality criteria
  rejected/       25 files with at least one critical failure
  reports/
    rng_audit.md
    ch02_ch05_quality.md
    ch08_ch12_quality.md
    ch18_ch22_quality.md
    ch28_ch31_quality.md
    ch40_ch45_quality.md
    summary.md
  prompts/
    assignments.json
    coder_briefing.md
    bio2e_ch*_manifest.yaml (10 files)
    Biology2e-WEB.txt (symlink)
```

## Test reports

- [docs/SWARM_TEST1_REPORT.md](SWARM_TEST1_REPORT.md) -- ch03 free-choice baseline
- [docs/SWARM_TEST2_REPORT.md](SWARM_TEST2_REPORT.md) -- ch03 modular assignment
- [docs/SWARM_TEST3_REPORT.md](SWARM_TEST3_REPORT.md) -- Bio2e full-scale
- [docs/SWARM_TEST4_REPORT.md](SWARM_TEST4_REPORT.md) -- Bio2e re-dispatch and quality
- [docs/SWARM_TEST5_REPORT.md](SWARM_TEST5_REPORT.md) -- Bio2e pipelined generation
- [docs/SWARM_TEST6_REPORT.md](SWARM_TEST6_REPORT.md) -- Bio2e quality gates (this report)
