---
id: IP-001.PHASE-01
slug: "001-project-scaffold"
name: "IP-001 Phase 01 — Project scaffold"
created: "2026-03-22"
updated: "2026-03-22"
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-001.PHASE-01
plan: IP-001
delta: DE-001
objective: >-
  Establish a functional Python package with hatch build system, linting,
  test infrastructure, and empty package skeleton matching spec-driver
  conventions. After this phase, `uv run pytest` and `ruff check` pass.
entrance_criteria:
  - DE-001 scoped
  - DR-001 reviewed (3 adversarial passes + DR-109 coherence)
exit_criteria:
  - hatch build system functional (uv run python -c "import autobahn")
  - ruff check passes with zero warnings
  - ruff format --check passes
  - pytest runs (zero tests is OK — infrastructure only)
  - pyproject.toml clean (no supekku references, correct metadata)
  - Justfile has basic commands (check, lint, format, test)
verification:
  tests: []
  evidence:
    - "uv run python -c 'import autobahn' succeeds"
    - "ruff check passes"
    - "uv run pytest passes (0 collected is OK)"
tasks:
  - id: "1.1"
    description: "Fix and modernise pyproject.toml"
  - id: "1.2"
    description: "Create package skeleton"
  - id: "1.3"
    description: "Configure Justfile"
  - id: "1.4"
    description: "Verify build + lint + test infrastructure"
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-001.PHASE-01
```

# Phase 01 — Project scaffold

## 1. Objective

Establish a functional Python package matching spec-driver conventions. No business logic — purely build/lint/test infrastructure.

## 2. Links & References

- **Delta**: DE-001
- **Design Revision Sections**: DR-001 §5 (module boundaries), §2 (conventions)
- **Reference**: spec-driver `pyproject.toml` for convention alignment

## 3. Entrance Criteria

- [x] DE-001 scoped
- [x] DR-001 reviewed

## 4. Exit Criteria / Done When

- [x] `uv run python -c "import autobahn"` succeeds — prints 0.0.1
- [x] `ruff check` passes with zero warnings
- [x] `ruff format --check` passes
- [x] `uv run pytest` runs successfully — 1 smoke test passes
- [x] pyproject.toml has correct metadata, hatch build system, pydantic dependency
- [x] Justfile has `check`, `lint`, `format`, `test` commands

## 5. Verification

- `uv run python -c "import autobahn"`
- `ruff check autobahn/ tests/`
- `ruff format --check autobahn/ tests/`
- `uv run pytest`

## 6. Assumptions & STOP Conditions

- Assumptions: nix flake provides Python 3.12+, uv, and ruff
- STOP when: build system issues that require flake.nix changes (escalate to user)

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [x] | 1.1 | Fix and modernise pyproject.toml | - | Hatch enabled, pydantic+pyyaml deps, supekku refs removed |
| [x] | 1.2 | Create package skeleton | - | `autobahn/__init__.py`, `tests/conftest.py`, `tests/fixtures/`, smoke test |
| [x] | 1.3 | Configure Justfile | [P] | check, lint, format, test, format-check |
| [x] | 1.4 | Verify infrastructure | - | All exit criteria pass |

### Task Details

- **1.1 Fix and modernise pyproject.toml**
  - **Approach**: Enable hatch build system (uncomment + fix), set `packages = ["autobahn"]`, add `pydantic>=2.0` and `pyyaml>=6.0` to dependencies. Remove supekku references from ruff/pylint per-file-ignores. Fix Homepage URL. Update keywords/classifiers.
  - **Files**: `pyproject.toml`

- **1.2 Create package skeleton**
  - **Approach**: Create `autobahn/__init__.py` (empty, just `__version__`), `tests/conftest.py`, `tests/fixtures/` dir. Add `tests/` to pytest testpaths.
  - **Files**: `autobahn/__init__.py`, `tests/conftest.py`

- **1.3 Configure Justfile**
  - **Approach**: Add recipes matching spec-driver's workflow: `just check` (lint + test), `just lint`, `just format`, `just test`
  - **Files**: `Justfile`

- **1.4 Verify infrastructure**
  - **Approach**: Run all exit criteria commands. Fix any issues.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| flake.nix may not expose hatchling | Check nix environment provides build deps | open |

## 9. Decisions & Outcomes

- Added README.md (minimal) — hatchling requires it when `readme = "README.md"` is set
- Added smoke test (`tests/test_smoke.py`) — pytest exit code 5 (no tests) causes `just check` to fail; a version assertion test is honest and useful
- Removed `watchfiles` from deps — not needed for library-first scope
- Added `format-check` recipe to Justfile — useful for CI (non-mutating check)

## 10. Findings / Research Notes

- `[lint.pydocstyle]` and `[lint.per-file-ignores]` in the original pyproject.toml were missing the `tool.ruff` prefix — ruff silently ignores them. Fixed.
- Duplicate `RET` in extend-select — harmless but messy, removed.
- `pyproject.toml` had supekku per-file-ignores for paths that don't exist in autobahn — removed.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (inline above)
- [ ] Hand-off notes to Phase 02
