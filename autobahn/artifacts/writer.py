"""Artifact writer — sessions.yaml persistence.

Pure function with atomic rename. No locking in v1 (DEC-022).
Platform assumption: POSIX (same-filesystem atomic rename).

Design authority: DR-002 §4.5, DR-003 §4.3.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from autobahn.artifacts.schema import write_version
from autobahn.models.artifacts import SessionEntry, SessionsFile

_SESSIONS_SCHEMA = "supekku.workflow.sessions"

# Fields required by spec-driver's MetadataValidator — must be present even
# when None. sandbox is canonical but optional (not required-present in output).
# NB: exclude_none=True drops all None values including autobahn-extra; if a
# future extra field needs explicit null semantics, refactor to field-level
# exclusion.
_REQUIRED_SESSION_FIELDS = {"session_name", "status", "last_seen"}


def _serialize_session_entry(entry: SessionEntry) -> dict:
  """Serialize a SessionEntry, preserving canonical nulls."""
  data = entry.model_dump(mode="json", exclude_none=True)
  # Canonical required fields must be present even when None
  for field in _REQUIRED_SESSION_FIELDS:
    if field not in data:
      data[field] = None
  return data


def write_sessions_file(path: Path, sessions: SessionsFile) -> None:
  """Write sessions.yaml atomically.

  Uses temp file + os.rename for crash safety.
  """
  data = {
    "schema": _SESSIONS_SCHEMA,
    "version": write_version(_SESSIONS_SCHEMA),
    "artifact": sessions.artifact.model_dump(mode="json"),
    "sessions": {
      role: _serialize_session_entry(entry) for role, entry in sessions.sessions.items()
    },
  }
  tmp = path.with_suffix(".tmp")
  tmp.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
  tmp.rename(path)
