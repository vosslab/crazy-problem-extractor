# Swarm test 4: Biology 2e re-dispatch and lessons learned

Report from the Biology 2e full-scale production swarm (tests 3 and 4 combined).

## Run summary

| Metric | Value |
| --- | --- |
| Textbook | OpenStax Biology 2e |
| Chapters | 47 |
| Total problems in manifests | ~1,515 |
| Total PGML files generated | 1,479+ |
| Chapters with output | 47/47 (100%) |
| Coders spawned (Wave 1) | ~100 (8 per chapter, ch01-ch13) |
| Coders spawned (Wave 2) | ~50 (coder_2 for ch25-ch47) |
| Coders spawned (Wave 3 re-dispatch) | 12 (2 per chapter, 6 chapters) |
| Peak task list size | 318 tasks |
| Orphaned pending tasks | 55 |

## Wave 3 re-dispatch results

Six chapters produced zero PGML output from Waves 1-2. All six were re-dispatched with 2 direct coders each (coder_9, coder_10) using `bypassPermissions` mode.

| Chapter | Title | Problems | Coder 9 | Coder 10 | Total |
| --- | --- | --- | --- | --- | --- |
| ch01 | The Study of Life | 23 | 21 | 21 | 42 |
| ch14 | DNA Structure and Function | 37 | 24 | 28 | 52 |
| ch16 | Gene Expression | 40 | 29 | 21 | 50 |
| ch19 | The Evolution of Populations | 23 | 23 | 23 | 46 |
| ch21 | Viruses | 34 | 26 | 23 | 49 |
| ch24 | Fungi | 34 | 28 | 26 | 54 |

All 6 chapters now have output. Re-dispatch added ~293 files, bringing total from ~1,200 to ~1,479.

### Why re-dispatch succeeded

- **Direct coder spawning** (no intermediary orchestrator or batch agents)
- **bypassPermissions mode** prevented permission prompt stalls
- **Explicit deny list** in the prompt (no validate_pgml.py, no for loops, no claude commands)
- **Full problem list** in the prompt (coders knew exactly what to generate)

### Root causes of original zero-output

| Chapter | Root cause |
| --- | --- |
| ch01 | Empty assignments from pre-fix dispatch (before `--include-all` flag existed) |
| ch14 | Failed orchestrator intermediary -- orchestrator agent type lacks Agent tool |
| ch16 | Failed orchestrator intermediary |
| ch19 | Failed orchestrator intermediary |
| ch21 | Coder stalled silently (no output, no error) |
| ch24 | Early shutdown before coders finished |

## Orphaned tasks

55 tasks remain in `pending` status with no owner and no agent to claim them. These were created by batch orchestrators that failed to spawn coders, or by dispatch plans that assumed more coder waves than actually ran.

### Orphaned tasks by chapter

| Chapter | Orphaned task IDs | Count |
| --- | --- | --- |
| ch17 | 150, 151, 152 | 3 |
| ch19 | 155, 156, 157, 158, 160, 161, 164, 165 | 8 |
| ch24 | 197, 198, 199, 200, 201, 202, 203, 204 | 8 |
| ch25 | 209, 210, 211, 212, 213, 214 | 6 |
| ch26 | 217, 219, 221, 223, 225, 226, 230 | 7 |
| ch27 | 237, 238, 240, 242, 244, 246 | 6 |
| ch28 | 248, 251, 252, 253, 254, 256, 258 | 7 |
| ch29 | 264, 266, 268, 270, 272, 273 | 6 |
| ch30 | 275, 276, 277, 278, 279, 280, 281 | 7 |

### How orphaned tasks happened

1. **Batch orchestrators created tasks but could not spawn coders.** The `orchestrator` agent type does not have access to the `Agent` tool. Orchestrators for ch25-30, ch31-36, ch37-42, and ch43-47 each created per-coder tasks but then failed to spawn agents for them.
2. **Over-provisioned coder slots.** Dispatch created 8 coder slots per chapter, but only 1-2 coders actually ran for later chapters (ch25-ch47).
3. **No cleanup mechanism.** Once an orchestrator failed, its orphaned tasks sat permanently in `pending` with no owner.

### Prevention

