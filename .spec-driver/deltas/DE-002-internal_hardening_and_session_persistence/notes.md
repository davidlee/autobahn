# Notes for DE-002

## Status

- DE-002 `in-progress`
- **Phase 01 complete** — all 5 tasks done, 101 tests pass, `just check` clean
- Phase 02 not started

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

## Phase 01 — Implementation Log

### Completed tasks

| Task | What | Commits |
|------|------|---------|
| 1.1 | Created `artifacts/schema.py` — `SCHEMA_VERSIONS` map + `write_version()` | `16bf42d` |
| 1.2 | Added `_validate_schema_marker` to loader, called before each `model_validate` | `16bf42d` |
| 1.3 | `TERMINAL_WORKFLOW_STATES` in `models/enums.py`; deleted local sets from `transition.py` and `reconcile.py` | `16bf42d` |
| 1.4 | Removed `Supervisor.observe`; inlined in `api/functions.py`; `spawn` patches handle via `model_copy` | `16bf42d` |
| 1.5 | Full suite: 101 tests pass (96 original + 5 new schema validation tests) | `16bf42d` |

### Adaptations from DR-002

- `_OPTIONAL_FILES` changed from `dict[str, type[BaseModel]]` to `dict[str, tuple[str, type[BaseModel]]]` — the tuple carries the expected schema string alongside the model class. DR-002 showed this pattern but didn't spell out the type change.
- `test_invalid_schema_raises` updated: the original test sent `foo: bar` which now hits schema validation (missing schema field) before pydantic validation. Changed the fixture to include valid schema+version so it still exercises the pydantic contract path.
- Removing `WorkflowStatus` import from `transition.py` — it was only used by the deleted `_TERMINAL_STATES` local.

### Surprises / observations

- None significant. DR-002 code samples were accurate; fixtures already had correct markers. Clean execution.
- Test count grew from 96 → 101 (5 new schema validation tests in `TestSchemaValidation`).

### Incomplete work / loose ends

- **DE-001 carry-forwards** still open: RE-001 brief.md update, spec-driver symlink cleanup, `.claude/settings.local.json` in git
- **DE-105** (spec-driver bug): `create phase` appends duplicate entry to IP phases list

### Commit-state guidance

- Code committed at `16bf42d`, delta status at `92419a2`
- `.spec-driver/**` notes pending (this file)
- Worktree otherwise clean except `.claude/settings.local.json` (pre-existing, not ours)

### Advice for next agent

- Phase 02 is the write path: `artifacts/writer.py`, spawn persistence in `api/functions.py`, `persist_session_statuses`, `DriftItem.session_id` in `reconcile.py`.
- `artifacts/schema.py` is now available for the writer to import `write_version()`.
- `DriftItem.session_id` addition (DEC-028) needs to happen in Phase 02 before `persist_session_statuses` — reconcile must populate it at each drift item creation site.
- The reconcile tests don't currently assert on `session_id` — they'll need updating when the field is added.
