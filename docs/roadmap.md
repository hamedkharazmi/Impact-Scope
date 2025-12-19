# Roadmap & Future Directions

ImpactScope is intentionally developed in **phases**, each solving a concrete sub-problem toward the broader goal of *impact-based test selection*. The core question is:

> _Given a code change, which tests must be re-run to maintain confidence — without running the entire suite?_

This cannot be reliably solved with a single method. ImpactScope follows a layered approach inspired by both industry practice and research: combining static structure, dynamic coverage, heuristics, and learned prioritization.

---

## Phase 1 — Deterministic Static Impact Analysis (Implemented)

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

---

## Phase 2 — Test Awareness & Coverage Mapping (Next Step)

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

## Phase 3 — Test Selection & Confidence Modeling (Planned)

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

## Phase 4 — Learning & AI Assistance (Optional, Assistive)

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

---

## Future Directions

ImpactScope is currently an MVP focused on correctness, determinism, and architectural clarity.
The following items outline possible next steps and directions, based on review of industrial Change Impact Analysis tools and real-world workflows. They are intentionally non-binding and exploratory.

### Near-Term Extensions (Natural Next Steps)

These represent obvious follow-ups once deterministic impact data is available.

- Impact scoring and basic risk categorization (e.g. LOW / MEDIUM / HIGH)
- Human-readable summaries explaining why a change is risky
- Noise reduction heuristics to prioritize relevant impact paths
- Improved output formatting for CI and automation use

### Industry-Inspired Capabilities (Observed in Mature Tools)

Based on reviewing established CIA tools (e.g. certification-grade and enterprise systems), potential directions include:

- Change-based test selection and prioritization
- Baseline-to-baseline impact comparison
- Cross-module and system-level impact impact aggregation
- Lightweight traceability between changes, impact, and tests

These are not goals of the MVP, but provide context for how ImpactScope could evolve.

### AI-Assisted Enhancements (Optional & Assistive)

AI is considered only as a supporting layer, not part of core analysis.

Possible roles include:

- Explaining impact paths and propagation in natural language
- Suggesting review or testing focus areas
- Summarizing impact results for CI or pull request discussions

Beyond LLMs, learning-based approaches could be explored in the future:

- Learning which impact patterns are frequently low-risk vs high-risk
- Ranking or prioritizing impact paths based on historical data
- Assisting in noise reduction without removing deterministic results

AI components would operate strictly on top of structured output, not replace static analysis.

### Long-Term Outlook

If ImpactScope grows beyond MVP scope, longer-term directions may include:

- Data-flow or control-flow–aware impact propagation
- Scalable graph backends for large codebases
- Support for additional languages

**Positioning Note**

This roadmap is intended to show awareness and design thinking, not fixed commitments.
ImpactScope remains an MVP focused on building a correct, deterministic foundation before exploring advanced capabilities.

---

## Status

ImpactScope is currently a **working prototype** under active development.

The focus so far has been on **correctness, clarity, and architectural soundness** rather than feature completeness. The goal is to evolve ImpactScope into a **portfolio-grade Change Impact Analysis tool** that demonstrates:

- Static analysis fundamentals
- Call graph reasoning
- Deterministic tooling design
- Realistic CI and developer workflows
