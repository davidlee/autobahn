---
id: IP-001.PHASE-05
slug: "005-vertical-slice-integration"
name: "IP-001 Phase 05 — Vertical slice integration"
created: "2026-03-22"
updated: "2026-03-22"
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-001.PHASE-05
plan: IP-001
delta: DE-001
objective: >-
  End-to-end integration test proving the full session lifecycle with a real
  subprocess: load_context -> transition_from_handoff -> spawn -> observe ->
  terminate -> reconcile. Uses Claude Code adapter + subprocess backend against
  fixture workflow directory.
entrance_criteria:
  - Phase 04 complete (runtime + public API)
exit_criteria:
  - Integration test exercises full lifecycle with real subprocess (VA-004)
  - Test uses fixture workflow dir, not mocks
  - All verification gates pass (just check)
  - DE-001 acceptance criteria met
verification:
  tests:
    - VA-004 real subprocess backend integration test
  evidence:
    - "just check passes"
    - "Integration test spawns real process, observes completion, reconciles"
tasks:
  - id: "5.1"
    description: "Write end-to-end integration test"
  - id: "5.2"
    description: "Verify all tests pass and acceptance criteria met"
risks:
  - description: "Subprocess timing sensitivity"
    mitigation: "Use fast-completing commands (echo/python -c)"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-001.PHASE-05
```

# Phase 05 — Vertical slice integration

## 1. Objective

Prove the architecture with an end-to-end integration test exercising the full API flow with a real subprocess.

## 2. Links & References

- **Delta**: DE-001
- **Design Revision Sections**: DR-001 §3 (orchestration loop), §8 (public API)
- **IP-001 §6**: Integration test plan (VA-004)

## 3. Entrance Criteria

- [x] Phase 04 complete

## 4. Exit Criteria / Done When

- [x] Integration test: load → transition → spawn → observe → reconcile (full lifecycle)
- [x] Uses real subprocess backend (python -c one-liner)
- [x] `just check` passes — 95 tests
- [x] All DE-001 acceptance criteria met

## 5. Verification

- `just check`
- Integration test spawns a real `python -c` process, observes it complete, reconciles state

## 6. Assumptions & STOP Conditions

- Assumptions: `python` available on PATH for subprocess
- STOP when: nix sandbox interferes with subprocess spawning

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [x] | 5.1 | Write end-to-end integration test | - | VA-004 — real subprocess lifecycle |
| [x] | 5.2 | Verify all tests + acceptance criteria | - | 95 tests, all green |

### Task Details

- **5.1 Write end-to-end integration test**
  - **Approach**: Create fixture workflow dir in tmp_path, use real ClaudeCodeAdapter (with `python` as executable override) + SubprocessBackend. Exercise: load_context → transition_from_handoff → spawn_role_session → observe_session → reconcile.
  - **Files**: `tests/test_integration.py`

- **5.2 Verify all tests pass**
  - **Approach**: `just check`, verify DE-001 acceptance criteria

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|

## 9. Decisions & Outcomes

- Test harness uses `sys.executable -c "print('...')"` instead of `echo` — guarantees correct Python is used
- Integration test expects SESSION_DIED_UNEXPECTEDLY drift — session completes but workflow is still "implementing". This is correct behaviour: the reconciler reports that a session ended while the workflow hasn't moved to a terminal state.

## 10. Findings / Research Notes

- Real subprocess lifecycle works cleanly — no timing issues with the 0.05s poll interval
- SubprocessBackend in-memory dict pattern works for single-process orchestration (DEC-011)

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (95 tests, all green)
- [x] All DE-001 acceptance criteria met
