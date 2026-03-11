# Swarm test 3: Biology 2e full-scale production (47 chapters)

## Test design

Full-scale production run across all 47 chapters of OpenStax Biology 2e. 1,515 problems extracted (146 visual connection, 804 review MC, 565 critical thinking). No answer key available in the textbook, so `--include-all` flag was used. Modular assignment with 8 coders per chapter for early chapters, 1-2 coders for later chapters, plus a second wave of coder_2 agents for ch25-47.

## Results

| Metric | Value |
| --- | --- |
| Total PGML files generated | 1,151+ |
| Chapters with output | 41 / 47 (87%) |
| Chapters with zero output | 6 (ch01, ch14, ch16, ch19, ch21, ch24) |
| Wrong file extension (.pg not .pgml) | 4 files (ch26 coder_2) |
| Peak files per chapter | 113 (ch11), 112 (ch07) |
| Coder slots used | 8 (coder_1=265, coder_2=227, coders 3-8 lower) |
| Wall time for full swarm | ~5 minutes generation, ~30 min with coordination overhead |

## Distribution by chapter tier

| Tier | Chapters | Files per chapter | Notes |
| --- | --- | --- | --- |
| Heavy (50+) | ch07-12 | 51-113 | Wave 1 with 8 coders, ran longest |
| Medium (20-49) | ch05-06, ch13, ch15, ch17-18, ch20, ch22-23 | 21-57 | Mix of batch orchestrators and direct coders |
| Light (5-19) | ch25-47 | 3-19 | coder_1 + coder_2 wave |
| Zero | ch01, ch14, ch16, ch19, ch21, ch24 | 0 | See failure analysis below |

## What worked

### Modular assignment at scale
- Modular assignment scaled from 18 problems to 1,515 problems without modification.
- `multi_agent_folder_setup.py` with `--include-all` and `--prefix bio2e_ch` handled all 47 chapters.
- Each coder received a clear `assignments.yaml` with required and optional lists.

### bypassPermissions mode is essential
- Coders spawned with `mode: "bypassPermissions"` ran autonomously without user interruption.
- Without this mode, every file write and bash command prompted the user for approval, making the swarm unusable.
- This was the single most important operational lesson.

### Self-validation over tool-based validation
- Original briefing told coders to run `validate_pgml.py` after each file.
- This caused two problems: (1) user got prompted for permission on every validation command, (2) coders used for loops to batch-validate, which also prompted.
- Solution: instruct coders to self-validate by re-reading files after writing. Coders checked their own output for DOCUMENT/ENDDOCUMENT, BEGIN_PGML/END_PGML, loadMacros, etc.
- Validation should be a separate batch step run by a tester agent after all coders finish.

### Two-wave coder strategy
- Wave 1: 8 coders per chapter for early chapters (heavy competition).
- Wave 2: coder_2 agents for ch25-47 (added competition to single-coverage chapters).
- This produced 12+ files per chapter for ch25-47, up from 5-8 with coder_1 alone.

### Direct coder spawning over batch orchestrators
- Individual `Agent` calls with `subagent_type: "coder"` were the most reliable spawning method.
- Each coder got a focused prompt with exact file paths and rules.

## What did not work

### Orchestrator agents cannot spawn sub-agents
- The `orchestrator` agent type does NOT have the `Agent` tool in its toolset.
- Batch orchestrators (ch25-30-batch, ch31-36-batch, ch37-42-batch, ch43-47-batch) could not spawn coder sub-agents.
- Some orchestrators worked around this by running `claude` CLI commands via Bash, which was unreliable and caused permission prompts.
- Fix: use `parallelizer` agent type (has Agent tool) or spawn coders directly from the team lead.

### Six chapters produced zero output
- ch01, ch14, ch16, ch19, ch21, ch24 all have zero PGML files despite having coders assigned.
- Root cause analysis:
  - **ch01**: coders were among the first spawned, before `--include-all` fix. They received empty assignments.yaml and may have stalled.
  - **ch14, ch16, ch19**: spawned via batch orchestrators that used `claude` CLI workaround. These processes may have failed silently or produced output in wrong directories.
  - **ch21**: spawned via ch21-batch orchestrator, coders show in_progress but no output visible.
  - **ch24**: spawned via ch24-batch orchestrator which was shut down early.
- Lesson: coders spawned through indirect methods (orchestrator -> claude CLI -> coder) are unreliable. Always spawn directly.

### Empty assignments bug (Wave 1)
- Biology 2e has no answer key. The original `build_manifest()` filtered problems by whether they had answers.
- All 47 chapters produced empty manifests (0 problems) until the `--include-all` flag was added.
- Wave 1 coders (ch01-ch12) were spawned before the fix. Many received empty `assignments.yaml` files.
- Some coders used "creative freedom" to generate files anyway by reading the manifest directly, but others stalled.
- Lesson: always verify manifest content before spawning coders. A smoke test (check problem count > 0) should gate dispatch.

### Wrong file extensions
- 4 files in ch26 coder_2 used `.pg` extension instead of `.pgml`.
- The coder briefing specifies `.pgml` but one coder ignored this.
- Lesson: file naming conventions should be enforced by validation, not just documented.

### Coders running unauthorized commands
- Some coders tried to run `claude --print-agent-details` (a Claude Code introspection command).
- Some coders ran for loops to batch-validate files.
- Some coders ran `validate_pgml.py` despite being told not to.
- Each of these triggered permission prompts that interrupted the user.
- Lesson: the coder briefing must include an explicit deny-list of commands. "DO NOT run validate_pgml.py, for loops, or claude commands" was effective once added.

### Task list sprawl
- 305+ tasks were created across the swarm.
- Many tasks remained in `pending` or `in_progress` state for coders that were shut down or never spawned.
- The task list became difficult to scan for actionable items.
- Lesson: use fewer, coarser tasks (per-chapter instead of per-coder), or clean up completed/orphaned tasks more aggressively.

### Idle notification spam
- Completed coders sent repeated idle notifications to the team lead.
- Some agents sent 5-10 idle notifications in rapid succession.
- This cluttered the team lead's inbox and made it harder to spot real messages.
- Lesson: shut down completed coders immediately after they report completion. Do not wait for batch shutdown.

## Scaling observations

- **Coder throughput**: 5-8 files per coder per chapter (consistent with ch03 test).
- **Diminishing returns**: 8 coders per chapter produces heavy overlap on popular problems. 2-4 coders per chapter is sufficient for good coverage with competition.
- **Sweet spot**: 2 coders per chapter guarantees competition on every assigned problem. 4 coders adds widget diversity. 8 coders is overkill for most chapters.
- **Parallel capacity**: ~100 simultaneous coder agents ran without file conflicts. The staging directory structure (`coder_N/chNN_slug/`) prevents all collisions.
- **Context window**: the team lead's context fills up fast managing 100+ agents. Batch operations (spawn 16 coders, shut down 20 coders) are more efficient than individual management.
