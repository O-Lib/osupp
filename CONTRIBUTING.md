# Contributing to osupp

First off, thank you for considering contributing to `osupp`. It's people like you that make this library better for the entire osu! Python community.

Following these guidelines helps communicate that you respect the time of the maintainers and other contributors. In return, we'll respect your time and address your contributions in a timely manner.

---

### Table of Contents

* [Code of Conduct](#code-of-conduct)
* [What We Accept](#what-we-accept)
* [What We Do Not Accept](#what-we-do-not-accept)
* [No AI-Generated Contributions](#no-ai-generated-contributions)
* [Getting Started](#getting-started)

  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Features](#suggesting-features)
  * [Submitting Pull Requests](#submitting-pull-requests)
* [Development Setup](#development-setup)
* [Coding Standards](#coding-standards)
* [Commit Guidelines](#commit-guidelines)
* [Testing](#testing)
* [Documentation](#documentation)
* [Review Process](#review-process)
* [Recognition](#recognition)

---

### Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

Please report unacceptable behavior to **[security@osupp.dev](mailto:security@olib.dev)**.

---

### What We Accept

We welcome contributions in the following areas:

| Type                           | Description                                                                                 |
| ------------------------------ | ------------------------------------------------------------------------------------------- |
| 🐛 **Bug fixes**               | Issues that cause incorrect behavior, crashes, or unexpected results                        |
| 📄 **Documentation**           | Typos, clarifications, examples, or missing docstrings                                      |
| ⚡ **Performance improvements** | Faster parsing, lower memory usage, better algorithms                                       |
| ✨ **New features**             | Additional mods, game mode support, or API extensions (must align with osu! official specs) |
| 🧪 **Tests**                   | Additional test cases, edge cases, or improved coverage                                     |
| 🔧 **Tooling**                 | Better developer experience, CI/CD improvements, build scripts                              |

---

### What We Do Not Accept

* Breaking changes without prior discussion
* Changes that only benefit a specific niche use case
* Code that degrades performance without clear justification
* Changes that introduce unnecessary dependencies

---

### Getting Started

### Reporting Bugs

Before submitting a bug report:

1. **Check the latest version** – Your issue may already be fixed
2. **Search existing issues** – Someone might have reported it already
3. **Reproduce without modifications** – Test with a clean environment

A good bug report includes:

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Load beatmap `example.osu`
2. Apply mods `['HR', 'DT']`
3. Call `calculate_pp()`

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened, including error messages or wrong output.

**Environment:**
- osupp version: 0.5.0
- Python version: 3.11 / 3.12 / 3.13
- OS: Windows / Linux / macOS

**Additional context**
Beatmap file (if public), screenshots, or relevant code snippets.

---

### Suggesting Features

We love good feature suggestions. Before submitting:

* Check if the feature already exists
* Consider the scope
* Explain the use case

A good feature request includes:

**Problem statement**
What problem does this solve? What can't you do right now?

**Proposed solution**
How would this work? Include API examples if possible.

**Alternatives considered**
What other approaches did you think about?

**Impact**
Who benefits from this?

---

### Submitting Pull Requests

* Open an issue first (unless trivial)
* Fork the repository and create a branch from `main`
* Write your code following standards
* Add tests
* Update documentation
* Run the test suite
* Open a draft PR
* Request review

---

### Development Setup

### Prerequisites

* Python 3.9+ (3.11+ recommended)
* `uv` or `pip` + `venv`
* `pytest`

### Clone and Install

```bash
git clone https://github.com/your-username/osupp.git
cd osupp

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -e ".[dev]"
# or
uv pip install -e ".[dev]"
```

### Verify Setup

```bash
pytest
mypy osupp/
ruff check osupp/
```

---

### Coding Standards

We follow **PEP 8** with additions:

### Formatting

| Rule        | Standard                              |
| ----------- | ------------------------------------- |
| Line length | 88 characters                         |
| Indentation | 4 spaces                              |
| Quotes      | `"""` for docstrings, `'` for strings |
| Imports     | Grouped                               |

### Naming

| Type      | Convention       |
| --------- | ---------------- |
| Variables | snake_case       |
| Functions | snake_case       |
| Classes   | PascalCase       |
| Constants | UPPER_SNAKE_CASE |

### Type Hints

```python
def calculate_pp(beatmap: Beatmap, mods: list[Mod], accuracy: float = 1.0) -> float:
    ...
```

### Docstrings

```python
def parse_beatmap(file_path: Path) -> Beatmap:
    """
    Parse an osu! beatmap file.

    Args:
        file_path: Path to the .osu file.

    Returns:
        Beatmap object.

    Raises:
        FileNotFoundError
    """
```

---

### Commit Guidelines

We follow **Conventional Commits**:

<type>(<scope>): <subject>

### Types

* feat
* fix
* docs
* style
* refactor
* perf
* test
* chore

### Examples

```
feat(parser): add support for version 14
fix(pp): correct HD calculation
docs(readme): update install
```

---

### Testing

Tests are required.

### Structure

```
tests/
├── test_parser/
├── test_mods/
├── test_pp/
└── fixtures/
```

### Example

```python
def test_calculate_pp():
    assert True
```

### Run

```bash
pytest
pytest --cov=osupp
pytest -n auto
```

Minimum coverage: **85%**

---

### Documentation

Document:

* Public APIs
* Complex logic
* Edge cases
* Examples

---

### Review Process

### Reviewers check:

* Style
* Types
* Tests
* Docs
* Performance

### Timeline

| Step         | Time     |
| ------------ | -------- |
| First review | 5 days   |
| Follow-ups   | 2–3 days |
| Merge        | 24h      |

---

### Recognition

Contributors are listed in:

* `README.md`
* `CHANGELOG.md`
* GitHub Contributors

Major contributors → `AUTHORS.md`

---

### Final Notes

> "Code is read more often than it is written."

If unsure, open an issue first.

---

**Thank you for contributing to osupp! 🚀**
- The O!Lib Team
