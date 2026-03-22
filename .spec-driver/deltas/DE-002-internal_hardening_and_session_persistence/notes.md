# Notes for DE-002

## Status

- DE-002 scoped, DR-002 drafted and reviewed (2 external adversarial passes)
- IP-002 created with 2 phases, both phase sheets populated
- No implementation code written yet
- All `.spec-driver` changes committed and clean

## New Agent Instructions

### Task card

Delta: `DE-002` — Internal hardening and session persistence

### Required reading (in order)

1. `.spec-driver/deltas/DE-002-internal_hardening_and_session_persistence/DE-002.md` — delta scope
2. `.spec-driver/deltas/DE-002-internal_hardening_and_session_persistence/DR-002.md` — design revision (primary authority, 9 decisions DEC-020–DEC-028, 2 adversarial reviews in Appendix A)
3. `.spec-driver/deltas/DE-002-internal_hardening_and_session_persistence/IP-002.md` — implementation plan (2 phases)
4. `.spec-driver/deltas/DE-002-internal_hardening_and_session_persistence/phases/phase-01.md` — active phase sheet

### Related documents

- `.spec-driver/audits/AUD-001-de_001_conformance_audit/AUD-001.md` — source audit (findings F-001, F-002, F-005, F-007, F-011)
- `.spec-driver/deltas/DE-001-repository_bootstrap_and_architecture_foundation/DR-001.md` — predecessor design (coupling rules §5, adapter protocols §7, public API §8, artifact contract §9)

### Key files to modify

- `autobahn/artifacts/loader.py` — add schema validation (§4.1)
- `autobahn/artifacts/schema.py` — NEW: shared SCHEMA_VERSIONS (§4.1/§4.5)
- `autobahn/artifacts/writer.py` — NEW: write_sessions_file (§4.5, Phase 2)
- `autobahn/runtime/supervisor.py` — remove observe, patch handle metadata (§4.2/§4.3)
- `autobahn/api/functions.py` — inline observe, spawn persistence, persist_session_statuses (§4.2/§4.6/§4.8)
- `autobahn/models/enums.py` — add TERMINAL_WORKFLOW_STATES (§4.4)
- `autobahn/runtime/transition.py` — import shared constant (§4.4)
- `autobahn/runtime/reconcile.py` — import shared constant, add session_id to DriftItem (§4.4/§4.8)

### Relevant memories

- `project_pytest_invocation.md` — use `uv run python -m pytest`, not `uv run pytest` (nix devshell shadow)
- `project_track_specdriver_conventions.md` — hatch, >=3.12, ruff, 2-space indent

### Relevant doctrine

- Commit policy: frequent small commits of `.spec-driver/**`, conventional messages (`fix(DE-002): ...`)
- Ceremony mode: `town_planner`

### Key design decisions (DR-002)

- **DEC-020**: Schema validation — exact match, frozenset[int] per schema
- **DEC-021**: observe is a free async generator, not Supervisor method
- **DEC-022**: Writer: pure function, atomic rename, explicit DR-001 §9 write protocol override (no lock, no output validation)
- **DEC-023**: Supervisor.spawn patches handle via model_copy
- **DEC-024**: TERMINAL_WORKFLOW_STATES frozenset in models/enums.py
- **DEC-025**: reconcile stays read-only; persist_session_statuses is sync, report-driven, no backend param
- **DEC-026**: Spawn persistence failure → success with warning
- **DEC-027**: SCHEMA_VERSIONS in artifacts/schema.py (public, shared); write at highest supported version
- **DEC-028**: DriftItem gains session_id field for persist_session_statuses

### Incomplete work / loose ends

- **DE-001 carry-forwards** still open: RE-001 brief.md update, spec-driver symlink cleanup, `.claude/settings.local.json` in git
- **DE-105** (spec-driver bug): `create phase` appends duplicate entry to IP phases list — next agent will need to fix these manually after each `create phase` (as we did throughout DE-001)

### Commit-state guidance

- All `.spec-driver/**` changes committed and clean
- No code changes pending
- Worktree is clean except `.claude/settings.local.json` (pre-existing, not ours)

### Advice for next agent

- Phase 01 is pure refactoring — no new write paths. All 96 existing tests should continue passing throughout. Run `just check` after each task.
- Schema validation (task 1.2) will touch the loader's core `load_workflow_dir` function — be careful with the callsite ordering (validate schema marker BEFORE model_validate, not after).
- The Supervisor refactor (task 1.4) and observe inline (task 1.5) can be done together since they're tightly coupled — removing observe from Supervisor and inlining it in api/functions.py.
- The existing test_api.py `TestObserveSession` test should pass unchanged since observe_session's signature doesn't change.
- All test fixtures already carry correct `schema` and `version` fields — confirmed during AUD-001. No fixture updates needed.
- Phase 02 depends on Phase 01 completing (schema.py needed by the writer).
