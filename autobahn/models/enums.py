"""Enum transcriptions from spec-driver workflow metadata.

Core enums (Role, WorkflowStatus, etc.) are autobahn-owned transcriptions
validated by contract tests. Review-related enums are re-exported from
spec-driver's public API (ADR-002, DEC-004-005).

Design authority: DR-001 §6, DEC-019, DR-004 §4.1.
"""

from __future__ import annotations

from enum import StrEnum

# --- Core enums (autobahn transcriptions — slice 1) ---


class Role(StrEnum):
  """Agent role. Source: ROLE_VALUES L55."""

  ARCHITECT = "architect"
  IMPLEMENTER = "implementer"
  REVIEWER = "reviewer"
  OPERATOR = "operator"
  OTHER = "other"


class WorkflowStatus(StrEnum):
  """Workflow lifecycle status. Source: WORKFLOW_STATUS_VALUES L56-64."""

  PLANNED = "planned"
  IMPLEMENTING = "implementing"
  AWAITING_HANDOFF = "awaiting_handoff"
  REVIEWING = "reviewing"
  CHANGES_REQUESTED = "changes_requested"
  APPROVED = "approved"
  BLOCKED = "blocked"


TERMINAL_WORKFLOW_STATES: frozenset[WorkflowStatus] = frozenset(
  {
    WorkflowStatus.APPROVED,
  }
)


class PhaseStatus(StrEnum):
  """Phase execution status. Source: PHASE_STATUS_VALUES L54."""

  NOT_STARTED = "not_started"
  IN_PROGRESS = "in_progress"
  BLOCKED = "blocked"
  COMPLETE = "complete"
  SKIPPED = "skipped"


class ArtifactKind(StrEnum):
  """Artifact type. Source: ARTIFACT_KIND_VALUES L53."""

  DELTA = "delta"
  PLAN = "plan"
  REVISION = "revision"
  AUDIT = "audit"
  TASK = "task"
  OTHER = "other"


class SessionStatus(StrEnum):
  """Session lifecycle status. Source: SESSION_STATUS_VALUES L93."""

  ACTIVE = "active"
  PAUSED = "paused"  # placeholder — no pause in v1 protocol
  ABSENT = "absent"
  DEAD = "dead"
  UNKNOWN = "unknown"


class NextActivityKind(StrEnum):
  """Next activity type from handoff. Source: NEXT_ACTIVITY_KIND_VALUES L67-73."""

  IMPLEMENTATION = "implementation"
  REVIEW = "review"
  ARCHITECTURE = "architecture"
  VERIFICATION = "verification"
  OPERATOR_ATTENTION = "operator_attention"


class HandoffTransitionStatus(StrEnum):
  """Handoff transition status. Source: HANDOFF_TRANSITION_STATUS_VALUES L65."""

  PENDING = "pending"
  ACCEPTED = "accepted"
  SUPERSEDED = "superseded"


# --- Review-related enums (re-exported from spec-driver — ADR-002, DEC-004-005) ---

from spec_driver.orchestration import (  # noqa: E402
  BootstrapStatus,
  DispositionAuthority,
  FindingDispositionAction,
  FindingStatus,
  ReviewStatus,
)

__all__ = [
  # Autobahn transcriptions
  "Role",
  "WorkflowStatus",
  "TERMINAL_WORKFLOW_STATES",
  "PhaseStatus",
  "ArtifactKind",
  "SessionStatus",
  "NextActivityKind",
  "HandoffTransitionStatus",
  # Re-exports from spec-driver
  "BootstrapStatus",
  "ReviewStatus",
  "FindingDispositionAction",
  "DispositionAuthority",
  "FindingStatus",
]
