"""Tests for runtime models and error taxonomy."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from autobahn.models.enums import (
  NextActivityKind,
  Role,
  WorkflowStatus,
)
from autobahn.models.errors import (
  ArtifactContractError,
  ArtifactParseError,
  AutobahnError,
  BackendTransportError,
  BackendUnavailableError,
  PreconditionError,
  SessionError,
)
from autobahn.models.runtime import (
  LaunchSpec,
  OperationResult,
  RuntimePolicy,
  SessionHandle,
  SessionMetadata,
  SessionOutcome,
  TransitionPlan,
)

# --- Runtime models ---


class TestTransitionPlan:
  def test_construction(self):
    plan = TransitionPlan(
      source_state=WorkflowStatus.IMPLEMENTING,
      target_role=Role.REVIEWER,
      activity=NextActivityKind.REVIEW,
      artifact_id="DE-099",
      phase_id="IP-099.PHASE-01",
      handoff_path="workflow/handoff.current.yaml",
      required_reading=["DE-099.md", "notes.md"],
    )
    assert plan.target_role == Role.REVIEWER
    assert plan.resume_session is None


class TestLaunchSpec:
  def test_construction(self):
    spec = LaunchSpec(
      command="claude",
      args=["--continue"],
      env={"CLAUDE_MODEL": "opus"},
      work_dir=Path("/tmp/work"),
    )
    assert spec.command == "claude"
    assert spec.work_dir == Path("/tmp/work")


class TestSessionHandle:
  def test_construction(self):
    handle = SessionHandle(
      session_id="sess-001",
      role=Role.IMPLEMENTER,
      artifact_id="DE-099",
      backend_ref="pid:12345",
      launched_at=datetime(2026, 3, 22, tzinfo=UTC),
    )
    assert handle.session_id == "sess-001"


class TestSessionMetadata:
  def test_alive_session(self):
    meta = SessionMetadata(alive=True, runtime_seconds=120.5)
    assert meta.alive is True
    assert meta.exit_code is None

  def test_dead_session(self):
    meta = SessionMetadata(alive=False, exit_code=0, runtime_seconds=300.0)
    assert meta.alive is False
    assert meta.exit_code == 0


class TestSessionOutcome:
  def test_construction(self):
    outcome = SessionOutcome(
      exit_code=0,
      interpretation="completed normally",
      artifacts_modified=True,
    )
    assert outcome.exit_code == 0


class TestRuntimePolicy:
  def test_construction(self):
    policy = RuntimePolicy(
      harness="claude_code",
      session_backend="subprocess",
      work_dir=Path("/tmp/work"),
    )
    assert policy.harness_executable is None
    assert policy.timeout_seconds is None


class TestOperationResult:
  def test_success(self):
    result = OperationResult[str](success=True, value="done")
    assert result.success is True
    assert result.value == "done"

  def test_failure(self):
    result = OperationResult[str](
      success=False,
      error="something went wrong",
      warnings=["partial data"],
    )
    assert result.success is False
    assert result.error == "something went wrong"
    assert len(result.warnings) == 1


# --- Error taxonomy ---


class TestErrorHierarchy:
  @pytest.mark.parametrize(
    "exc_cls",
    [
      ArtifactParseError,
      ArtifactContractError,
      BackendUnavailableError,
      BackendTransportError,
      PreconditionError,
      SessionError,
    ],
  )
  def test_all_inherit_from_autobahn_error(self, exc_cls):
    assert issubclass(exc_cls, AutobahnError)

  def test_can_catch_by_base(self):
    with pytest.raises(AutobahnError):
      raise ArtifactParseError("bad yaml")
