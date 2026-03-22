---
id: IP-001.PHASE-04
slug: "004-runtime-and-public-api"
name: "IP-001 Phase 04 — Runtime and public API"
created: "2026-03-22"
updated: "2026-03-22"
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-001.PHASE-04
plan: IP-001
delta: DE-001
objective: >-
  Supervisor coordinating harness + backend, public API functions
  (check_prerequisites, load_context, transition_from_handoff,
  spawn_role_session, observe_session, terminate_session, reconcile),
  and ReconciliationReport model.
entrance_criteria:
  - Phase 03 complete (adapter protocols + concrete implementations)
exit_criteria:
  - Supervisor class coordinates harness + backend per DR-001 §7
  - Public API functions per DR-001 §8 pass with mock adapters (VA-003)
  - transition_from_handoff computes correct plan from context
  - reconcile detects drift between artifact state and session state
  - autobahn.api module exports all public functions
  - just check passes
verification:
  tests:
    - VA-003 API function tests with mock adapters
    - Supervisor unit tests
    - Transition logic tests
    - Reconciliation drift detection tests
  evidence:
    - "just check passes"
tasks:
  - id: "4.1"
    description: "Implement Supervisor"
  - id: "4.2"
    description: "Implement transition_from_handoff"
  - id: "4.3"
    description: "Implement public API functions"
  - id: "4.4"
    description: "Implement reconciliation"
  - id: "4.5"
    description: "Wire up autobahn.api module"
  - id: "4.6"
    description: "Verify all tests pass"
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-001.PHASE-04
```

# Phase 04 — Runtime and public API

## 1. Objective

Wire together adapters with a Supervisor, implement transition logic and reconciliation, and expose the public API surface per DR-001 §8.

## 2. Links & References

- **Delta**: DE-001
- **Design Revision Sections**: DR-001 §7 (composition/Supervisor), §8 (public API), §3 (orchestration loop)
- **Design Decisions**: DEC-002 (sync reads, async runs), DEC-007 (caller-injected adapters), DEC-012 (v1: spawn/observe/terminate), DEC-017 (reconciliation re-reads state.yaml)

## 3. Entrance Criteria

- [x] Phase 03 complete

## 4. Exit Criteria / Done When

- [x] `Supervisor` in `autobahn/runtime/supervisor.py`
- [x] `transition_from_handoff` computes TransitionPlan from WorkflowContext
- [x] Public API: all 7 functions implemented
- [x] ReconciliationReport + DriftItem models defined
- [x] `from autobahn.api import ...` works for all public functions
- [x] API function tests with mock adapters (VA-003) — 13 tests
- [x] Reconciliation detects 4 drift types (state changed, session outlived, session died, orphaned)
- [x] `just check` passes — 94 tests

## 5. Verification

- `just check`
- API tests use mock harness/backend (no real subprocess needed — that's P05)
- Transition logic tests cover key workflow states
- Reconciliation tests: session alive but artifact terminal, session dead but artifact active

## 6. Assumptions & STOP Conditions

- Assumptions: mock adapters sufficient for API tests; real integration is Phase 05
- STOP when: reconciliation semantics unclear (check DEC-017)

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [x] | 4.1 | Implement Supervisor | - | spawn/observe/terminate |
| [x] | 4.2 | Implement transition_from_handoff | [P] | Terminal state + missing handoff checks |
| [x] | 4.3 | Implement public API functions | - | 7 functions, 13 API tests |
| [x] | 4.4 | Implement reconciliation | [P] | 4 drift types, 5 tests |
| [x] | 4.5 | Wire up autobahn.api module | - | All 7 functions exportable |
| [x] | 4.6 | Verify all tests pass | - | 94 total, lint+format clean |

### Task Details

- **4.1 Implement Supervisor**
  - **Approach**: Per DR-001 §7 composition — holds harness + backend, spawn/observe/terminate delegating to both.
  - **Files**: `autobahn/runtime/__init__.py`, `autobahn/runtime/supervisor.py`

- **4.2 Implement transition_from_handoff**
  - **Approach**: Read handoff from context, compute TransitionPlan. Raise PreconditionError if terminal state or missing handoff.
  - **Files**: `autobahn/runtime/transition.py`

- **4.3 Implement public API functions**
  - **Approach**: Per DR-001 §8. check_prerequisites (sync), load_context (sync, delegates to artifacts.loader), spawn/observe/terminate (async, delegates to Supervisor).
  - **Files**: `autobahn/api/__init__.py`, `autobahn/api/functions.py`

- **4.4 Implement reconciliation**
  - **Approach**: Re-read state.yaml (DEC-017), compare against sessions, report drift. ReconciliationReport model.
  - **Files**: `autobahn/runtime/reconcile.py`

- **4.5 Wire up autobahn.api module**
  - **Approach**: Export all public functions from `autobahn.api`.

- **4.6 Verify all tests pass**

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|

## 9. Decisions & Outcomes

- `observe_session` wraps `Supervisor.observe` as an async generator — avoids exposing Supervisor in the public API
- `ReconciliationReport` and `DriftItem` defined in reconcile.py alongside the logic (not in models/) — they're runtime-specific, not shared
- Reconciliation doesn't remove `Path` import from unused (removed from models/runtime.py)

## 10. Findings / Research Notes

- Async generators work cleanly with pytest-asyncio — no special fixtures needed
- Mock adapters pattern is clean: define in test file, Protocol structural typing validates them automatically

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (94 tests, just check green)
- [ ] Hand-off notes to Phase 05
