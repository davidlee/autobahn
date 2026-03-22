---
id: ADR-001
title: 'ADR-001: Spec-driver schema authority and autobahn extension contract'
status: accepted
created: '2026-03-22'
updated: '2026-03-22'
reviewed: '2026-03-22'
owners: []
supersedes: []
superseded_by: []
policies: []
specs: []
requirements: []
deltas:
  - DE-003
audits: []
related_decisions: []
related_policies: []
tags:
  - architecture
  - schema
  - authority
summary: 'Establishes spec-driver as schema authority for workflow files; defines conformance obligations and extension point contract for autobahn.'
---

# ADR-001: Spec-driver schema authority and autobahn extension contract

## Context

autobahn consumes and writes spec-driver workflow files (state.yaml, handoff.current.yaml, review-index.yaml, review-findings.yaml, sessions.yaml). During DE-001 and DE-002, autobahn built pydantic models and a sessions.yaml writer based on early schema understanding. Three spec-driver deltas have since landed (DE-108, DE-109, DE-110) that formalise schemas, change enum values, and export canonical examples.

This created concrete drift:

- `BootstrapStatus.WARMING` and `ReviewStatus.BLOCKED` exist in autobahn but were removed upstream (DEC-109-002, DEC-109-003).
- autobahn's `SessionsFile` uses a list of `SessionEntry` objects; the canonical `workflow.sessions` schema uses a role-keyed dict.
- Review-index and review-findings models are missing fields added by DE-109 (judgment_status, dispositions, domain_map, etc.).
- Handoff model is missing fields from current schema (key_files, verification, structured open_items).

The fundamental question: who is authoritative for what, and how does autobahn extend schemas it doesn't own?

## Decision

### 1. Spec-driver is schema authority for all workflow files

Spec-driver defines the canonical schema for every `supekku.workflow.*` file. autobahn's pydantic models MUST conform to these schemas. When spec-driver changes a schema, autobahn updates to match.

This applies to:
- File structure and field names
- Enum value sets
- Schema version identifiers
- Serialization format (YAML shape, key ordering conventions)

Autobahn may use `extra="ignore"` to consume a subset of fields, but the fields it does consume must match the canonical types and semantics. Fields autobahn writes must produce YAML that spec-driver can load without error.

### 2. Enum values are cited transcriptions, not autobahn definitions

This was established informally in DR-001 (DEC-019) and is now formalised. Autobahn's enum classes transcribe spec-driver's canonical values. Contract tests validate the transcription. When spec-driver changes values, autobahn's contract tests break and autobahn updates to match.

The authoritative source is `supekku/scripts/lib/blocks/workflow_metadata.py` for value lists and `supekku/scripts/lib/workflow/review_state_machine.py` for review-specific enums.

### 3. Extension points are explicit and negotiated

Autobahn may own structure within spec-driver schemas only at designated extension points. An extension point is a field where:

- Spec-driver defines the field's existence and outer type (e.g., "dict", "list")
- Spec-driver validates the outer type but does not interpret contents
- Autobahn defines the inner schema and is responsible for its evolution

**Currently established extension points:**

| File | Field | Outer type | Owner | Authority |
|------|-------|-----------|-------|-----------|
| `review-findings.yaml` | `rounds[].session` | `dict` | autobahn | DEC-109-009 |

**Extension point contract:**

- Extension points are created by spec-driver design decisions, not unilaterally by autobahn.
- Autobahn documents its inner schema in its own DR/specs but does not expect spec-driver to validate it.
- Spec-driver preserves extension point contents faithfully (round-trip safe).
- If autobahn needs a new extension point, it proposes one to spec-driver as a design decision in the relevant spec-driver delta.

### 4. Schema reconciliation is a maintenance obligation

When spec-driver lands schema changes, autobahn must reconcile before building new features on the affected schemas. Reconciliation is scoped as a delta (not ad-hoc fixes) when it touches more than one model or changes serialization format.

The reconciliation sequence:
1. Update enum transcriptions to match canonical values
2. Update pydantic models to match canonical schema shape
3. Update writer(s) to produce conformant output
4. Update fixtures to match canonical examples
5. Verify round-trip: written files load without error through both autobahn and spec-driver

### 5. `spec-driver show schema` is the contract verification surface

DE-110 exports canonical YAML examples and JSON Schema for all registered block types. Autobahn can use these to validate model conformance programmatically. The command `spec-driver show schema workflow.<type> --format yaml-example` produces the reference shape.

## Consequences

### Positive

- Clear authority eliminates ambiguity when schemas diverge (autobahn conforms, not negotiates)
- Extension point contract prevents autobahn from silently inventing schema that spec-driver can't load
- Contract tests + canonical examples create a fast feedback loop for drift
- Reconciliation-as-delta creates traceable history of schema evolution

### Negative

- autobahn cannot innovate on file shape without upstream coordination (by design — the constraint is the feature)
- Schema reconciliation deltas are maintenance overhead when spec-driver evolves rapidly
- Extension points are sparse — autobahn must work within spec-driver's schema rather than extending freely

### Neutral

- DR-001's `extra="ignore"` policy remains correct — autobahn reads a subset but must not contradict the superset
- The sessions.yaml list-vs-dict divergence is now clearly a conformance bug, not a design choice — DE-003 fixes it

## Verification

- Contract tests in `test_enums.py` validate enum transcriptions against canonical values
- Round-trip tests (write → load) verify serialization conformance
- `just check` catches model/enum drift as part of normal development
- Future: automated check against `spec-driver show schema --format json-schema` (not in scope for DE-003, but the ADR establishes the intent)

## References

- DR-001 §6 (models), §9 (artifact integration contract), DEC-019 (enum transcription policy)
- DR-002 §4.1 (schema validation), DEC-027 (SCHEMA_VERSIONS)
- spec-driver DEC-109-002 (warming removed), DEC-109-003 (blocked removed), DEC-109-009 (round session extension point)
- spec-driver DR-110 (schema export for all block types)
