# Getting Started with ImpactScope

**ImpactScope** is a developer-first **Change Impact Analysis (CIA)** tool for large C codebases, designed as a foundation for **change-based test selection and prioritization**.

Given a Git commit (or diff), ImpactScope performs deterministic static analysis to answer a deceptively complex question:

> **For a code change, which parts of the code are impacted — and which tests should run?**

## Quick Installation

### Requirements

- Python **3.10+**
- Git
- A C repository to analyze

### Setup (recommended: `uv`)

```bash
uv sync
```

This installs dependencies from `pyproject.toml` and manages the virtual environment automatically.

### Alternative: Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# or .\.venv\Scripts\Activate.ps1 on Windows
pip install -e .
```

## Your First Analysis

Run ImpactScope against a repository and a commit:

```bash
uv run -m src.main --repo-path ../your-c-project --commit HEAD
```

### Common options

- `--repo-path` *(required)*: Path to the target Git repository
- `--commit` *(required)*: Commit hash or ref to analyze
- `--depth` *(optional, default=1)*: Call graph traversal depth
- `--visualize` *(optional)*: Generate an HTML call graph under `artifacts/`
- `--output` *(optional, default=text)*: Output format — `text` for terminal-friendly output, `json` for machine-readable JSON

## Try the Sample Project

The fastest way to see ImpactScope in action:

```bash
# From the project root directory
uv run -m src.main --repo-path examples/sample-c-project-1 --commit HEAD
```

This includes a real code change to demonstrate impact analysis.

## Next Steps

- **[User Guide](user-guide.md)**: Detailed usage instructions and examples
- **[API Reference](api-reference.md)**: Complete CLI options and JSON schema
- **[Architecture](architecture.md)**: Technical deep dive
- **[CI Integration](ci-integration.md)**: Automation and CI/CD setup
