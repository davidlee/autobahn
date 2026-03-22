"""Public API surface for autobahn.

Design authority: DR-001 §8, DR-004 §4.6.
"""

from __future__ import annotations

from autobahn.api.functions import (
  check_prerequisites,
  disposition_finding,
  load_context,
  observe_session,
  persist_session_statuses,
  prime_review,
  reconcile,
  spawn_role_session,
  summarize_review_outcome,
  terminate_session,
  transition_from_handoff,
)

__all__ = [
  # Slice 1: session lifecycle
  "check_prerequisites",
  "load_context",
  "observe_session",
  "persist_session_statuses",
  "reconcile",
  "spawn_role_session",
  "terminate_session",
  "transition_from_handoff",
  # Slice 2: review operations (DR-004)
  "prime_review",
  "summarize_review_outcome",
  "disposition_finding",
]
