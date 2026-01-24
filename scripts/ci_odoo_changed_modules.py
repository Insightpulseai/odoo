#!/usr/bin/env python3
"""
Detect changed Odoo modules in a PR/commit range.
Outputs JSON list of changed modules with name and path.
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


def sh(*cmd: str) -> str:
    """Run shell command and return stripped output."""
    return subprocess.check_output(cmd, text=True).strip()


def repo_root() -> Path:
    """Get the repository root directory."""
    return Path(sh("git", "rev-parse", "--show-toplevel"))


def changed_files(base_ref: str, head_ref: str) -> list[str]:
    """Get list of changed files between two refs."""
    try:
        out = sh("git", "diff", "--name-only", f"{base_ref}...{head_ref}")
    except subprocess.CalledProcessError:
        # Fallback for initial commits or missing refs
        out = sh("git", "diff", "--name-only", "HEAD~1", "HEAD")
    return [x for x in out.splitlines() if x.strip()]


def load_yaml(path: Path) -> dict:
    """Load YAML file, returning empty dict if missing or invalid."""
    try:
        import yaml
        return yaml.safe_load(path.read_text("utf-8")) or {}
    except Exception:
        return {}


def find_module_root(addons_root: Path, file_path: Path) -> Optional[Path]:
    """
    Given a changed file under addons_root, find the immediate module folder.
    A valid module has __manifest__.py or __openerp__.py.
    """
    try:
        rel = file_path.relative_to(addons_root)
    except ValueError:
        return None

    if len(rel.parts) < 2:
        return None

    module_dir = addons_root / rel.parts[0]

    # Check for manifest
    if (module_dir / "__manifest__.py").exists():
        return module_dir
    if (module_dir / "__openerp__.py").exists():
        return module_dir

    return None


def main():
    # Get refs from environment or defaults
    base = os.environ.get("GITHUB_BASE_REF", "")
    head = os.environ.get("GITHUB_HEAD_REF", "HEAD")

    # Normalize refs
    if base:
        if not base.startswith("origin/"):
            base_ref = f"origin/{base}"
        else:
            base_ref = base
    else:
        base_ref = "origin/main"

    head_ref = "HEAD"

    root = repo_root()
    policy_path = root / "config/odoo/ci_policy.yml"

    if not policy_path.exists():
        # No policy = no module detection
        print("[]")
        return

    policy = load_yaml(policy_path)
    addons_roots = [root / p for p in (policy.get("addons_roots") or [])]

    # Get changed files
    files = [root / f for f in changed_files(base_ref, head_ref)]

    modules = set()
    for f in files:
        for ar in addons_roots:
            if not ar.exists():
                continue
            if not str(f).startswith(str(ar) + os.sep):
                continue
            mr = find_module_root(ar, f)
            if mr:
                modules.add(mr)

    # Output as JSON
    out = [
        {"name": p.name, "path": str(p.relative_to(root))}
        for p in sorted(modules)
    ]
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
