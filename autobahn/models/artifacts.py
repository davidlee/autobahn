"""Pydantic models for spec-driver workflow YAML files.

Narrow models covering only the fields autobahn consumes.
Unknown fields are silently ignored (extra="ignore") per DEC-001/DEC-015.

Schema authority resides in spec-driver. These models are validated
by contract tests against authoritative fixtures.

Design authority: DR-001 §6.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from autobahn.models.enums import (
  ArtifactKind,
  BootstrapStatus,
  FindingDispositionAction,
  FindingStatus,
  HandoffTransitionStatus,
  NextActivityKind,
  PhaseStatus,
  ReviewStatus,
  Role,
  SessionStatus,
  WorkflowStatus,
)

# --- Shared sub-models ---


class ArtifactBlock(BaseModel):
  model_config = ConfigDict(extra="ignore")

  id: str
  kind: ArtifactKind
  path: str | None = None
  notes_path: str | None = None


class PhaseBlock(BaseModel):
  model_config = ConfigDict(extra="ignore")

  id: str
  status: PhaseStatus
  path: str | None = None


class TimestampsBlock(BaseModel):
  model_config = ConfigDict(extra="ignore")

  created: datetime | None = None
  updated: datetime | None = None
  emitted_at: datetime | None = None


# --- state.yaml (supekku:workflow.state@v1) ---


class WorkflowBlock(BaseModel):
  model_config = ConfigDict(extra="ignore")

  status: WorkflowStatus
  active_role: Role
  claimed_by: str | None = None
  handoff_boundary: str | None = None


class PointersBlock(BaseModel):
  model_config = ConfigDict(extra="ignore")

  delta: str | None = None
  plan: str | None = None


class PlanBlock(BaseModel):
  model_config = ConfigDict(extra="ignore")

  id: str
  path: str | None = None


class WorkflowStateFile(BaseModel):
  """Stable subset of supekku:workflow.state@v1."""

  model_config = ConfigDict(extra="ignore")

  schema_: str | None = None  # 'schema' is reserved
  version: int | None = None
  artifact: ArtifactBlock
  phase: PhaseBlock
  workflow: WorkflowBlock
  pointers: PointersBlock | None = None
  timestamps: TimestampsBlock
  plan: PlanBlock | None = None

  def model_post_init(self, __context):
    # Map 'schema' key from YAML to schema_ field
    pass


# --- handoff.current.yaml (supekku:workflow.handoff@v1) ---


class TransitionBlock(BaseModel):
  model_config = ConfigDict(extra="ignore")

  from_role: Role
  to_role: Role
  status: HandoffTransitionStatus
  boundary: str | None = None


class NextActivityBlock(BaseModel):
  model_config = ConfigDict(extra="ignore")

  kind: NextActivityKind


class OpenItemBlock(BaseModel):
  model_config = ConfigDict(extra="ignore")

  kind: str
  description: str


class HandoffFile(BaseModel):
  """Stable subset of supekku:workflow.handoff@v1."""

  model_config = ConfigDict(extra="ignore")

  artifact: ArtifactBlock
  transition: TransitionBlock
  phase: PhaseBlock
  required_reading: list[str] = []
  next_activity: NextActivityBlock
  open_items: list[OpenItemBlock] = []
  timestamps: TimestampsBlock | None = None


# --- review-index.yaml (supekku:workflow.review-index@v1) ---


class StalenessKeyBlock(BaseModel):
  model_config = ConfigDict(extra="ignore")

  head: str | None = None
  state_sha: str | None = None


class StalenessBlock(BaseModel):
  model_config = ConfigDict(extra="ignore")

  cache_key: StalenessKeyBlock | None = None


class ReviewBlock(BaseModel):
  model_config = ConfigDict(extra="ignore")

  bootstrap_status: BootstrapStatus
  judgment_status: ReviewStatus | None = None
  scope: str | None = None
  current_round: int | None = None


class ReviewIndexFile(BaseModel):
  """Minimal read surface: bootstrap status + staleness key."""

  model_config = ConfigDict(extra="ignore")

  artifact: ArtifactBlock
  review: ReviewBlock
  staleness: StalenessBlock | None = None
  timestamps: TimestampsBlock | None = None


# --- review-findings.yaml (supekku:workflow.review-findings@v2) ---


class FindingDisposition(BaseModel):
  model_config = ConfigDict(extra="ignore")

  action: FindingDispositionAction
  authority: str | None = None
  rationale: str | None = None


class Finding(BaseModel):
  model_config = ConfigDict(extra="ignore")

  id: str
  summary: str
  status: FindingStatus
  disposition: FindingDisposition | None = None


class ReviewRound(BaseModel):
  model_config = ConfigDict(extra="ignore")

  round: int
  status: ReviewStatus
  blocking: list[Finding] = []
  non_blocking: list[Finding] = []


class ReviewFindingsBlock(BaseModel):
  model_config = ConfigDict(extra="ignore")

  current_round: int


class ReviewFindingsFile(BaseModel):
  """Minimal: round, status, finding counts."""

  model_config = ConfigDict(extra="ignore")

  artifact: ArtifactBlock
  review: ReviewFindingsBlock
  rounds: list[ReviewRound] = []
  timestamps: TimestampsBlock | None = None


# --- sessions.yaml (supekku:workflow.sessions@v1) — autobahn-owned ---


class SessionEntry(BaseModel):
  model_config = ConfigDict(extra="ignore")

  session_id: str
  role: Role
  status: SessionStatus
  backend: str
  launched_at: datetime
  last_activity: datetime | None = None
  harness: str | None = None
  pid: int | None = None


class SessionsFile(BaseModel):
  """Full model — autobahn owns this file."""

  model_config = ConfigDict(extra="ignore")

  artifact: ArtifactBlock
  sessions: list[SessionEntry] = []