- Do not use `orchestrator` agent type for spawning sub-agents. Use `parallelizer` or spawn coders directly from the team lead.
- Match task creation to actual coder count. Do not pre-create 8 coder tasks if only 2 coders will run.
- Add a cleanup pass after each wave to delete unclaimed tasks.

## Lessons learned

### 1. bypassPermissions is required but risky

**Problem:** Without `bypassPermissions`, every file write and bash command prompts the user for approval. With 100+ simultaneous agents, this makes the swarm unusable.

**Risk:** `bypassPermissions` gives agents unrestricted file system and command access. A misbehaving coder could delete files, run destructive commands, or write outside its staging directory.

**Alternatives to explore:**

| Approach | Pros | Cons |
| --- | --- | --- |
| `bypassPermissions` | Works now, no prompts | Unrestricted access, no guardrails |
| `mode: "auto"` | May auto-approve safe operations | Untested at swarm scale, may still prompt |
| `mode: "acceptEdits"` | Auto-approves file edits only | Bash commands still prompt |
| Permission hooks | Fine-grained control per agent | Requires hook infrastructure per coder |
| Pre-approved allowedPrompts | Whitelist specific actions | Requires knowing all actions in advance |

**Recommendation for future runs:** Test `mode: "auto"` with a single coder first. If it auto-approves file writes and basic bash commands without prompting, it could replace `bypassPermissions` with less risk. The `acceptEdits` mode is another candidate since coders primarily write files.

### 2. Use cheaper models for coder agents

**Problem:** All spawned agents inherit the parent model (Opus). The Agent tool has no `model` parameter. Running 100+ Opus agents is expensive.

**Solution: custom agent `model` frontmatter.**

Custom agent definitions in `~/.claude/agents/` support a `model` field in their YAML frontmatter. Adding `model: haiku` to `~/.claude/agents/coder.md` routes all coder-type agents to Haiku while the team lead stays on Opus.

```yaml
---
name: coder
model: haiku
description: "Implementation agent..."
tools: Bash, Glob, Grep, Read, Edit, Write, ...
---
```

Valid model values: `opus`, `sonnet`, `haiku`, `inherit`. Default is `inherit` (uses parent session model). Full model IDs like `claude-haiku-4-5-20251001` also work.

**Global override:** The `CLAUDE_CODE_SUBAGENT_MODEL` environment variable overrides the model for all subagents. This affects every subagent regardless of frontmatter, so use per-agent `model` fields for role-based tiering.

**Model selection priority:**
1. Per-agent frontmatter `model` field (most specific)
2. `CLAUDE_CODE_SUBAGENT_MODEL` env var (global override)
3. `inherit` from parent session (default)

**Fallback options (not recommended):**

| Method | How | Trade-off |
| --- | --- | --- |
| Claude CLI subprocess | `bash -c "claude --model haiku ..."` in agent prompt | Loses team context, no task list access |
| Separate session | Launch coder sessions from a shell script outside Claude Code | No integration with swarm coordination |

**Recommended model tiers:**

| Role | Model | Rationale |
| --- | --- | --- |
| Team lead / orchestrator | Opus | Needs full reasoning for coordination |
| Coder | Haiku or Sonnet | PGML generation is templated, pattern-following work |
| Referee / reviewer | Sonnet | Needs judgment but not full Opus reasoning |
| Tester / validator | Haiku | Running scripts and checking output |

**Cost estimate:** Haiku coders would reduce per-coder cost by ~10-20x. For a 100-coder swarm, this could reduce total cost from ~$50-100 to ~$5-10.

**Quality concern:** Haiku may produce lower-quality PGML (worse distractors, simpler randomization, more validation errors). The referee/promote pipeline mitigates this since bad files get filtered out. Test with a single chapter first to measure quality delta.

### 3. Orchestrator agent type cannot spawn sub-agents

The `orchestrator` agent type does not have the `Agent` tool in its tool set. This was discovered when batch orchestrators (ch25-30-batch, ch31-36-batch, ch37-42-batch, ch43-47-batch) all failed to spawn coder sub-agents.

Some orchestrators worked around this by running `claude` CLI commands in Bash, which was unreliable and produced inconsistent results.

**Rule:** Never use `orchestrator` for tasks that require spawning sub-agents. Use `parallelizer` (which has the Agent tool) or spawn coders directly from the team lead.

