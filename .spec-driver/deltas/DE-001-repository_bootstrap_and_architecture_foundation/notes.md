# Notes for DE-001

## Status

- DE-001 scoped, DR-001 drafted and reviewed (3 external adversarial passes + DR-109 coherence review)
- RE-001 filed for brief sandbox revision
- IP-001 created with 5 phases
- Phase 01 sheet populated, ready for execution
- No implementation code written yet

## New Agent Instructions

### Task card

Delta: `DE-001` — Repository bootstrap and architecture foundation

### Required reading (in order)

1. `.spec-driver/deltas/DE-001-repository_bootstrap_and_architecture_foundation/DE-001.md` — delta scope
2. `.spec-driver/deltas/DE-001-repository_bootstrap_and_architecture_foundation/DR-001.md` — design revision (primary authority)
3. `.spec-driver/deltas/DE-001-repository_bootstrap_and_architecture_foundation/IP-001.md` — implementation plan (5 phases)
4. `.spec-driver/deltas/DE-001-repository_bootstrap_and_architecture_foundation/phases/phase-01.md` — active phase sheet

### Related documents

- `brief.md` — original architecture brief (§5.5 sandbox adapter superseded by RE-001)
- `.spec-driver/revisions/RE-001-sandbox_adapter_layer_removed_from_autobahn_scope/RE-001.md` — sandbox revision
- spec-driver `DR-109` at `../spec-driver/.spec-driver/deltas/DE-109-review_state_machine_formalisation/DR-109.md` — review state machine (3 review passes complete, substantially answers OQ-003)

### Key files

- `pyproject.toml` — needs hatch build system, pydantic dep, supekku cleanup (Phase 01 task 1.1)
- `VERSION` — `0.0.1`
- `Justfile` — empty, needs basic commands (Phase 01 task 1.3)
- `flake.nix` — nix build environment (do not modify without user approval)
- `.envrc` — `use flake`

### Relevant memories

- `project_de107_pydantic.md` — DE-107 is internal pydantic migration, not shared schema surface; convergence via DE-110 fixtures
- `project_track_specdriver_conventions.md` — hatch, >=3.12, ruff, 2-space indent, flat package layout
- `project_pi_mono_preferred_harness.md` — pi-mono first-class via extension protocols

### Relevant doctrine

- `.spec-driver/hooks/doctrine.md` — commit policy: frequent small commits of `.spec-driver/**`, conventional messages (`fix(DE-001): ...`)
- Ceremony mode: `town_planner` — delta-first flow

### Key user instructions and decisions

- **19 design decisions** in DR-001 frontmatter (DEC-001 through DEC-019). Key ones:
  - DEC-001: Narrow pydantic models (stable field subset, `extra="ignore"`)
  - DEC-003: Sandbox is not autobahn's concern (RE-001)
  - DEC-006: 4-op async session backend (spawn/observe/terminate only in v1)
  - DEC-010: Structured references not prompts — spec-driver owns prompt content
  - DEC-012: v1 API is spawn/observe/terminate only
  - DEC-013: Observation is structured logging only in v1
  - DEC-014: Review APIs internal/experimental until spec-driver contract lands
  - DEC-017: Reconciliation re-reads state.yaml to detect external workflow changes

- **User preferences**: quality > speed, DRY, small composable units, 2-space indent, TDD (red/green/refactor), obsess over coupling/cohesion

### Incomplete work / loose ends

- **RE-001 actions not completed**: brief.md sections need updating per RE-001 §5. Not blocking for implementation but should be done before DE-001 closes.
- **pyproject.toml already partially fixed**: `long_description_content_type` removed, license changed to `FSL-1.1-ALv2`. Build system still commented out.
- **Spec-driver worktree symlink**: `spec-driver` symlink exists at repo root (committed in earlier pass) — may need cleanup.
- **`.claude/settings.local.json`**: committed — verify this is intentional or gitignore it.
- **`autobahn.egg-info/`**: may exist from earlier build attempt — gitignore it.
- **`DR-001-design-conversation.txt`**: exported conversation file committed — consider gitignoring.

### Commit-state guidance

- `.spec-driver/**` changes are committed and clean
- No code changes to commit
- The `spec-driver` symlink, `DR-001-design-conversation.txt`, `.claude/settings.local.json`, and `autobahn.egg-info/` were committed and should be reviewed — some may belong in `.gitignore`

### Advice for next agent

- Phase 01 is pure infrastructure — no business logic. Keep it tight.
- The `pyproject.toml` is a mess of copy-paste from spec-driver. Task 1.1 is a cleanup pass: enable hatch, set `packages = ["autobahn"]`, add pydantic + pyyaml deps, remove all supekku references from tool config sections.
- The flake.nix already provides Python, uv, ruff. Don't modify it without asking.
- `spec-driver` is available via `uv run spec-driver` — already verified.
- After Phase 01, the next agent should create Phase 02 sheet before implementing (per IP process — one phase sheet at a time).
