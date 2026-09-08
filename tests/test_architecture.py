from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).parents[1] / "book_loop"


FORBIDDEN = {
    "domain": ("book_loop.infrastructure", "book_loop.workflow", "fastapi", "langgraph"),
    "application": ("book_loop.infrastructure", "book_loop.workflow", "fastapi", "langgraph"),
    "workflow": ("book_loop.infrastructure", "fastapi"),
}


def _imports(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend((node.lineno, alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append((node.lineno, node.module))
    return imports


def test_clean_architecture_dependency_direction() -> None:
    violations: list[str] = []
    for layer, forbidden_prefixes in FORBIDDEN.items():
        layer_root = ROOT / layer
        if not layer_root.exists():
            continue
        for path in layer_root.rglob("*.py"):
            for lineno, imported in _imports(path):
                if any(imported == prefix or imported.startswith(prefix + ".") for prefix in forbidden_prefixes):
                    violations.append(f"{path.relative_to(ROOT)}:{lineno} imports {imported}")

    assert not violations, "Clean Architecture dependency violations:\n" + "\n".join(sorted(violations))
