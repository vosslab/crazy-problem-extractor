# File structure

```
crazy-problem-extractor/
  # Layer 1: textbook parsing (4 modules + 2 orchestrators)
  textbook_clean.py           # text normalization, page number removal
  textbook_chapters.py        # chapter boundary detection, section extraction
  textbook_problems.py        # problem extraction (standard, challenge, data interp)
  textbook_answers.py         # answer key parsing
  parse_textbook.py           # Tymoczko orchestrator: imports all 4 modules, produces JSON
  parse_biology2e.py          # Biology 2e orchestrator

  # PGML helpers (3 modules)
  pgml_template.py            # OPL header and preamble generation
  pgml_checks.py              # validation check functions
  pgml_macros.py              # widget-to-macro mapping

  # Validators and indexer
  validate_pgml.py            # static PGML validator (imports pgml_checks + pgml_macros)
  validate_pgml_render.py     # renderer API validator (standalone)
  build_index.py              # concept index builder (standalone)

  # Scripts
  scripts/
    multi_agent_folder_setup.py  # manifest builder and staging dir setup for swarm dispatch

  # Repo metadata
  pyproject.toml              # version (CalVer 26.03), project metadata
  VERSION                     # synced with pyproject.toml
  pip_requirements.txt        # runtime deps (pyyaml, rich)
  pip_requirements-dev.txt    # dev deps (pyflakes, pytest, etc.)
  source_me.sh                # bash bootstrap for python environment

  # Data directories (gitignored)
  artifacts/                  # user-placed textbook files
  structured/                 # Layer 1 output
    chapters/ch{NN}_{slug}.json
  concepts/                   # Layer 2 output (agent-generated)
    ch{NN}_concepts.yaml
  output/                     # Layer 3 output (agent-generated)
    ch{NN}_{slug}/{concept_id}.pgml
    concept_index.yaml        # Layer 5
  reports/                    # validation and coverage reports

  # Swarm staging (gitignored, historical)
  _staging/                   # multi-agent coder output directories
  _prompts/                   # coder briefing and referee rubric docs

  # Tests
  tests/
    test_textbook_clean.py
    test_textbook_chapters.py
    test_textbook_problems.py
    test_textbook_answers.py
    test_parse_biology2e.py

  # Documentation
  docs/
    AGENT_SETUP.md
    CHANGELOG.md
    CODE_ARCHITECTURE.md
    FILE_STRUCTURE.md
    INSTALL.md
    USAGE.md
    SWARM_STRATEGIES.md         # best practices for multi-agent generation
    SWARM_TEST1_REPORT.md       # ch03 free-choice baseline
    SWARM_TEST2_REPORT.md       # ch03 modular assignment
    SWARM_TEST3_REPORT.md       # Biology 2e full-scale production
    SWARM_TEST4_REPORT.md       # Biology 2e re-dispatch and quality findings

  # Dev utilities
  devel/
    commit_changelog.py
```
