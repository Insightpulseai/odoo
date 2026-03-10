#!/usr/bin/env python3
from __future__ import annotations

"""Validate Azure SSOT consistency across target-state, service-matrix, and dns-migration-plan.

Checks:
  - All 3 required SSOT files exist: target-state.yaml, service-matrix.yaml, dns-migration-plan.yaml
  - Each file is parseable YAML
  - service-matrix.yaml has a ``parent`` field pointing to ssot/azure/target-state.yaml
  - dns-migration-plan.yaml has a ``parent`` field pointing to ssot/azure/target-state.yaml
  - All ``promotion_state`` values in service-matrix are from the allowed set
  - All ``migration_state`` values in dns-migration-plan are from the allowed set
  - ``erp_positioning.prohibited_terms`` exists in service-matrix and warns if spec/ docs contain them

Exit 0 on pass, exit 1 on fail.
Uses only stdlib -- no pip dependencies.
"""

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SSOT_DIR = os.path.join(REPO_ROOT, "ssot", "azure")
SPEC_DIR = os.path.join(REPO_ROOT, "spec")

REQUIRED_FILES = [
    "target-state.yaml",
    "service-matrix.yaml",
    "dns-migration-plan.yaml",
]

EXPECTED_PARENT = "ssot/azure/target-state.yaml"

ALLOWED_PROMOTION_STATES = {"repo-only", "configured", "deployed", "live"}
ALLOWED_MIGRATION_STATES = {"pending", "in_progress", "complete", "deprecated"}


# ---------------------------------------------------------------------------
# Minimal YAML loader (stdlib only, no PyYAML required)
# ---------------------------------------------------------------------------

def load_yaml(path: str):
    """Load YAML file using PyYAML if available, otherwise a minimal fallback."""
    try:
        import yaml  # type: ignore[import-untyped]

        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        return _fallback_yaml_load(path)


def _fallback_yaml_load(path: str):
    """Minimal YAML parser for flat/nested key-value structures.

    Handles enough YAML to validate SSOT files: top-level scalars, nested dicts,
    and lists of dicts.  Does NOT handle multi-line strings, anchors, etc.
    Returns None if file is empty.
    """
    result: dict = {}
    stack: list[tuple[int, dict]] = [(-1, result)]
    current_list_key: str | None = None

    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip()
            # Skip blanks and comments
            if not line or line.lstrip().startswith("#"):
                continue

            stripped = line.lstrip()
            indent = len(line) - len(stripped)

            # Pop stack to correct level
            while len(stack) > 1 and indent <= stack[-1][0]:
                stack.pop()

            parent = stack[-1][1]

            # List item
            if stripped.startswith("- "):
                item_text = stripped[2:].strip()
                if ":" in item_text:
                    key, _, value = item_text.partition(":")
                    key = key.strip().strip('"').strip("'")
                    value = value.strip().strip('"').strip("'")
                    new_item: dict = {key: value} if value else {key: {}}
                    if current_list_key and current_list_key in parent:
                        if isinstance(parent[current_list_key], list):
                            parent[current_list_key].append(new_item)
                        else:
                            parent[current_list_key] = [new_item]
                    stack.append((indent + 2, new_item))
                continue

            if ":" not in stripped:
                continue

            key, _, value = stripped.partition(":")
            key = key.strip().strip('"').strip("'")
            value = value.strip().strip('"').strip("'")

            if value:
                parent[key] = value
            else:
                # New nested dict or list
                new_dict: dict = {}
                parent[key] = new_dict
                stack.append((indent, new_dict))
                current_list_key = key

    return result if result else None


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

def collect_values_recursive(data, target_key: str) -> list[str]:
    """Recursively find all values for a given key in nested dicts/lists."""
    values: list[str] = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k == target_key and isinstance(v, str):
                values.append(v)
            else:
                values.extend(collect_values_recursive(v, target_key))
    elif isinstance(data, list):
        for item in data:
            values.extend(collect_values_recursive(item, target_key))
    return values


def get_nested(data, *keys):
    """Safely traverse nested dicts."""
    current = data
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return None
    return current


