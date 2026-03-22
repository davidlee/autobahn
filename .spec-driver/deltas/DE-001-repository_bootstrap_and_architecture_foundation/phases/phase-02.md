---
id: IP-001.PHASE-02
slug: "002-models-and-artifact-layer"
name: "IP-001 Phase 02 — Models and artifact layer"
created: "2026-03-22"
updated: "2026-03-22"
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-001.PHASE-02
plan: IP-001
delta: DE-001
objective: >-
  Typed pydantic models (enums, artifact file models, runtime models, error
  taxonomy) and an artifact loader that reads spec-driver workflow YAML files.
  Validated by contract tests against hand-maintained fixtures.
entrance_criteria:
  - Phase 01 complete (hatch build, ruff, pytest functional)
exit_criteria:
  - All enums from DR-001 §6 implemented with contract test coverage
  - Artifact file models (state, handoff, review-index, review-findings, sessions) parse fixtures
  - Runtime models (WorkflowContext, TransitionPlan, LaunchSpec, SessionHandle, SessionMetadata, SessionOutcome, RuntimePolicy, OperationResult) defined
  - Error taxonomy defined (AutobahnError hierarchy)
  - Artifact loader reads workflow directory into WorkflowContext
  - Contract tests pass against hand-maintained YAML fixtures (VA-001)
  - Artifact loader tests pass (VA-002)
  - ruff check + ruff format --check pass
  - just check passes
verification:
  tests:
    - VA-001 contract tests (enum values, model parsing against fixtures)
    - VA-002 artifact loader tests (read workflow dir, missing files, malformed YAML)
  evidence:
    - "just check passes"
    - "Contract tests validate all enum values match spec-driver source"
    - "Artifact models parse all fixture files without error"
tasks:
  - id: "2.1"
    description: "Create YAML contract test fixtures"
  - id: "2.2"
    description: "Implement enums"
  - id: "2.3"
    description: "Implement artifact file models"
  - id: "2.4"
    description: "Implement runtime models and error taxonomy"
  - id: "2.5"
    description: "Implement artifact loader"
  - id: "2.6"
    description: "Verify all tests pass"
risks:
  - description: "Hand-maintained fixtures may not match current spec-driver schemas"
    mitigation: "Fixtures note source commit; contract tests catch drift"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-001.PHASE-02
