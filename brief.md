Yes. Below is a repo-bootstrap brief for `autobahn` focused on **boundary APIs, responsibility split, and first-iteration architecture**.

../spec-driver/

---

# Brief: `autobahn` Repository Bootstrap and Boundary API Design

## Purpose

Create a new external Python repository, `autobahn`, that provides the runtime orchestration/supervision layer for artifact-driven agent workflows.

`autobahn` is **not** the workflow/artifact authority. That remains with `spec-driver`.

`autobahn` is **not** initially a CLI, daemon, service, or protocol server. It is a **library-first runtime substrate** with a small top-level API, designed to be called by higher-level tooling.

The repository should be designed so that:

* hard boundaries with `spec-driver` are enforced early
* orchestration concerns are kept out of `spec-driver`
* agent context remains bounded
* later addition of a CLI/daemon/service remains possible without redesigning the core

---

## Core architectural stance

### `spec-driver` owns

* workflow semantics
* workflow artifact schemas
* artifact mutation rules
* DE/IP/phase/notes authority
* structured workflow state under artifact directories
* handoff/review-state file definitions and validation
* continuation/handoff semantics

### `autobahn` owns

* process/session orchestration
* role/session lifecycle
* attach/resume/detach/pause/terminate
* harness adapters
* sandbox adapters
* runtime observation and reconciliation
* reviewer bootstrap execution logic
* session-to-artifact coordination against the `spec-driver` control plane

### Integration rule

`autobahn` must treat `spec-driver` as an external authority and consume:

* workflow files
* public CLI/API surfaces
* explicit schemas/contracts

It must **not** depend on unstable internal Python objects from `spec-driver` unless that dependency is explicitly formalized as public.

---

## Non-goals

Do not design `autobahn` as:

* a replacement for `spec-driver`
* a general autonomous agent platform
* a transcript-native memory system
* a protocol-heavy distributed orchestrator
* a framework that requires a daemon to function
* a bundle of shell scripts with implicit state

Do not assume:

* tmux is the only session backend
* bubblewrap is the only sandbox backend
* Claude/Opus/Gemini/Codex are modeled directly in core artifact semantics
* subagents are the primary unit of orchestration

---

## Product shape

`autobahn` should start as:

* a Python library
* one top-level public API surface
* typed core models
* pluggable harness/sandbox/session adapters
* no user-facing CLI
* no network transport requirement
* no mandatory background service

The design should still permit future addition of:

* a thin CLI wrapper
* a long-lived supervisor
* a daemon/service mode
* richer observation tooling
* UI/TUI integrations

---

## Boundary contract with `spec-driver`

The design must assume the following seam.

### Canonical durable state

Comes from `spec-driver` artifact/workflow files, for example:

* `workflow/state.yaml`
* `workflow/handoff.current.yaml`
* `workflow/review-index.yaml`
* `workflow/review-findings.yaml`
* `workflow/sessions.yaml`
* `workflow/review-bootstrap.md`

### Canonical workflow semantics

Come from `spec-driver`, not `autobahn`.

Examples:

* what counts as `awaiting_review`
* what a phase boundary means
* what a warm/stale review cache means
* what fields belong in handoff/review files

### `autobahn` responsibilities at the boundary

`autobahn` may:

* read workflow artifacts
* validate them against public models
* write/update runtime-owned fields where explicitly allowed
* spawn and supervise sessions based on workflow state
* compile runtime actions from artifact state
* update runtime/session tracking artifacts if that ownership is explicitly assigned

`autobahn` must not:

* invent alternate workflow truth
* silently bypass artifact contracts
* rely on prose parsing as its primary mechanism
* let process-local state become more authoritative than artifact state

---

## Design goals

### 1. Hard boundary discipline

A caller should be able to understand exactly where `spec-driver` ends and `autobahn` begins.

### 2. Artifact-first continuity

The system must recover from process/session death using durable workflow state.

### 3. Runtime pluggability

Harnesses, session backends, and sandboxes should be adapter-driven.

### 4. Coarse, typed public APIs

The public API should expose a small number of high-value operations, not a pile of tiny primitives.

### 5. Future daemonability

The public API should be suitable for eventual service wrapping, even though no daemon is required now.

### 6. Bounded context

