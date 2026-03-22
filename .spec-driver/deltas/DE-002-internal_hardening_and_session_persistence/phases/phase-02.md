---
id: IP-002.PHASE-02
slug: "002-write-path"
name: "IP-002 Phase 02 — Write path"
created: "2026-03-22"
updated: "2026-03-22"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-002.PHASE-02
plan: IP-002
delta: DE-002
objective: >-
  Sessions.yaml writer, DriftItem.session_id, spawn persistence,
  persist_session_statuses. autobahn can now persist and update session state.
entrance_criteria:
  - Phase 01 complete (schema validation, Supervisor refactor)
exit_criteria:
  - write_sessions_file() in artifacts/writer.py with atomic rename
  - DriftItem gains session_id field; reconcile populates it
  - spawn_role_session writes to sessions.yaml (DEC-026 error handling)
  - persist_session_statuses (sync, report-driven) updates dead/orphaned sessions
  - Round-trip test via load_workflow_dir (VA-005)
  - just check passes
verification:
  tests:
    - VA-005 writer tests (atomic write, round-trip, empty sessions)
    - VA-003 updated — spawn writes, persist_session_statuses 3 cases
    - Integration test updated if needed
  evidence:
    - "just check passes"
tasks:
  - id: "2.1"
    description: "Implement write_sessions_file in artifacts/writer.py"
  - id: "2.2"
    description: "Add session_id to DriftItem, update reconcile"
  - id: "2.3"
    description: "Spawn persistence in api/functions.py"
  - id: "2.4"
    description: "Implement persist_session_statuses"
  - id: "2.5"
    description: "Verify all tests pass"
risks:
  - description: "Datetime YAML round-trip"
    mitigation: "VA-005 round-trip test covers this explicitly"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-002.PHASE-02
```

# Phase 02 — Write path

## 1. Objective

Sessions.yaml write support. After this phase, autobahn persists session state across invocations and updates dead/orphaned session statuses.

## 2. Links & References

- **DR-002**: §4.5 (writer), §4.6 (spawn writes), §4.7 (reconcile read-only), §4.8 (persist_session_statuses)
- **Decisions**: DEC-022, DEC-025, DEC-026, DEC-027, DEC-028

## 3. Entrance Criteria

- [ ] Phase 01 complete

## 4. Exit Criteria / Done When

- [ ] `artifacts/writer.py` with `write_sessions_file()` (atomic rename, version from schema.py)
- [ ] `DriftItem.session_id` field populated by reconcile
- [ ] `spawn_role_session` writes session entry (DEC-026: success+warning on write failure)
- [ ] `persist_session_statuses(context, report)` — sync, report-driven, 3 cases tested
- [ ] VA-005: round-trip via `load_workflow_dir`, empty sessions
- [ ] `just check` passes

## 5. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 2.1 | Implement write_sessions_file | - | DEC-022, DEC-027 |
| [ ] | 2.2 | DriftItem.session_id + update reconcile | [P] | DEC-028 |
| [ ] | 2.3 | Spawn persistence in api/functions.py | - | Depends on 2.1; DEC-026 |
| [ ] | 2.4 | Implement persist_session_statuses | - | Depends on 2.1, 2.2; DEC-025 |
| [ ] | 2.5 | Verify all tests pass | - | Depends on all |

## 6. Decisions & Outcomes

_(filled during execution)_

## 7. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] DE-002 acceptance criteria met
