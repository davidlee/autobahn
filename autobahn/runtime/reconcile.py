"""Reconciliation — compare artifact state vs live sessions.

Re-reads state.yaml to detect external workflow changes (DEC-017).

Design authority: DR-001 §8 (reconcile).
"""

from __future__ import annotations

from pydantic import BaseModel

from autobahn.adapters.session.protocol import SessionBackend
from autobahn.artifacts.loader import load_workflow_dir
from autobahn.models.enums import (
  TERMINAL_WORKFLOW_STATES,
  SessionStatus,
  WorkflowStatus,
)
from autobahn.models.runtime import (
  OperationResult,
  RuntimePolicy,
  SessionHandle,
  WorkflowContext,
)


class DriftItem(BaseModel):
  """A single detected divergence between artifact and session state."""

  kind: str
  description: str
  session_id: str | None = None


class ReconciliationReport(BaseModel):
  """Diagnosis of artifact-vs-session divergence."""

  artifact_id: str
  workflow_status: WorkflowStatus
  drift_items: list[DriftItem] = []
  has_drift: bool = False


async def reconcile(
  context: WorkflowContext,
  *,
  policy: RuntimePolicy,
  backend: SessionBackend,
  active_handles: list[SessionHandle] | None = None,
) -> OperationResult[ReconciliationReport]:
  """Compare artifact state vs live sessions, report drift.

  Re-reads state.yaml for fresh workflow status (DEC-017).
  Does not auto-repair — returns diagnosis.
  """
  # Re-read artifact state for freshness
  fresh_context = load_workflow_dir(context.artifact_dir)
  fresh_status = fresh_context.state.workflow.status

  drift_items: list[DriftItem] = []

  # Check: workflow state changed externally
  if fresh_status != context.state.workflow.status:
    drift_items.append(
      DriftItem(
        kind="WORKFLOW_STATE_CHANGED",
        description=(
          f"Workflow status changed from {context.state.workflow.status} "
          f"to {fresh_status} externally"
        ),
      )
    )

  # Check active handles against workflow state
  if active_handles:
    for handle in active_handles:
      alive = await backend.is_alive(handle)

      if alive and fresh_status in TERMINAL_WORKFLOW_STATES:
        drift_items.append(
          DriftItem(
            kind="SESSION_OUTLIVED_WORKFLOW",
            description=(
              f"Session {handle.session_id} still alive but "
              f"workflow is in terminal state {fresh_status}"
            ),
            session_id=handle.session_id,
          )
        )

      if not alive and fresh_status not in TERMINAL_WORKFLOW_STATES:
        drift_items.append(
          DriftItem(
            kind="SESSION_DIED_UNEXPECTEDLY",
            description=(
              f"Session {handle.session_id} is dead but "
              f"workflow is still {fresh_status}"
            ),
            session_id=handle.session_id,
          )
        )

  # Check sessions.yaml consistency
  if fresh_context.sessions:
    for entry in fresh_context.sessions.sessions:
      if entry.status == SessionStatus.ACTIVE:
        # If we have handles, check if the active session matches
        handle_ids = {h.session_id for h in (active_handles or [])}
        if entry.session_id not in handle_ids:
          drift_items.append(
            DriftItem(
              kind="ORPHANED_SESSION",
              description=(
                f"sessions.yaml lists {entry.session_id} as active "
                f"but no matching live handle"
              ),
              session_id=entry.session_id,
            )
          )

  report = ReconciliationReport(
    artifact_id=fresh_context.artifact_id,
    workflow_status=fresh_status,
    drift_items=drift_items,
    has_drift=len(drift_items) > 0,
  )

  return OperationResult(success=True, value=report)
