# Addressing Phase 1 Limitations: Research & Design Notes

This document summarizes research findings and practical design decisions aimed at mitigating the known limitations of Phase 1 in Impact-Scope.

The goal is **not to eliminate all limitations**, but to reduce false positives and improve precision where it matters, while preserving scalability and explainability.

---

## 1. Why These Limitations Exist

C (especially low-level and driver code) introduces inherent challenges:

- Extensive use of pointers and indirect calls
- Data-dependent control flow
- Macros and conditional compilation
- Inline assembly and platform-specific behavior

Any scalable static analysis must therefore trade precision for performance.

---

## 2. Over-Approximation and False Positives

**Problem:**
Pure call-graph and AST-based analysis propagates impact conservatively, often including code that is not actually affected.

**Relevant Research:**
- *Refining Interprocedural Change-Impact Analysis using Equivalence Relations* (ISSTA 2017)
  https://www.microsoft.com/en-us/research/wp-content/uploads/2017/05/main.pdf

**Mitigation Strategy:**
- Introduce semantic-aware filtering to downgrade or ignore semantics-preserving changes
- Refine propagation only when necessary (on-demand)

---

## 3. Function Pointers and Indirect Calls

**Problem:**
Function pointers and callbacks prevent accurate call-graph construction.

**Relevant Research:**
- Andersen’s Pointer Analysis
  https://en.wikipedia.org/wiki/Andersen%27s_algorithm
- Steensgaard’s Pointer Analysis
  https://en.wikipedia.org/wiki/Steensgaard%27s_algorithm
- *SUPA: Demand-Driven Pointer Analysis via Value-Flow Refinement*
  https://yuleisui.github.io/publications/tse18.pdf

**Mitigation Strategy:**
- Use a conservative call graph as a baseline
- Apply **demand-driven pointer/value-flow analysis** only for affected regions
- Refine indirect call targets incrementally instead of globally

---

## 4. Data-Flow and Control-Flow Precision

**Problem:**
Runtime execution paths and data-dependent branches are not modeled precisely in Phase 1.

**Relevant Research:**
- Statement-level Change Impact Analysis for C
  https://www.sciencedirect.com/science/article/pii/S0140366421004199

**Mitigation Strategy:**
- Track impact at statement granularity where possible
- Use refined def-use and value-flow relations to improve precision
- Accept that full path sensitivity is not scalable for large C codebases

---

## 5. Scalability and Noise

**Problem:**
Improving precision often increases computational cost.

**Relevant Research / Implementations:**
- SVF: Static Value-Flow Analysis Framework
  https://github.com/SVF-tools/SVF

**Mitigation Strategy:**
- Separate analysis into:
  - fast over-approximate base analysis
  - bounded, on-demand refinement
- Enforce analysis budgets and depth limits
- Prefer explainable, deterministic results over maximal precision

---

## 6. Role of AI and LLMs

AI is **not used in the core analysis**.

Potential auxiliary uses include:
- Ranking ambiguous candidates
- Suggesting likely indirect call targets
- Explaining analysis results

AI is treated strictly as an assistive layer, never as a replacement for static analysis.

---

## 7. Summary

Impact-Scope follows a **hybrid approach**:

- Fast, conservative static analysis
- Demand-driven pointer and value-flow refinement
- Semantic filtering to reduce noise
- Coverage-aware test selection (future work)

This design aligns with existing research while remaining practical and implementable for real-world C projects.
