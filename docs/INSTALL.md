# Install

## Requirements

- Python 3.12
- Bash shell (for `source_me.sh`)

## Setup

```bash
pip3 install -r pip_requirements.txt
pip3 install -r pip_requirements-dev.txt
```

## Textbook artifact

Place the textbook file at `artifacts/Tymoczko_3rd_edition.txt`. This file is not tracked in git.

## Optional: WeBWorK renderer

For render-based validation (`validate_pgml_render.py`), a local WeBWorK renderer must be running at `http://localhost:3000/render-api`.
