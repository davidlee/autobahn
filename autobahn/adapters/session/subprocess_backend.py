"""Subprocess session backend.

Manages agent sessions as async subprocesses.

Design authority: DR-001 §7, DEC-006.
"""

from __future__ import annotations

import asyncio
import time
from datetime import UTC, datetime

from autobahn.models.enums import Role
from autobahn.models.runtime import (
  LaunchSpec,
  SessionHandle,
  SessionMetadata,
)


class SubprocessBackend:
  """Concrete SessionBackend using asyncio subprocesses."""

  def __init__(self) -> None:
    self._processes: dict[str, asyncio.subprocess.Process] = {}
    self._launch_times: dict[str, float] = {}

  def is_available(self) -> bool:
    """Subprocess backend is always available on POSIX systems."""
    return True

  async def create(
    self,
    session_id: str,
    launch: LaunchSpec,
  ) -> SessionHandle:
    """Spawn a subprocess from a LaunchSpec."""
    env = {**launch.env} if launch.env else None

    process = await asyncio.create_subprocess_exec(
      launch.command,
      *launch.args,
      cwd=launch.work_dir,
      env=env,
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.PIPE,
    )

    self._processes[session_id] = process
    self._launch_times[session_id] = time.monotonic()

    return SessionHandle(
      session_id=session_id,
      role=Role.OTHER,  # caller should set from context
      artifact_id="",  # caller should set from context
      backend_ref=f"pid:{process.pid}",
      launched_at=datetime.now(tz=UTC),
    )

  async def is_alive(self, handle: SessionHandle) -> bool:
    """Check if the subprocess is still running."""
    process = self._processes.get(handle.session_id)
    if process is None:
      return False
    return process.returncode is None

  async def terminate(self, handle: SessionHandle) -> None:
    """Terminate the subprocess (SIGTERM, then wait)."""
    process = self._processes.get(handle.session_id)
    if process is None:
      return
    if process.returncode is not None:
      return

    process.terminate()
    try:
      await asyncio.wait_for(process.wait(), timeout=5.0)
    except TimeoutError:
      process.kill()
      await process.wait()

  async def get_metadata(
    self,
    handle: SessionHandle,
  ) -> SessionMetadata:
    """Get observable state of the subprocess."""
    process = self._processes.get(handle.session_id)
    if process is None:
      return SessionMetadata(alive=False)

    alive = process.returncode is None
    launch_time = self._launch_times.get(handle.session_id)
    runtime = time.monotonic() - launch_time if launch_time else None

    return SessionMetadata(
      alive=alive,
      exit_code=process.returncode,
      runtime_seconds=runtime,
    )