### 4. Self-validation beats tool-based validation during generation

Coders running `validate_pgml.py` caused permission prompts (even with `bypassPermissions` in some cases) and for-loop complaints from the permission hook. Instructing coders to re-read their files after writing is sufficient for generation-time quality.

Batch validation should be a separate post-generation step run by a tester agent or directly by the team lead.

### 5. Coder deny list is mandatory

Coders must be explicitly told what NOT to do. Without a deny list, coders will:
- Run `validate_pgml.py` (triggers permission prompts)
- Use for loops in Bash (blocked by permission hook)
- Run `claude` commands (spawns uncontrolled sub-processes)
- Use `.pg` extension instead of `.pgml`

**Standard deny list for coder prompts:**
```
- DO NOT run validate_pgml.py
- DO NOT use for loops in Bash
- DO NOT run claude commands
- DO NOT run any validation scripts
- Use .pgml extension ONLY (never .pg)
```

### 6. Task list sprawl is a real problem at scale

318 tasks were created across the swarm. Of these, 55 are orphaned `pending` tasks that will never be claimed. The task list becomes unmanageable beyond ~50 tasks.

**Recommendations:**
- Use coarser per-chapter tasks instead of per-coder tasks
- Clean up orphaned tasks after each wave
- Limit task creation to items that actually have assigned agents
- Consider a maximum task list size (delete completed tasks periodically)

### 7. Direct coder spawning is the most reliable pattern

The most reliable pattern across all tests is:

1. Team lead reads manifest
2. Team lead spawns coder agents directly via Agent tool
3. Each coder gets a complete prompt with: chapter info, output directory, problem list, deny list
4. Coder writes files and reports back
5. Team lead shuts down coder when done

Intermediary layers (orchestrators, batch agents) add failure modes without adding value. The team lead can manage 10-15 simultaneous coders directly.

## Production pipeline (updated)

Based on tests 1-4, the recommended production pipeline is:

1. **Parse** textbook to structured JSON (`parse_biology2e.py` or equivalent)
2. **Dispatch** per chapter (`scripts/multi_agent_folder_setup.py --include-all --assign modular`)
3. **Spawn coders** directly from team lead, 2-4 per chapter, in waves of 10-15 agents
4. **Use `bypassPermissions`** (or test `mode: "auto"`) with explicit deny list
5. **Wait for completion**, shut down coders as they finish
6. **Batch validate** all files with `validate_pgml.py` (tester agent or team lead)
7. **Curate** manually review and move validated files to `output/`

## Swarm statistics

| Metric | Value |
| --- | --- |
| Unique agents spawned | 145 (137 coders + 8 orchestrators) |
| Coder directories used | 10 (coder_1 through coder_10) |
| Team config file size | 191 KB (190,951 bytes) |
| Total PGML files | 1,479 |
| Total PGML lines | 129,408 |
| Total PGML bytes | 3.9 MB (3,902,750 bytes) |
| Average lines per file | ~87 |
| Average bytes per file | ~2,638 |
| Peak task list size | 318 tasks |
| Completed tasks | ~263 |
| Orphaned pending tasks | 55 |
| Chapters covered | 47/47 (100%) |
| Waves | 3 (Wave 1: ch01-ch13 x8 coders, Wave 2: ch25-ch47 x1-2 coders, Wave 3: 6 zero-output chapters x2 coders) |

### Token usage

Token counts are not directly available from the Agent tool or team infrastructure. Claude Code does not expose per-agent token metrics. Rough estimates based on typical PGML generation patterns:

| Role | Agents | Est. input tokens/agent | Est. output tokens/agent | Est. total |
| --- | --- | --- | --- | --- |
| Team lead (Opus) | 1 | ~500K | ~200K | ~700K |
| Orchestrators (Opus) | 8 | ~50K each | ~20K each | ~560K |
| Coders (Opus) | 137 | ~30K each | ~40K each | ~9.6M |
| **Total estimated** | **146** | | | **~10.9M tokens** |

At Opus pricing (~$15/M input, ~$75/M output), rough cost estimate:
- Input: ~8.6M tokens x $15/M = ~$129
- Output: ~5.7M tokens x $75/M = ~$428
- **Estimated total: ~$557**

