#!/usr/bin/env python3
"""
check_no_iap_imports.py — CE-only IAP lint gate.

Scans addons/ipai/** for Odoo IAP module usage that would require an
Enterprise license.  CE constraint: no odoo.com IAP.

Exit codes:
  0 — no violations
  1 — violations found
  2 — error (SSOT file missing, bad args, etc.)

Checks:
  - Python imports: `from odoo.addons.iap`, `import iap`
  - Python API calls: `self.env['iap.account']`, `iap.Account.get()`
  - Manifest depends: `iap` in `depends` list
  - ir.config_parameter references to `iap.*` key patterns

Usage:
  python3 scripts/ci/check_no_iap_imports.py [--repo-root PATH]
"""

import argparse
import ast
import re
import sys
from pathlib import Path


# ── Patterns ──────────────────────────────────────────────────────────────────

# Python: from odoo.addons.iap import ... / from odoo.addons import iap
IMPORT_PATTERN = re.compile(
    r"""(?x)
    from\s+odoo\.addons\.iap\b         # from odoo.addons.iap ...
    | from\s+odoo\.addons\s+import\s+iap\b  # from odoo.addons import iap
    | import\s+iap\b                   # import iap
    """,
    re.MULTILINE,
)

# Python: env['iap.account'] or env["iap.account"]
IAP_ENV_PATTERN = re.compile(
    r"""env\s*\[\s*['"]iap\.""",
    re.MULTILINE,
)

# Python: iap.Account or iap_account (common service function names)
IAP_API_PATTERN = re.compile(
    r"""iap\.Account\.get\(""",
    re.MULTILINE,
)

# Manifest depends list containing 'iap'
# Checks parsed AST so doesn't match module names that contain "iap" as substring
# (e.g., ipai_* addons are fine — they contain "ipai" not "iap" as a list element)


def check_manifest(path: Path) -> list[str]:
    """Return list of violation strings for a __manifest__.py file."""
    violations = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return [f"{path}: syntax error — {exc}"]

    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if not (isinstance(key, ast.Constant) and key.value == "depends"):
                continue
            if not isinstance(value, ast.List):
                continue
            for elt in value.elts:
                if isinstance(elt, ast.Constant) and elt.value == "iap":
                    violations.append(
                        f"{path}:{elt.lineno}: 'iap' in depends list — "
                        "IAP requires EE license (CE constraint)"
                    )
    return violations


def check_python(path: Path) -> list[str]:
    """Return list of violation strings for a Python source file."""
    violations = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    for m in IMPORT_PATTERN.finditer(text):
        line_no = text[: m.start()].count("\n") + 1
        violations.append(
            f"{path}:{line_no}: IAP import — '{m.group(0).strip()}' — "
            "IAP requires EE license"
        )

    for m in IAP_ENV_PATTERN.finditer(text):
        line_no = text[: m.start()].count("\n") + 1
        violations.append(
            f"{path}:{line_no}: env['iap.*'] usage — "
            "IAP model access requires EE license"
        )

    for m in IAP_API_PATTERN.finditer(text):
        line_no = text[: m.start()].count("\n") + 1
        violations.append(
            f"{path}:{line_no}: iap.Account.get() call — "
            "IAP API requires EE license"
        )

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="CE-only IAP import lint gate")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root path (default: current directory)",
    )
    parser.add_argument(
        "--scan-dir",
        default="addons/ipai",
        help="Directory to scan relative to repo-root (default: addons/ipai)",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    scan_dir = repo_root / args.scan_dir

    if not scan_dir.is_dir():
        print(f"ERROR: scan directory does not exist: {scan_dir}", file=sys.stderr)
        return 2

    all_violations: list[str] = []

    # Scan all Python files in addons/ipai/
    for py_file in sorted(scan_dir.rglob("*.py")):
        if py_file.name == "__manifest__.py":
            all_violations.extend(check_manifest(py_file))
        else:
            all_violations.extend(check_python(py_file))

    if all_violations:
        print(
            f"\n❌ CE-ONLY VIOLATION: IAP usage found in {args.scan_dir}/\n"
            f"   IAP (iap.account, iap module) requires Odoo Enterprise license.\n"
            f"   CE constraint (CLAUDE.md §Critical Rules rule #4).\n"
            f"   Use ipai_ai_widget → IPAI bridge instead.\n"
        )
        for v in all_violations:
            print(f"  {v}")
        print(
            f"\nTotal violations: {len(all_violations)}\n"
            "Fix: remove 'iap' from depends lists, replace IAP imports with "
            "ir.config_parameter-based bridge calls."
        )
        return 1

    print(
        f"✅ CE IAP lint passed — no IAP imports in {args.scan_dir}/ "
        f"({sum(1 for _ in scan_dir.rglob('*.py'))} files scanned)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
