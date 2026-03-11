# Code architecture

## Pipeline overview

The pipeline converts textbook content into WeBWorK PG/PGML questions for ADAPT. Currently supports Tymoczko "Biochemistry: A Short Course" (3rd ed.) and OpenStax Biology 2e.

```
Layer 1: Ingestion       parse_textbook.py / parse_biology2e.py --> structured/chapters/*.json
Layer 2: Concepts         Claude agents     --> concepts/ch{NN}_concepts.yaml
Layer 3: Questions        Claude agents     --> output/**/*.pgml
Layer 4: Validation       validate_pgml.py + validate_pgml_render.py
Layer 5: Index            build_index.py    --> reports/coverage_report.txt
```

## Layer 1: Textbook parsing

Four independent library modules handle different parsing tasks:

- [textbook_clean.py](../textbook_clean.py) -- text normalization (whitespace, page numbers, split lines)
- [textbook_chapters.py](../textbook_chapters.py) -- chapter boundary detection and section extraction
- [textbook_problems.py](../textbook_problems.py) -- problem extraction (standard, challenge, data interpretation)
- [textbook_answers.py](../textbook_answers.py) -- answer key parsing from back-of-book section

[parse_textbook.py](../parse_textbook.py) orchestrates all four modules to produce per-chapter JSON for Tymoczko.
[parse_biology2e.py](../parse_biology2e.py) handles OpenStax Biology 2e.

## PGML helpers

Three independent modules support PGML question generation and validation:

- [pgml_template.py](../pgml_template.py) -- OPL header and preamble generation
- [pgml_checks.py](../pgml_checks.py) -- static validation checks (HTML whitelist, passthrough, graders, structure)
- [pgml_macros.py](../pgml_macros.py) -- widget-to-macro mapping (RadioButtons, PopUp, niceTables, etc.)

## Validators

- [validate_pgml.py](../validate_pgml.py) -- static PGML validator (imports pgml_checks + pgml_macros)
- [validate_pgml_render.py](../validate_pgml_render.py) -- renderer API validator (standalone)

## Index

- [build_index.py](../build_index.py) -- reads concepts and questions, produces coverage reports

## Scripts

- [scripts/multi_agent_folder_setup.py](../scripts/multi_agent_folder_setup.py) -- builds problem manifests and staging directories for multi-agent PGML generation

## Data flow

```
artifacts/Tymoczko_3rd_edition.txt (or Biology2e.txt)
    |
    v
parse_textbook.py / parse_biology2e.py (Layer 1)
    |
    v
structured/chapters/ch{NN}_{slug}.json
    |
    v
Claude agents (Layer 2) --> concepts/ch{NN}_concepts.yaml
    |
    v
Claude agents (Layer 3) --> output/ch{NN}_{slug}/{concept_id}.pgml
    |
    v
validate_pgml.py + validate_pgml_render.py (Layer 4)
    |
    v
build_index.py (Layer 5) --> output/concept_index.yaml + reports/coverage_report.txt
```