The repo structure and API should minimize cross-contamination between artifact semantics and runtime mechanics.

---

## Top-level public API expectations

The repository should expose a small set of orchestration functions, centered on artifact-driven operations.

The exact names are up to the implementing agent, but the public API should cover at least these conceptual operations:

### Workflow loading / context assembly

Load runtime-relevant workflow state for an artifact.

Example conceptual operation:

* `load_context(...)`

### Handoff-driven role transition

Interpret current workflow state and prepare the next runtime action.

Example conceptual operation:

* `transition_from_handoff(...)`

### Reviewer bootstrap / priming

Build or refresh reviewer runtime state from workflow artifacts and current code state.

Example conceptual operation:

* `prime_review(...)`

### Session lifecycle

Create/resume/pause/terminate/observe a role session.

Example conceptual operations:

* `spawn_role_session(...)`
* `resume_role_session(...)`
* `pause_role_session(...)`
* `terminate_session(...)`
* `observe_session(...)`

### Review result recording

Translate reviewer outcomes into durable workflow-facing updates.

Example conceptual operations:

* `record_review_outcome(...)`
* `approve_review(...)`
* `request_changes(...)`

### Reconciliation

Inspect artifact state and runtime session state, then repair drift.

Example conceptual operation:

* `reconcile(...)`

These functions should be designed around:

* artifact identity/path
* policy/config
* adapter selection
* explicit options
* typed results

They should **not** be designed around freeform prompt construction as the primary abstraction.

---

## Public model requirements

The public API should use typed models rather than raw dicts.

Models should exist for at least:

### Workflow context

Normalized runtime view of artifact/workflow state.

### Session handle / session state

Opaque but inspectable handle for a live or recoverable session.

### Runtime policy

Selected harness, sandbox, supervision, review, and invalidation settings.

### Review bootstrap state

Inputs/outputs for reviewer priming and cache invalidation.

### Transition plan

A computed next-action object derived from current handoff/workflow state.

### Operation result / event summary

Standard structured return values for top-level operations.

The implementation may use:

* pydantic
* dataclasses plus validation
* another typed validation approach

But the public surface should not devolve into untyped YAML blobs.

---

## Internal subsystem expectations

The repository should likely be divided into these subsystems.

### 1. API layer

Small public entrypoints only.

Responsibilities:

* expose stable coarse-grained operations
* validate inputs
* return typed outputs
* avoid leaking internal adapter complexity

### 2. Artifact integration layer

Consumes `spec-driver` workflow artifacts.

Responsibilities:

* locate artifact workflow files
* load/validate YAML/TOML/markdown bridge content
* normalize workflow state for runtime use
* write only allowed runtime-facing updates

### 3. Supervisor/runtime layer

Owns live session/process orchestration.

Responsibilities:

* spawn
* resume
* pause
* terminate
* observe
* reconcile drift

### 4. Harness adapter layer

Per-agent/harness execution adapters.

Examples:

* Claude Code
* pi-mono
* Gemini
* Codex

Responsibilities:

* launch semantics
* prompt/bootstrap injection
* attach/detach semantics
* output/log capture contracts
* config/bootstrap requirements

### 5. Sandbox adapter layer

Per-sandbox execution adapters.

Examples:

* bubblewrap
* no-sandbox/dev
* future isolated runners

Responsibilities:

* process wrapping
* cwd/env/mount policy
* signal propagation
* cleanup semantics

### 6. Review subsystem

Own reviewer bootstrap/amortization mechanics.

Responsibilities:

* bootstrap cache refresh
* invalidation detection
* reviewer resume strategy
* findings continuity support

### 7. Observation/reconciliation layer

Responsibilities:

* structured events
* runtime status summaries
* session health
* state drift detection
* debugging visibility

---

## Adapter interface expectations

The repo should define explicit adapter interfaces/protocols for:

### Harness adapters

Need to answer questions like:

* how is a role session launched?
* how is bootstrap material supplied?
* what does attach/detach mean?
* how are logs or outputs surfaced?
* what constitutes session identity?
* what installation/config preconditions must be satisfied?

### Sandbox adapters

Need to answer questions like:

* how is a process wrapped?
* how is the environment built?
* how are files/mounts/cwd handled?
* how are signals propagated?
* how are cleanup and teardown handled?