If coders had used Haiku (~$0.25/M input, ~$1.25/M output):
- Coder input: ~4.1M x $0.25/M = ~$1
- Coder output: ~5.5M x $1.25/M = ~$7
- Lead + orchestrators (still Opus): ~$129
- **Estimated total with Haiku coders: ~$137** (75% savings)

These are rough estimates. Actual token usage depends on manifest sizes read, number of files written, and re-read verification passes.

## Claude Code Agent tool reference

The Agent tool is Claude Code's mechanism for spawning sub-agents (called "subagents" or "sidechain agents"). Each subagent is a child execution branch inside the same session -- not a separate top-level chat. It gets its own context window, custom system prompt, tool access, and permissions.

### Architecture

When the main session delegates a task:
1. Claude creates a sidechain agent record at `~/.claude/projects/<session>/subagents/agent-<id>.jsonl`
2. The subagent runs with `isSidechain: true`, its own `agentId`, the same `sessionId`, and a `parentUuid` linking back to the parent
3. The subagent emits its own assistant messages and tool calls as a JSONL event stream
4. Results are folded back into the parent conversation when the subagent completes

Built-in subagent types include `Explore` (may use Haiku by default), `Plan`, and `general-purpose` (both inherit parent model). Custom subagents are defined in `~/.claude/agents/` as Markdown files with YAML frontmatter.

### Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `prompt` | string | yes | Full task description with all context the agent needs |
| `description` | string | yes | Short 3-5 word summary (shown in UI) |
| `name` | string | no | Human-readable name for the agent (used for messaging and task assignment) |
| `subagent_type` | string | no | Agent type, determines available tools (default: `general-purpose`) |
| `mode` | string | no | Permission mode controlling what the agent can do without prompting |
| `run_in_background` | boolean | no | If true, agent runs without blocking the parent; parent is notified on completion |
| `team_name` | string | no | Team to join (created via TeamCreate) |
| `isolation` | string | no | Set to `"worktree"` to run in an isolated git worktree copy of the repo |
| `resume` | string | no | Agent ID from a previous invocation to resume with full context preserved |

### Permission modes

| Mode | Behavior |
| --- | --- |
| `default` | Prompts user for approval on file writes and bash commands |
| `bypassPermissions` | No prompts -- agent has unrestricted access (used for swarm coders) |
| `acceptEdits` | Auto-approves file edits (Read, Edit, Write) but still prompts for Bash |
| `auto` | May auto-approve safe operations (untested at swarm scale) |
| `plan` | Agent must write a plan and get approval before implementing |
| `dontAsk` | Similar to bypass but with different semantics |

### Agent types and their tools

| Type | Tools available | Use case |
| --- | --- | --- |
| `general-purpose` | All tools | Default, full capability |
| `coder` | Bash, Glob, Grep, Read, Edit, Write, WebFetch, WebSearch, Task tools | Production code writing |
| `tester` | Bash, Glob, Grep, Read, Edit, Write, Task tools, SendMessage | Test creation and validation |
| `reviewer` | Bash, Glob, Grep, Read, WebFetch, WebSearch, Task tools (read-only) | Code review, cannot edit files |
| `orchestrator` | Bash, Glob, Grep, Read, Edit, Write, Task tools | Task coordination (**cannot spawn agents**) |
| `parallelizer` | All tools including Agent, TeamCreate, SendMessage | Parallel coordination (**can spawn agents**) |
| `planner` | Bash, Glob, Grep, Read, Edit, Write, WebFetch, WebSearch, Task tools | Plans and docs only, no production code |
| `maintainer` | Bash, Glob, Grep, Read, Edit, Write, Task tools | Cleanup, lint, index regeneration |
| `architect` | All tools plus SendMessage | Cross-cutting design decisions |
| `monitor` | Bash, Glob, Grep, Read, Task tools, SendMessage | Progress observation, stall detection |
| `scheduler` | Bash, Glob, Grep, Read, Task tools, SendMessage | Workflow triggers, retry logic |
| `integrator` | Bash, Glob, Grep, Read, Edit, Write, Task tools, SendMessage | Merge management, conflict resolution |
| `Explore` | All tools except Agent, Edit, Write | Fast codebase exploration (read-only) |
| `Plan` | All tools except Agent, Edit, Write | Implementation planning (read-only) |

