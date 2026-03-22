"""Schema version registry for spec-driver workflow artifacts.

Shared by loader (validation) and writer (serialization).
Write-version policy: autobahn writes at the highest supported version
for a given schema.

Design authority: DR-002 §4.1, DEC-027.
"""

from __future__ import annotations

SCHEMA_VERSIONS: dict[str, frozenset[int]] = {
  "supekku.workflow.state": frozenset({1}),
  "supekku.workflow.handoff": frozenset({1}),
  "supekku.workflow.review-index": frozenset({1}),
  "supekku.workflow.review-findings": frozenset({1, 2}),
  "supekku.workflow.sessions": frozenset({1}),
}


def write_version(schema: str) -> int:
  """Return the version to use when writing a schema file."""
  return max(SCHEMA_VERSIONS[schema])
