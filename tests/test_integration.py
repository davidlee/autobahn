"""End-to-end integration test (VA-004).

Exercises the full session lifecycle with a real subprocess:
load_context -> transition_from_handoff -> spawn -> observe -> reconcile.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

from autobahn.adapters.session.subprocess_backend import SubprocessBackend
from autobahn.api import (
  check_prerequisites,
  load_context,
  observe_session,
  reconcile,
  spawn_role_session,
  transition_from_handoff,
)
from autobahn.models.runtime import LaunchSpec, RuntimePolicy, SessionOutcome

FIXTURES = Path(__file__).parent / "fixtures" / "workflow"


class _TestHarness:
  """Harness adapter that launches a Python one-liner instead of claude."""

  @property
  def name(self) -> str:
    return "test_harness"

  def is_available(self, policy):
    return True

  def launch_spec(self, *, work_dir, plan, policy):
    return LaunchSpec(
      command=sys.executable,
      args=["-c", "print('integration test complete')"],
      work_dir=work_dir,
    )

  def parse_exit(self, exit_code):
    return SessionOutcome(
      exit_code=exit_code,
      interpretation="completed" if exit_code == 0 else "failed",
      artifacts_modified=exit_code == 0,
    )


def _setup_workflow_dir(tmp_path: Path) -> Path:
  """Copy fixture workflow files into a proper artifact dir structure."""
  artifact_dir = tmp_path / "artifact"
  workflow_dir = artifact_dir / "workflow"
  workflow_dir.mkdir(parents=True)
  for f in FIXTURES.iterdir():
    if f.is_file():
      shutil.copy(f, workflow_dir / f.name)
  return artifact_dir


class TestFullLifecycle:
  """Integration test: full session lifecycle with real subprocess."""

  @pytest.mark.asyncio
  async def test_load_transition_spawn_observe_reconcile(self, tmp_path):
    artifact_dir = _setup_workflow_dir(tmp_path)
    backend = SubprocessBackend()
    harness = _TestHarness()
    policy = RuntimePolicy(
      harness="test_harness",
      session_backend="subprocess",
      work_dir=artifact_dir,
    )

    # 1. Preflight
    errors = check_prerequisites(policy, harness=harness, backend=backend)
    assert errors == []

    # 2. Load context
    ctx = load_context(artifact_dir)
    assert ctx.artifact_id == "DE-099"
    assert ctx.handoff is not None

    # 3. Compute transition
    plan = transition_from_handoff(ctx)
    assert plan.artifact_id == "DE-099"
    assert plan.phase_id == "IP-099.PHASE-01"

    # 4. Spawn real subprocess
    result = await spawn_role_session(
      ctx,
      plan,
      policy=policy,
      harness=harness,
      backend=backend,
    )
    assert result.success is True
    handle = result.value
    assert handle is not None
    assert handle.backend_ref.startswith("pid:")

    # 5. Observe until completion
    observations = []
    async for meta in observe_session(
      handle,
      backend=backend,
      poll_interval=0.05,
    ):
      observations.append(meta)

    # Process should have completed
    assert len(observations) >= 1
    assert observations[-1].alive is False
    assert observations[-1].exit_code == 0

    # 6. Reconcile
    report = await reconcile(
      ctx,
      policy=policy,
      backend=backend,
      active_handles=[handle],
    )
    assert report.success is True
    assert report.value is not None
    # Session is dead but workflow is still implementing — expected drift
    drift_kinds = [d.kind for d in report.value.drift_items]
    assert "SESSION_DIED_UNEXPECTEDLY" in drift_kinds
