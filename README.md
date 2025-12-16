## ImpactScope

**ImpactScope** is a developer-focused static analysis tool that helps you understand the *blast radius* of code changes in large C codebases. Given a Git commit, it identifies which functions are directly modified, traces how those changes propagate through the call graph, and highlights which parts of the system are most likely affected.

Rather than focusing on individual files or diffs in isolation, ImpactScope takes a **project-level view**: it connects Git history, abstract syntax trees (ASTs), and call graph analysis to answer a practical question:

> *“If I change this code, what else should I worry about?”*

---

## Why ImpactScope exists

In large or long-lived C projects:

- A small change can silently affect distant parts of the system.
- Call chains are often implicit and poorly documented.
- Reviewing diffs alone does not reveal downstream or upstream effects.

ImpactScope is designed to:

- Reduce cognitive load during code reviews
- Support safer refactoring
- Help developers reason about risk before merging changes
- Lay the groundwork for smarter test selection and CI optimization

This project is intentionally **static and language-aware**, avoiding runtime instrumentation or heavyweight build integration.

---

## Current capabilities

### Change-aware impact analysis

- Parses a Git commit and extracts **changed line ranges** for C source files.
- Maps those line ranges to the **functions they belong to** using Tree-sitter ASTs.

### Call graph construction

- Builds a function-level call graph from C source files.
- Tracks **direct callees** and **callers** of impacted functions, with configurable depth.

### Impact reporting

For each affected file, ImpactScope reports:

- Directly impacted functions
- Functions called by those functions
- Functions that call into those functions (upstream)
- Aggregated impact set at a chosen depth

This provides a concrete, explainable view of how a change propagates through the code.

---

## Example output

```text
File: src/auth/auth.c
 Changed lines: [(5, 10)]
 Directly impacted functions: ['login_user']
 Functions called by impacted functions:
   login_user -> ['connect_db', 'query_user', 'printf']
 Impacted (depth=1): ['login_user', 'connect_db', 'query_user', 'printf']
```

This tells you, at a glance, which functional areas may require review, testing, or additional scrutiny.

---

## Installation

### Requirements

- Python **3.10+**
- Git
- A C repository to analyze

### Using `uv` (recommended)

```bash
uv sync
```

This installs all dependencies declared in `pyproject.toml` and manages the virtual environment automatically.

If you prefer a manual virtualenv:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # PowerShell on Windows
pip install -e .
```

---

## Usage

Run the analyzer against a repository and commit:

```bash
uv run main.py --repo-path ../c-impact-demo --commit HEAD
```

### CLI options

- `--repo-path` *(required)*: Path to the target Git repository
- `--commit` *(required)*: Commit hash or ref to analyze
- `--depth` *(optional, default=1)*: How far to propagate impact through the call graph
- `--visualize` *(optional, default=False)*: Generate an interactive HTML call graph under `artifacts/call_graphs/`

Behavior notes:

- If there are no `.c`/`.h` changes in the commit, the CLI will say so explicitly.
- If changed lines do not fall inside any function, that is reported per file.
- If the commit hash does not exist, you get a clear, human-readable error instead of a traceback.

---

## Architecture overview

ImpactScope is structured as a pipeline:

1. **Git diff analysis** – Identify changed files and line ranges
2. **AST parsing** – Locate functions and call expressions using Tree-sitter
3. **Impact mapping** – Map changes to functions and propagate through calls
4. **Graph modeling** – Represent relationships using NetworkX
5. **Presentation** – Expose results via a clean CLI interface (and optional HTML graph)

Key modules:

- `git_diff.py` – Commit-aware diff extraction
- `parser.py` – Tree-sitter–based C parser
- `impact_mapper.py` – Maps code changes to functions and computes upstream/downstream impact
- `call_mapper.py` – Extracts function call relationships
- `call_graph.py` – Graph construction utilities
- `visualization.py` – PyVis-based HTML visualization of the call graph
- `cli.py` – User-facing command-line interface

---

## Design principles

- **Language-aware, not regex-based** – Uses ASTs instead of brittle text matching
- **Incremental depth** – Starts shallow (depth=1) but scales naturally
- **Explainable output** – Every result can be traced back to code and calls
- **Tooling-friendly** – Intended to integrate with CI, code review, and developer workflows

---

## Roadmap / future work

ImpactScope is intentionally built as a foundation. Planned and possible extensions include:

### Deeper impact analysis

- More advanced multi-hop call propagation and pruning strategies
- Smarter handling of utility/low-signal functions

### Test impact analysis

- Map impacted functions to relevant test files
- Heuristic-based test selection (naming, paths, symbols)
- Optional AST parsing of test code

### CI & automation

- Machine-readable JSON output
- GitHub/GitLab CI integration
- Fail or warn on high-impact changes

### Visualization & UX

- Richer interactive call graphs and summaries
- Impact summaries per commit and per file
- Comparison of impact across commits

### Language support

- C++ (classes, methods, namespaces)
- Other Tree-sitter–supported languages

---

## Project status

ImpactScope is currently in **active development** and should be considered an evolving prototype. The focus so far has been on correctness, clarity, and architectural soundness rather than feature completeness.

Feedback, experimentation, and extension are encouraged.
