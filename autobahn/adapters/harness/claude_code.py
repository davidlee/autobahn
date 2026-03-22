"""Claude Code harness adapter.

Builds launch commands for Claude Code CLI agent sessions.

Design authority: DR-001 §7 (harness adapter baseline).
"""

from __future__ import annotations

import shutil
from pathlib import Path

from autobahn.models.runtime import (
  LaunchSpec,
  RuntimePolicy,
  SessionOutcome,
  TransitionPlan,
)


class ClaudeCodeAdapter:
  """Concrete HarnessAdapter for Claude Code CLI."""

  _DEFAULT_COMMAND = "claude"

  @property
  def name(self) -> str:
    return "claude_code"

  def is_available(self, policy: RuntimePolicy) -> bool:
    """Check if claude executable is on PATH or at policy.harness_executable."""
    executable = policy.harness_executable or self._DEFAULT_COMMAND
    return shutil.which(executable) is not None

  def launch_spec(
    self,
    *,
    work_dir: Path,
    plan: TransitionPlan,
    policy: RuntimePolicy,
  ) -> LaunchSpec:
    """Build claude CLI command from transition plan."""
    executable = policy.harness_executable or self._DEFAULT_COMMAND

    prompt = f"resume {plan.artifact_id} phase {plan.phase_id}"

    args = ["-p", prompt, "--no-input"]

    env: dict[str, str] = {}
    if policy.timeout_seconds is not None:
      env["CLAUDE_TIMEOUT"] = str(policy.timeout_seconds)

    return LaunchSpec(
      command=executable,
      args=args,
      env=env,
      work_dir=work_dir,
    )

  def parse_exit(self, exit_code: int) -> SessionOutcome:
    """Interpret Claude Code exit codes."""
    if exit_code == 0:
      return SessionOutcome(
        exit_code=0,
        interpretation="completed normally",
        artifacts_modified=True,
      )
    if exit_code == 1:
      return SessionOutcome(
        exit_code=1,
        interpretation="error during execution",
        artifacts_modified=None,
      )
    return SessionOutcome(
      exit_code=exit_code,
      interpretation=f"unexpected exit code {exit_code}",
      artifacts_modified=None,
    )
