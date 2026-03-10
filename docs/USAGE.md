# Usage

## Parse textbook

Extract chapters, problems, and answers from the textbook into structured JSON:

```bash
source source_me.sh && python3 parse_textbook.py
```

Output: `structured/chapters/ch{NN}_{slug}.json` (one file per chapter).

## Validate PGML files

Run static validation on generated `.pgml` files:

```bash
source source_me.sh && python3 validate_pgml.py output/
```

## Validate via renderer

Send `.pgml` files to a local WeBWorK renderer for deeper validation:

```bash
source source_me.sh && python3 validate_pgml_render.py -i output/ch03_amino_acids/concept01.pgml
```

Requires a renderer running at `http://localhost:3000/render-api`.

## Build concept index

Generate coverage reports from concept YAML and generated questions:

```bash
source source_me.sh && python3 build_index.py
```

Output: `output/concept_index.yaml` and `reports/coverage_report.txt`.

## Run tests

```bash
source source_me.sh && python3 -m pytest tests/
```
