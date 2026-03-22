"""Tests for public API functions (VA-003)."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest

from autobahn.api import (
  check_prerequisites,
  load_context,
  observe_session,
  spawn_role_session,
  terminate_session,
  transition_from_handoff,
)
from autobahn.models.enums import (
  NextActivityKind,
  Role,
  WorkflowStatus,
)
from autobahn.models.errors import PreconditionError
from autobahn.models.runtime import (
  LaunchSpec,
  RuntimePolicy,
  SessionHandle,
  SessionMetadata,
  SessionOutcome,
)

FIXTURES = Path(__file__).parent / "fixtures" / "workflow"


# --- Mock adapters ---


class MockHarness:
  @property
  def name(self) -> str:
    return "mock"

  def __init__(self, *, available: bool = True) -> None:
    self._available = available

  def is_available(self, policy: RuntimePolicy) -> bool:
    return self._available

  def launch_spec(
    self,
    *,
    work_dir,
    plan,
    policy,
  ) -> LaunchSpec:
    return LaunchSpec(
      command="echo",
      args=["mock"],
      work_dir=work_dir,
    )

  def parse_exit(self, exit_code: int) -> SessionOutcome:
    return SessionOutcome(
      exit_code=exit_code,
      interpretation="mock",
    )


class MockBackend:
  def __init__(self, *, available: bool = True) -> None:
    self._available = available
    self._alive = True

  def is_available(self) -> bool:
    return self._available

  async def create(self, session_id, launch) -> SessionHandle:
    return SessionHandle(
      session_id=session_id,
      role=Role.OTHER,
      artifact_id="",
      backend_ref="mock:1",
      launched_at=datetime.now(tz=UTC),
    )

  async def is_alive(self, handle) -> bool:
    return self._alive

  async def terminate(self, handle) -> None:
    self._alive = False

  async def get_metadata(self, handle) -> SessionMetadata:
    return SessionMetadata(
      alive=self._alive,
      exit_code=None if self._alive else 0,
    )


def _policy(*, work_dir: Path | None = None) -> RuntimePolicy:
  return RuntimePolicy(
    harness="mock",
    session_backend="mock",
    work_dir=work_dir or Path("/tmp"),
  )


# --- check_prerequisites ---


class TestCheckPrerequisites:
  def test_all_good(self, tmp_path):
    errors = check_prerequisites(
      _policy(work_dir=tmp_path),
      harness=MockHarness(),
      backend=MockBackend(),
    )
    assert errors == []

  def test_harness_unavailable(self, tmp_path):
    errors = check_prerequisites(
      _policy(work_dir=tmp_path),
      harness=MockHarness(available=False),
      backend=MockBackend(),
    )
    assert len(errors) == 1
    assert "Harness" in str(errors[0])

  def test_backend_unavailable(self, tmp_path):
    errors = check_prerequisites(
      _policy(work_dir=tmp_path),
      harness=MockHarness(),
      backend=MockBackend(available=False),
    )
    assert len(errors) == 1
    assert "backend" in str(errors[0])

  def test_work_dir_missing(self):
    errors = check_prerequisites(
      _policy(work_dir=Path("/nonexistent/dir/xyz")),
      harness=MockHarness(),
      backend=MockBackend(),
    )
    assert len(errors) == 1
    assert "Work directory" in str(errors[0])

  def test_multiple_errors(self):
    errors = check_prerequisites(
      _policy(work_dir=Path("/nonexistent")),
      harness=MockHarness(available=False),
      backend=MockBackend(available=False),
    )
    assert len(errors) == 3


# --- load_context ---


class TestLoadContext:
  def test_loads_from_artifact_dir(self, tmp_path):
    # Create workflow subdir with state.yaml
    workflow_dir = tmp_path / "workflow"
    workflow_dir.mkdir()
    shutil.copy(FIXTURES / "state.yaml", workflow_dir / "state.yaml")
    ctx = load_context(tmp_path)
    assert ctx.artifact_id == "DE-099"

  def test_custom_workflow_dir(self, tmp_path):
    custom = tmp_path / "custom"
    custom.mkdir()
    shutil.copy(FIXTURES / "state.yaml", custom / "state.yaml")
    ctx = load_context(tmp_path, workflow_dir="custom")
    assert ctx.artifact_id == "DE-099"


# --- transition_from_handoff ---


class TestTransitionFromHandoff:
  def test_computes_plan(self):
    ctx = load_context(
      FIXTURES.parent,
      workflow_dir="workflow",
    )
    plan = transition_from_handoff(ctx)
    assert plan.artifact_id == "DE-099"
    assert plan.target_role == Role.REVIEWER
    assert plan.activity == NextActivityKind.REVIEW
    assert plan.phase_id == "IP-099.PHASE-01"
    assert len(plan.required_reading) == 4

  def test_terminal_state_raises(self):
    ctx = load_context(
      FIXTURES.parent,
      workflow_dir="workflow",
    )
    ctx.state.workflow.status = WorkflowStatus.APPROVED
    with pytest.raises(PreconditionError, match="terminal"):
      transition_from_handoff(ctx)

  def test_missing_handoff_raises(self, tmp_path):
    workflow_dir = tmp_path / "workflow"
    workflow_dir.mkdir()
    shutil.copy(FIXTURES / "state.yaml", workflow_dir / "state.yaml")
    ctx = load_context(tmp_path)
    assert ctx.handoff is None
    with pytest.raises(PreconditionError, match="handoff"):
      transition_from_handoff(ctx)


# --- spawn_role_session ---


class TestSpawnRoleSession:
  @pytest.mark.asyncio
  async def test_spawn_success(self):
    ctx = load_context(FIXTURES.parent, workflow_dir="workflow")
    plan = transition_from_handoff(ctx)
    result = await spawn_role_session(
      ctx,
      plan,
      policy=_policy(),
      harness=MockHarness(),
      backend=MockBackend(),
    )
    assert result.success is True
    assert result.value is not None
    assert result.value.session_id == "DE-099-reviewer"


# --- terminate_session ---


class TestTerminateSession:
  @pytest.mark.asyncio
  async def test_terminate_alive(self):
    handle = SessionHandle(
      session_id="sess-001",
      role=Role.IMPLEMENTER,
      artifact_id="DE-099",
      backend_ref="mock:1",
      launched_at=datetime.now(tz=UTC),
    )
    result = await terminate_session(
      handle,
      harness=MockHarness(),
      backend=MockBackend(),
    )
    assert result.success is True
    assert result.value is not None
    assert result.value.exit_code == 0


# --- observe_session ---


class TestObserveSession:
  @pytest.mark.asyncio
  async def test_observe_until_dead(self):
    backend = MockBackend()
    handle = SessionHandle(
      session_id="sess-001",
      role=Role.IMPLEMENTER,
      artifact_id="DE-099",
      backend_ref="mock:1",
      launched_at=datetime.now(tz=UTC),
    )
    # Kill after first observation
    observations = []
    async for meta in observe_session(
      handle,
      backend=backend,
      poll_interval=0.01,
    ):
      observations.append(meta)
      backend._alive = False

    assert len(observations) == 2  # alive, then dead
    assert observations[0].alive is True
    assert observations[-1].alive is False
