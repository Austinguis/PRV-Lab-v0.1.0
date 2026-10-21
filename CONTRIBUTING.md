# Contributing to PRV-Lab

Thank you for considering a contribution.

## Before opening an issue

- Search existing issues and discussions.
- Include your operating system, Python version, PRV-Lab version, dependency versions, exact command, and a minimal reproducible example.
- Remove private data from logs and attached files.

## Development setup

```bash
python -m venv .venv
python -m pip install -e '.[dev,prv]'
python -m pytest
ruff check .
```

If you do not need the optional PRV backend, use `python -m pip install -e '.[dev]'`.

## Pull request expectations

- Keep changes focused and explain the problem they solve.
- Add tests for bug fixes and new behavior.
- Preserve lower/estimate/upper outputs from external accountants.
- Document mathematical assumptions and cite the source of any algorithm.
- Do not claim an improvement without matched settings, repeatable measurements, and uncertainty/error analysis.
- Do not include credentials, private datasets, or personally identifying information in tests or examples.
- Update documentation and the changelog when user-visible behavior changes.

## Style

Use type hints for public functions, clear names, and comments that explain mathematical choices rather than restating code. Run `pytest` and `ruff check .` before submitting.

By submitting a contribution, you agree that it may be distributed under the project's MIT license.
