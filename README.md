# crazy-problem-extractor

Extract textbook problems from biochemistry and biology courses and convert them into large banks of concept-aligned WeBWorK PG/PGML questions for ADAPT. Currently supports Tymoczko "Biochemistry: A Short Course" (3rd ed.) and OpenStax Biology 2e.

## Quick start

```bash
pip3 install -r pip_requirements.txt
source source_me.sh && python3 parse_textbook.py
source source_me.sh && python3 validate_pgml.py output/
```

See [docs/INSTALL.md](docs/INSTALL.md) for setup and [docs/USAGE.md](docs/USAGE.md) for full usage.

## Documentation

### Getting started

- [docs/INSTALL.md](docs/INSTALL.md) -- setup and dependencies
- [docs/USAGE.md](docs/USAGE.md) -- how to run each tool

### Architecture and layout

- [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md) -- pipeline design and data flow
- [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md) -- directory layout

### Agents and swarm

- [docs/AGENT_SETUP.md](docs/AGENT_SETUP.md) -- agent roles, skills, and configuration
- [docs/SWARM_STRATEGIES.md](docs/SWARM_STRATEGIES.md) -- best practices for multi-agent swarm generation
- [docs/SWARM_TEST1_REPORT.md](docs/SWARM_TEST1_REPORT.md) -- ch03 free-choice baseline
- [docs/SWARM_TEST2_REPORT.md](docs/SWARM_TEST2_REPORT.md) -- ch03 modular assignment
- [docs/SWARM_TEST3_REPORT.md](docs/SWARM_TEST3_REPORT.md) -- Biology 2e full-scale production
- [docs/SWARM_TEST4_REPORT.md](docs/SWARM_TEST4_REPORT.md) -- Biology 2e re-dispatch and quality findings

### History

- [docs/CHANGELOG.md](docs/CHANGELOG.md) -- change history

## Testing

```bash
source source_me.sh && python3 -m pytest tests/
```

## Author

Neil Voss, <https://bsky.app/profile/neilvosslab.bsky.social>

## License

AGPL v3. See [LICENSE.AGPL_v3](LICENSE.AGPL_v3).
