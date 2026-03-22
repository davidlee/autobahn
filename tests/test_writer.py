"""Tests for artifact writer (VA-005)."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

import yaml

from autobahn.artifacts.loader import load_workflow_dir
from autobahn.artifacts.writer import (
  _REQUIRED_SESSION_FIELDS,
  write_sessions_file,
)
from autobahn.models.artifacts import ArtifactBlock, SessionEntry, SessionsFile
from autobahn.models.enums import ArtifactKind, SessionStatus

FIXTURES = Path(__file__).parent / "fixtures" / "workflow"


def _artifact_block() -> ArtifactBlock:
  return ArtifactBlock(id="DE-099", kind=ArtifactKind.DELTA)


def _session_entry(**overrides) -> SessionEntry:
  defaults = {
    "session_name": "DE-099-implementer",
    "status": SessionStatus.ACTIVE,
    "last_seen": datetime(2026, 3, 22, 14, 0, tzinfo=UTC),
    "backend": "subprocess",
    "launched_at": datetime(2026, 3, 22, 14, 0, tzinfo=UTC),
    "harness": "claude_code",
  }
  defaults.update(overrides)
  return SessionEntry(**defaults)


class TestWriteSessionsFile:
  def test_atomic_write_creates_file(self, tmp_path):
    path = tmp_path / "sessions.yaml"
    sf = SessionsFile(
      artifact=_artifact_block(),
      sessions={"implementer": _session_entry()},
    )
    write_sessions_file(path, sf)
    assert path.exists()
    # tmp file should not remain
    assert not path.with_suffix(".tmp").exists()

  def test_round_trip_via_load_workflow_dir(self, tmp_path):
    """Written sessions.yaml must be loadable by the reader (VA-005)."""
    shutil.copy(FIXTURES / "state.yaml", tmp_path / "state.yaml")

    sf = SessionsFile(
      artifact=_artifact_block(),
      sessions={"implementer": _session_entry()},
    )
    write_sessions_file(tmp_path / "sessions.yaml", sf)

    ctx = load_workflow_dir(tmp_path)
    assert ctx.sessions is not None
    assert len(ctx.sessions.sessions) == 1
    entry = ctx.sessions.sessions["implementer"]
    assert entry.session_name == "DE-099-implementer"
    assert entry.status == SessionStatus.ACTIVE
    assert entry.launched_at == datetime(2026, 3, 22, 14, 0, tzinfo=UTC)

  def test_empty_sessions_round_trip(self, tmp_path):
    """Empty sessions dict must survive write/read cycle."""
    shutil.copy(FIXTURES / "state.yaml", tmp_path / "state.yaml")

    sf = SessionsFile(artifact=_artifact_block(), sessions={})
    write_sessions_file(tmp_path / "sessions.yaml", sf)

    ctx = load_workflow_dir(tmp_path)
    assert ctx.sessions is not None
    assert ctx.sessions.sessions == {}

  def test_overwrites_existing(self, tmp_path):
    path = tmp_path / "sessions.yaml"
    sf1 = SessionsFile(
      artifact=_artifact_block(),
      sessions={"implementer": _session_entry(session_name="old")},
    )
    write_sessions_file(path, sf1)

    sf2 = SessionsFile(
      artifact=_artifact_block(),
      sessions={"implementer": _session_entry(session_name="new")},
    )
    write_sessions_file(path, sf2)

    data = yaml.safe_load(path.read_text())
    assert len(data["sessions"]) == 1
    assert data["sessions"]["implementer"]["session_name"] == "new"

  def test_canonical_null_preservation(self, tmp_path):
    """Canonical required fields appear even when None (absent session)."""
    path = tmp_path / "sessions.yaml"
    entry = SessionEntry()  # all defaults — absent session
    sf = SessionsFile(
      artifact=_artifact_block(),
      sessions={"reviewer": entry},
    )
    write_sessions_file(path, sf)
    data = yaml.safe_load(path.read_text())
    session = data["sessions"]["reviewer"]
    assert session["session_name"] is None
    assert session["status"] == "absent"
    assert session["last_seen"] is None

  def test_required_session_fields_subset_of_model(self):
    """Contract: _REQUIRED_SESSION_FIELDS ⊆ SessionEntry.model_fields."""
    assert set(SessionEntry.model_fields) >= _REQUIRED_SESSION_FIELDS
