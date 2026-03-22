"""Tests for artifact loader (VA-002)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from autobahn.artifacts.loader import load_workflow_dir
from autobahn.models.enums import ArtifactKind, WorkflowStatus
from autobahn.models.errors import ArtifactContractError, ArtifactParseError

FIXTURES = Path(__file__).parent / "fixtures" / "workflow"


class TestLoadWorkflowDir:
  def test_happy_path(self):
    ctx = load_workflow_dir(FIXTURES)
    assert ctx.artifact_id == "DE-099"
    assert ctx.artifact_kind == ArtifactKind.DELTA
    assert ctx.artifact_dir == FIXTURES
    assert ctx.state.workflow.status == WorkflowStatus.IMPLEMENTING
    assert ctx.handoff is not None
    assert ctx.review_index is not None
    assert ctx.review_findings is not None
    assert ctx.sessions is not None

  def test_missing_optional_files(self, tmp_path):
    # Copy only state.yaml
    shutil.copy(FIXTURES / "state.yaml", tmp_path / "state.yaml")
    ctx = load_workflow_dir(tmp_path)
    assert ctx.artifact_id == "DE-099"
    assert ctx.handoff is None
    assert ctx.review_index is None
    assert ctx.review_findings is None
    assert ctx.sessions is None

  def test_missing_state_yaml_raises(self, tmp_path):
    with pytest.raises(ArtifactParseError, match="Required file missing"):
      load_workflow_dir(tmp_path)

  def test_malformed_yaml_raises(self, tmp_path):
    (tmp_path / "state.yaml").write_text(": :\n  bad: [unclosed")
    with pytest.raises(ArtifactParseError, match="Malformed YAML"):
      load_workflow_dir(tmp_path)

  def test_invalid_schema_raises(self, tmp_path):
    # Valid YAML but wrong schema — hits schema validation first
    (tmp_path / "state.yaml").write_text(
      "schema: supekku.workflow.state\nversion: 1\nfoo: bar\n"
    )
    with pytest.raises(ArtifactContractError, match="Schema contract violation"):
      load_workflow_dir(tmp_path)

  def test_non_mapping_yaml_raises(self, tmp_path):
    (tmp_path / "state.yaml").write_text("- just\n- a\n- list\n")
    with pytest.raises(ArtifactParseError, match="Expected mapping"):
      load_workflow_dir(tmp_path)


class TestSchemaValidation:
  """Schema marker validation (DR-002 §4.1, DEC-020)."""

  def test_missing_schema_field(self, tmp_path):
    (tmp_path / "state.yaml").write_text("foo: bar\n")
    with pytest.raises(ArtifactContractError, match="Missing 'schema' field"):
      load_workflow_dir(tmp_path)

  def test_wrong_schema_marker(self, tmp_path):
    (tmp_path / "state.yaml").write_text("schema: supekku.workflow.wrong\nversion: 1\n")
    with pytest.raises(ArtifactContractError, match="Unknown schema"):
      load_workflow_dir(tmp_path)

  def test_unsupported_version(self, tmp_path):
    (tmp_path / "state.yaml").write_text(
      "schema: supekku.workflow.state\nversion: 99\n"
    )
    with pytest.raises(ArtifactContractError, match="Unsupported version"):
      load_workflow_dir(tmp_path)

  def test_optional_file_wrong_schema(self, tmp_path):
    shutil.copy(FIXTURES / "state.yaml", tmp_path / "state.yaml")
    (tmp_path / "sessions.yaml").write_text(
      "schema: supekku.workflow.wrong\nversion: 1\n"
    )
    with pytest.raises(ArtifactContractError, match="Unknown schema"):
      load_workflow_dir(tmp_path)

  def test_optional_file_missing_schema(self, tmp_path):
    shutil.copy(FIXTURES / "state.yaml", tmp_path / "state.yaml")
    (tmp_path / "sessions.yaml").write_text("artifact:\n  id: X\n  kind: delta\n")
    with pytest.raises(ArtifactContractError, match="Missing 'schema' field"):
      load_workflow_dir(tmp_path)
