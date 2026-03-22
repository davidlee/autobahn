---
id: IP-002.PHASE-01
slug: "001-refactors"
name: "IP-002 Phase 01 — Refactors"
created: "2026-03-22"
updated: "2026-03-22"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-002.PHASE-01
plan: IP-002
delta: DE-002
objective: >-
  Schema validation in loader, extract shared constants, refactor Supervisor
  (remove observe, patch handle metadata). No new write paths.
entrance_criteria:
  - DR-002 reviewed (2 adversarial rounds)
exit_criteria:
  - SCHEMA_VERSIONS in artifacts/schema.py
  - Loader validates schema markers for all files
  - Observe inlined in api/functions.py
  - Supervisor.spawn patches handle metadata
  - TERMINAL_WORKFLOW_STATES shared constant
  - just check passes
verification:
  tests:
    - Schema validation acceptance + rejection tests
    - Regression — all 96 existing tests pass
  evidence:
    - "just check passes"
tasks:
  - id: "1.1"
    description: "Create artifacts/schema.py"
  - id: "1.2"
    description: "Add schema validation to loader"
  - id: "1.3"
    description: "TERMINAL_WORKFLOW_STATES + update consumers"
  - id: "1.4"
    description: "Refactor Supervisor + inline observe"
  - id: "1.5"
    description: "Verify all tests pass"
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-002.PHASE-01
```

# Phase 01 — Refactors

## 1. Objective

Schema validation, shared constants, Supervisor cleanup. No new write paths.

## 2. Links & References

- **DR-002**: §4.1 (schema), §4.2 (observe), §4.3 (handle), §4.4 (terminal states)
- **Decisions**: DEC-020, DEC-021, DEC-023, DEC-024, DEC-027

## 3. Entrance Criteria

- [x] DR-002 reviewed (2 adversarial rounds)

## 4. Exit Criteria / Done When

- [ ] `artifacts/schema.py` with `SCHEMA_VERSIONS` and `write_version()`
- [ ] Loader validates schema markers (state.yaml + all optional files)
- [ ] Loader rejects: missing schema, wrong schema, unsupported version
- [ ] `observe_session` inlined — no Supervisor involvement
- [ ] `Supervisor.observe` deleted
- [ ] `Supervisor.spawn` patches handle via `model_copy`
- [ ] `TERMINAL_WORKFLOW_STATES` in `models/enums.py`; local sets deleted
- [ ] `just check` passes

## 5. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 1.1 | Create artifacts/schema.py | [P] | DEC-027 |
| [ ] | 1.2 | Add schema validation to loader | - | Depends on 1.1; DEC-020 |
| [ ] | 1.3 | TERMINAL_WORKFLOW_STATES + update consumers | [P] | DEC-024 |
| [ ] | 1.4 | Refactor Supervisor + inline observe | [P] | DEC-021, DEC-023 |
| [ ] | 1.5 | Verify all tests pass | - | Depends on all |

## 6. Decisions & Outcomes

_(filled during execution)_

## 7. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes to Phase 02
