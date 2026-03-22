---
id: mem.pattern.project.spec-driver-integration
name: spec-driver integration boundary
kind: memory
status: active
memory_type: pattern
created: '2026-03-23'
updated: '2026-03-23'
verified: '2026-03-23'
confidence: high
tags:
- integration
- spec-driver
- review
- ADR-002
summary: "autobahn imports spec_driver.orchestration for review operations — thin wrappers, no duplication, exceptions propagate. ADR-002 governs."
scope:
  paths:
    - autobahn/api/functions.py
    - autobahn/models/enums.py
  globs:
    - autobahn/api/**
    - autobahn/models/**
provenance:
  sources:
    - kind: adr
      ref: ADR-002
    - kind: doc
      ref: .spec-driver/deltas/DE-004-review_operations/DR-004.md
---

# spec-driver integration boundary

## Principle

**CLI for agents/humans, Python imports for orchestrators** ([[ADR-002]]).

autobahn is a Python library in the same uv workspace as spec-driver. It imports `spec_driver.orchestration` directly — no subprocess, no JSON envelope.

## Rules

1. **Don't duplicate, don't map — import or alias.** Types that spec-driver owns come from `spec_driver.orchestration`. autobahn does not maintain parallel definitions. Re-export aliases in `models/enums.py` for backward compat.

2. **Exceptions propagate.** spec-driver exceptions (`StateNotFoundError`, `FindingsNotFoundError`, `FindingNotFoundError`, etc.) reach autobahn callers directly. autobahn's own error taxonomy is for autobahn concerns (sessions, backends).

3. **spec-driver exports operations, not primitives.** autobahn calls composed operations (`prime_review`, `summarize_review`, `disposition_finding`), not building blocks. Domain logic (guards, validation, staleness) stays in spec-driver.

4. **Wrappers are thin.** autobahn's review API functions are ~1–10 lines of delegation. If a wrapper grows beyond trivial delegation, the operation belongs in spec-driver.

## Current public surface

```python
from spec_driver.orchestration import (
    prime_review, summarize_review, disposition_finding,  # operations
    PrimeResult, ReviewSummary, DispositionResult,        # result types
    BootstrapStatus, ReviewStatus, FindingStatus,          # enums
    FindingDispositionAction, DispositionAuthority,
    StateNotFoundError, FindingNotFoundError,               # exceptions
)
```

## Review enums in autobahn

Review-related enums (`BootstrapStatus`, `ReviewStatus`, `FindingStatus`, `FindingDispositionAction`, `DispositionAuthority`) are **re-exports** in `autobahn/models/enums.py`, not autobahn-owned definitions. Identity tests verify `autobahn.models.enums.BootstrapStatus is spec_driver.orchestration.BootstrapStatus`.

Non-review enums (`Role`, `WorkflowStatus`, `PhaseStatus`, etc.) are still autobahn-owned transcriptions — spec-driver doesn't yet export them as StrEnums.

## Workspace setup

```toml
# autobahn/pyproject.toml
[tool.uv.workspace]
members = ["spec-driver"]

[tool.uv.sources]
spec-driver = { workspace = true, editable = true }
```
