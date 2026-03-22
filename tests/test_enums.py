"""Contract tests for enum values.

Validates that autobahn's enum transcriptions match spec-driver's
canonical values from workflow_metadata.py.
"""

from __future__ import annotations

from autobahn.models.enums import (
  ArtifactKind,
  BootstrapStatus,
  DispositionAuthority,
  FindingDispositionAction,
  FindingStatus,
  HandoffTransitionStatus,
  NextActivityKind,
  PhaseStatus,
  ReviewStatus,
  Role,
  SessionStatus,
  WorkflowStatus,
)


def _values(enum_cls):
  return [m.value for m in enum_cls]


# Source: supekku/scripts/lib/blocks/workflow_metadata.py L53-93 (2026-03-22)


def test_role_values():
  assert _values(Role) == [
    "architect",
    "implementer",
    "reviewer",
    "operator",
    "other",
  ]


def test_workflow_status_values():
  assert _values(WorkflowStatus) == [
    "planned",
    "implementing",
    "awaiting_handoff",
    "reviewing",
    "changes_requested",
    "approved",
    "blocked",
  ]


def test_phase_status_values():
  assert _values(PhaseStatus) == [
    "not_started",
    "in_progress",
    "blocked",
    "complete",
    "skipped",
  ]


def test_artifact_kind_values():
  assert _values(ArtifactKind) == [
    "delta",
    "plan",
    "revision",
    "audit",
    "task",
    "other",
  ]


def test_session_status_values():
  assert _values(SessionStatus) == [
    "active",
    "paused",
    "absent",
    "dead",
    "unknown",
  ]


def test_next_activity_kind_values():
  assert _values(NextActivityKind) == [
    "implementation",
    "review",
    "architecture",
    "verification",
    "operator_attention",
  ]


def test_handoff_transition_status_values():
  assert _values(HandoffTransitionStatus) == [
    "pending",
    "accepted",
    "superseded",
  ]


def test_bootstrap_status_values():
  assert _values(BootstrapStatus) == [
    "cold",
    "warm",
    "stale",
    "reusable",
    "invalid",
  ]


def test_review_status_values():
  assert _values(ReviewStatus) == [
    "not_started",
    "in_progress",
    "approved",
    "changes_requested",
  ]


def test_finding_disposition_action_values():
  assert _values(FindingDispositionAction) == [
    "fix",
    "defer",
    "waive",
    "supersede",
  ]


def test_disposition_authority_values():
  assert _values(DispositionAuthority) == ["user", "agent"]


def test_finding_status_values():
  assert _values(FindingStatus) == [
    "open",
    "resolved",
    "waived",
    "superseded",
  ]
