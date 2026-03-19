#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def _load_yaml(path: Path) -> dict:
    """
    Minimal YAML loader for our constrained schema.
    Tries PyYAML if available, else uses a small fallback parser.
    """
    try:
        import yaml  # type: ignore

        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        # Fallback: supports only simple YAML mappings/lists used here.
        data: Dict[str, object] = {}
        stack: List[Tuple[int, object]] = []
        current = data
        current_indent = 0

        def set_kv(obj: dict, k: str, v: object):
            obj[k] = v

        lines = path.read_text(encoding="utf-8").splitlines()
        for raw in lines:
            line = raw.rstrip()
            if not line or line.lstrip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip(" "))
            line = line.lstrip(" ")

            while stack and indent < stack[-1][0]:
                stack.pop()
            if stack:
                current_indent, current = stack[-1]
            else:
                current_indent, current = 0, data

            if line.startswith("- "):
                # list item
                item = line[2:].strip()
                if not isinstance(current, list):
                    raise RuntimeError(f"Fallback YAML parser expected list at: {raw}")
                current.append(item)
                continue

            if ":" in line:
                k, rest = line.split(":", 1)
                k = k.strip()
                rest = rest.strip()
                if rest == "":
                    # start nested mapping or list (unknown yet)
                    # default to dict, may be replaced if next line is list item
                    new_obj: object = {}
                    set_kv(current, k, new_obj)
                    stack.append((indent + 2, new_obj))
                elif rest.startswith("[") and rest.endswith("]"):
                    # very simple inline list
                    inner = rest[1:-1].strip()
                    if not inner:
                        set_kv(current, k, [])
                    else:
                        set_kv(current, k, [x.strip() for x in inner.split(",")])
                elif rest.lower() in ("true", "false"):
                    set_kv(current, k, rest.lower() == "true")
                else:
                    # scalar string/number
                    try:
                        set_kv(current, k, int(rest))
                    except Exception:
                        set_kv(current, k, rest)
                continue

            raise RuntimeError(f"Fallback YAML parser cannot parse line: {raw}")

        # Fix-up: convert dict placeholders to list when needed is not supported in fallback
        return data


def _is_odoo_module_dir(p: Path) -> bool:
    if not p.is_dir():
        return False
    return (p / "__manifest__.py").exists() or (p / "__openerp__.py").exists()


def _scan_ipai_modules(addons_root: Path) -> Set[str]:
    found: Set[str] = set()
    if not addons_root.exists():
        return found
    try:
        for child in addons_root.iterdir():
            if child.is_dir() and child.name.startswith("ipai_") and _is_odoo_module_dir(child):
                found.add(child.name)
    except PermissionError:
        # Skip directories we can't read
        pass
    return found


def _flatten_allowlist(doc: dict) -> Set[str]:
    allow: Set[str] = set()
    if doc.get("allow_all_ipai") is True:
        return allow  # special flag handled elsewhere

    allowlist = doc.get("allowlist") or {}
    if isinstance(allowlist, dict):
        for _, v in allowlist.items():
            if isinstance(v, list):
                allow.update([str(x) for x in v])

    extra = doc.get("extra_allow") or []
    if isinstance(extra, list):
        allow.update([str(x) for x in extra])

    return allow


def main() -> int:
    repo_root = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd())).resolve()
    allowlist_path = repo_root / "spec" / "ipai_custom_modules_allowlist.yaml"
    override_path = repo_root / "spec" / "allow_custom_modules.yaml"

    if not allowlist_path.exists():
        print(f"[ipai-guard] ERROR: missing {allowlist_path}", file=sys.stderr)
        return 2

    allow_doc = _load_yaml(allowlist_path)
    addons_root_rel = os.environ.get("IPAI_ADDONS_ROOT") or str(
        allow_doc.get("addons_root") or "addons"
    )
    addons_root = (repo_root / addons_root_rel).resolve()

    found = _scan_ipai_modules(addons_root)

    allow_all = bool(allow_doc.get("allow_all_ipai") is True)
    allow = _flatten_allowlist(allow_doc)

    override_allow: Set[str] = set()
    if override_path.exists():
        ov = _load_yaml(override_path) or {}
        ov_allow = ov.get("allow") or []
        if isinstance(ov_allow, list):
            override_allow = set(str(x) for x in ov_allow)

    if allow_all:
        # still report for visibility
        print("[ipai-guard] allow_all_ipai=true (NO ENFORCEMENT). Found:", sorted(found))
        return 0

    permitted = allow | override_allow
    blocked = sorted(found - permitted)

    report = {
        "repo_root": str(repo_root),
        "addons_root": str(addons_root),
        "found_ipai_modules": sorted(found),
        "permitted_ipai_modules": sorted(permitted),
        "blocked_ipai_modules": blocked,
        "override_allow": sorted(override_allow),
    }

    print("[ipai-guard] report:\n" + json.dumps(report, indent=2))

    if blocked:
        print(
            "\n[ipai-guard] FAIL: Unapproved ipai_* modules detected:\n  - "
            + "\n  - ".join(blocked)
            + "\n\nFix by either:\n"
            "  1) Adding to spec/ipai_custom_modules_allowlist.yaml (preferred), or\n"
            "  2) Temporarily adding to spec/allow_custom_modules.yaml (time-boxed exception).\n",
            file=sys.stderr,
        )
        return 1

    print("[ipai-guard] OK: All ipai_* modules are allowlisted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
