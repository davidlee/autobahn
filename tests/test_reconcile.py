"""Tests for reconciliation logic."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

from autobahn.api import load_context, reconcile
from autobahn.models.enums import Role
from autobahn.models.runtime import (
  RuntimePolicy,
  SessionHandle,
  SessionMetadata,
)

FIXTURES = Path(__file__).parent / "fixtures" / "workflow"


class MockBackendForReconcile:
  def __init__(self, *, alive: bool = True) -> None:
    self._alive = alive

  def is_available(self) -> bool:
    return True

  async def is_alive(self, handle) -> bool:
    return self._alive

  async def get_metadata(self, handle) -> SessionMetadata:
    return SessionMetadata(alive=self._alive)


def _handle(session_id: str = "DE-099-implementer") -> SessionHandle:
  return SessionHandle(
    session_id=session_id,
    role=Role.IMPLEMENTER,
    artifact_id="DE-099",
    backend_ref="mock:1",
    launched_at=datetime.now(tz=UTC),
  )


def _policy() -> RuntimePolicy:
  return RuntimePolicy(
    harness="mock",
    session_backend="mock",
    work_dir=Path("/tmp"),
  )


def _make_workflow_dir(tmp_path: Path, **state_overrides) -> Path:
  """Copy fixtures and optionally override state.yaml fields."""
  for f in FIXTURES.iterdir():
    if f.is_file():
      shutil.copy(f, tmp_path / f.name)
  if state_overrides:
    state_path = tmp_path / "state.yaml"
    data = yaml.safe_load(state_path.read_text())
    for key, value in state_overrides.items():
      keys = key.split(".")
      target = data
      for k in keys[:-1]:
        target = target[k]
      target[keys[-1]] = value
    state_path.write_text(yaml.dump(data))
  return tmp_path


class TestReconcile:
  @pytest.mark.asyncio
  async def test_no_drift(self, tmp_path):
    _make_workflow_dir(tmp_path)
    # Remove sessions.yaml so no orphan detection
    (tmp_path / "sessions.yaml").unlink()
    ctx = load_context(tmp_path.parent, workflow_dir=tmp_path.name)
    result = await reconcile(
      ctx,
      policy=_policy(),
      backend=MockBackendForReconcile(),
    )
    assert result.success is True
    assert result.value is not None
    assert result.value.has_drift is False

  @pytest.mark.asyncio
  async def test_workflow_state_changed(self, tmp_path):
    _make_workflow_dir(tmp_path)
    ctx = load_context(tmp_path.parent, workflow_dir=tmp_path.name)

    # Externally change state.yaml
    state_path = tmp_path / "state.yaml"
    data = yaml.safe_load(state_path.read_text())
    data["workflow"]["status"] = "approved"
    state_path.write_text(yaml.dump(data))

    result = await reconcile(
      ctx,
      policy=_policy(),
      backend=MockBackendForReconcile(),
    )
    assert result.value.has_drift is True
    kinds = [d.kind for d in result.value.drift_items]
    assert "WORKFLOW_STATE_CHANGED" in kinds

  @pytest.mark.asyncio
  async def test_session_outlived_workflow(self, tmp_path):
    _make_workflow_dir(tmp_path, **{"workflow.status": "approved"})
    ctx = load_context(tmp_path.parent, workflow_dir=tmp_path.name)

    result = await reconcile(
      ctx,
      policy=_policy(),
      backend=MockBackendForReconcile(alive=True),
      active_handles=[_handle()],
    )
    assert result.value.has_drift is True
    kinds = [d.kind for d in result.value.drift_items]
    assert "SESSION_OUTLIVED_WORKFLOW" in kinds

  @pytest.mark.asyncio
  async def test_session_died_unexpectedly(self, tmp_path):
    _make_workflow_dir(tmp_path)
    ctx = load_context(tmp_path.parent, workflow_dir=tmp_path.name)

    result = await reconcile(
      ctx,
      policy=_policy(),
      backend=MockBackendForReconcile(alive=False),
      active_handles=[_handle()],
    )
    assert result.value.has_drift is True
    kinds = [d.kind for d in result.value.drift_items]
    assert "SESSION_DIED_UNEXPECTEDLY" in kinds

  @pytest.mark.asyncio
  async def test_orphaned_session(self, tmp_path):
    _make_workflow_dir(tmp_path)
    ctx = load_context(tmp_path.parent, workflow_dir=tmp_path.name)
    # sessions.yaml has "sess-001" active, but we pass no handles
    result = await reconcile(
      ctx,
      policy=_policy(),
      backend=MockBackendForReconcile(),
      active_handles=[],
    )
    assert result.value.has_drift is True
    kinds = [d.kind for d in result.value.drift_items]
    assert "ORPHANED_SESSION" in kinds