def scan_spec_for_terms(terms: list[str]) -> list[str]:
    """Scan spec/ directory for prohibited terms. Returns list of warnings."""
    warnings: list[str] = []
    if not os.path.isdir(SPEC_DIR):
        return warnings

    for root, _dirs, files in os.walk(SPEC_DIR):
        for fname in files:
            if not fname.endswith((".md", ".yaml", ".yml")):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read().lower()
            except Exception:
                continue

            rel_path = os.path.relpath(fpath, REPO_ROOT)
            for term in terms:
                if term.lower() in content:
                    warnings.append(
                        f'Prohibited term "{term}" found in {rel_path}'
                    )
    return warnings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    errors: list[str] = []
    info: list[str] = []

    # ------------------------------------------------------------------
    # 1. Check SSOT directory exists
    # ------------------------------------------------------------------
    if not os.path.isdir(SSOT_DIR):
        errors.append(f"SSOT directory missing: ssot/azure/")
        return _report(errors, info)

    # ------------------------------------------------------------------
    # 2. Check all required files exist
    # ------------------------------------------------------------------
    loaded: dict[str, dict | None] = {}
    for fname in REQUIRED_FILES:
        fpath = os.path.join(SSOT_DIR, fname)
        if not os.path.isfile(fpath):
            errors.append(f"Required SSOT file missing: ssot/azure/{fname}")
            loaded[fname] = None
        else:
            try:
                data = load_yaml(fpath)
                if data is None:
                    errors.append(f"ssot/azure/{fname} is empty or unparseable")
                else:
                    info.append(f"ssot/azure/{fname} parsed OK")
                loaded[fname] = data
            except Exception as exc:
                errors.append(f"ssot/azure/{fname} YAML parse error: {exc}")
                loaded[fname] = None

    # ------------------------------------------------------------------
    # 3. Validate parent field in service-matrix.yaml
    # ------------------------------------------------------------------
    sm = loaded.get("service-matrix.yaml")
    if sm is not None:
        parent = sm.get("parent") if isinstance(sm, dict) else None
        if parent is None:
            errors.append(
                f'service-matrix.yaml: missing "parent" field '
                f'(expected: "{EXPECTED_PARENT}")'
            )
        elif str(parent) != EXPECTED_PARENT:
            errors.append(
                f'service-matrix.yaml: "parent" is "{parent}" '
                f'but expected "{EXPECTED_PARENT}"'
            )
        else:
            info.append(f"service-matrix.yaml parent field: OK")

    # ------------------------------------------------------------------
    # 4. Validate parent field in dns-migration-plan.yaml
    # ------------------------------------------------------------------
    dns = loaded.get("dns-migration-plan.yaml")
    if dns is not None:
        parent = dns.get("parent") if isinstance(dns, dict) else None
        if parent is None:
            errors.append(
                f'dns-migration-plan.yaml: missing "parent" field '
                f'(expected: "{EXPECTED_PARENT}")'
            )
        elif str(parent) != EXPECTED_PARENT:
            errors.append(
                f'dns-migration-plan.yaml: "parent" is "{parent}" '
                f'but expected "{EXPECTED_PARENT}"'
            )
        else:
            info.append(f"dns-migration-plan.yaml parent field: OK")

    # ------------------------------------------------------------------
    # 5. Validate promotion_state values in service-matrix.yaml
    # ------------------------------------------------------------------
    if sm is not None:
        promo_states = collect_values_recursive(sm, "promotion_state")
        if promo_states:
            info.append(f"Found {len(promo_states)} promotion_state value(s)")
            for ps in promo_states:
                if ps not in ALLOWED_PROMOTION_STATES:
                    errors.append(
                        f'service-matrix.yaml: invalid promotion_state "{ps}" '
                        f"(allowed: {sorted(ALLOWED_PROMOTION_STATES)})"
                    )
        else:
            info.append("service-matrix.yaml: no promotion_state fields found (OK if not yet added)")

    # ------------------------------------------------------------------
    # 6. Validate migration_state values in dns-migration-plan.yaml
    # ------------------------------------------------------------------
    if dns is not None:
        mig_states = collect_values_recursive(dns, "migration_state")
        if mig_states:
            info.append(f"Found {len(mig_states)} migration_state value(s)")
            for ms in mig_states:
                if ms not in ALLOWED_MIGRATION_STATES:
                    errors.append(
                        f'dns-migration-plan.yaml: invalid migration_state "{ms}" '
                        f"(allowed: {sorted(ALLOWED_MIGRATION_STATES)})"
                    )
        else:
            info.append("dns-migration-plan.yaml: no migration_state fields found (OK if not yet added)")

    # ------------------------------------------------------------------
    # 7. Check erp_positioning.prohibited_terms and scan spec/
    # ------------------------------------------------------------------
    if sm is not None:
        erp_pos = get_nested(sm, "erp_positioning")
        if erp_pos is None:
            info.append(
                "service-matrix.yaml: no erp_positioning section found (OK if not yet added)"
            )
        else:
            prohibited = None
            if isinstance(erp_pos, dict):
                prohibited = erp_pos.get("prohibited_terms")
            if prohibited is None:
                info.append(
                    "service-matrix.yaml: erp_positioning exists but no prohibited_terms list"
                )
            else:
                # prohibited_terms may be a list or a comma-separated string
                if isinstance(prohibited, str):
                    terms = [t.strip() for t in prohibited.split(",") if t.strip()]
                elif isinstance(prohibited, list):
                    terms = [str(t).strip() for t in prohibited if str(t).strip()]
                else:
                    terms = []

                if terms:
                    info.append(f"Checking {len(terms)} prohibited terms against spec/ docs")
                    term_warnings = scan_spec_for_terms(terms)
                    for tw in term_warnings:
                        info.append(f"WARN: {tw}")

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    return _report(errors, info)


def _report(errors: list[str], info: list[str]) -> int:
    print("=" * 60)
    print("Azure SSOT Consistency Validator")
    print("=" * 60)

    if info:
        for i in info:
            print(f"  INFO: {i}")

    if errors:
        print()
        for e in errors:
            print(f"  FAIL: {e}")
        print()
        print(f"Result: FAILED ({len(errors)} error(s))")
        print("=" * 60)
        return 1

    print()
    print("  All Azure SSOT checks passed.")
    print()
    print("Result: PASSED")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
