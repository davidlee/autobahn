"""Public API function implementations.

Design authority: DR-001 §8.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

from autobahn.adapters.harness.protocol import HarnessAdapter
from autobahn.adapters.session.protocol import SessionBackend
from autobahn.artifacts.loader import load_workflow_dir
from autobahn.models.errors import PreconditionError
from autobahn.models.runtime import (
  OperationResult,
  RuntimePolicy,
  SessionHandle,
  SessionMetadata,
  SessionOutcome,
  TransitionPlan,
  WorkflowContext,
)
from autobahn.runtime.reconcile import ReconciliationReport
from autobahn.runtime.reconcile import reconcile as _reconcile_impl
from autobahn.runtime.supervisor import Supervisor
from autobahn.runtime.transition import (
  transition_from_handoff as _transition_impl,
)


def check_prerequisites(
  policy: RuntimePolicy,
  *,
  harness: HarnessAdapter,
  backend: SessionBackend,
) -> list[PreconditionError]:
  """Validate runtime environment before orchestration.

  Returns empty list if all checks pass.
  """
  errors: list[PreconditionError] = []

  if not harness.is_available(policy):
    errors.append(PreconditionError(f"Harness '{harness.name}' is not available"))

  if not backend.is_available():
    errors.append(PreconditionError("Session backend is not available"))

  if not policy.work_dir.exists():
    errors.append(
      PreconditionError(f"Work directory does not exist: {policy.work_dir}")
    )

  return errors


def load_context(
  artifact_dir: Path,
  *,
  workflow_dir: str = "workflow",
) -> WorkflowContext:
  """Read all workflow files and assemble typed context.

  Missing optional files result in None fields, not errors.

  Raises:
    ArtifactParseError: YAML is malformed or unreadable.
    ArtifactContractError: YAML violates schema contract.
  """
  return load_workflow_dir(artifact_dir / workflow_dir)


def transition_from_handoff(
  context: WorkflowContext,
) -> TransitionPlan:
  """Compute next runtime action from handoff + state.

  Raises:
    PreconditionError: Workflow in terminal state or missing handoff.
  """
  return _transition_impl(context)


async def spawn_role_session(
  context: WorkflowContext,
  plan: TransitionPlan,
  *,
  policy: RuntimePolicy,
  harness: HarnessAdapter,
  backend: SessionBackend,
) -> OperationResult[SessionHandle]:
  """Launch agent session.

  Returns failed result if session fails to start.
  """
  supervisor = Supervisor(harness, backend)
  return await supervisor.spawn(context, plan, policy)


async def observe_session(
  handle: SessionHandle,
  *,
  backend: SessionBackend,
  poll_interval: float = 5.0,
) -> AsyncIterator[SessionMetadata]:
  """Yield session metadata until session ends."""
  supervisor = Supervisor.__new__(Supervisor)
  supervisor.backend = backend
  async for meta in supervisor.observe(handle, poll_interval=poll_interval):
    yield meta


async def terminate_session(
  handle: SessionHandle,
  *,
  harness: HarnessAdapter,
  backend: SessionBackend,
) -> OperationResult[SessionOutcome]:
  """Signal stop, return final outcome."""
  supervisor = Supervisor(harness, backend)
  return await supervisor.terminate(handle)


async def reconcile(
  context: WorkflowContext,
  *,
  policy: RuntimePolicy,
  backend: SessionBackend,
  active_handles: list[SessionHandle] | None = None,
) -> OperationResult[ReconciliationReport]:
  """Compare artifact state vs live sessions, report drift.

  Does not auto-repair. Returns diagnosis.
  """
  return await _reconcile_impl(
    context,
    policy=policy,
    backend=backend,
    active_handles=active_handles,
  )
