# ImpactScope

**ImpactScope** is a developer-first **Change Impact Analysis (CIA)** tool for large C codebases, designed as a foundation for **change-based test selection and prioritization**.

Given a Git commit (or diff), ImpactScope performs deterministic static analysis to answer a deceptively complex question:

> **For a code change, which parts of the code are impacted — and which tests should run?**

ImpactScope bridges Git diffs, AST-level code structure, and call-graph analysis to compute the _blast radius_ of a change. Its long-term goal is to enable selective testing in CI/CD workflows, minimizing test costs while preserving confidence.

---

## Project Scope & Phased Approach

ImpactScope is intentionally developed in **phases**, each solving a concrete sub-problem toward the broader goal of *impact-based test selection*. The core question is:

> _Given a code change, which tests must be re-run to maintain confidence — without running the entire suite?_

This cannot be reliably solved with a single method. ImpactScope follows a layered approach inspired by both industry practice and research: combining static structure, dynamic coverage, heuristics, and learned prioritization.

This section covers:

- [<a href="#phase1">Phase 1</a>] — Deterministic Static Impact Analysis (Implemented)
- [<a href="#phase2">Phase 2</a>] — Test Awareness & Coverage Mapping (Next Step)
- [<a href="#phase3">Phase 3</a>] — Test Selection & Confidence Modeling (Planned)
- [<a href="#phase4">Phase 4</a>] — Learning & AI Assistance (Optional, Assistive)

---

<a id="phase1"></a>
### Phase 1 — Deterministic Static Impact Analysis (Implemented)

**Goal:** Identify which parts of the codebase are _structurally impacted_ by a change.

This phase answers:

> _Which code could be affected by this change, based purely on program structure?_

### Implemented in ImpactScope

- Git diff parsing with precise line ranges
- AST function extraction (Tree-sitter)
- Function-level call graph construction
- **Downstream impact analysis** (calls from changed code)
- **Upstream impact analysis** (calls into changed code)
- Depth-limited traversal to control noise
- Standard-library filtering
- CLI-first workflow
- Optional HTML visualization

### Why this phase matters

Static impact analysis provides a **safe upper bound** — it may include extra results, but avoids missing potential impacts. This deterministic foundation is essential before practical test selection can be attempted.

✨ **Technical Building Blocks (Phase 1)**

- Git diff parsing and line/function mapping
- Tree-sitter AST extraction
- Call graph construction
- Impact propagation (upstream/downstream)

### Limitations / Known Issues

While Phase 1 provides a solid foundation for static impact analysis, it has the following limitations:

- **Over-approximation / False positives:** The analysis lists all code that *might* be affected, not necessarily what *actually* will be impacted.
- **No runtime data/control-flow awareness:** Branches, loops, and data-dependent execution paths are not modeled, so actual program behavior may differ.
- **Incomplete handling of function pointers and complex C constructs:** Indirect calls, callbacks, macros, and inline assembly may be missed or misattributed in the call graph.
- **Scalability and noise:** Depth limits help reduce noise, but very large or macro-heavy codebases may still produce extensive impact sets.

---

<a id="phase2"></a>
### Phase 2 — Test Awareness & Coverage Mapping (Next Step)

**Goal:** Link impacted code to the tests that actually execute it.

Static analysis alone can only _suggest possible impact paths_. To make ImpactScope practically useful, it must become **test-aware** by incorporating _coverage data_ — dynamically measured information about which tests exercise which parts of the code.

### What this adds

- Per-test coverage collection (e.g., via coverage tools)
- Mapping between:
  - functions/files
  - and tests that cover them
- Combining static impact with dynamic coverage

### What this enables

- Selection of tests that truly execute impacted code
- Avoidance of unrelated test runs
- A test-to-change dependency matrix for prioritization

After this phase, ImpactScope can answer:

> _Which tests are directly affected by a change?_

✨ **Technical Building Blocks (Phase 2)**

- Coverage collection (gcov/lcov or similar)
- Test → code mapping
- Integration of coverage with impact data

---

<a id="phase3"></a>
### Phase 3 — Test Selection & Confidence Modeling (Planned)

**Goal:** Decide _which tests to execute first_, and with what confidence level.

Static impact + coverage gives a list of relevant tests. But _ordering and prioritizing_ those tests optimally is a core challenge in regression testing and continuous integration. Research and practices in test prioritization show that ordering tests to detect faults early and minimize execution time is crucial.

### Methods & Strategy

**1. Coverage-Driven Test Selection**
Select tests that cover the changed code as a baseline — tests that execute impacted code are most relevant.

**2. Prioritization Metrics**
Tests can be scored by:
- **execution cost** (faster tests first)
- **coverage weight** (how much impacted code they exercise)
- **historical relevance** (e.g., tests that usually detect regressions)