### Session backend abstraction

Need to avoid hard-coding tmux into core logic, even if tmux is the first backend.

Need to answer:

* how is a session created?
* how is it resumed?
* how is it observed?
* how is liveness determined?
* what metadata is available?

---

## Explicit tradeoffs to consider

The implementing agent should scope/design with these tradeoffs in mind.

### Library boundary vs process boundary

A library repo gives strong codebase separation but not hard runtime isolation.
Design APIs so a future daemon/service wrapper remains possible.

### Artifact truth vs runtime convenience

Artifact state must remain canonical. Runtime/session-local state is secondary.

### Generality vs practical usefulness

Do not over-generalize into a framework for every future use case. Build around the known artifact-driven workflow.

### Adapter flexibility vs core simplicity

Keep core models and API narrow. Push harness/sandbox variation behind adapters.

### Rich supervision vs early complexity

Do not require a background supervisor for correctness in the first version unless the design proves it is unavoidable.

---

## Invariants to maintain

### Canonical-state invariant

Workflow artifacts remain the durable source of truth.

### Runtime-secondary invariant

Process/session state must be reconstructible from artifact state plus adapter policy.

### Typed-boundary invariant

Public `autobahn` APIs should expose typed models, not loose dict contracts.

### Adapter-isolation invariant

Harness-specific and sandbox-specific behavior must not leak into core workflow logic.

### Recoverability invariant

Loss of a session must not imply loss of workflow continuity.

### Extractability invariant

The internal design should allow future wrapping in a CLI/daemon/service without rewriting the core.

---

## Packaging and repository expectations

The repo should be structured to keep the public API small and internal complexity compartmentalized.

A reasonable initial package shape would look roughly like:

```text
autobahn/
  src/autobahn/
    api/
    models/
    artifacts/
    runtime/
    adapters/
      harness/
      sandbox/
      session/
    review/
    observation/
    util/
  tests/
  pyproject.toml
  README.md
  docs/
```

Exact layout is flexible, but the separation of concerns should be visible in the repo structure.

---

## Initial implementation scope

The first design should support one narrow vertical slice well.

Recommended slice:

* load artifact workflow state
* compute next role transition from handoff
* prime reviewer state
* spawn/resume a reviewer session through one harness adapter
* record review outcome
* reconcile runtime/session state against workflow files

This is enough to prove the A/B boundary without prematurely solving everything.

---

## Expected outputs from the implementing agent

The local agent should produce:

### 1. Repository architecture proposal

Including package layout, subsystem responsibilities, and dependency boundaries.

### 2. Public API proposal

Including top-level functions/classes, input/output models, and error model.

### 3. Adapter interface proposal

For harnesses, sandboxes, and session backends.

### 4. Artifact integration contract

Exactly how `autobahn` reads/writes `spec-driver` workflow artifacts, and which files/fields it treats as canonical vs advisory.

### 5. Initial runtime model

How spawn/resume/pause/observe/reconcile are represented.

### 6. Vertical slice design

A first narrow end-to-end path proving the architecture.

### 7. Deferred decisions list

Questions intentionally left open for later, such as:

* daemonization
* network protocols
* multi-client coordination
* advanced subagent topology
* distributed execution

---

## Success criteria

A good design should make it possible to answer “yes” to these:

* Can `autobahn` supervise workflow progression without owning workflow semantics?
* Can it resume useful reviewer work without relying on transcript replay?
* Can it support one harness/backend without hard-coding that choice into core logic?
* Can it recover from session loss using artifact state?
* Can the public API remain small and typed despite internal runtime complexity?
* Would it still make sense if wrapped later in a daemon or thin CLI?

---

## Final design heuristic

`autobahn` should feel like:

* a runtime library consuming a stable workflow kernel
* externally separate from `spec-driver`
* internally modular
* typed at the boundary
* adapter-driven at the edges
* artifact-first in continuity and recovery

It should not feel like:

* a second workflow system
* a bundle of harness-specific hacks
* a protocol/server project pretending not to be one
* a hidden extension of `spec-driver` internals

---

If useful, I can also turn this into a `README bootstrap + repo scaffold brief` with proposed `pyproject.toml`, package layout, and initial Python interface skeletons.
