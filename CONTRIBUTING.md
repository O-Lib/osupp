# Contributing to OSUPP

Thank you for taking the time to contribute. These guidelines help us keep the codebase consistent and review cycles short.

---

### Table of Contents

- [Code of Conduct](#code-of-conduct)
- [What We Accept](#what-we-accept)
- [What We Do Not Accept](#what-we-do-not-accept)
- [Getting Started](#getting-started)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Submitting Pull Requests](#submitting-pull-requests)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)
- [Review Process](#review-process)

---

### Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

Please report unacceptable behavior to **[conduct@olib.dev](mailto:conduct@olib.dev)**.

---

### What We Accept

| Type | Description |
| --- | --- |
| Bug fixes | Incorrect behavior, crashes, or unexpected results |
| Documentation | Typos, clarifications, examples, missing docstrings |
| Performance improvements | Faster parsing, lower memory usage, better algorithms |
| New features | Additional functionality aligned with the osu! spec |
| Tests | Additional test cases, edge cases, improved coverage |
| Tooling | Better developer experience, CI/CD improvements |

---

### What We Do Not Accept

- Breaking changes without prior discussion (open an issue first)
- Changes that only benefit a narrow niche use case
- Code that degrades performance without clear justification
- Changes that introduce unnecessary dependencies

---

### Getting Started

### Reporting Bugs

Before submitting:

1. **Check the latest version** - your issue may already be fixed
2. **Search existing issues** - someone may have reported it already
3. **Reproduce in a clean environment**

A good bug report includes:

- What you expected vs. what actually happened
- A minimal code snippet that reproduces the issue
- osupp version, Python version, and OS
- Full error traceback if applicable

### Suggesting Features

Before submitting:

- Check if the feature already exists
- Consider the scope and whether it fits the library's purpose
- Describe the problem it solves, not just the solution

Include:

- **Problem statement** - what can't you do right now?
- **Proposed API** - a code example helps
- **Alternatives considered**

### Submitting Pull Requests

1. Open an issue first for non-trivial changes
2. Fork and create a branch from `main`
3. Write code following the standards below
4. Add or update tests
5. Update documentation if needed
6. Ensure pre-commit passes: `pre-commit run --all-files`
7. Open a PR - drafts are welcome for early feedback

---

### Development Setup

### Prerequisites

- Python 3.10+ (3.12 recommended)
- [`uv`](https://github.com/astral-sh/uv) or `pip` + `venv`

### Install

```bash
git clone https://github.com/O-Lib/osupp.git
cd osupp

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
# or
uv pip install -e ".[dev]"
```

### Verify

```bash
pytest
mypy osupp/
ruff check osupp/
```

### Pre-commit

```bash
pre-commit install
pre-commit run --all-files
```

---

### Coding Standards

We follow **PEP 8** with these additions:

| Rule | Standard |
| --- | --- |
| Line length | 88 characters |
| Indentation | 4 spaces |
| Quotes | `"""` for docstrings, `'` for strings |
| Imports | Grouped: stdlib → third-party → local |
| Naming | `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants |

### Type Hints

All public functions and methods must have full type annotations:

```python
def parse_beatmap(file_path: Path) -> Beatmap:
    ...
```

### Docstrings

All public APIs require docstrings:

```python
def parse_beatmap(file_path: Path) -> Beatmap:
    """
    Parse an osu! beatmap file.

    Args:
        file_path: Path to the .osu file.

    Returns:
        Parsed Beatmap instance.

    Raises:
        FileNotFoundError: If the file does not exist.
        ParseBeatmapError: If the file format is invalid.
    """
```

---

### Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

**Scopes:** `beatmap`, `mods`, `pp`, `ci`, `packaging`

**Examples:**

```
feat(beatmap): support format version 15
fix(mods): correct legacy bitfield for NF+DT combination
docs(readme): add quick start examples
perf(beatmap): reduce allocations in hit object parser
chore(ci): pin ruff to 0.9.10
```

---

### Testing

Tests are required for all non-trivial changes.

### Structure

```
tests/
├── test_beatmap/
├── test_mods/
├── test_pp/
└── fixtures/
```

### Run

```bash
pytest
pytest --cov=osupp
pytest -n auto # parallel
```

Minimum coverage target: **85%**

---

### Documentation

Document all public APIs. For complex internal logic, inline comments are preferred over docstrings. Update the README if you add top-level features.

---

### Review Process

| Step | Timeline |
| --- | --- |
| First review | Within 5 business days |
| Follow-up reviews | Within 2–3 business days |
| Merge after approval | Within 24 hours |

Reviewers check: correctness, types, tests, docs, performance, and style.

---

<p align="center">
	<img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/footers/gray0_ctp_on_line.svg?sanitize=true" />
</p>

<p align="center">
        <code>&copy 2026-Present <a href="https://github.com/O-Lib">O!Lib Team</a></code>
</p>
