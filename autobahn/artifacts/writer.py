"""Artifact writer — sessions.yaml persistence.

Pure function with atomic rename. No locking in v1 (DEC-022).
Platform assumption: POSIX (same-filesystem atomic rename).

Design authority: DR-002 §4.5.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from autobahn.artifacts.schema import write_version
from autobahn.models.artifacts import SessionsFile

_SESSIONS_SCHEMA = "supekku.workflow.sessions"


def write_sessions_file(path: Path, sessions: SessionsFile) -> None:
  """Write sessions.yaml atomically.

  Uses temp file + os.rename for crash safety.
  """
  data = {
    "schema": _SESSIONS_SCHEMA,
    "version": write_version(_SESSIONS_SCHEMA),
    "artifact": sessions.artifact.model_dump(mode="json"),
    "sessions": [s.model_dump(mode="json") for s in sessions.sessions],
  }
  tmp = path.with_suffix(".tmp")
  tmp.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
  tmp.rename(path)
