"""Guard against __init__.py importing sibling modules that don't exist.

This test prevents the exact startup regression that hit ipai_odoo_copilot
and ipai_enterprise_bridge (commits d385487ac4, 1ea56c6519) where phantom
imports in __init__.py caused ImportError on Odoo module load.
"""
from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ADDONS_ROOT = REPO_ROOT / "addons"


def _iter_addon_init_files() -> list[Path]:
    if not ADDONS_ROOT.exists():
        return []
    return sorted(
        path for path in ADDONS_ROOT.rglob("__init__.py")
        if path.is_file()
    )


def _missing_sibling_imports(init_file: Path) -> list[str]:
    tree = ast.parse(init_file.read_text(encoding="utf-8"), filename=str(init_file))
    package_dir = init_file.parent
    missing: set[str] = set()

    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.level != 1 or node.module is not None:
            continue
        for alias in node.names:
            name = alias.name
            if name == "*":
                continue
            module_file = package_dir / f"{name}.py"
            package_init = package_dir / name / "__init__.py"
            if not module_file.exists() and not package_init.exists():
                missing.add(name)

    return sorted(missing)


def test_addon_init_files_do_not_import_missing_siblings() -> None:
    failures: dict[str, list[str]] = {}

    for init_file in _iter_addon_init_files():
        unresolved = _missing_sibling_imports(init_file)
        if unresolved:
            failures[str(init_file.relative_to(REPO_ROOT))] = unresolved

    if failures:
        lines = ["Phantom addon imports detected:"]
        for path, names in sorted(failures.items()):
            lines.append(f"- {path}: {', '.join(names)}")
        raise AssertionError("\n".join(lines))
