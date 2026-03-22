"""Import coupling tests.

Enforces DR-001 §5 coupling rules:
- adapters/ depends on models/ only — never on api/, runtime/, or each other
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest


def _get_imports(module_path: Path) -> set[str]:
  """Extract all import targets from a Python file."""
  source = module_path.read_text()
  tree = ast.parse(source)
  imports = set()
  for node in ast.walk(tree):
    if isinstance(node, ast.Import):
      for alias in node.names:
        imports.add(alias.name)
    elif isinstance(node, ast.ImportFrom) and node.module:
      imports.add(node.module)
  return imports


def _autobahn_imports(imports: set[str]) -> set[str]:
  """Filter to only autobahn internal imports."""
  return {i for i in imports if i.startswith("autobahn.")}


ADAPTERS_DIR = Path(__file__).parent.parent / "autobahn" / "adapters"


def _adapter_source_files() -> list[Path]:
  """All .py files under autobahn/adapters/."""
  return [p for p in ADAPTERS_DIR.rglob("*.py") if p.name != "__init__.py"]


class TestAdapterCoupling:
  @pytest.mark.parametrize(
    "source_file",
    _adapter_source_files(),
    ids=lambda p: str(p.relative_to(ADAPTERS_DIR)),
  )
  def test_adapters_import_only_models(self, source_file):
    imports = _autobahn_imports(_get_imports(source_file))
    allowed_prefixes = ("autobahn.models",)
    for imp in imports:
      assert any(imp.startswith(prefix) for prefix in allowed_prefixes), (
        f"{source_file.name} imports {imp}, "
        f"but adapters/ should only import from models/"
      )

  def test_adapter_modules_importable(self):
    """Verify all adapter modules can be imported."""
    importlib.import_module("autobahn.adapters.harness.claude_code")
    importlib.import_module("autobahn.adapters.session.subprocess_backend")
