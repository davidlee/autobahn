---
id: IP-004-P01
slug: "004-review_operations-phase-01"
name: "Enum retirement and cleanup"
created: "2026-03-23"
updated: "2026-03-23"
status: draft
kind: phase
plan: IP-004
delta: DE-004
---

# Phase 1 — Enum retirement and cleanup

## 1. Objective

Replace autobahn's review-related enum definitions with re-export aliases from `spec_driver.workflow`. Update artifact model imports. Remove dead error types. Verify all existing tests pass with zero behaviour change.

## 2. Links & References

- **Delta**: DE-004
- **Design Revision**: DR-004 §4.1–§4.3
- **Decisions**: DEC-004-005 (enum aliasing), DEC-004-009 (no duplicates), DEC-004-012 (dead code removal)
- **ADR**: ADR-002 (Python API boundary)

## 3. Entrance Criteria

- [x] DR-004 approved (3 review rounds complete)
- [ ] spec-driver DE-124 landed — `from spec_driver.workflow import BootstrapStatus` works
- [ ] `uv sync` succeeds with updated spec-driver

## 4. Exit Criteria / Done When

- [ ] Review enums removed from `autobahn/models/enums.py`, replaced with re-export aliases
- [ ] `autobahn/models/artifacts.py` imports review types from `spec_driver.workflow`
- [ ] `ToolInvocationError` and `ToolContractError` removed from `autobahn/models/errors.py`
- [ ] All 116 existing tests pass (zero failures, zero changes to test logic)
- [ ] `uv run ruff check autobahn tests` clean
- [ ] `uv run ruff format --check autobahn tests` clean
- [ ] Re-export alias smoke: `from autobahn.models.enums import BootstrapStatus` resolves and `is` `spec_driver.workflow.BootstrapStatus`

## 5. Verification

- `uv run python -m pytest` — all 116 existing tests pass
- `uv run ruff check autobahn tests` — zero warnings
- `uv run ruff format --check autobahn tests` — no changes needed
- Manual check: `uv run python -c "from autobahn.models.enums import BootstrapStatus; from spec_driver.workflow import BootstrapStatus as SD; assert BootstrapStatus is SD"`

## 6. Assumptions & STOP Conditions

- **Assumption**: spec-driver DE-124 exports all review-related enums and types listed in DR-124 §5.3
- **Assumption**: spec-driver's review types are structurally compatible (same field names, same `extra="ignore"`)
- **STOP when**: `from spec_driver.workflow import BootstrapStatus` fails (DE-124 not landed or incomplete)
- **STOP when**: existing test failures that aren't explained by the enum/import changes

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 1.1 | Verify DE-124 availability | | Gate check |
| [ ] | 1.2 | Retire review enums in `models/enums.py` | | DEC-004-005 |
| [ ] | 1.3 | Update `models/artifacts.py` imports | [P] | Can parallel with 1.4 |
| [ ] | 1.4 | Remove dead error types from `models/errors.py` | [P] | DEC-004-012 |
| [ ] | 1.5 | Update `test_enums.py` | | Remove contract tests, add alias verification |
| [ ] | 1.6 | Run full test suite + lint | | Exit gate |

### Task Details

- **1.1 Verify DE-124 availability**
  - **Approach**: `uv sync && uv run python -c "from spec_driver.workflow import BootstrapStatus, ReviewStatus, FindingDispositionAction, DispositionAuthority, FindingStatus, FindingDisposition, ReviewFinding"`
  - **STOP** if this fails — DE-124 is the blocking prerequisite.

- **1.2 Retire review enums in `models/enums.py`**
  - **Files**: `autobahn/models/enums.py`
  - **Approach**: Remove class definitions for `BootstrapStatus`, `ReviewStatus`, `FindingDispositionAction`, `DispositionAuthority`, `FindingStatus`. Replace with:
    ```python
    from spec_driver.workflow import (
      BootstrapStatus,
      ReviewStatus,
      FindingDispositionAction,
      DispositionAuthority,
      FindingStatus,
    )
    ```
  - **Testing**: Existing imports from `autobahn.models.enums` continue to resolve via re-export.

- **1.3 Update `models/artifacts.py` imports**
  - **Files**: `autobahn/models/artifacts.py`
  - **Approach**: Change review-related type imports to use `spec_driver.workflow` as canonical source. Specifically: `BootstrapStatus`, `ReviewStatus`, `FindingStatus`, `FindingDispositionAction`, `DispositionAuthority` in `ReviewBlock`, `FindingDisposition`, `Finding`, `ReviewRound` models.
  - **Testing**: `test_artifacts.py` YAML loading unchanged.

- **1.4 Remove dead error types from `models/errors.py`**
  - **Files**: `autobahn/models/errors.py`
  - **Approach**: Delete `ToolInvocationError` and `ToolContractError` class definitions. Grep codebase to confirm zero usage.
  - **Testing**: No tests reference these types.

- **1.5 Update `test_enums.py`**
  - **Files**: `tests/test_enums.py`
  - **Approach**: Remove contract tests that validated review enum values against spec-driver source strings (these were the transcription verification tests from DEC-019). Add alias identity tests:
    ```python
    def test_review_enums_are_spec_driver_types():
      from autobahn.models.enums import BootstrapStatus
      from spec_driver.workflow import BootstrapStatus as SD
      assert BootstrapStatus is SD
    ```
  - Repeat for all 5 retired enums.

- **1.6 Run full test suite + lint**
  - `uv run python -m pytest` — 116 tests pass
  - `uv run ruff check autobahn tests`
  - `uv run ruff format --check autobahn tests`

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|-----------|--------|
| DE-124 not landed | Phase blocked until available | open |
| Pydantic model validation differs between autobahn and spec-driver types | Both use `extra="ignore"` — structurally compatible by design (ADR-001) | expected ok |

## 9. Decisions & Outcomes

_(Populated during execution)_

## 10. Findings / Research Notes

_(Populated during execution)_

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated with lessons
- [ ] Hand-off to Phase 2
