"""Enum transcriptions from spec-driver workflow metadata.

Source: supekku/scripts/lib/blocks/workflow_metadata.py as of 2026-03-22.
These are cited transcriptions, not autobahn definitions — when spec-driver
changes values, autobahn's contract tests break and autobahn updates to match.

Design authority: DR-001 §6, DEC-019.
"""

from __future__ import annotations

from enum import StrEnum

# --- Core enums (slice 1) ---


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


# --- Review-related enums ---


class BootstrapStatus(StrEnum):
  """Review bootstrap status. Source: BOOTSTRAP_STATUS_VALUES L75-82."""

  COLD = "cold"
  WARM = "warm"
  STALE = "stale"
  REUSABLE = "reusable"
  INVALID = "invalid"


class ReviewStatus(StrEnum):
  """Review status. Source: REVIEW_STATUS_VALUES L83-89."""

  NOT_STARTED = "not_started"
  IN_PROGRESS = "in_progress"
  APPROVED = "approved"
  CHANGES_REQUESTED = "changes_requested"


class FindingDispositionAction(StrEnum):
  """Finding disposition action. Source: FINDING_DISPOSITION_ACTION_VALUES L91."""

  FIX = "fix"
  DEFER = "defer"
  WAIVE = "waive"
  SUPERSEDE = "supersede"


class DispositionAuthority(StrEnum):
  """Who made the disposition decision. Source: DISPOSITION_AUTHORITY_VALUES L92."""

  USER = "user"
  AGENT = "agent"


class FindingStatus(StrEnum):
  """Finding lifecycle status. Source: FINDING_STATUS_VALUES L90."""

  OPEN = "open"
  RESOLVED = "resolved"
  WAIVED = "waived"
  SUPERSEDED = "superseded"
