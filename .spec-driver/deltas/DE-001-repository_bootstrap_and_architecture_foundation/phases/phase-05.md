---
id: IP-001.PHASE-05
slug: "005-vertical-slice-integration"
name: "IP-001 Phase 05 — Vertical slice integration"
created: "2026-03-22"
updated: "2026-03-22"
status: draft
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

- [ ] Integration test: load → transition → spawn → observe → terminate → reconcile
- [ ] Uses real subprocess backend (not mocks)
- [ ] `just check` passes
- [ ] All DE-001 acceptance criteria met

## 5. Verification

- `just check`
- Integration test spawns a real `python -c` process, observes it complete, reconciles state

## 6. Assumptions & STOP Conditions

- Assumptions: `python` available on PATH for subprocess
- STOP when: nix sandbox interferes with subprocess spawning

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 5.1 | Write end-to-end integration test | - | VA-004 |
| [ ] | 5.2 | Verify all tests + acceptance criteria | - | Depends on 5.1 |

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

_(filled during execution)_

## 10. Findings / Research Notes

_(filled during execution)_

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] All DE-001 acceptance criteria met
