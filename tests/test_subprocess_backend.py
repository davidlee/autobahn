"""Tests for subprocess session backend."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from autobahn.adapters.session.protocol import SessionBackend
from autobahn.adapters.session.subprocess_backend import SubprocessBackend
from autobahn.models.enums import Role
from autobahn.models.runtime import LaunchSpec, SessionHandle


def _launch_spec(
  command: str = sys.executable,
  args: list[str] | None = None,
) -> LaunchSpec:
  return LaunchSpec(
    command=command,
    args=args or ["-c", "print('hello')"],
    work_dir=Path("/tmp"),
  )


class TestSubprocessBackend:
  def test_satisfies_protocol(self):
    backend = SubprocessBackend()
    assert isinstance(backend, SessionBackend)

  def test_is_available(self):
    assert SubprocessBackend().is_available() is True

  @pytest.mark.asyncio
  async def test_create_returns_handle(self):
    backend = SubprocessBackend()
    handle = await backend.create("sess-001", _launch_spec())
    assert handle.session_id == "sess-001"
    assert handle.backend_ref.startswith("pid:")
    # Wait for completion to avoid zombie
    await backend._processes["sess-001"].wait()

  @pytest.mark.asyncio
  async def test_is_alive_running(self):
    backend = SubprocessBackend()
    spec = _launch_spec(args=["-c", "import time; time.sleep(10)"])
    handle = await backend.create("sess-alive", spec)
    assert await backend.is_alive(handle) is True
    await backend.terminate(handle)

  @pytest.mark.asyncio
  async def test_is_alive_completed(self):
    backend = SubprocessBackend()
    handle = await backend.create("sess-done", _launch_spec())
    await backend._processes["sess-done"].wait()
    assert await backend.is_alive(handle) is False

  @pytest.mark.asyncio
  async def test_terminate(self):
    backend = SubprocessBackend()
    spec = _launch_spec(args=["-c", "import time; time.sleep(10)"])
    handle = await backend.create("sess-term", spec)
    assert await backend.is_alive(handle) is True
    await backend.terminate(handle)
    assert await backend.is_alive(handle) is False

  @pytest.mark.asyncio
  async def test_terminate_already_dead(self):
    backend = SubprocessBackend()
    handle = await backend.create("sess-dead", _launch_spec())
    await backend._processes["sess-dead"].wait()
    # Should not raise
    await backend.terminate(handle)

  @pytest.mark.asyncio
  async def test_terminate_unknown_session(self):
    backend = SubprocessBackend()
    handle = SessionHandle(
      session_id="nonexistent",
      role=Role.OTHER,
      artifact_id="",
      backend_ref="pid:0",
      launched_at=datetime.now(tz=UTC),
    )
    # Should not raise
    await backend.terminate(handle)

  @pytest.mark.asyncio
  async def test_get_metadata_alive(self):
    backend = SubprocessBackend()
    spec = _launch_spec(args=["-c", "import time; time.sleep(10)"])
    handle = await backend.create("sess-meta", spec)
    meta = await backend.get_metadata(handle)
    assert meta.alive is True
    assert meta.exit_code is None
    assert meta.runtime_seconds is not None
    await backend.terminate(handle)

  @pytest.mark.asyncio
  async def test_get_metadata_completed(self):
    backend = SubprocessBackend()
    handle = await backend.create("sess-meta-done", _launch_spec())
    await backend._processes["sess-meta-done"].wait()
    meta = await backend.get_metadata(handle)
    assert meta.alive is False
    assert meta.exit_code == 0

  @pytest.mark.asyncio
  async def test_get_metadata_unknown(self):
    backend = SubprocessBackend()
    handle = SessionHandle(
      session_id="unknown",
      role=Role.OTHER,
      artifact_id="",
      backend_ref="pid:0",
      launched_at=datetime.now(tz=UTC),
    )
    meta = await backend.get_metadata(handle)
    assert meta.alive is False

  @pytest.mark.asyncio
  async def test_create_inherits_parent_env_with_extras(self):
    """F-003 regression: env vars should augment, not replace, parent env."""
    backend = SubprocessBackend()
    spec = LaunchSpec(
      command=sys.executable,
      args=["-c", "import os; assert 'PATH' in os.environ; print('ok')"],
      env={"AUTOBAHN_TEST": "1"},
      work_dir=Path("/tmp"),
    )
    await backend.create("sess-env", spec)
    proc = backend._processes["sess-env"]
    await proc.wait()
    assert proc.returncode == 0
