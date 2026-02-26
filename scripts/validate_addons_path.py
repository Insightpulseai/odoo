#!/usr/bin/env python3
"""
validate_addons_path.py — CI guardrail for addons_path / compose mount parity.

Invariant: every path segment in infra/odoo.conf addons_path that starts with
/mnt/ must have a corresponding bind-mount in the ipai-odoo service in
infra/stack/compose.stack.yml.

Exit codes:
  0 — all /mnt/* addons_path entries have a matching compose bind mount
  1 — one or more entries are missing a bind mount (CI fails)
  2 — script error (bad config path, parse error, etc.)

Usage:
  python3 scripts/validate_addons_path.py
  python3 scripts/validate_addons_path.py --conf infra/odoo.conf --compose infra/stack/compose.stack.yml
"""

import argparse
import configparser
import os
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths (relative to repo root — resolved from script location)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONF = REPO_ROOT / "infra" / "odoo.conf"
DEFAULT_COMPOSE = REPO_ROOT / "infra" / "stack" / "compose.stack.yml"


def parse_addons_path(conf_path: Path) -> list[str]:
    """Return the list of addons_path entries from an odoo.conf file."""
    if not conf_path.exists():
        raise FileNotFoundError(f"odoo.conf not found: {conf_path}")

    content = conf_path.read_text()
    # Strip out ${VAR} substitution markers (not valid in configparser)
    content_cleaned = re.sub(r"\$\{[^}]+\}", "PLACEHOLDER", content)
    # configparser needs a section header; inject one only if absent
    if not re.search(r"^\[options\]", content_cleaned, re.MULTILINE):
        content_with_section = "[options]\n" + content_cleaned
    else:
        content_with_section = content_cleaned

    parser = configparser.RawConfigParser()
    parser.read_string(content_with_section)
    raw = parser.get("options", "addons_path", fallback="")
    return [p.strip() for p in raw.split(",") if p.strip()]


def parse_compose_odoo_mounts(compose_path: Path) -> list[str]:
    """
    Return the list of container-side paths bound in the ipai-odoo service
    by scanning the compose YAML for lines of the form:
      - <host_path>:<container_path>[:<options>]

    We do a lightweight line-by-line parse rather than importing a YAML
    library so that this script has zero dependencies beyond the stdlib.
    """
    if not compose_path.exists():
        raise FileNotFoundError(f"compose file not found: {compose_path}")

    lines = compose_path.read_text().splitlines()

    # --- locate the odoo service block ---
    # A service block starts at "  <name>:" (exactly 2 leading spaces + word chars + colon).
    # We collect lines from "  odoo:" until the next sibling service definition.
    service_re = re.compile(r"^  \w[\w-]*:")
    volume_re = re.compile(r"^\s+-\s+([^:]+):(/[^:\s]+)")

    in_odoo = False
    odoo_lines: list[str] = []

    for line in lines:
        if service_re.match(line):
            if line.startswith("  odoo:"):
                in_odoo = True
            elif in_odoo:
                # Hit next sibling service — stop
                break
        if in_odoo:
            odoo_lines.append(line)

    if not odoo_lines:
        raise ValueError("Could not find 'odoo:' service block in compose file")

    container_paths = []
    for line in odoo_lines:
        m = volume_re.match(line)
        if m:
            container_paths.append(m.group(2))

    return container_paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--conf", default=str(DEFAULT_CONF), help="Path to odoo.conf")
    parser.add_argument(
        "--compose", default=str(DEFAULT_COMPOSE), help="Path to compose.stack.yml"
    )
    args = parser.parse_args()

    conf_path = Path(args.conf)
    compose_path = Path(args.compose)

    # ------------------------------------------------------------------
    # Parse
    # ------------------------------------------------------------------
    try:
        addons_entries = parse_addons_path(conf_path)
    except Exception as exc:
        print(f"ERROR parsing odoo.conf: {exc}", file=sys.stderr)
        return 2

    try:
        mounted_paths = parse_compose_odoo_mounts(compose_path)
    except Exception as exc:
        print(f"ERROR parsing compose file: {exc}", file=sys.stderr)
        return 2

    # ------------------------------------------------------------------
    # Check: every /mnt/* addons_path entry must be mounted
    # ------------------------------------------------------------------
    mnt_entries = [p for p in addons_entries if p.startswith("/mnt/")]
    mounted_set = set(mounted_paths)

    missing = [p for p in mnt_entries if p not in mounted_set]

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    print(f"addons_path /mnt/* entries : {len(mnt_entries)}")
    print(f"compose bind-mounts found  : {len(mounted_paths)}")
    print(f"missing bind-mounts        : {len(missing)}")

    if missing:
        print("\n❌ MISSING BIND MOUNTS — add these to infra/stack/compose.stack.yml:", file=sys.stderr)
        for p in sorted(missing):
            # Derive the expected host path (relative to repo root)
            oca_name = p.removeprefix("/mnt/oca/")
            if p.startswith("/mnt/oca/"):
                host = f"../../addons/oca/{oca_name}"
            else:
                host = f"../../addons/ipai"
            print(f"  - {host}:{p}:ro", file=sys.stderr)
        print(
            "\nFix: edit infra/stack/compose.stack.yml and add the missing volumes, "
            "then run git-aggregator to hydrate the missing repos.",
            file=sys.stderr,
        )
        return 1

    print("\n✅ All addons_path /mnt/* entries have matching compose bind mounts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
