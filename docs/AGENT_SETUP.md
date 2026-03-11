# Agent setup

Custom agents for multi-agent swarm workflows. Agent definitions live in `~/.claude/agents/`.

## Agent roles

| Agent | Model | Gas Town role | Primary responsibility |
| --- | --- | --- | --- |
| coder | haiku | Crew | Write production code and PGML files |
| tester | haiku | -- | Write tests, run validation, check coverage |
| reviewer | sonnet | -- | Read-only code review and plan auditing |
| planner | inherit | -- | Plans and docs only, never production code |
| architect | inherit | -- | Approve or reject cross-cutting design changes |
| orchestrator | sonnet | -- | Coordinate parallel tasks via task lists |
| parallelizer | inherit | -- | Coordinate teams with messaging and agent spawning |
| integrator | sonnet | Refinery | Merge branches, resolve conflicts |
| maintainer | haiku | Dogs | Cleanup, lint, index regeneration |
| monitor | haiku | Witness | Observe progress, detect stalls |
| scheduler | haiku | Deacon | Trigger workflows, retry failed tasks |

## Relevant skills

Skills are reusable prompt packages that can be preloaded into agents via the `skills:` frontmatter field.

| Skill | Purpose | Useful for |
| --- | --- | --- |
| `webwork-writer` | PGML question authoring with reference docs | coder |
| `python-code-review` | Python code review checklist | reviewer |
| `gas-town-workflow` | Multi-agent coordination conventions | all team agents |
| `read-repo-rules` | Load repo conventions (CLAUDE.md, AGENTS.md) | all agents |
| `unit-test-starter` | Test scaffolding | tester |
| `arch-docs` | Architecture doc refresh | planner, architect |
| `docset-refresh` | Documentation refresh | planner |

### webwork-writer references

The `webwork-writer` skill includes reference docs particularly relevant to PGML generation:

| Reference | Content |
| --- | --- |
| `PGML_QUESTION_TYPES.md` | Widget types (RadioButtons, PopUp, CheckboxList, Numeric, etc.) |
| `RANDOMIZATION_REFERENCE.md` | RNG patterns and parallel array techniques |
| `WEBWORK_PROBLEM_AUTHOR_GUIDE.md` | Full PG/PGML authoring guide |
| `PGML_LINTER_EXPECTATIONS.md` | What `validate_pgml.py` checks |
| `PG_COMMON_PITFALLS.md` | Common PGML mistakes and fixes |
| `MATCHING_PROBLEMS.md` | Matching question type implementation |
| `ORDERING_PROBLEMS.md` | Ordering question type implementation |
| `WEBWORK_HEADER_STYLE.md` | OPL header conventions |
| `HOW_TO_MAKE_GRAPHS.md` | Graph generation in PGML |
| `RDKIT_MOLECULAR_STRUCTURES.md` | Chemistry structure rendering |
| `RENDERER_API_USAGE.md` | Renderer API for validation |
| `HOW_TO_LINT.md` | Linting workflow |

## Agent configuration tips

### Preloading skills

Add `skills:` to agent frontmatter to inject domain knowledge at startup:

```yaml
---
name: coder
skills:
  - webwork-writer
  - read-repo-rules
---
```

### Other useful frontmatter fields

- `maxTurns`: limit agent runtime to prevent silent stalls
- `background: true`: always run as background task
- `memory: user`: persistent memory across sessions
- `hooks`: enforce rules (e.g., block forbidden commands via PreToolUse)

See [Claude Code subagent docs](https://docs.anthropic.com) for full configuration reference.

## Escalation paths

| Agent | Escalates to | When |
| --- | --- | --- |
| coder | architect | Design conflict or architectural question |
| coder | planner | Ambiguous or incomplete task |
| reviewer | planner | Plan drift or missing plan |
| planner | architect | Architecture decision needed |
| integrator | human | Failed merge after retry |
| monitor | orchestrator | Stuck worker detected |
| monitor | human | Systemic failure |
