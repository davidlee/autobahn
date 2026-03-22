---
id: IP-004-P02
slug: "004-review_operations-phase-02"
name: "Review API functions"
created: "2026-03-23"
updated: "2026-03-23"
status: draft
kind: phase
plan: IP-004
delta: DE-004
---

# Phase 2 — Review API functions

## 1. Objective

Implement `prime_review`, `summarize_review_outcome`, and `disposition_finding` as thin wrappers around `spec_driver.orchestration` composed operations. Export from autobahn's public API. Write tests.

## 2. Links & References

- **Delta**: DE-004
- **Design Revision**: DR-004 §4.5–§4.6
- **Decisions**: DEC-004-001 through DEC-004-014
- **spec-driver**: DR-124 §4.1 (operations), §5.3 (exports)

## 3. Entrance Criteria

- [ ] Phase 1 complete (enum retirement, all existing tests passing)
- [ ] `spec_driver.orchestration.prime_review`, `summarize_review`, `disposition_finding` importable

## 4. Exit Criteria / Done When

- [ ] `prime_review(delta_dir, repo_root) → PrimeResult` implemented and exported
- [ ] `summarize_review_outcome(delta_dir) → ReviewSummary` implemented and exported
- [ ] `disposition_finding(delta_dir, finding_id, *, action, ...) → DispositionResult` implemented and exported
- [ ] `api/__init__.py` exports all three
- [ ] Tests cover: delegation, return passthrough, exception propagation
- [ ] `uv run python -m pytest` all pass (existing + new)
- [ ] `uv run ruff check autobahn tests` clean
- [ ] `uv run ruff format --check autobahn tests` clean

## 5. Verification

- `uv run python -m pytest tests/test_api.py -v` — new review tests pass
- `uv run python -m pytest` — full suite passes
- `uv run ruff check autobahn tests && uv run ruff format --check autobahn tests`
- Manual: `from autobahn.api import prime_review, summarize_review_outcome, disposition_finding`

## 6. Assumptions & STOP Conditions

- **Assumption**: spec-driver's composed operations have the signatures described in DR-124 (with typed kwargs and enum results per cross-review reconciliation)
- **STOP when**: spec-driver operation signatures don't match DR-124 updated spec (indicates DR-124 cross-review findings not yet integrated)
- **STOP when**: substantive design questions emerge about orchestrator-vs-agent responsibility boundary

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 2.1 | Verify spec-driver operation signatures | | Gate check |
| [ ] | 2.2 | Write tests for `prime_review` (TDD red) | | |
| [ ] | 2.3 | Implement `prime_review` | | |
| [ ] | 2.4 | Write tests for `summarize_review_outcome` (TDD red) | | |
| [ ] | 2.5 | Implement `summarize_review_outcome` | | |
| [ ] | 2.6 | Write tests for `disposition_finding` (TDD red) | | |
| [ ] | 2.7 | Implement `disposition_finding` | | |
| [ ] | 2.8 | Update `api/__init__.py` exports | | |
| [ ] | 2.9 | Update `test_coupling.py` | | Import boundary check |
| [ ] | 2.10 | Full suite + lint | | Exit gate |

### Task Details

- **2.1 Verify spec-driver operation signatures**
  - **Approach**: Inspect `spec_driver.orchestration` imports, confirm:
    - `prime_review(delta_dir: Path, repo_root: Path) → PrimeResult`
    - `summarize_review(delta_dir: Path) → ReviewSummary`
    - `disposition_finding(delta_dir: Path, finding_id: str, *, action: FindingDispositionAction, authority: DispositionAuthority, ...) → DispositionResult`
  - **STOP** if signatures don't match — coordinate with spec-driver.

- **2.2–2.3 `prime_review`**
  - **Files**: `autobahn/api/functions.py`, `tests/test_api.py`
  - **Test approach**: Mock `spec_driver.orchestration.prime_review`, verify:
    - Called with correct `(delta_dir, repo_root)` args
    - Return value passed through as-is
    - spec-driver exceptions propagate (mock raising `StateNotFoundError` → caller sees it)
  - **Implementation**: ~5 lines per DR-004 §4.5

- **2.4–2.5 `summarize_review_outcome`**
  - **Files**: `autobahn/api/functions.py`, `tests/test_api.py`
  - **Test approach**: Mock `spec_driver.orchestration.summarize_review`, verify delegation + exception propagation (`FindingsNotFoundError`, `FindingsVersionError`)
  - **Implementation**: ~3 lines

- **2.6–2.7 `disposition_finding`**
  - **Files**: `autobahn/api/functions.py`, `tests/test_api.py`
  - **Test approach**: Mock `spec_driver.orchestration.disposition_finding`, verify:
    - All keyword args forwarded correctly
    - `FindingNotFoundError` propagates
    - Default `authority=DispositionAuthority.AGENT` applied
  - **Implementation**: ~10 lines

- **2.8 Update `api/__init__.py`**
  - Add `prime_review`, `summarize_review_outcome`, `disposition_finding` to imports and `__all__`

- **2.9 Update `test_coupling.py`**
  - Verify `spec_driver.orchestration` is in the allowed import set for `autobahn.api.functions`

- **2.10 Full suite + lint**
  - `uv run python -m pytest` — all pass
  - `uv run ruff check autobahn tests`
  - `uv run ruff format --check autobahn tests`

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|-----------|--------|
| spec-driver operation signatures changed since DR-124 | Task 2.1 gate check catches early | open |
| Mocking spec-driver operations in tests may be fragile | Mock at import boundary, not internals; verify call args only | expected ok |

## 9. Decisions & Outcomes

_(Populated during execution)_

## 10. Findings / Research Notes

_(Populated during execution)_

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated
- [ ] ADR-002 status updated (draft → accepted if appropriate)
- [ ] Delta closure readiness assessed
