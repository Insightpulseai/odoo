#!/usr/bin/env python3
"""
validate_parity_targets.py
CI gate for ERP SaaS parity SSOT.

Checks:
  1. Schema validity for every entry in parity_targets.yaml
  2. OCA modules referenced under resolution OCA/PORT are in oca_installed_allowlist.yaml
  3. BRIDGE capabilities have a non-null runbook that exists under docs/ops/ or docs/architecture/
  4. GAP/blocked capabilities have a non-empty notes field
  5. ipai_* connectors referenced exist in addons/ipai/ as directories

Exit codes:
  0 = all checks pass
  1 = validation failures found
  2 = missing dependency / file not found error
"""

import sys
import pathlib
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PARITY_YAML = REPO_ROOT / "odoo" / "ssot" / "parity_targets.yaml"
ALLOWLIST_YAML = REPO_ROOT / "odoo" / "ssot" / "oca_installed_allowlist.yaml"
IPAI_ADDONS = REPO_ROOT / "addons" / "ipai"

VALID_RESOLUTIONS = {"CE", "OCA", "PORT", "BRIDGE", "GAP"}
VALID_STATUSES = {"installed", "partial", "planned", "blocked"}


def load_yaml(path: pathlib.Path) -> dict:
    if not path.exists():
        print(f"[ERROR] Required file not found: {path.relative_to(REPO_ROOT)}", file=sys.stderr)
        sys.exit(2)
    with open(path) as f:
        return yaml.safe_load(f)


def load_allowlist() -> set[str]:
    """Returns set of allowed OCA module names (empty set if no allowlist yet)."""
    if not ALLOWLIST_YAML.exists():
        return set()
    data = load_yaml(ALLOWLIST_YAML)
    return set(data.get("oca_modules", []))


def check_runbook_exists(runbook: str) -> bool:
    """Runbook path is relative to repo root."""
    if not runbook:
        return False
    return (REPO_ROOT / runbook).exists()


def check_ipai_connector(connector: str) -> bool:
    """Connector module must have a directory in addons/ipai/."""
    return (IPAI_ADDONS / connector).is_dir()


def validate(targets: list, allowlist: set) -> list[str]:
    errors = []
    seen_ids = set()

    for entry in targets:
        cap_id = entry.get("capability_id", "<no id>")
        name = entry.get("name", "<no name>")
        label = f"{cap_id} ({name})"

        # 1. No duplicate IDs
        if cap_id in seen_ids:
            errors.append(f"[{label}] Duplicate capability_id: {cap_id}")
        seen_ids.add(cap_id)

        # 2. Required fields
        for field in ("capability_id", "name", "resolution", "status"):
            if not entry.get(field):
                errors.append(f"[{label}] Missing required field: {field}")

        # 3. Valid resolution
        resolution = entry.get("resolution", "")
        if resolution not in VALID_RESOLUTIONS:
            errors.append(f"[{label}] Invalid resolution '{resolution}'. Must be one of {VALID_RESOLUTIONS}")

        # 4. Valid status
        status = entry.get("status", "")
        if status not in VALID_STATUSES:
            errors.append(f"[{label}] Invalid status '{status}'. Must be one of {VALID_STATUSES}")

        oca_modules = entry.get("oca_modules") or []
        ipai_connectors = entry.get("ipai_connectors") or []
        bridge_services = entry.get("bridge_services") or []
        runbook = entry.get("runbook")
        notes = entry.get("notes") or ""

        # 5. OCA/PORT: all referenced modules must be in allowlist (if allowlist exists)
        if resolution in ("OCA", "PORT") and allowlist:
            for mod in oca_modules:
                if mod not in allowlist:
                    errors.append(
                        f"[{label}] OCA module '{mod}' not in oca_installed_allowlist.yaml"
                    )

        # 6. BRIDGE: must have a runbook, and the runbook file must exist
        if resolution == "BRIDGE":
            if not runbook:
                errors.append(
                    f"[{label}] BRIDGE capability must have a runbook path"
                )
            elif not check_runbook_exists(runbook):
                errors.append(
                    f"[{label}] BRIDGE runbook does not exist: {runbook}"
                )
            if not bridge_services:
                errors.append(
                    f"[{label}] BRIDGE capability must list at least one bridge_service"
                )

        # 7. GAP/blocked: must have a non-empty notes rationale
        if resolution == "GAP" or status == "blocked":
            if not notes.strip():
                errors.append(
                    f"[{label}] GAP/blocked capability must have a notes rationale"
                )

        # 8. ipai_* connectors must exist in addons/ipai/ (if IPAI_ADDONS dir present)
        if IPAI_ADDONS.exists():
            for connector in ipai_connectors:
                if not connector.startswith("ipai_"):
                    errors.append(
                        f"[{label}] ipai_connectors entry '{connector}' must start with 'ipai_'"
                    )
                elif not check_ipai_connector(connector):
                    errors.append(
                        f"[{label}] ipai connector '{connector}' not found in addons/ipai/"
                    )

    return errors


def main() -> int:
    data = load_yaml(PARITY_YAML)
    targets = data.get("parity_targets", [])
    if not targets:
        print("[ERROR] parity_targets.yaml has no entries under 'parity_targets:'", file=sys.stderr)
        return 2

    allowlist = load_allowlist()
    if allowlist:
        print(f"[INFO] Allowlist loaded: {len(allowlist)} OCA modules")
    else:
        print("[INFO] No oca_installed_allowlist.yaml found — skipping allowlist cross-check")

    errors = validate(targets, allowlist)

    if errors:
        print(f"\n[FAIL] {len(errors)} validation error(s) found:\n")
        for e in errors:
            print(f"  ✗ {e}")
        return 1

    print(f"[PASS] {len(targets)} parity targets validated — no errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
