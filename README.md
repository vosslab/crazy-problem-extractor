# crazy-problem-extractor

Extract and convert Tymoczko "Biochemistry: A Short Course" (3rd ed.) textbook problems into large banks of concept-aligned WeBWorK PG/PGML questions for ADAPT.

## Quick start

```bash
pip3 install -r pip_requirements.txt
source source_me.sh && python3 parse_textbook.py
source source_me.sh && python3 validate_pgml.py output/
```

See [docs/INSTALL.md](docs/INSTALL.md) for setup and [docs/USAGE.md](docs/USAGE.md) for full usage.

## Documentation

- [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md) -- pipeline design and data flow
- [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md) -- directory layout
- [docs/INSTALL.md](docs/INSTALL.md) -- setup and dependencies
- [docs/USAGE.md](docs/USAGE.md) -- how to run each tool
- [docs/CHANGELOG.md](docs/CHANGELOG.md) -- change history

## Author

Neil Voss, <https://bsky.app/profile/neilvosslab.bsky.social>

## License

AGPL v3. See [LICENSE.AGPL_v3](LICENSE.AGPL_v3).
