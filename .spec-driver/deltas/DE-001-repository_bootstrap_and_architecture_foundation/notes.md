# Notes for DE-001

## Status

- DE-001 in-progress
- Phase 01 complete — all exit criteria verified
- Phase 02 not yet started (sheet needs creation per IP process)

## Phase 01 — Project scaffold (complete)

### What's done

- `pyproject.toml`: hatch build system enabled, `packages = ["autobahn"]`, pydantic+pyyaml deps added, supekku refs removed, broken ruff config prefixes fixed, keywords/URLs corrected
- Package skeleton: `autobahn/__init__.py` (`__version__ = "0.0.1"`), `tests/conftest.py`, `tests/fixtures/.gitkeep`
- Justfile: `check`, `lint`, `format`, `test`, `format-check` recipes
- Smoke test: `tests/test_smoke.py` — version assertion
- `README.md`: minimal (hatchling requires it when `readme` field is set)
- `.gitignore`: extended with `__pycache__/`, `*.pyc`, `.pytest_cache/`, `dist/`, `.venv/`, `.direnv/`, `.uv-cache/`

### Surprises / adaptations

- `[lint.pydocstyle]` and `[lint.per-file-ignores]` had wrong TOML table paths (missing `tool.ruff` prefix) — ruff silently ignored them
- Hatchling fails hard if README.md doesn't exist when `readme = "README.md"` is in pyproject.toml
- `pytest` exit code 5 (no tests collected) makes `just check` fail — added smoke test rather than suppressing

### Verification

`just check` passes — format, lint, test all green.

### Commits

Uncommitted — all changes pending commit.

### Loose ends (carried from prior agent)

- **RE-001 actions**: brief.md sections need updating per RE-001 §5 — not blocking
- **spec-driver symlink**: still at repo root — consider cleanup
- **`.claude/settings.local.json`**: committed — verify intentional
- **`DR-001-design-conversation.txt`**: committed — consider gitignoring

## New Agent Instructions

### Task card

Delta: `DE-001` — Repository bootstrap and architecture foundation

### What to do next

Create Phase 02 sheet (`phases/phase-02.md`) per IP-001 §4 then execute it. Phase 02 is models + artifacts: typed pydantic models and artifact loader with contract test fixtures.

### Required reading

1. `DE-001.md` — delta scope
2. `DR-001.md` — design revision (primary authority for model shapes, decisions DEC-001 through DEC-019)
3. `IP-001.md` — implementation plan
4. Phase 02 row in IP-001 §4 — entrance: P01 complete, exit: models validate against fixtures

### Key files

- `pyproject.toml` — clean, hatch functional
- `autobahn/__init__.py` — package root
- `tests/conftest.py` — empty, ready for fixtures
- `tests/fixtures/` — empty dir for YAML contract fixtures
- `Justfile` — `just check` is the verification command

### Relevant memories

- `project_de107_pydantic.md` — DE-107 is internal migration, convergence via DE-110 fixtures
- `project_track_specdriver_conventions.md` — hatch, >=3.12, ruff, 2-space indent
- `project_pi_mono_preferred_harness.md` — pi-mono first-class via extension protocols

### Key decisions for Phase 02

- DEC-001: Narrow pydantic models — stable field subset, `extra="ignore"`
- DEC-010: Structured references not prompts
- DEC-017: Reconciliation re-reads state.yaml