### Key limitations

- **No `model` parameter on the Agent tool call.** However, custom agent definitions in `~/.claude/agents/` support a `model` field in YAML frontmatter (values: `opus`, `sonnet`, `haiku`, `inherit`). Setting `model: haiku` in `~/.claude/agents/coder.md` routes all `subagent_type="coder"` agents to Haiku. The `CLAUDE_CODE_SUBAGENT_MODEL` env var provides a global override for all subagents.
- **Orchestrator cannot spawn agents.** The `orchestrator` type does not have the Agent tool. Use `parallelizer` instead for tasks that need to spawn sub-agents.
- **Context window is independent.** Each agent gets its own context window. It does not share context with the parent or siblings. All necessary information must be in the `prompt`.
- **Team membership is optional.** Agents can run standalone or join a team. Team agents can use SendMessage and Task tools for coordination.
- **Background agents notify on completion.** The parent is automatically notified when a background agent finishes -- no polling needed.

### Swarm-relevant patterns

**Direct spawn (recommended):**
```
Agent(
  prompt="Generate PGML files for ch01...",
  name="ch01-coder9",
  subagent_type="coder",
  mode="bypassPermissions",
  run_in_background=True,
  team_name="bio2e-swarm"
)
```

**Resume a previous agent:**
```
Agent(
  prompt="Continue where you left off",
  resume="ch01-coder9@bio2e-swarm"
)
```

**Parallel launch:** Multiple Agent calls in a single message are launched simultaneously. This is how 12 coders were dispatched at once for the Wave 3 re-dispatch.

## Remaining pipeline steps (not yet run)

The swarm completed generation only. The following pipeline steps have **not** been executed:

| Step | Script | Status |
| --- | --- | --- |
| Batch validation | `validate_pgml.py` on all 1,479 files | Not run |
| Quality curation | Manual review of validated files | Not run |
| Wrong extension fix | 4 `.pg` files in ch26 coder_2 need renaming to `.pgml` | Not fixed |

All 1,479 PGML files remain in `_staging/coder_*/` directories. No files have been promoted to `output/`. Quality is unknown -- files were self-checked by coders (re-read after writing) but never validated against `validate_pgml.py` or reviewed by referee agents.

**Next session should:**
1. Run `validate_pgml.py` on all staging files (batch, not per-coder)
2. Fix or discard files that fail validation
3. Rename the 4 `.pg` files in ch26 to `.pgml`
4. Manually review validated files and curate best versions to `output/`

## Quality findings

### Verbatim content

Sampling files from ch01 and ch04 revealed that 100% of generated PGML files are near-verbatim copies of the textbook multiple-choice questions. Question stems match the manifest text exactly. Answer choices are identical to the textbook with no distractors replaced.

### Decorative RNG

Every file initializes the RNG correctly (`PGrandom->new()` seeded with `$problemSeed`) but no file uses `$rng->random()` to select from pools. The randomization infrastructure exists but is decorative -- all students see the same question with the same choices.

### No widget diversity

All sampled files use RadioButtons exclusively, matching the textbook's MC format. No files use CheckboxList, PopUp, or Numeric even when those widget types would better test the concept.

### Transformation required

All 1,479 staging files need a transformation pass before production use:
- Reword stems to test the same concept from a different angle
- Replace at least 1-2 distractors with new plausible wrong answers
- Add meaningful `$rng->random()` randomization with parallel arrays
- Consider alternative widget types where appropriate
- Add `BEGIN_PGML_SOLUTION` explanations (many are minimal or absent)

The root cause was the coder briefing lacking explicit instructions against verbatim copying. This has been fixed in `_prompts/_coder_briefing.md` with a new "Transformation requirements" section.

## Open questions

- Can `mode: "auto"` replace `bypassPermissions` without introducing prompts?
- What is the quality delta between Haiku and Opus for PGML generation?
- ~~Is there a way to set per-agent model in Claude Code's Agent tool?~~ **Yes.** Add `model: haiku` to `~/.claude/agents/coder.md` frontmatter. Not yet tested at swarm scale.
- Should the referee step use a different model than the coders?
- What is the optimal coder-per-chapter ratio? (2 seems sufficient for coverage, 8 is overkill)
