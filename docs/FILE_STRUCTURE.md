# File structure

```
crazy-problem-extractor/
  # Layer 1: textbook parsing (4 modules + orchestrator)
  textbook_clean.py           # text normalization, page number removal
  textbook_chapters.py        # chapter boundary detection, section extraction
  textbook_problems.py        # problem extraction (standard, challenge, data interp)
  textbook_answers.py         # answer key parsing
  parse_textbook.py           # orchestrator: imports all 4 modules, produces JSON

  # PGML helpers (3 modules)
  pgml_template.py            # OPL header and preamble generation
  pgml_checks.py              # validation check functions
  pgml_macros.py              # widget-to-macro mapping

  # Validators and indexer
  validate_pgml.py            # static PGML validator (imports pgml_checks + pgml_macros)
  validate_pgml_render.py     # renderer API validator (standalone)
  build_index.py              # concept index builder (standalone)

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

  # Tests
  tests/
    test_textbook_clean.py
    test_textbook_chapters.py
    test_textbook_problems.py
    test_textbook_answers.py
    test_pgml_template.py
    test_pgml_checks.py
    test_pgml_macros.py
    test_validate_pgml.py
    test_build_index.py

  # Documentation
  docs/
    CHANGELOG.md
    CODE_ARCHITECTURE.md
    FILE_STRUCTURE.md
    INSTALL.md
    USAGE.md
```
