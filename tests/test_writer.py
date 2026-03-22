"""Tests for artifact writer (VA-005)."""

from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

import yaml

from autobahn.artifacts.loader import load_workflow_dir
from autobahn.artifacts.writer import write_sessions_file
from autobahn.models.artifacts import ArtifactBlock, SessionEntry, SessionsFile
from autobahn.models.enums import ArtifactKind, Role, SessionStatus

FIXTURES = Path(__file__).parent / "fixtures" / "workflow"


def _artifact_block() -> ArtifactBlock:
  return ArtifactBlock(id="DE-099", kind=ArtifactKind.DELTA)


def _session_entry(**overrides) -> SessionEntry:
  defaults = {
    "session_id": "DE-099-implementer",
    "role": Role.IMPLEMENTER,
    "status": SessionStatus.ACTIVE,
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
      sessions=[_session_entry()],
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
      sessions=[_session_entry()],
    )
    write_sessions_file(tmp_path / "sessions.yaml", sf)

    ctx = load_workflow_dir(tmp_path)
    assert ctx.sessions is not None
    assert len(ctx.sessions.sessions) == 1
    entry = ctx.sessions.sessions[0]
    assert entry.session_id == "DE-099-implementer"
    assert entry.role == Role.IMPLEMENTER
    assert entry.status == SessionStatus.ACTIVE
    assert entry.launched_at == datetime(2026, 3, 22, 14, 0, tzinfo=UTC)

  def test_empty_sessions_round_trip(self, tmp_path):
    """Empty sessions list must survive write/read cycle."""
    shutil.copy(FIXTURES / "state.yaml", tmp_path / "state.yaml")

    sf = SessionsFile(artifact=_artifact_block(), sessions=[])
    write_sessions_file(tmp_path / "sessions.yaml", sf)

    ctx = load_workflow_dir(tmp_path)
    assert ctx.sessions is not None
    assert ctx.sessions.sessions == []

  def test_overwrites_existing(self, tmp_path):
    path = tmp_path / "sessions.yaml"
    sf1 = SessionsFile(
      artifact=_artifact_block(),
      sessions=[_session_entry(session_id="old")],
    )
    write_sessions_file(path, sf1)

    sf2 = SessionsFile(
      artifact=_artifact_block(),
      sessions=[_session_entry(session_id="new")],
    )
    write_sessions_file(path, sf2)

    data = yaml.safe_load(path.read_text())
    assert len(data["sessions"]) == 1
    assert data["sessions"][0]["session_id"] == "new"
