# Notes for DE-001

## Status

- DE-001 in-progress
- Phase 01 complete — project scaffold (commit `5eb1c05`)
- Phase 02 complete — models + artifact layer (50 tests)
- Phase 03 not yet started (sheet needs creation)

## Phase 02 — Models and artifact layer (complete)

### What's done

- `autobahn/models/enums.py` — 12 StrEnum classes transcribed from spec-driver workflow_metadata.py
- `autobahn/models/artifacts.py` — 5 pydantic file models (WorkflowStateFile, HandoffFile, ReviewIndexFile, ReviewFindingsFile, SessionsFile) with shared sub-models
- `autobahn/models/runtime.py` — 8 runtime models (WorkflowContext, TransitionPlan, LaunchSpec, SessionHandle, SessionMetadata, SessionOutcome, RuntimePolicy, OperationResult)
- `autobahn/models/errors.py` — AutobahnError + 8 subclasses
- `autobahn/artifacts/loader.py` — `load_workflow_dir()` reads workflow dir into WorkflowContext
- `tests/fixtures/workflow/` — 5 hand-maintained YAML fixtures (state, handoff, review-index, review-findings, sessions)
- `tests/test_enums.py` — 12 contract tests
- `tests/test_artifacts.py` — 13 model parsing tests
- `tests/test_models.py` — 18 runtime model + error taxonomy tests
- `tests/test_loader.py` — 6 loader tests (happy path, missing files, malformed YAML)

### Surprises / adaptations

- UP046/UP047 suppressed — pydantic Generic doesn't work with PEP 695 type params
- ruff auto-fixed 8 issues (unused imports, formatting)
- `review-findings.yaml` is at schema version 2, not 1

### Verification

`just check` passes — 50 tests, lint+format clean.

## New Agent Instructions

### Task card

Delta: `DE-001` — Repository bootstrap and architecture foundation

### What to do next

Create Phase 03 sheet then execute. Phase 03 is adapter protocols: harness + session backend protocols with concrete implementations (Claude Code adapter + subprocess backend).

### Required reading

1. `DR-001.md` §7 — adapter protocols (HarnessAdapter, SessionBackend, extensions)
2. `IP-001.md` §4 — Phase 03 row
3. `DR-001.md` §5 — module boundaries and coupling rules for adapters/

### Key decisions for Phase 03

- DEC-005: Thin baseline protocol + optional typed extensions; pi-mono first-class
- DEC-006: 4-op async session backend (spawn/observe/terminate only in v1)
- DEC-007: Adapters injected by caller, not from registry
- DEC-016: Adapters expose is_available() probe for preflight

### Package structure so far

```
autobahn/
  __init__.py
  models/
    __init__.py
    enums.py         # 12 StrEnum classes
    artifacts.py     # 5 file models + sub-models
    runtime.py       # 8 runtime models
    errors.py        # error taxonomy
  artifacts/
    __init__.py
    loader.py        # load_workflow_dir()
tests/
  fixtures/workflow/  # 5 YAML fixtures
  test_enums.py       # 12 contract tests
  test_artifacts.py   # 13 model tests
  test_models.py      # 18 runtime model tests
  test_loader.py      # 6 loader tests
  test_smoke.py       # 1 smoke test
```
