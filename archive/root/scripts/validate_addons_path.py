#!/usr/bin/env python3
"""
validate_addons_path.py — CI guardrail for addons_path / compose mount parity.

Invariant: every path segment in infra/odoo.conf addons_path that starts with
/mnt/ must have a corresponding bind-mount in the ipai-odoo service in
infra/stack/compose.stack.yml.

Exit codes:
  0 — all checks pass
  1 — one or more entries are missing a bind mount OR odoo field check failed
  2 — script error (bad config path, parse error, etc.)

Usage:
  # Filesystem parity only (CI default — no DB required):
  python3 scripts/validate_addons_path.py

  # Semantic field check against a running container (prod / staging):
  python3 scripts/validate_addons_path.py --odoo-check
  python3 scripts/validate_addons_path.py --odoo-check --container ipai-odoo --db odoo_prod

  # Explicit paths:
  python3 scripts/validate_addons_path.py --conf infra/odoo.conf --compose infra/stack/compose.stack.yml
"""

import argparse
import configparser
import re
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths (relative to repo root — resolved from script location)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONF = REPO_ROOT / "infra" / "odoo.conf"
DEFAULT_COMPOSE = REPO_ROOT / "infra" / "stack" / "compose.stack.yml"

# Fields we assert must be registered on res.config.settings.
# Add more here if additional OCA compat shims are needed.
REQUIRED_FIELDS = [
    ("res.config.settings", "anglo_saxon_accounting"),
]


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_addons_path(conf_path: Path) -> list[str]:
    """Return the list of addons_path entries from an odoo.conf file."""
    if not conf_path.exists():
        raise FileNotFoundError(f"odoo.conf not found: {conf_path}")

    content = conf_path.read_text()
    # Strip ${VAR} markers (not valid in configparser)
    content_cleaned = re.sub(r"\$\{[^}]+\}", "PLACEHOLDER", content)
    # Inject [options] section header only if absent
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
    Return the list of container-side paths bound in the odoo service
    by scanning compose YAML for lines of the form:
      - <host_path>:<container_path>[:<options>]

    Line-by-line parse — no external YAML library required.
    """
    if not compose_path.exists():
        raise FileNotFoundError(f"compose file not found: {compose_path}")

    lines = compose_path.read_text().splitlines()

    # Locate the odoo service block: starts at "  odoo:" and ends at next sibling.
    service_re = re.compile(r"^  \w[\w-]*:")
    volume_re = re.compile(r"^\s+-\s+([^:]+):(/[^:\s]+)")

    in_odoo = False
    odoo_lines: list[str] = []

    for line in lines:
        if service_re.match(line):
            if line.startswith("  odoo:"):
                in_odoo = True
            elif in_odoo:
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


# ---------------------------------------------------------------------------
# Semantic field check (requires running Odoo container)
# ---------------------------------------------------------------------------

_ODOO_CHECK_SCRIPT = """\
import sys
try:
    import odoo
    from odoo.tools import config
    config.parse_config(["--no-http"])
    from odoo import api, SUPERUSER_ID, registry as odoo_registry
    reg = odoo_registry({db!r})
    with reg.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {{}})
        fields = env[{model!r}].fields_get()
        if {field!r} in fields:
            print("FIELD_OK: {{model}}.{{field}} is registered".format(
                model={model!r}, field={field!r}))
            sys.exit(0)
        else:
            print("FIELD_MISSING: {{model}}.{{field}} NOT in fields_get()".format(
                model={model!r}, field={field!r}))
            sys.exit(1)
except Exception as exc:
    print(f"FIELD_CHECK_ERROR: {{exc}}")
    sys.exit(2)
"""


def odoo_field_check(container: str, db: str) -> bool:
    """
    Run a tiny Odoo Python snippet inside *container* to verify that
    every (model, field) pair in REQUIRED_FIELDS is registered at runtime.

    Returns True if all fields are present; False otherwise.
    Requires `docker` to be available on the host PATH.
    """
    all_ok = True
    for model, field in REQUIRED_FIELDS:
        script = _ODOO_CHECK_SCRIPT.format(db=db, model=model, field=field)
        result = subprocess.run(
            ["docker", "exec", container, "python3", "-c", script],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = (result.stdout + result.stderr).strip()
        if result.returncode == 0:
            print(f"  ✅ {output}")
        else:
            print(f"  ❌ {output}", file=sys.stderr)
            all_ok = False
    return all_ok


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--conf", default=str(DEFAULT_CONF), help="Path to odoo.conf")
    parser.add_argument("--compose", default=str(DEFAULT_COMPOSE),
                        help="Path to compose.stack.yml")
    parser.add_argument("--odoo-check", action="store_true",
                        help="Also verify required fields exist in the running Odoo container")
    parser.add_argument("--container", default="ipai-odoo",
                        help="Docker container name for --odoo-check (default: ipai-odoo)")
    parser.add_argument("--db", default="odoo_prod",
                        help="Odoo database name for --odoo-check (default: odoo_prod)")
    args = parser.parse_args()

    conf_path = Path(args.conf)
    compose_path = Path(args.compose)
    rc = 0

    # ------------------------------------------------------------------
    # Phase 1: filesystem parity
    # ------------------------------------------------------------------
    print("=== Phase 1: addons_path ↔ compose mount parity ===")
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

    mnt_entries = [p for p in addons_entries if p.startswith("/mnt/")]
    mounted_set = set(mounted_paths)
    missing = [p for p in mnt_entries if p not in mounted_set]

    print(f"  addons_path /mnt/* entries : {len(mnt_entries)}")
    print(f"  compose bind-mounts found  : {len(mounted_paths)}")
    print(f"  missing bind-mounts        : {len(missing)}")

    if missing:
        print("\n  ❌ MISSING BIND MOUNTS:", file=sys.stderr)
        for p in sorted(missing):
            if p.startswith("/mnt/oca/"):
                host = f"../../addons/oca/{p.removeprefix('/mnt/oca/')}"
            else:
                host = "../../addons/ipai"
            print(f"    - {host}:{p}:ro", file=sys.stderr)
        print(
            "\n  Fix: edit infra/stack/compose.stack.yml and add the missing volumes,\n"
            "  then run git-aggregator to hydrate the missing repos.",
            file=sys.stderr,
        )
        rc = 1
    else:
        print("  ✅ All addons_path /mnt/* entries have matching compose bind mounts.")

    # ------------------------------------------------------------------
    # Phase 2: semantic Odoo field check (optional)
    # ------------------------------------------------------------------
    if args.odoo_check:
        print(f"\n=== Phase 2: Odoo runtime field check (container={args.container}, db={args.db}) ===")
        try:
            ok = odoo_field_check(args.container, args.db)
        except FileNotFoundError:
            print("ERROR: 'docker' not found on PATH — cannot run --odoo-check", file=sys.stderr)
            return 2
        except subprocess.TimeoutExpired:
            print("ERROR: --odoo-check timed out (container may be starting up)", file=sys.stderr)
            return 2
        except Exception as exc:
            print(f"ERROR during --odoo-check: {exc}", file=sys.stderr)
            return 2

        if not ok:
            rc = 1
        else:
            print("  ✅ All required Odoo fields are registered at runtime.")

    return rc


if __name__ == "__main__":
    sys.exit(main())
