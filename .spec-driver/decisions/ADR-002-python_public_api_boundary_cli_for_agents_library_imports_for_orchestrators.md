---
id: ADR-002
title: "ADR-002: Python public API boundary \u2014 CLI for agents, library imports for orchestrators"
status: draft
created: '2026-03-23'
updated: '2026-03-23'
reviewed: '2026-03-23'
owners: []
supersedes: []
superseded_by: []
policies: []
specs: []
requirements: []
deltas:
  - DE-004
revisions: []
audits: []
related_decisions:
  - ADR-001
related_policies: []
tags:
  - architecture
  - integration
  - api-boundary
summary: 'spec-driver exposes two interfaces: CLI for agents/humans, Python public API for orchestrators. autobahn imports the Python API directly instead of shelling out to CLI subprocess.'
---

# ADR-002: Python public API boundary — CLI for agents, library imports for orchestrators

## Context

autobahn orchestrates spec-driver workflow operations (review priming, finding disposition, state transitions). The original design (DR-001 §8, DE-004 initial scope) assumed autobahn would invoke spec-driver via CLI subprocess with `--format json`, parsing the JSON envelope from stdout.

However:

1. **Both packages live in the same uv workspace.** spec-driver is already an editable dependency of autobahn. There is no process boundary to respect.
2. **The CLI is a presentation layer.** Review commands in `cli/workflow.py` are thin wrappers around domain functions in `supekku.scripts.lib.workflow.*`. The orchestrator doesn't need the JSON serialization round-trip.
3. **subprocess invocation is lossy and complex.** It requires: process spawn, stdout capture, JSON parsing, exit code interpretation, error kind mapping — all to call Python functions that are already importable.
4. **The CLI contract (DR-108) was designed for agents and humans**, not for Python orchestrators. Agents need text/JSON. Orchestrators need typed Python objects.

The question: what is the right integration boundary between autobahn and spec-driver?

## Decision

### 1. Two interfaces, two audiences

spec-driver exposes two distinct interfaces:

| Interface | Audience | Transport | Contract |
|-----------|----------|-----------|----------|
| CLI (`spec-driver review ...`) | Agents, humans | Text/JSON via stdout, exit codes | DR-108 JSON envelope |
| Python public API (`spec_driver.workflow`) | Orchestrators (autobahn) | Direct function calls, typed returns | Re-export module |

### 2. New `spec_driver` top-level package

A new `spec_driver/` package in the spec-driver repo serves as the narrow, stable public API surface. It starts as a re-export façade over `supekku` internals:

```
spec_driver/
  __init__.py              # version only
  workflow/
    __init__.py            # curated re-exports from supekku internals
    review.py              # review-specific re-exports (if __init__ grows)
    types.py               # type re-exports autobahn needs
```

Both `supekku` and `spec_driver` ship in the same distribution. `spec_driver` is the public API; `supekku` is the implementation. This follows the standard pattern (cf. `_pytest` vs `pytest`).

### 3. The re-export file is the contract

If spec-driver refactors internals (renames modules, moves functions), only the re-export file changes. autobahn's imports don't break because they target `spec_driver.workflow`, not `supekku.scripts.lib.workflow.*`.

The public surface is narrow and auditable — approximately 30 symbols for the review operations surface.

### 4. autobahn imports from `spec_driver.workflow`

```python
# autobahn/api/functions.py
from spec_driver.workflow import (
    read_state, build_review_index, evaluate_staleness,
    BootstrapStatus, ReviewFinding, ...
)
```

No subprocess. No JSON envelope parsing. No exit code mapping. No tool adapter layer.

### 5. CLI remains the agent/human interface

The CLI commands (`spec-driver review prime`, etc.) continue to exist unchanged. They remain the interface for agents calling spec-driver from within sessions. This decision does not deprecate or reduce the CLI — it clarifies that the CLI is not the only interface.

## Consequences

### Positive

- Eliminates subprocess spawn, JSON serialization round-trip, and envelope parsing for every review operation
- Real Python exceptions instead of exit code + error kind mapping
- Type safety at the import boundary — spec-driver's Pydantic models are directly usable
- autobahn's "tool adapter" layer (protocol.py, spec_driver.py in DE-004 original scope) becomes unnecessary — simpler codebase
- The re-export pattern provides a clean migration path: when/if `supekku` is renamed to `spec_driver`, the public surface is already in the right namespace

### Negative

- autobahn is now coupled to spec-driver at the Python import level, not just at the CLI contract level — though this coupling is managed by the re-export façade
- spec-driver gains a new maintenance obligation: the `spec_driver.workflow` re-export surface must stay current when internals change
- If the repos were ever separated (different CI, different release cadence), the import boundary would need to become a versioned package dependency instead of a workspace member

### Neutral

- ADR-001 (schema authority) is unaffected — spec-driver remains authoritative for workflow file schemas regardless of integration mechanism
- The `ToolInvocationError` and `ToolContractError` error types in autobahn's taxonomy remain valid for cases where autobahn does invoke external tools (future harness adapters), but are not needed for spec-driver review operations

## Verification

- autobahn's existing contract tests (enum transcription, model conformance) continue to validate alignment
- Import-time failures surface immediately via `uv run python -c "from spec_driver.workflow import ..."`
- `uv run pytest` in both packages catches breakage within the same workspace

## References

- ADR-001: Spec-driver schema authority and autobahn extension contract
- DR-001 §8: Original review operations API sketch (OQ-001)
- DR-108: Review CLI contract for structured machine consumption
- DE-004: Review operations (autobahn) — re-scoped by this decision
