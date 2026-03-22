"""Public API function implementations.

Design authority: DR-001 §8, DR-002 §4.6/§4.8, DR-004 §4.5.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from pathlib import Path

from spec_driver.orchestration import (
  DispositionAuthority,
  DispositionResult,
  FindingDispositionAction,
  PrimeResult,
  ReviewSummary,
)
from spec_driver.orchestration import (
  disposition_finding as _sd_disposition_finding,
)
from spec_driver.orchestration import (
  prime_review as _sd_prime_review,
)
from spec_driver.orchestration import (
  summarize_review as _sd_summarize_review,
)

from autobahn.adapters.harness.protocol import HarnessAdapter
from autobahn.adapters.session.protocol import SessionBackend
from autobahn.artifacts.loader import load_workflow_dir
from autobahn.artifacts.writer import write_sessions_file
from autobahn.models.artifacts import ArtifactBlock, SessionEntry, SessionsFile
from autobahn.models.enums import SessionStatus
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

logger = logging.getLogger(__name__)


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
  """Launch agent session and persist to sessions.yaml.

  Returns failed result if session fails to start.
  Persistence failure yields success with warning (DEC-026).
  """
  supervisor = Supervisor(harness, backend)
  result = await supervisor.spawn(context, plan, policy)
  if result.success and result.value:
    _persist_new_session(context, result.value, harness.name, result)
  return result


def _persist_new_session(
  context: WorkflowContext,
  handle: SessionHandle,
  harness_name: str,
  result: OperationResult[SessionHandle],
) -> None:
  """Write session entry to sessions.yaml. Warns on failure."""
  sessions_path = context.artifact_dir / "sessions.yaml"
  try:
    if context.sessions is not None:
      sf = context.sessions
    else:
      sf = SessionsFile(
        artifact=ArtifactBlock(
          id=context.artifact_id,
          kind=context.artifact_kind,
        ),
      )
    role_key = handle.role.value
    existing = sf.sessions.get(role_key)
    if existing is not None and existing.status == SessionStatus.ACTIVE:
      logger.warning(
        "Overwriting active session for role %s (session_name=%s)",
        role_key,
        existing.session_name,
      )
    entry = SessionEntry(
      session_name=handle.session_id,
      status=SessionStatus.ACTIVE,
      last_seen=handle.launched_at,
      backend=harness_name,
      launched_at=handle.launched_at,
    )
    sf = sf.model_copy(
      update={
        "sessions": {**sf.sessions, role_key: entry},
      }
    )
    write_sessions_file(sessions_path, sf)
  except Exception:  # noqa: BLE001
    msg = f"Failed to persist session {handle.session_id} to sessions.yaml"
    logger.warning(msg, exc_info=True)
    result.warnings.append(msg)


async def observe_session(
  handle: SessionHandle,
  *,
  backend: SessionBackend,
  poll_interval: float = 5.0,
) -> AsyncIterator[SessionMetadata]:
  """Yield session metadata until session ends."""
  while True:
    meta = await backend.get_metadata(handle)
    yield meta
    if not meta.alive:
      return
    await asyncio.sleep(poll_interval)


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


_DEAD_DRIFT_KINDS = frozenset(
  {
    "SESSION_DIED_UNEXPECTEDLY",
    "SESSION_OUTLIVED_WORKFLOW",
    "ORPHANED_SESSION",
  }
)


def persist_session_statuses(
  context: WorkflowContext,
  report: ReconciliationReport,
) -> None:
  """Update sessions.yaml to reflect reconciliation findings.

  Caller invokes this after inspecting a ReconciliationReport.
  Marks sessions as dead based on drift items — does not re-probe
  liveness (reconcile already did that).

  Sync function: reads sessions.yaml, applies status changes, writes.
  Design authority: DR-002 §4.8, DEC-025.
  """
  sessions_path = context.artifact_dir / "sessions.yaml"
  if context.sessions is None:
    return

  dead_ids = {
    item.session_id
    for item in report.drift_items
    if item.kind in _DEAD_DRIFT_KINDS and item.session_id is not None
  }
  if not dead_ids:
    return

  changed = False
  new_sessions: dict[str, SessionEntry] = {}
  for role, entry in context.sessions.sessions.items():
    if entry.session_name in dead_ids and entry.status == SessionStatus.ACTIVE:
      new_sessions[role] = entry.model_copy(update={"status": SessionStatus.DEAD})
      changed = True
    else:
      new_sessions[role] = entry

  if changed:
    sf = context.sessions.model_copy(update={"sessions": new_sessions})
    write_sessions_file(sessions_path, sf)


# --- Review operations (DR-004, ADR-002) ---


def prime_review(
  delta_dir: Path,
  repo_root: Path,
) -> PrimeResult:
  """Prime a review via spec-driver.

  Evaluates staleness, builds/refreshes review index, writes
  review-index.yaml + review-bootstrap.md, transitions judgment
  to in_progress.

  Design authority: DR-004 §4.5, DEC-004-002.

  Raises:
    spec_driver.orchestration.StateNotFoundError
    spec_driver.orchestration.StateValidationError
    spec_driver.orchestration.ReviewIndexValidationError
  """
  return _sd_prime_review(delta_dir, repo_root)


def summarize_review_outcome(
  delta_dir: Path,
) -> ReviewSummary:
  """Query review findings and return outcome digest.

  Design authority: DR-004 §4.5, DEC-004-003.

  Raises:
    spec_driver.orchestration.FindingsNotFoundError
    spec_driver.orchestration.FindingsVersionError
    spec_driver.orchestration.ReviewIndexNotFoundError
  """
  return _sd_summarize_review(delta_dir)


def disposition_finding(
  delta_dir: Path,
  finding_id: str,
  *,
  action: FindingDispositionAction,
  authority: DispositionAuthority = DispositionAuthority.AGENT,
  rationale: str | None = None,
  backlog_ref: str | None = None,
  resolved_at: str | None = None,
  superseded_by: str | None = None,
) -> DispositionResult:
  """Disposition a review finding.

  Constraint validation (rationale for waive, backlog_ref for
  blocking defer, etc.) is enforced by spec-driver's operation.

  Design authority: DR-004 §4.5, DEC-004-004, DEC-004-011.

  Raises:
    spec_driver.orchestration.FindingsNotFoundError
    spec_driver.orchestration.FindingsVersionError
    spec_driver.orchestration.FindingNotFoundError
    spec_driver.orchestration.DispositionValidationError
  """
  return _sd_disposition_finding(
    delta_dir,
    finding_id,
    action=action,
    authority=authority,
    rationale=rationale,
    backlog_ref=backlog_ref,
    resolved_at=resolved_at,
    superseded_by=superseded_by,
  )