```

# Phase 02 — Models and artifact layer

## 1. Objective

Typed pydantic models and artifact loader. After this phase, autobahn has a complete model layer (enums, artifact file models, runtime models, errors) and can load a spec-driver workflow directory into a `WorkflowContext`.

## 2. Links & References

- **Delta**: DE-001
- **Design Revision Sections**: DR-001 §6 (core models), §5 (module boundaries/coupling)
- **Design Decisions**: DEC-001 (narrow models, `extra="ignore"`), DEC-015 (stable field subset), DEC-019 (enums are cited transcriptions)

## 3. Entrance Criteria

- [x] Phase 01 complete

## 4. Exit Criteria / Done When

- [ ] Enums match DR-001 §6 values (core + review-related)
- [ ] Artifact file models parse YAML fixtures: state, handoff, review-index, review-findings, sessions
- [ ] Runtime models defined: WorkflowContext, TransitionPlan, LaunchSpec, SessionHandle, SessionMetadata, SessionOutcome, RuntimePolicy, OperationResult
- [ ] Error taxonomy: AutobahnError hierarchy per DR-001 §6
- [ ] Artifact loader: `load_workflow_dir(path) -> WorkflowContext`
- [ ] Contract tests (VA-001): enum values, model parsing
- [ ] Artifact loader tests (VA-002): happy path, missing optional files, malformed YAML
- [ ] `just check` passes

## 5. Verification

- `just check` (lint + format + test)
- Contract tests validate enum values against spec-driver source comments
- Artifact models parse all fixture files without error
- Loader handles missing optional files (handoff, review-index, review-findings, sessions)

## 6. Assumptions & STOP Conditions

- Assumptions: spec-driver workflow YAML schemas are stable at v1; fixture files derived from spec-driver as of 2026-03-22
- STOP when: spec-driver schema changes mid-implementation (check DE-109 status)

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 2.1 | Create YAML contract test fixtures | - | Hand-maintained, note source commit |
| [ ] | 2.2 | Implement enums | [P] | Can parallel with 2.1 |
| [ ] | 2.3 | Implement artifact file models | - | Depends on 2.1 (fixtures) + 2.2 (enums) |
| [ ] | 2.4 | Implement runtime models + error taxonomy | [P] | Can parallel with 2.3 |
| [ ] | 2.5 | Implement artifact loader | - | Depends on 2.3 |
| [ ] | 2.6 | Verify all tests pass | - | Depends on all above |

### Task Details

- **2.1 Create YAML contract test fixtures**
  - **Approach**: Hand-maintain fixture files in `tests/fixtures/workflow/` representing a typical spec-driver workflow directory: `state.yaml`, `handoff.current.yaml`, `review-index.yaml`, `review-findings.yaml`, `sessions.yaml`. Each file carries a comment noting the spec-driver commit it was derived from.
  - **Files**: `tests/fixtures/workflow/*.yaml`

- **2.2 Implement enums**
  - **Approach**: `autobahn/models/enums.py` — transcribe all enums from DR-001 §6 (Role, WorkflowStatus, PhaseStatus, ArtifactKind, SessionStatus, NextActivityKind, HandoffTransitionStatus, BootstrapStatus, ReviewStatus, FindingDispositionAction, DispositionAuthority, FindingStatus). Use `StrEnum`. Include source line citations as comments.
  - **Files**: `autobahn/models/enums.py`, `autobahn/models/__init__.py`
  - **Testing**: Contract tests asserting enum member names/values match spec-driver source

- **2.3 Implement artifact file models**
  - **Approach**: `autobahn/models/artifacts.py` — pydantic models per DR-001 §6: WorkflowStateFile, HandoffFile, ReviewIndexFile, ReviewFindingsFile, SessionsFile. All use `model_config = ConfigDict(extra="ignore")` per DEC-001/DEC-015. Only fields autobahn consumes (per DR-001 consumed-fields table).
  - **Files**: `autobahn/models/artifacts.py`
  - **Testing**: Parse each fixture file, assert key fields present and typed correctly

- **2.4 Implement runtime models + error taxonomy**
  - **Approach**: `autobahn/models/runtime.py` — WorkflowContext, TransitionPlan, LaunchSpec, SessionHandle, SessionMetadata, SessionOutcome, RuntimePolicy, OperationResult. `autobahn/models/errors.py` — exception hierarchy per DR-001 §6.
  - **Files**: `autobahn/models/runtime.py`, `autobahn/models/errors.py`
  - **Testing**: Construction tests, OperationResult generic usage

- **2.5 Implement artifact loader**
  - **Approach**: `autobahn/artifacts/loader.py` — `load_workflow_dir(path) -> WorkflowContext`. Reads YAML files, parses via artifact models, assembles WorkflowContext. state.yaml is required; others are optional. Raises ArtifactParseError/ArtifactContractError on failure.
  - **Files**: `autobahn/artifacts/__init__.py`, `autobahn/artifacts/loader.py`
  - **Testing**: Happy path, missing optional files, malformed YAML, missing required state.yaml

- **2.6 Verify all tests pass**
  - **Approach**: Run `just check`, fix any issues

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| Fixtures drift from spec-driver schemas | Note source commit; DE-110 will replace with generated exports | open |
| DE-109 changes enum values before completion | Enum values cite source lines; contract tests catch drift | open |

## 9. Decisions & Outcomes

_(filled during execution)_

## 10. Findings / Research Notes

_(filled during execution)_

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes to Phase 03