**3. Confidence Scoring**
Reflect how well selected tests cover impacted code, enabling quality gates (e.g., stop when enough coverage confidence is reached).

**4. Test Staging**
Group tests into stages (smoke, regression, integration) based on priority and coverage depth.

✨ **Technical Building Blocks (Phase 3)**

- Coverage maps (test → code)
- Greedy and weighted algorithms for prioritization (e.g., additional coverage, set-cover heuristics)
- Heuristics combining impact, coverage, cost, and risk
- Confidence scoring and thresholds

### What this phase enables

- _Ranked_ test lists rather than undifferentiated sets
- Fast detection of likely regressions with minimal execution
- Adaptive strategies based on test cost and impact coverage

After this phase, ImpactScope can answer:

> _Which tests should run first, and with what confidence?_

---

<a id="phase4"></a>
### Phase 4 — Learning & AI Assistance (Optional, Assistive)

AI/ML is **not part of core deterministic analysis**; it _augments_ structured signals (impact + coverage + history) to make smarter prioritization decisions over time. Predictive test selection uses historical code changes and test outcomes to estimate which tests are likely to detect regressions for new changes.

### Where AI/ML Can Help

**1. Historical Dataset**
Collect over time:
- change features (which files/functions changed)
- test outcomes (pass/fail history)
- coverage and prioritization results
This dataset serves as the basis for ML modeling.

**2. Predictive Models**
Train supervised models (e.g., tree ensembles, logistic regression, or neural networks) to predict _failure likelihood_ for each test given a code change. Features can include:
- coverage overlap with impacted code
- historical failure rates
- test execution cost
Models can output probabilities used for ordering tests or deciding thresholds where deeper testing is needed.

**3. Retraining & Adaptation**
Continuously retrain models as:
- new tests are added/removed
- code and test suites evolve
- more outcome data accumulates
This ensures the model adapts to changes in the codebase and testing patterns.

**4. Assistive AI Usages**
In addition to predictive models, AI (e.g., language models) can provide:
- **natural language explanations** of why tests were prioritized
- **confidence insights** supporting decision-making
- **recommendations** for areas needing stronger coverage

These AI outputs augment explainability and help developers interpret results — they do _not_ replace core decisions.

✨ **Technical Building Blocks (Phase 4)**

- Historical dataset (change + test outcomes + coverage + priority results)
- Predictive models that output failure likelihood for tests
- Model retraining and adaptation over time
- AI for human-oriented reporting and insights (explanations, summaries)

### Explicit Non-Goals

- Replacing core impact logic with black-box AI
- Making test decisions solely based on prediction
- Sacrificing explainability for opaque models

AI/ML here _enhances_ deterministic logic and prioritization without replacing it.

**This roadmap is intended to show awareness and design thinking, not fixed commitments. ImpactScope remains an MVP focused on building a correct, deterministic foundation before exploring advanced capabilities.**

---

## Installation

### Requirements

- Python **3.10+**
- Git
- A C repository to analyze

### Setup (recommended: `uv`)

```bash
uv sync
```

This installs dependencies from `pyproject.toml` and manages the virtual environment automatically.

Alternatively, using a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# or .\.venv\Scripts\Activate.ps1 on Windows
pip install -e .
```

---

## Usage

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

If a commit contains no relevant C changes, ImpactScope reports this explicitly.

### Output Formats

ImpactScope supports two output formats: **text** (human-readable terminal output) and **JSON** (machine-readable for automation). For detailed examples and schema information, see the **[User Guide](docs/user-guide.md#understanding-output)**.

This shows both **who depends on the changed function** (upstream) and **what it depends on** (downstream), giving a concrete view of how a change propagates through the system.

---

## Architecture Overview

ImpactScope processes C code changes through a structured pipeline: Git diff analysis → AST parsing → call graph construction → impact propagation → results presentation. The codebase follows a modular architecture with clear separation of concerns across core analysis, utilities, output formatting, CLI, and visualization components. For detailed technical information, see the **[Architecture Guide](docs/architecture.md)**.

---

## Documentation

For more detailed information, see our comprehensive documentation:

- **[Getting Started](docs/getting-started.md)** - Quick start guide and installation
- **[User Guide](docs/user-guide.md)** - Detailed usage instructions and examples
- **[API Reference](docs/api-reference.md)** - Complete CLI options and JSON schema
- **[Architecture](docs/architecture.md)** - Technical deep dive
- **[CI Integration](docs/ci-integration.md)** - Automation and CI/CD setup
- **[Visualization Guide](docs/visualization-guide.md)** - HTML call graph usage
- **[Contributing](docs/contributing.md)** - Development setup and guidelines
- **[Roadmap](docs/roadmap.md)** - Future directions and vision
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and debugging
