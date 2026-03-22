"""Contract tests for artifact file models.

Validates that pydantic models parse spec-driver workflow YAML fixtures
without error and that key fields are correctly typed.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from autobahn.models.artifacts import (
  HandoffFile,
  ReviewFindingsFile,
  ReviewIndexFile,
  SessionsFile,
  WorkflowStateFile,
)
from autobahn.models.enums import (
  ArtifactKind,
  BootstrapStatus,
  FindingStatus,
  HandoffTransitionStatus,
  NextActivityKind,
  PhaseStatus,
  ReviewStatus,
  Role,
  SessionStatus,
  WorkflowStatus,
)

FIXTURES = Path(__file__).parent / "fixtures" / "workflow"


def _load_yaml(name: str) -> dict:
  return yaml.safe_load((FIXTURES / name).read_text())


# --- state.yaml ---


class TestWorkflowStateFile:
  def test_parses_fixture(self):
    data = _load_yaml("state.yaml")
    state = WorkflowStateFile.model_validate(data)
    assert state.artifact.id == "DE-099"
    assert state.artifact.kind == ArtifactKind.DELTA
    assert state.workflow.status == WorkflowStatus.IMPLEMENTING
    assert state.workflow.active_role == Role.IMPLEMENTER
    assert state.phase.id == "IP-099.PHASE-01"
    assert state.phase.status == PhaseStatus.IN_PROGRESS

  def test_timestamps_parsed(self):
    data = _load_yaml("state.yaml")
    state = WorkflowStateFile.model_validate(data)
    assert state.timestamps.updated is not None

  def test_pointers(self):
    data = _load_yaml("state.yaml")
    state = WorkflowStateFile.model_validate(data)
    assert state.pointers is not None
    assert state.pointers.delta is not None

  def test_ignores_extra_fields(self):
    data = _load_yaml("state.yaml")
    data["unknown_field"] = "should be ignored"
    state = WorkflowStateFile.model_validate(data)
    assert state.artifact.id == "DE-099"


# --- handoff.current.yaml ---


class TestHandoffFile:
  def test_parses_fixture(self):
    data = _load_yaml("handoff.current.yaml")
    handoff = HandoffFile.model_validate(data)
    assert handoff.artifact.id == "DE-099"
    assert handoff.transition.from_role == Role.IMPLEMENTER
    assert handoff.transition.to_role == Role.REVIEWER
    assert handoff.transition.status == HandoffTransitionStatus.PENDING
    assert handoff.next_activity.kind == NextActivityKind.REVIEW

  def test_required_reading(self):
    data = _load_yaml("handoff.current.yaml")
    handoff = HandoffFile.model_validate(data)
    assert len(handoff.required_reading) == 4

  def test_open_items(self):
    data = _load_yaml("handoff.current.yaml")
    handoff = HandoffFile.model_validate(data)
    assert len(handoff.open_items) == 1
    assert handoff.open_items[0].kind == "next_step"


# --- review-index.yaml ---


class TestReviewIndexFile:
  def test_parses_fixture(self):
    data = _load_yaml("review-index.yaml")
    idx = ReviewIndexFile.model_validate(data)
    assert idx.artifact.id == "DE-099"
    assert idx.review.bootstrap_status == BootstrapStatus.WARM
    assert idx.review.judgment_status == ReviewStatus.IN_PROGRESS

  def test_staleness_key(self):
    data = _load_yaml("review-index.yaml")
    idx = ReviewIndexFile.model_validate(data)
    assert idx.staleness is not None
    assert idx.staleness.cache_key is not None
    assert idx.staleness.cache_key.head == "abc123de"


# --- review-findings.yaml ---


class TestReviewFindingsFile:
  def test_parses_fixture(self):
    data = _load_yaml("review-findings.yaml")
    findings = ReviewFindingsFile.model_validate(data)
    assert findings.artifact.id == "DE-099"
    assert findings.review.current_round == 1
    assert len(findings.rounds) == 1

  def test_round_findings(self):
    data = _load_yaml("review-findings.yaml")
    findings = ReviewFindingsFile.model_validate(data)
    r1 = findings.rounds[0]
    assert r1.round == 1
    assert r1.status == ReviewStatus.IN_PROGRESS
    assert len(r1.blocking) == 1
    assert r1.blocking[0].status == FindingStatus.OPEN
    assert len(r1.non_blocking) == 1


# --- sessions.yaml ---


class TestSessionsFile:
  def test_parses_fixture(self):
    data = _load_yaml("sessions.yaml")
    sessions = SessionsFile.model_validate(data)
    assert sessions.artifact.id == "DE-099"
    assert len(sessions.sessions) == 1

  def test_session_entry(self):
    data = _load_yaml("sessions.yaml")
    sessions = SessionsFile.model_validate(data)
    entry = sessions.sessions[0]
    assert entry.session_id == "sess-001"
    assert entry.role == Role.IMPLEMENTER
    assert entry.status == SessionStatus.ACTIVE
    assert entry.backend == "subprocess"
    assert entry.harness == "claude_code"
    assert entry.pid == 12345
