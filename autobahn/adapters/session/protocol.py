"""Session backend protocol.

Design authority: DR-001 §7, DEC-006, DEC-012.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from autobahn.models.runtime import (
  LaunchSpec,
  SessionHandle,
  SessionMetadata,
)


@runtime_checkable
class SessionBackend(Protocol):
  """v1 session backend — spawn/observe/terminate only."""

  def is_available(self) -> bool:
    """Check if this backend's prerequisites are met.

    Used by check_prerequisites().
    """
    ...

  async def create(
    self,
    session_id: str,
    launch: LaunchSpec,
  ) -> SessionHandle: ...

  async def is_alive(self, handle: SessionHandle) -> bool: ...

  async def terminate(self, handle: SessionHandle) -> None: ...

  async def get_metadata(
    self,
    handle: SessionHandle,
  ) -> SessionMetadata: ...
