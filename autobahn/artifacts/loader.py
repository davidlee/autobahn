"""Artifact loader — reads spec-driver workflow directory into WorkflowContext.

state.yaml is required; all other files are optional.

Design authority: DR-001 §5 (module boundaries), §6 (models).
"""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel, ValidationError

from autobahn.artifacts.schema import SCHEMA_VERSIONS
from autobahn.models.artifacts import (
  HandoffFile,
  ReviewFindingsFile,
  ReviewIndexFile,
  SessionsFile,
  WorkflowStateFile,
)
from autobahn.models.errors import ArtifactContractError, ArtifactParseError
from autobahn.models.runtime import WorkflowContext

M = TypeVar("M", bound=BaseModel)

_OPTIONAL_FILES: dict[str, tuple[str, type[BaseModel]]] = {
  "handoff.current.yaml": ("supekku.workflow.handoff", HandoffFile),
  "review-index.yaml": ("supekku.workflow.review-index", ReviewIndexFile),
  "review-findings.yaml": ("supekku.workflow.review-findings", ReviewFindingsFile),
  "sessions.yaml": ("supekku.workflow.sessions", SessionsFile),
}


def _read_yaml(path: Path) -> dict:
  """Read and parse a YAML file, raising ArtifactParseError on failure."""
  try:
    text = path.read_text()
  except OSError as exc:
    msg = f"Cannot read {path}: {exc}"
    raise ArtifactParseError(msg) from exc

  try:
    data = yaml.safe_load(text)
  except yaml.YAMLError as exc:
    msg = f"Malformed YAML in {path}: {exc}"
    raise ArtifactParseError(msg) from exc

  if not isinstance(data, dict):
    msg = f"Expected mapping in {path}, got {type(data).__name__}"
    raise ArtifactParseError(msg)

  return data


def _validate(model_cls: type[M], data: dict, path: Path) -> M:
  """Validate data against a pydantic model, raising ArtifactContractError."""
  try:
    return model_cls.model_validate(data)
  except ValidationError as exc:
    msg = f"Schema contract violation in {path}: {exc}"
    raise ArtifactContractError(msg) from exc


def _validate_schema_marker(
  data: dict,
  expected_schema: str,
  path: Path,
) -> None:
  """Validate schema and version fields in YAML data.

  Raises ArtifactContractError if schema is missing, unknown,
  or version not in the supported set.
  """
  schema = data.get("schema")
  version = data.get("version")

  if schema is None:
    msg = f"Missing 'schema' field in {path}"
    raise ArtifactContractError(msg)

  if schema != expected_schema:
    msg = f"Unknown schema '{schema}' in {path}, expected '{expected_schema}'"
    raise ArtifactContractError(msg)

  supported = SCHEMA_VERSIONS.get(expected_schema, frozenset())
  if version not in supported:
    msg = (
      f"Unsupported version {version} in {path}, expected one of {sorted(supported)}"
    )
    raise ArtifactContractError(msg)


def load_workflow_dir(workflow_dir: Path) -> WorkflowContext:
  """Load a spec-driver workflow directory into a WorkflowContext.

  Args:
    workflow_dir: Path to the workflow directory containing state.yaml
      and optional handoff/review/sessions files.

  Returns:
    Assembled WorkflowContext.

  Raises:
    ArtifactParseError: YAML is malformed or unreadable.
    ArtifactContractError: YAML is valid but violates schema contract.
  """
  state_path = workflow_dir / "state.yaml"
  if not state_path.exists():
    msg = f"Required file missing: {state_path}"
    raise ArtifactParseError(msg)

  state_data = _read_yaml(state_path)
  _validate_schema_marker(state_data, "supekku.workflow.state", state_path)
  state = _validate(WorkflowStateFile, state_data, state_path)

  optionals: dict[str, BaseModel | None] = {}
  for filename, (expected_schema, model_cls) in _OPTIONAL_FILES.items():
    filepath = workflow_dir / filename
    if filepath.exists():
      data = _read_yaml(filepath)
      _validate_schema_marker(data, expected_schema, filepath)
      optionals[filename] = _validate(model_cls, data, filepath)
    else:
      optionals[filename] = None

  return WorkflowContext(
    artifact_id=state.artifact.id,
    artifact_kind=state.artifact.kind,
    artifact_dir=workflow_dir,
    state=state,
    handoff=optionals["handoff.current.yaml"],
    review_index=optionals["review-index.yaml"],
    review_findings=optionals["review-findings.yaml"],
    sessions=optionals["sessions.yaml"],
  )
