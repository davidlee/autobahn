# Notes for DE-003

## Status

- DE-003 `draft`, DR-003 reviewed (2 adversarial rounds), IP-003 planned (1 phase, 7 tasks)
- ADR-001 accepted — establishes schema authority contract
- DE-004 (review operations) scoped but not designed — depends on DE-003 completing
- No implementation code written yet
- All `.spec-driver` changes committed and clean

## New Agent Instructions

### Task card

Delta: `DE-003` — Schema reconciliation with spec-driver DE-108/109/110

### Required reading (in order)

1. `.spec-driver/decisions/ADR-001-spec_driver_schema_authority_and_autobahn_extension_contract.md` — governs all model decisions
2. `.spec-driver/deltas/DE-003-schema_reconciliation_with_spec_driver_de_108_109_110/DE-003.md` — delta scope
3. `.spec-driver/deltas/DE-003-schema_reconciliation_with_spec_driver_de_108_109_110/DR-003.md` — design revision (primary authority, 4 decisions DEC-030–DEC-033, 2 adversarial reviews in Appendix A)
4. `.spec-driver/deltas/DE-003-schema_reconciliation_with_spec_driver_de_108_109_110/IP-003.md` — implementation plan (1 phase)
5. `.spec-driver/deltas/DE-003-schema_reconciliation_with_spec_driver_de_108_109_110/phases/phase-01.md` — active phase sheet

### Related documents

- `.spec-driver/deltas/DE-002-internal_hardening_and_session_persistence/DR-002.md` — predecessor design (sessions.yaml writer, reconcile, API patterns)
- `.spec-driver/deltas/DE-001-repository_bootstrap_and_architecture_foundation/DR-001.md` — coupling rules §5, models §6, API §8, artifact contract §9

### Key files to modify

- `autobahn/models/enums.py` — remove `WARMING`, `BLOCKED`; reorder `BootstrapStatus` (§4.1)
- `autobahn/models/artifacts.py` — `SessionEntry`/`SessionsFile` restructure; `FindingDisposition`, `Finding`, `ReviewRound`, `ReviewBlock`, `StalenessKeyBlock` updates (§4.2, §4.7–4.11)
- `autobahn/artifacts/writer.py` — role-keyed dict output with `_serialize_session_entry` (§4.3)
- `autobahn/api/functions.py` — `_persist_new_session` (dict + overwrite warning), `persist_session_statuses` (session_name matching) (§4.4–4.5)
- `autobahn/runtime/reconcile.py` — orphan detection for dict sessions, hoist `handle_ids` (§4.6)
- `tests/fixtures/workflow/sessions.yaml` — role-keyed dict format
- `tests/fixtures/workflow/review-findings.yaml` — add `title` to findings, add disposition fixture
- `tests/fixtures/workflow/review-index.yaml` — add `last_bootstrapped_at`, rename `scope`→`session_scope`
- `tests/test_enums.py` — updated value lists
- `tests/test_api.py` — dict-based spawn/persist tests
- `tests/test_writer.py` — dict round-trip
- `tests/test_reconcile.py` — dict orphan detection
- `tests/test_models.py` or `tests/test_artifacts.py` — new FindingDisposition model test, `_CANONICAL_SESSION_FIELDS` assertion

### Canonical schema references (in spec-driver repo at `~/dev/spec-driver`)

- Enum source: `supekku/scripts/lib/workflow/review_state_machine.py`
- Schema definitions: `supekku/scripts/lib/blocks/workflow_metadata.py` (§3.3 review-index, §3.4 review-findings, §3.5 sessions)
- Validator: `supekku/scripts/lib/blocks/metadata/validator.py` — confirmed: does NOT reject unknown fields
- Review I/O: `supekku/scripts/lib/workflow/review_io.py` (build_findings, build_round_entry)

### Relevant memories

- `project_pytest_invocation.md` — use `uv run python -m pytest`, not `uv run pytest` (nix devshell shadow)
- `project_track_specdriver_conventions.md` — hatch, >=3.12, ruff, 2-space indent

### Relevant doctrine

- Commit policy: frequent small commits of `.spec-driver/**`, conventional messages (`feat(DE-003): ...`)
- Ceremony mode: `town_planner`
- ADR-001: spec-driver is schema authority; autobahn conforms; extension points explicit

### Key design decisions (DR-003)

- **DEC-030**: Sessions.yaml conforms to role-keyed dict. autobahn adds extra fields spec-driver tolerates. Last-writer-wins (warn on active overwrite).
- **DEC-031**: `session_name` ← `SessionHandle.session_id`. Role is dict key.
- **DEC-032**: Read-surface limited to fix breakage + DE-004 needs. Deferred: domain_map, invariants, risk_areas, review_focus, known_decisions, handoff verification/git.
- **DEC-033**: `FindingDisposition.authority` is `DispositionAuthority` enum, **required**. Constructor-level breaking change.

### Adversarial review findings to implement

DR-003 Appendix A documents all findings. Key ones to not miss during implementation:

1. **F-1**: `_persist_new_session` must warn if overwriting active session entry
2. **F-4**: Fixture must include finding with populated disposition; add model test for FindingDisposition with required authority
3. **F-8**: `DriftItem.session_id` naming kept as-is; add comment explaining chain
4. **F-9**: Hoist `handle_ids` above orphan detection loop (fixes existing bug)
5. **F-2**: Add contract test `_CANONICAL_SESSION_FIELDS ⊆ SessionEntry.model_fields`
6. **F-3**: Add comment about `exclude_none` future footgun

### Incomplete work / loose ends

- **DE-001 carry-forwards** still open: RE-001 brief.md update, spec-driver symlink cleanup, `.claude/settings.local.json` in git
- **DE-105** (spec-driver bug): `create phase` appends duplicate entry to IP phases list — manually fixed in IP-003
- **DE-004** scoped (`DE-004.md`) but DR-004 not drafted — depends on DE-003 models

### Commit-state guidance

- All `.spec-driver/**` changes committed and clean
- No code changes pending
- Worktree clean except `.claude/settings.local.json` (pre-existing, not ours)

### Advice for next agent

- Tasks 1.1 (enums), 1.2 (sessions model), and 1.4 (review/finding models) are parallelisable — but in practice do 1.1 first (quick win, unblocks contract tests).
- Sessions restructure (1.2) is the biggest change — affects writer, API, reconcile, fixtures. Do 1.2→1.3→1.5 as a block.
- Review/finding model updates (1.4) are straightforward field additions — can be done independently until fixture update (1.6) ties everything together.
- The `BootstrapStatus` reorder is subtle: canonical order is `COLD, WARM, STALE, REUSABLE, INVALID` (not autobahn's current `COLD, WARMING, WARM, STALE, INVALID, REUSABLE`).
- `exclude_none=True` on the writer needs the `_serialize_session_entry` helper to re-inject canonical nulls. See DR-003 §4.3.
- Current test count: 111. Expect it to stay roughly the same (updating tests, not adding many new ones) plus a few new model/contract tests.
