"""Supervisor — coordinates harness adapter and session backend.

Design authority: DR-001 §7 (composition).
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from autobahn.adapters.harness.protocol import HarnessAdapter
from autobahn.adapters.session.protocol import SessionBackend
from autobahn.models.runtime import (
  OperationResult,
  RuntimePolicy,
  SessionHandle,
  SessionMetadata,
  SessionOutcome,
  TransitionPlan,
  WorkflowContext,
)


class Supervisor:
  """Coordinates harness (what to run) and backend (how to run it)."""

  def __init__(
    self,
    harness: HarnessAdapter,
    backend: SessionBackend,
  ) -> None:
    self.harness = harness
    self.backend = backend

  async def spawn(
    self,
    context: WorkflowContext,
    plan: TransitionPlan,
    policy: RuntimePolicy,
  ) -> OperationResult[SessionHandle]:
    """Launch an agent session."""
    launch = self.harness.launch_spec(
      work_dir=policy.work_dir,
      plan=plan,
      policy=policy,
    )
    session_id = f"{context.artifact_id}-{plan.target_role}"

    try:
      handle = await self.backend.create(session_id, launch)
    except Exception as exc:  # noqa: BLE001
      return OperationResult(
        success=False,
        error=f"Failed to create session: {exc}",
      )

    return OperationResult(success=True, value=handle)

  async def observe(
    self,
    handle: SessionHandle,
    *,
    poll_interval: float = 5.0,
  ) -> AsyncIterator[SessionMetadata]:
    """Yield session metadata until session ends."""
    while True:
      meta = await self.backend.get_metadata(handle)
      yield meta
      if not meta.alive:
        return
      await asyncio.sleep(poll_interval)

  async def terminate(
    self,
    handle: SessionHandle,
  ) -> OperationResult[SessionOutcome]:
    """Terminate a session and return its outcome."""
    meta = await self.backend.get_metadata(handle)
    if not meta.alive:
      exit_code = meta.exit_code if meta.exit_code is not None else -1
      outcome = self.harness.parse_exit(exit_code)
      return OperationResult(
        success=False,
        value=outcome,
        error="Session already dead",
      )

    await self.backend.terminate(handle)
    meta = await self.backend.get_metadata(handle)
    exit_code = meta.exit_code if meta.exit_code is not None else -1
    outcome = self.harness.parse_exit(exit_code)
    return OperationResult(success=True, value=outcome)
