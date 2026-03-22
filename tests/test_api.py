"""Tests for public API functions (VA-003)."""

from __future__ import annotations

import logging
import shutil
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml
from spec_driver.orchestration import (
  BootstrapStatus,
  DispositionAuthority,
  FindingDispositionAction,
  FindingNotFoundError,
  FindingsNotFoundError,
  FindingStatus,
  PrimeAction,
  ReviewStatus,
  StateNotFoundError,
)

from autobahn.api import (
  check_prerequisites,
  disposition_finding,
  load_context,
  observe_session,
  persist_session_statuses,
  prime_review,
  reconcile,
  spawn_role_session,
  summarize_review_outcome,
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


def _writable_workflow_dir(tmp_path: Path) -> Path:
  """Copy fixtures to a writable tmp dir for persistence tests."""
  workflow_dir = tmp_path / "workflow"
  workflow_dir.mkdir()
  for f in FIXTURES.iterdir():
    if f.is_file():
      shutil.copy(f, workflow_dir / f.name)
  return tmp_path


class TestSpawnRoleSession:
  @pytest.mark.asyncio
  async def test_spawn_success(self, tmp_path):
    base = _writable_workflow_dir(tmp_path)
    ctx = load_context(base)
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

  @pytest.mark.asyncio
  async def test_spawn_writes_sessions_yaml(self, tmp_path):
    base = _writable_workflow_dir(tmp_path)
    # Remove existing sessions.yaml so we test fresh creation
    (base / "workflow" / "sessions.yaml").unlink()
    ctx = load_context(base)
    plan = transition_from_handoff(ctx)
    result = await spawn_role_session(
      ctx,
      plan,
      policy=_policy(),
      harness=MockHarness(),
      backend=MockBackend(),
    )
    assert result.success is True
    assert result.warnings == []
    sessions_path = base / "workflow" / "sessions.yaml"
    assert sessions_path.exists()
    data = yaml.safe_load(sessions_path.read_text())
    assert len(data["sessions"]) == 1
    assert data["sessions"]["reviewer"]["session_name"] == "DE-099-reviewer"
    assert data["sessions"]["reviewer"]["status"] == "active"

  @pytest.mark.asyncio
  async def test_spawn_overwrites_role_entry(self, tmp_path):
    """Spawning for a role that already has a session overwrites the entry."""
    base = _writable_workflow_dir(tmp_path)
    ctx = load_context(base)
    plan = transition_from_handoff(ctx)
    result = await spawn_role_session(
      ctx,
      plan,
      policy=_policy(),
      harness=MockHarness(),
      backend=MockBackend(),
    )
    assert result.success is True
    data = yaml.safe_load((base / "workflow" / "sessions.yaml").read_text())
    # Original fixture had implementer; spawn added reviewer
    assert set(data["sessions"].keys()) == {"implementer", "reviewer"}

  @pytest.mark.asyncio
  async def test_spawn_handle_has_correct_metadata(self, tmp_path):
    """Verify DEC-023: handle has patched role and artifact_id."""
    base = _writable_workflow_dir(tmp_path)
    ctx = load_context(base)
    plan = transition_from_handoff(ctx)
    result = await spawn_role_session(
      ctx,
      plan,
      policy=_policy(),
      harness=MockHarness(),
      backend=MockBackend(),
    )
    assert result.value.role == Role.REVIEWER
    assert result.value.artifact_id == "DE-099"

  @pytest.mark.asyncio
  async def test_spawn_warns_on_active_overwrite(self, tmp_path, caplog):
    """F-1: overwriting active session logs a warning."""
    base = _writable_workflow_dir(tmp_path)
    ctx = load_context(base)
    # Spawn once to create active reviewer entry
    plan = transition_from_handoff(ctx)
    await spawn_role_session(
      ctx,
      plan,
      policy=_policy(),
      harness=MockHarness(),
      backend=MockBackend(),
    )
    # Reload context and spawn again for the same role
    ctx = load_context(base)
    plan = transition_from_handoff(ctx)
    with caplog.at_level(logging.WARNING):
      await spawn_role_session(
        ctx,
        plan,
        policy=_policy(),
        harness=MockHarness(),
        backend=MockBackend(),
      )
    assert "Overwriting active session" in caplog.text


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


# --- persist_session_statuses ---


class TestPersistSessionStatuses:
  @pytest.mark.asyncio
  async def test_dead_session_marked_dead(self, tmp_path):
    """Dead handle → sessions.yaml entry status becomes dead."""
    base = _writable_workflow_dir(tmp_path)
    ctx = load_context(base)
    handle = SessionHandle(
      session_id="sess-001",
      role=Role.IMPLEMENTER,
      artifact_id="DE-099",
      backend_ref="mock:1",
      launched_at=datetime.now(tz=UTC),
    )
    # Kill the backend to create SESSION_DIED_UNEXPECTEDLY
    backend_dead = MockBackend()
    backend_dead._alive = False
    result = await reconcile(
      ctx,
      policy=_policy(),
      backend=backend_dead,
      active_handles=[handle],
    )
    assert result.value.has_drift is True
    persist_session_statuses(ctx, result.value)
    data = yaml.safe_load((base / "workflow" / "sessions.yaml").read_text())
    assert data["sessions"]["implementer"]["status"] == "dead"

  @pytest.mark.asyncio
  async def test_orphaned_session_marked_dead(self, tmp_path):
    """Orphaned session → sessions.yaml entry status becomes dead."""
    base = _writable_workflow_dir(tmp_path)
    ctx = load_context(base)
    # No handles → sess-001 in sessions.yaml is orphaned
    result = await reconcile(
      ctx,
      policy=_policy(),
      backend=MockBackend(),
      active_handles=[],
    )
    assert result.value.has_drift is True
    kinds = [d.kind for d in result.value.drift_items]
    assert "ORPHANED_SESSION" in kinds
    persist_session_statuses(ctx, result.value)
    data = yaml.safe_load((base / "workflow" / "sessions.yaml").read_text())
    assert data["sessions"]["implementer"]["status"] == "dead"

  @pytest.mark.asyncio
  async def test_alive_session_unchanged(self, tmp_path):
    """Alive handle with no drift → sessions.yaml entry unchanged."""
    base = _writable_workflow_dir(tmp_path)
    # Remove sessions.yaml to avoid orphan detection, then write clean one
    (base / "workflow" / "sessions.yaml").unlink()
    ctx = load_context(base)
    # Spawn a session to create sessions.yaml
    plan = transition_from_handoff(ctx)
    await spawn_role_session(
      ctx,
      plan,
      policy=_policy(),
      harness=MockHarness(),
      backend=MockBackend(),
    )
    # Reload context to pick up the new sessions.yaml
    ctx = load_context(base)
    handle = SessionHandle(
      session_id="DE-099-reviewer",
      role=Role.REVIEWER,
      artifact_id="DE-099",
      backend_ref="mock:1",
      launched_at=datetime.now(tz=UTC),
    )
    result = await reconcile(
      ctx,
      policy=_policy(),
      backend=MockBackend(available=True),
      active_handles=[handle],
    )
    persist_session_statuses(ctx, result.value)
    data = yaml.safe_load((base / "workflow" / "sessions.yaml").read_text())
    assert data["sessions"]["reviewer"]["status"] == "active"


# --- Review operations (DE-004, Phase 2) ---


class TestPrimeReview:
  """Tests for prime_review — thin wrapper around spec_driver.orchestration."""

  def test_delegates_to_spec_driver(self, tmp_path, monkeypatch):
    """prime_review calls spec-driver's prime_review with correct args."""
    mock_result = MagicMock()
    mock_result.delta_id = "DE-099"
    mock_result.action = PrimeAction.CREATED
    mock_result.bootstrap_status = BootstrapStatus.WARM
    mock_result.judgment_status = ReviewStatus.IN_PROGRESS
    mock_result.review_round = 1
    mock_result.index_path = tmp_path / "review-index.yaml"
    mock_result.bootstrap_path = tmp_path / "review-bootstrap.md"

    mock_fn = MagicMock(return_value=mock_result)
    monkeypatch.setattr("autobahn.api.functions._sd_prime_review", mock_fn)

    result = prime_review(tmp_path / "delta", tmp_path)

    mock_fn.assert_called_once_with(tmp_path / "delta", tmp_path)
    assert result is mock_result

  def test_propagates_state_not_found(self, tmp_path, monkeypatch):
    """spec-driver StateNotFoundError propagates to caller."""
    mock_fn = MagicMock(side_effect=StateNotFoundError("no state"))
    monkeypatch.setattr("autobahn.api.functions._sd_prime_review", mock_fn)

    with pytest.raises(StateNotFoundError):
      prime_review(tmp_path / "delta", tmp_path)


class TestSummarizeReviewOutcome:
  """Tests for summarize_review_outcome — thin wrapper."""

  def test_delegates_to_spec_driver(self, tmp_path, monkeypatch):
    mock_result = MagicMock()
    mock_result.current_round = 1
    mock_result.judgment_status = ReviewStatus.APPROVED
    mock_result.blocking_total = 2
    mock_result.blocking_dispositioned = 2
    mock_result.non_blocking_total = 1
    mock_result.all_blocking_resolved = True
    mock_result.outcome_ready = True

    mock_fn = MagicMock(return_value=mock_result)
    monkeypatch.setattr("autobahn.api.functions._sd_summarize_review", mock_fn)

    result = summarize_review_outcome(tmp_path / "delta")

    mock_fn.assert_called_once_with(tmp_path / "delta")
    assert result is mock_result

  def test_propagates_findings_not_found(self, tmp_path, monkeypatch):
    mock_fn = MagicMock(side_effect=FindingsNotFoundError("no findings"))
    monkeypatch.setattr("autobahn.api.functions._sd_summarize_review", mock_fn)

    with pytest.raises(FindingsNotFoundError):
      summarize_review_outcome(tmp_path / "delta")


class TestDispositionFinding:
  """Tests for disposition_finding — thin wrapper."""

  def test_delegates_to_spec_driver(self, tmp_path, monkeypatch):
    mock_result = MagicMock()
    mock_result.delta_id = "DE-099"
    mock_result.finding_id = "R1-001"
    mock_result.action = FindingDispositionAction.FIX
    mock_result.previous_status = FindingStatus.OPEN
    mock_result.new_status = FindingStatus.RESOLVED

    mock_fn = MagicMock(return_value=mock_result)
    monkeypatch.setattr("autobahn.api.functions._sd_disposition_finding", mock_fn)

    result = disposition_finding(
      tmp_path / "delta",
      "R1-001",
      action=FindingDispositionAction.FIX,
      authority=DispositionAuthority.AGENT,
      resolved_at="abc123",
    )

    mock_fn.assert_called_once_with(
      tmp_path / "delta",
      "R1-001",
      action=FindingDispositionAction.FIX,
      authority=DispositionAuthority.AGENT,
      rationale=None,
      backlog_ref=None,
      resolved_at="abc123",
      superseded_by=None,
    )
    assert result is mock_result

  def test_default_authority_is_agent(self, tmp_path, monkeypatch):
    mock_fn = MagicMock()
    monkeypatch.setattr("autobahn.api.functions._sd_disposition_finding", mock_fn)

    disposition_finding(
      tmp_path / "delta",
      "R1-001",
      action=FindingDispositionAction.WAIVE,
      rationale="acceptable risk",
    )

    call_kwargs = mock_fn.call_args
    assert call_kwargs.kwargs["authority"] == DispositionAuthority.AGENT

  def test_propagates_finding_not_found(self, tmp_path, monkeypatch):
    mock_fn = MagicMock(
      side_effect=FindingNotFoundError("R1-999", ["R1-001", "R1-002"])
    )
    monkeypatch.setattr("autobahn.api.functions._sd_disposition_finding", mock_fn)

    with pytest.raises(FindingNotFoundError):
      disposition_finding(
        tmp_path / "delta",
        "R1-999",
        action=FindingDispositionAction.FIX,
      )
