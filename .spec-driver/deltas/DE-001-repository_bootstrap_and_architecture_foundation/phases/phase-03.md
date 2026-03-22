---
id: IP-001.PHASE-03
slug: "003-adapter-protocols"
name: "IP-001 Phase 03 — Adapter protocols"
created: "2026-03-22"
updated: "2026-03-22"
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-001.PHASE-03
plan: IP-001
delta: DE-001
objective: >-
  Define HarnessAdapter and SessionBackend protocols. Implement one concrete
  harness adapter (Claude Code) and one session backend (subprocess). Extension
  protocol seams for richer harnesses (pi-mono).
entrance_criteria:
  - Phase 02 complete (models + artifacts)
exit_criteria:
  - HarnessAdapter protocol defined with name, is_available, launch_spec, parse_exit
  - SessionBackend protocol defined with is_available, create, is_alive, terminate, get_metadata
  - Extension protocol seams defined (ContextEngineerable, SubAgentConfigurable)
  - Claude Code harness adapter passes unit tests
  - Subprocess session backend passes unit tests
  - Adapters depend only on models/ (coupling rule)
  - just check passes
verification:
  tests:
    - Claude Code adapter unit tests
    - Subprocess backend async unit tests
    - Import coupling test
  evidence:
    - "just check passes"
tasks:
  - id: "3.1"
    description: "Define adapter protocols"
  - id: "3.2"
    description: "Implement Claude Code harness adapter"
  - id: "3.3"
    description: "Implement subprocess session backend"
  - id: "3.4"
    description: "Verify all tests pass"
risks:
  - description: "Subprocess backend async testing complexity"
    mitigation: "Use asyncio subprocess with short-lived echo commands"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-001.PHASE-03
```

# Phase 03 — Adapter protocols

## 1. Objective

Define pluggable adapter protocols for harness and session backend. Implement Claude Code harness adapter and subprocess session backend as concrete implementations proving the protocol design.

## 2. Links & References

- **Delta**: DE-001
- **Design Revision Sections**: DR-001 §7 (adapter protocols, extensions, composition)
- **Design Decisions**: DEC-005 (thin baseline + extensions), DEC-006 (4-op async backend), DEC-007 (caller-injected), DEC-016 (is_available probe)

## 3. Entrance Criteria

- [x] Phase 02 complete

## 4. Exit Criteria / Done When

- [x] `HarnessAdapter` protocol in `autobahn/adapters/harness/protocol.py`
- [x] `SessionBackend` protocol in `autobahn/adapters/session/protocol.py`
- [x] Extension seams (`ContextEngineerable`, `SubAgentConfigurable`)
- [x] `ClaudeCodeAdapter` in `autobahn/adapters/harness/claude_code.py`
- [x] `SubprocessBackend` in `autobahn/adapters/session/subprocess_backend.py`
- [x] Unit tests for both concrete adapters (10 + 11 = 21 tests)
- [x] Import coupling: 5 coupling tests pass (adapters import only models/)
- [x] `just check` passes — 76 tests total

## 5. Verification

- `just check` (lint + format + test)
- Claude Code adapter: launch_spec produces correct command, parse_exit interprets codes, is_available checks PATH
- Subprocess backend: create spawns process, is_alive detects liveness, terminate kills, get_metadata returns state

## 6. Assumptions & STOP Conditions

- Assumptions: subprocess backend uses `asyncio.create_subprocess_exec`; no tmux in this phase
- STOP when: async testing reveals need for event loop fixtures not in pytest-asyncio

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [x] | 3.1 | Define adapter protocols | - | HarnessAdapter, SessionBackend, 2 extension seams |
| [x] | 3.2 | Implement Claude Code harness adapter | [P] | 10 unit tests |
| [x] | 3.3 | Implement subprocess session backend | [P] | 11 async unit tests |
| [x] | 3.4 | Verify all tests pass | - | 76 total, lint+format clean |

### Task Details

- **3.1 Define adapter protocols**
  - **Approach**: Protocol classes per DR-001 §7. HarnessAdapter (name, is_available, launch_spec, parse_exit). SessionBackend (is_available, create, is_alive, terminate, get_metadata). Extension seams as separate Protocol classes.
  - **Files**: `autobahn/adapters/harness/protocol.py`, `autobahn/adapters/session/protocol.py`

- **3.2 Implement Claude Code harness adapter**
  - **Approach**: `launch_spec` builds `claude -p "..."` from TransitionPlan. `parse_exit` interprets exit codes. `is_available` checks executable on PATH (or policy.harness_executable).
  - **Files**: `autobahn/adapters/harness/claude_code.py`

- **3.3 Implement subprocess session backend**
  - **Approach**: Async subprocess via `asyncio.create_subprocess_exec`. create spawns, is_alive checks returncode, terminate sends SIGTERM, get_metadata returns process state.
  - **Files**: `autobahn/adapters/session/subprocess_backend.py`

- **3.4 Verify all tests pass**
  - **Approach**: `just check`

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| Subprocess async test flakiness | Use deterministic short commands | open |

## 9. Decisions & Outcomes

- `uv run pytest` resolves to nix-provided pytest which lacks project deps. Fixed Justfile to use `uv run python -m pytest` which correctly uses the venv Python.
- All Protocol classes use `@runtime_checkable` for isinstance() checks per DR-001 §7
- SubprocessBackend stores processes in-memory dict — adequate for v1 single-orchestrator (DEC-011)

## 10. Findings / Research Notes

- nix devshell provides a system pytest that shadows the venv's — `python -m pytest` is the reliable invocation pattern
- ruff auto-fixed inline imports to top-level in test files (PLC0415)

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (76 tests, just check green)
- [ ] Hand-off notes to Phase 04
