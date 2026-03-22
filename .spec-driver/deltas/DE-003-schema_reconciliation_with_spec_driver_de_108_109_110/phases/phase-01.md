---
id: IP-003.PHASE-01
slug: "001-schema-reconciliation"
name: "IP-003 Phase 01 — Schema reconciliation"
created: "2026-03-22"
updated: "2026-03-22"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-003.PHASE-01
plan: IP-003
delta: DE-003
objective: >-
  Reconcile autobahn models with canonical spec-driver schemas (DE-108/109/110).
  Enum removals, sessions.yaml dict model, review/finding model enrichment,
  writer + API + reconcile updates, fixtures, contract tests.
entrance_criteria:
  - DR-003 reviewed (2 adversarial rounds)
  - ADR-001 accepted
exit_criteria:
  - BootstrapStatus has 5 values (no WARMING), canonical order
  - ReviewStatus has 4 values (no BLOCKED)
  - SessionsFile uses dict[str, SessionEntry]; writer produces role-keyed dict
  - FindingDisposition.authority is DispositionAuthority enum (required)
  - Finding has required title field
  - ReviewRound has reviewer_role, completed_at, summary, session
  - ReviewBlock has session_scope, last_bootstrapped_at, source_handoff
  - StalenessKeyBlock has phase_id (no state_sha)
  - All fixtures match canonical schemas
  - just check passes
verification:
  tests:
    - Contract tests for BootstrapStatus, ReviewStatus values
    - Loader tests with canonical-format fixtures
    - Writer round-trip with role-keyed dict
    - API tests — spawn writes dict, persist_session_statuses with dict
    - Reconcile tests — orphan detection with dict
    - Model tests — FindingDisposition, _CANONICAL_SESSION_FIELDS
    - Regression — all existing tests updated and passing
  evidence:
    - "just check passes"
tasks:
  - id: "1.1"
    description: "Enum removals + contract tests"
  - id: "1.2"
    description: "SessionEntry/SessionsFile restructure"
  - id: "1.3"
    description: "Writer update for role-keyed dict"
  - id: "1.4"
    description: "Review/finding model updates"
  - id: "1.5"
    description: "API + reconcile updates for dict sessions"
  - id: "1.6"
    description: "Fixture updates"
  - id: "1.7"
    description: "Verify all tests pass"
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-003.PHASE-01
```

# Phase 01 — Schema reconciliation

## 1. Objective

Reconcile all autobahn models with canonical spec-driver schemas. Single phase — all changes are interdependent.

## 2. Links & References

- **DR-003**: §4.1 (enums), §4.2 (sessions model), §4.3 (writer), §4.4 (spawn), §4.5 (persist), §4.6 (reconcile), §4.7–4.11 (review/finding models)
- **Decisions**: DEC-030, DEC-031, DEC-032, DEC-033
- **ADR-001**: Schema authority contract

## 3. Entrance Criteria

- [x] DR-003 reviewed (2 adversarial rounds)
- [x] ADR-001 accepted

## 4. Exit Criteria / Done When

- [ ] `BootstrapStatus` — 5 values, `COLD WARM STALE REUSABLE INVALID` order, no `WARMING`
- [ ] `ReviewStatus` — 4 values, no `BLOCKED`
- [ ] `SessionsFile.sessions` is `dict[str, SessionEntry]`
- [ ] `SessionEntry` has `session_name`, `status`, `last_seen`, `sandbox` (canonical) + autobahn-extra fields
- [ ] Writer produces role-keyed dict with canonical null preservation
- [ ] `_persist_new_session` warns on active session overwrite
- [ ] `persist_session_statuses` matches on `session_name`
- [ ] Reconcile orphan detection iterates dict, hoisted `handle_ids`
- [ ] `FindingDisposition.authority` is `DispositionAuthority` (required); 5 new fields
- [ ] `Finding` has `title` (required), `summary` optional, `files`, `related_invariants`
- [ ] `ReviewRound` has `reviewer_role`, `completed_at`, `summary`, `session`
- [ ] `ReviewBlock` has `session_scope`, `last_bootstrapped_at`, `source_handoff`; no `current_round`
- [ ] `StalenessKeyBlock` has `phase_id`; no `state_sha`
- [ ] Fixtures match canonical schemas
- [ ] `_CANONICAL_SESSION_FIELDS` contract test
- [ ] `FindingDisposition` model test with required authority
- [ ] `just check` passes

## 5. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 1.1 | Enum removals + contract tests | [P] | DEC-109-002, DEC-109-003 |
| [ ] | 1.2 | SessionEntry/SessionsFile restructure | [P] | DEC-030, DEC-031 |
| [ ] | 1.3 | Writer update for role-keyed dict | - | Depends on 1.2; DR-003 §4.3 |
| [ ] | 1.4 | Review/finding model updates | [P] | DEC-033; DR-003 §4.7–4.11 |
| [ ] | 1.5 | API + reconcile updates for dict sessions | - | Depends on 1.2; DR-003 §4.4–4.6 |
| [ ] | 1.6 | Fixture updates | - | Depends on 1.1, 1.2, 1.4 |
| [ ] | 1.7 | Verify all tests pass | - | Depends on all |

## 6. Decisions & Outcomes

_(filled during execution)_

## 7. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes for DE-004
