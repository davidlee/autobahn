"""Transition logic — compute next action from workflow context.

Design authority: DR-001 §8 (transition_from_handoff).
"""

from __future__ import annotations

from autobahn.models.enums import TERMINAL_WORKFLOW_STATES
from autobahn.models.errors import PreconditionError
from autobahn.models.runtime import TransitionPlan, WorkflowContext


def transition_from_handoff(context: WorkflowContext) -> TransitionPlan:
  """Compute next runtime action from handoff + state.

  Raises:
    PreconditionError: Workflow is in terminal state or handoff is missing.
  """
  current_status = context.state.workflow.status

  if current_status in TERMINAL_WORKFLOW_STATES:
    msg = f"Workflow is in terminal state: {current_status}"
    raise PreconditionError(msg)

  if context.handoff is None:
    msg = "No handoff file found — cannot compute transition"
    raise PreconditionError(msg)

  handoff = context.handoff

  return TransitionPlan(
    source_state=current_status,
    target_role=handoff.transition.to_role,
    activity=handoff.next_activity.kind,
    artifact_id=context.artifact_id,
    phase_id=handoff.phase.id,
    handoff_path="workflow/handoff.current.yaml",
    required_reading=list(handoff.required_reading),
    resume_session=None,
  )
