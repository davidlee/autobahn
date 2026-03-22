# Notes for DE-004

## 2026-03-23: Implementation

### Phase 1: Enum retirement & cleanup
- Replaced 5 review enum definitions in `models/enums.py` with re-export aliases from `spec_driver.orchestration`
- Removed `ToolInvocationError` and `ToolContractError` from `models/errors.py`
- Updated `test_enums.py`: replaced value-comparison contract tests with `is`-identity alias tests
- Updated `test_models.py`: removed references to deleted error types
- 114 tests passing, lint clean

### Phase 2: Review API functions
- Implemented 3 thin wrappers in `api/functions.py`: `prime_review`, `summarize_review_outcome`, `disposition_finding`
- Each delegates directly to `spec_driver.orchestration` operation — no result wrapping, no exception mapping
- 7 new tests covering delegation, return passthrough, exception propagation, default authority
- 121 tests passing, lint clean

### Module name: `spec_driver.orchestration` (not `.workflow`)
DE-124 delivered the public API as `spec_driver.orchestration`, not `spec_driver.workflow` as DR-004 originally assumed. Updated all references.

## 2026-03-23: Design session

### Key architectural pivot

Original DE-004 scope (tool adapter, CLI subprocess, JSON envelope parsing) was
replaced by direct Python imports after recognizing:

1. spec-driver is already an editable workspace member — no process boundary
2. CLI is a presentation layer for agents/humans; orchestrators need typed Python calls
3. Subprocess invocation adds complexity (spawn, JSON parsing, exit codes) for zero benefit

This led to ADR-002 (Python public API boundary) and re-scoping DE-004.

### Cross-review with DR-124

DR-004 and DR-124 (spec-driver public API facade) were cross-reviewed. Key reconciliations:

- **F2/F6**: DR-004 originally requested building blocks (read_findings, write_findings, etc.)
  that DR-124 deliberately does not export. Resolved by adding `summarize_review` as a
  composed query operation in spec-driver.

- **F3**: Disposition validation rules (rationale for waive, backlog_ref for defer) are
  spec-driver domain logic, not autobahn orchestration policy. Moved to spec-driver.

- **F5**: `ReviewBootstrapState` in autobahn was field-identical to `PrimeResult` in
  spec-driver. Eliminated — use spec-driver's type directly.

- **F7/F8**: DR-124 result types used `str` where enums exist, and `disposition: dict`
  where typed kwargs are appropriate. Flagged for spec-driver to fix.

### Design decisions summary

The wrappers are now genuinely thin — resolve delta_id to path, call spec-driver
operation, return result. No result wrapping, no exception translation, no
validation reimplementation.

### Blocking dependency

spec-driver DE-124 must land before DE-004 implementation. Specifically needs:
- `summarize_review` operation (not in original DR-124 scope — added from cross-review)
- Typed enums in result dataclasses (not `str`)
- Typed kwargs on `disposition_finding` (not `dict`)
- Optionally: `resolve_delta_dir` in public surface
