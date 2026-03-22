"""Tests for Claude Code harness adapter."""

from __future__ import annotations

from pathlib import Path

from autobahn.adapters.harness.claude_code import ClaudeCodeAdapter
from autobahn.adapters.harness.protocol import HarnessAdapter
from autobahn.models.enums import NextActivityKind, Role, WorkflowStatus
from autobahn.models.runtime import RuntimePolicy, TransitionPlan


def _policy(*, executable: str | None = None) -> RuntimePolicy:
  return RuntimePolicy(
    harness="claude_code",
    session_backend="subprocess",
    harness_executable=executable,
    work_dir=Path("/tmp/work"),
  )


def _plan() -> TransitionPlan:
  return TransitionPlan(
    source_state=WorkflowStatus.IMPLEMENTING,
    target_role=Role.IMPLEMENTER,
    activity=NextActivityKind.IMPLEMENTATION,
    artifact_id="DE-099",
    phase_id="IP-099.PHASE-01",
    handoff_path="workflow/handoff.current.yaml",
    required_reading=["DE-099.md"],
  )


class TestClaudeCodeAdapter:
  def test_satisfies_protocol(self):
    adapter = ClaudeCodeAdapter()
    assert isinstance(adapter, HarnessAdapter)

  def test_name(self):
    assert ClaudeCodeAdapter().name == "claude_code"

  def test_launch_spec_default_command(self):
    adapter = ClaudeCodeAdapter()
    spec = adapter.launch_spec(
      work_dir=Path("/tmp/work"),
      plan=_plan(),
      policy=_policy(),
    )
    assert spec.command == "claude"
    assert "-p" in spec.args
    assert "--no-input" in spec.args
    assert "DE-099" in spec.args[spec.args.index("-p") + 1]
    assert spec.work_dir == Path("/tmp/work")

  def test_launch_spec_custom_executable(self):
    adapter = ClaudeCodeAdapter()
    spec = adapter.launch_spec(
      work_dir=Path("/tmp/work"),
      plan=_plan(),
      policy=_policy(executable="/usr/bin/jailed-claude"),
    )
    assert spec.command == "/usr/bin/jailed-claude"

  def test_launch_spec_timeout_env(self):
    adapter = ClaudeCodeAdapter()
    policy = RuntimePolicy(
      harness="claude_code",
      session_backend="subprocess",
      work_dir=Path("/tmp/work"),
      timeout_seconds=300,
    )
    spec = adapter.launch_spec(
      work_dir=Path("/tmp/work"),
      plan=_plan(),
      policy=policy,
    )
    assert spec.env.get("CLAUDE_TIMEOUT") == "300"

  def test_parse_exit_success(self):
    outcome = ClaudeCodeAdapter().parse_exit(0)
    assert outcome.exit_code == 0
    assert outcome.artifacts_modified is True

  def test_parse_exit_error(self):
    outcome = ClaudeCodeAdapter().parse_exit(1)
    assert outcome.exit_code == 1
    assert "error" in outcome.interpretation

  def test_parse_exit_unexpected(self):
    outcome = ClaudeCodeAdapter().parse_exit(137)
    assert outcome.exit_code == 137
    assert "unexpected" in outcome.interpretation

  def test_is_available_with_real_command(self):
    # 'echo' is always available on POSIX
    adapter = ClaudeCodeAdapter()
    policy = _policy(executable="echo")
    assert adapter.is_available(policy) is True

  def test_is_available_missing_command(self):
    adapter = ClaudeCodeAdapter()
    policy = _policy(executable="nonexistent_binary_xyz_123")
    assert adapter.is_available(policy) is False
