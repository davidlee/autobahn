"""Runtime models — autobahn's own types, not mirroring YAML files.

Design authority: DR-001 §6.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel

from autobahn.models.artifacts import (
  HandoffFile,
  ReviewFindingsFile,
  ReviewIndexFile,
  SessionsFile,
  WorkflowStateFile,
)
from autobahn.models.enums import (
  ArtifactKind,
  NextActivityKind,
  Role,
  WorkflowStatus,
)

T = TypeVar("T")


class WorkflowContext(BaseModel):
  """Assembled runtime view of an artifact's workflow state."""

  artifact_id: str
  artifact_kind: ArtifactKind
  artifact_dir: Path
  state: WorkflowStateFile
  handoff: HandoffFile | None = None
  review_index: ReviewIndexFile | None = None
  review_findings: ReviewFindingsFile | None = None
  sessions: SessionsFile | None = None


class TransitionPlan(BaseModel):
  """Computed next action from current workflow state.

  Carries structured references, not prose — spec-driver
  owns prompt content via installed templates and CLI.
  """

  source_state: WorkflowStatus
  target_role: Role
  activity: NextActivityKind
  artifact_id: str
  phase_id: str
  handoff_path: str
  required_reading: list[str] = []
  resume_session: str | None = None


class LaunchSpec(BaseModel):
  """What to run — produced by harness adapter."""

  command: str
  args: list[str] = []
  env: dict[str, str] = {}
  work_dir: Path


class SessionHandle(BaseModel):
  """Handle for a managed session."""

  session_id: str
  role: Role
  artifact_id: str
  backend_ref: str
  launched_at: datetime


class SessionMetadata(BaseModel):
  """Observable state of a session."""

  alive: bool
  exit_code: int | None = None
  runtime_seconds: float | None = None
  last_activity: datetime | None = None


class SessionOutcome(BaseModel):
  """Interpreted result of a session ending."""

  exit_code: int
  interpretation: str
  artifacts_modified: bool | None = None


class RuntimePolicy(BaseModel):
  """Configuration for a specific orchestration run."""

  harness: str
  session_backend: str
  harness_executable: str | None = None
  sandbox_profile: str | None = None
  work_dir: Path
  timeout_seconds: int | None = None


class OperationResult(BaseModel, Generic[T]):
  """Standard return for expected operational failures."""

  success: bool
  value: T | None = None
  error: str | None = None
  warnings: list[str] = []
