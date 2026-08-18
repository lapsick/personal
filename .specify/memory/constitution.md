<!--
Sync Impact Report
Version change: [template] → 1.0.0 (initial ratification)
Modified principles: n/a (first concrete adoption; all placeholders replaced)
Added sections:
  - I. Code Quality
  - II. Testing Standards (NON-NEGOTIABLE)
  - III. User Experience Consistency
  - IV. Performance Requirements
  - Python Environment Standards
  - Development Workflow & Quality Gates
  - Governance
Removed sections: Principle 5 slot (template allows 5; project scope requires 4 — see user
  request: code quality, testing standards, UX consistency, performance requirements)
Deferred/TODO placeholders: none
Templates requiring follow-up: none — plan/spec/tasks templates consume this file at runtime
  and do not embed principle text directly.
-->

# Personal Constitution

## Core Principles

### I. Code Quality
All code MUST pass automated formatting (`ruff format` or `black`) and static analysis
(`ruff` or `flake8`) with zero errors before merge. Type checking (`mypy`) MUST pass on all
new and modified modules. Every function and module MUST have a single, clear responsibility;
public functions, classes, and modules MUST carry docstrings describing purpose, arguments,
and return values. Code review MUST explicitly verify readability, naming clarity, and absence
of duplicated logic — style nitpicks that automated tooling already enforces MUST NOT be
relitigated in review.

**Rationale**: Automated, consistently enforced quality gates keep defect rates low and remove
subjective style debate from code review, letting reviewers focus on correctness and design.

### II. Testing Standards (NON-NEGOTIABLE)
New functionality MUST ship with automated `pytest` tests covering the happy path and
edge/error cases before merge. Bug fixes MUST include a regression test that fails before the
fix is applied and passes after. The test suite MUST maintain a minimum line coverage threshold
of 80%, enforced in CI; coverage MUST NOT decrease between merges. Unit tests MUST run in
isolation with no network or external-service dependencies; tests that require external systems
MUST be tagged and run as a separate integration suite.

**Rationale**: Python has no compiler to catch type or contract errors, so disciplined,
isolated automated testing is the primary safety net against regressions.

### III. User Experience Consistency
All user-facing surfaces (CLI output, API responses, error messages) MUST follow one consistent
format across the codebase — a single structured output mode (e.g., JSON) plus a single
human-readable mode, not a mix invented per command. Breaking changes to user-facing interfaces
(CLI flags, public API signatures, output schemas) MUST be versioned and documented; they MUST
NOT ship silently. Error messages MUST state what failed and, where possible, how to resolve it;
generic or swallowed exceptions surfaced to users are prohibited.

**Rationale**: Predictable, uniform interfaces reduce user confusion and support burden as the
number of entry points into the project grows.

### IV. Performance Requirements
Performance-sensitive code paths MUST be identified and benchmarked; a regression beyond 10%
against the last recorded baseline MUST block merge until justified or fixed. Non-trivial
functions operating on unbounded input MUST avoid unnecessary quadratic-or-worse complexity;
where such complexity is unavoidable, it MUST be documented with a rationale. I/O-bound or
network-bound operations MUST use batching, streaming, or async/concurrency patterns rather
than blocking, sequential loops, wherever the underlying library supports it.

**Rationale**: Python's interpreter overhead makes performance regressions easy to introduce
unnoticed; explicit budgets and benchmarks keep the system responsive as it scales.

## Python Environment Standards

The supported Python version MUST be pinned explicitly (e.g., `requires-python` in
`pyproject.toml`) and matched in CI. Dependencies MUST be managed through a lockfile (e.g.,
`uv.lock`, `poetry.lock`, or a pinned `requirements.txt`) so environments are reproducible
across machines and CI runs. All development and CI execution MUST occur inside an isolated
virtual environment; installing packages into a global interpreter is prohibited. New
third-party dependencies MUST be evaluated for maintenance status and license compatibility
before being added.

## Development Workflow & Quality Gates

All changes MUST go through pull request review with at least one approval before merge.
CI MUST run linting, type checking, and the full test suite on every pull request; a failing
CI run MUST block merge with no exceptions. Formatting and lint auto-fixes MUST run via
pre-commit hooks so issues are caught before CI, not during it.

## Governance

This constitution supersedes any informal or conflicting practice; where a conflict exists,
this document governs. Amendments require a documented rationale, an update to this file, and
a version bump following semantic versioning: MAJOR for backward-incompatible principle
removals or redefinitions, MINOR for new principles or materially expanded guidance, PATCH for
clarifications and wording fixes. Every pull request MUST be checked against these principles
during review; unjustified complexity or deviation MUST be flagged and resolved before merge.
Compliance MUST be reviewed at least once per release cycle to catch drift between stated
principles and actual practice.

**Version**: 1.0.0 | **Ratified**: 2026-08-18 | **Last Amended**: 2026-08-18
