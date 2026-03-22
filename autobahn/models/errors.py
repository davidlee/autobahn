"""Error taxonomy for autobahn.

Convention: these exceptions are for invariant violations and environment
failures — bugs, incompatible environments, broken contracts. OperationResult
is for expected operational outcomes.

Design authority: DR-001 §6.
"""

from __future__ import annotations


class AutobahnError(Exception):
  """Base for all autobahn errors."""


# Artifact layer


class ArtifactParseError(AutobahnError):
  """YAML is malformed or unreadable."""


class ArtifactContractError(AutobahnError):
  """YAML is valid but violates schema contract.

  Unknown schema, unsupported version, missing required fields.
  """


# External tool layer


class ToolInvocationError(AutobahnError):
  """spec-driver CLI or other external tool failed to execute."""


class ToolContractError(AutobahnError):
  """External tool returned unexpected output format or
  exit 0 with invalid payload."""


# Backend layer


class BackendUnavailableError(AutobahnError):
  """Session backend prerequisites not met (tmux missing, etc.)."""


class BackendTransportError(AutobahnError):
  """Communication with backend failed mid-operation."""


# Policy layer


class PreconditionError(AutobahnError):
  """Runtime precondition not met.

  Harness not found, terminal state, missing required files.
  """


# Session layer


class SessionError(AutobahnError):
  """Session operation failed (already dead, not found, etc.)."""
