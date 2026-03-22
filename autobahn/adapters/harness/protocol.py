"""Harness adapter protocol and extension seams.

Design authority: DR-001 §7, DEC-005, DEC-016.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from autobahn.models.enums import Role
from autobahn.models.runtime import (
  LaunchSpec,
  RuntimePolicy,
  SessionOutcome,
  TransitionPlan,
  WorkflowContext,
)


@runtime_checkable
class HarnessAdapter(Protocol):
  """Baseline harness protocol — what every harness must implement."""

  @property
  def name(self) -> str:
    """Adapter identifier, e.g. 'claude_code', 'pi_mono'."""
    ...

  def is_available(self, policy: RuntimePolicy) -> bool:
    """Check if this harness can run (executable exists, etc.).

    Used by check_prerequisites().
    """
    ...

  def launch_spec(
    self,
    *,
    work_dir: Path,
    plan: TransitionPlan,
    policy: RuntimePolicy,
  ) -> LaunchSpec:
    """Produce command, args, env to start an agent.

    Harness builds launch args from plan's structured references
    (artifact_id, phase_id, handoff_path).
    Policy.harness_executable overrides adapter's default command.
    """
    ...

  def parse_exit(self, exit_code: int) -> SessionOutcome:
    """Interpret agent exit into structured outcome."""
    ...


# --- Extension seams (illustrative — not locked) ---


@runtime_checkable
class ContextEngineerable(Protocol):
  """Harness supports structured context injection."""

  def context_sections(
    self,
    context: WorkflowContext,
  ) -> dict[str, str]: ...


@runtime_checkable
class SubAgentConfigurable(Protocol):
  """Harness supports declaring sub-agent topology."""

  def sub_agent_spec(
    self,
    roles: list[Role],
    policy: RuntimePolicy,
  ) -> dict[str, LaunchSpec]: ...
