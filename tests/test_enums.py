"""Contract tests for enum values.

Autobahn-owned transcriptions are validated against spec-driver's
canonical values from workflow_metadata.py.

Review-related enums are re-exported from spec_driver.orchestration
(ADR-002, DEC-004-005) — alias identity tests verify the re-export.
"""

from __future__ import annotations

import spec_driver.orchestration as sd

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


# --- Autobahn-owned transcriptions (contract tests) ---
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


# --- Re-export alias identity tests (DEC-004-005) ---


def test_bootstrap_status_is_spec_driver_type():
  assert BootstrapStatus is sd.BootstrapStatus


def test_review_status_is_spec_driver_type():
  assert ReviewStatus is sd.ReviewStatus


def test_finding_disposition_action_is_spec_driver_type():
  assert FindingDispositionAction is sd.FindingDispositionAction


def test_disposition_authority_is_spec_driver_type():
  assert DispositionAuthority is sd.DispositionAuthority


def test_finding_status_is_spec_driver_type():
  assert FindingStatus is sd.FindingStatus
