#!/usr/bin/env python3
"""Validate cross-layer consistency across the three governance YAML files.

Checks:
  1. KPI foreign keys: all kpi_ref values in enterprise_okrs.yaml (both
     strategic_objectives and canonical_okrs key_results) exist in
     control_room_kpis.yaml kpis[].id
  2. Parent objective integrity: all parent_objectives[] in canonical_okrs
     reference valid strategic_objectives[].id within enterprise_okrs.yaml
  3. KPI index consistency: kpi_index keys are valid objective IDs (from
     strategic_objectives), values are valid KPI IDs (from control_room_kpis)
  4. KPI namespace overlap (WARN): KPI IDs used in platform-strategy-2026.yaml
     kpis[].id should overlap with kpi_ref values used in enterprise_okrs.yaml.
     Strategy OBJ-001..007 vs operational obj_A..E are complementary, not 1:1.
  5. Planning index crosswalk integrity (WARN): crosswalks[].from and
     crosswalks[].to layer references should contain known layer IDs from the
     planning index. Unparseable or non-matching references are soft warnings.

Exit 0 on success, 1 on validation failure (checks 1-3).
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

ENTERPRISE_OKRS = REPO_ROOT / "ssot" / "governance" / "enterprise_okrs.yaml"
STRATEGY = REPO_ROOT / "ssot" / "governance" / "platform-strategy-2026.yaml"
KPI_CONTRACTS = REPO_ROOT / "platform" / "data" / "contracts" / "control_room_kpis.yaml"
PLANNING_INDEX = REPO_ROOT / "ssot" / "governance" / "planning_system_index.yaml"

try:
    import yaml
except ImportError:
    yaml = None


def load_yaml(path: Path) -> dict:
    text = path.read_text()
    if yaml is not None:
        return yaml.safe_load(text)
    import json
    try:
        return json.loads(text)
    except Exception:
        print(f"ERROR: PyYAML not installed and {path.name} is not JSON-compatible.")
        print("       Install: pip install pyyaml")
        sys.exit(1)


def _report(errors: list[str], warnings: list[str]) -> None:
    if warnings:
        print(f"\n{'=' * 60}")
        print(f"WARN: {len(warnings)} warning(s)")
        print(f"{'=' * 60}")
        for i, w in enumerate(warnings, 1):
            print(f"  {i}. {w}")
    if errors:
        print(f"\n{'=' * 60}")
        print(f"FAIL: {len(errors)} error(s)")
        print(f"{'=' * 60}")
        for i, e in enumerate(errors, 1):
            print(f"  {i}. {e}")
    if not errors and not warnings:
        print(f"\n{'=' * 60}")
        print("PASS: All checks passed")
        print(f"{'=' * 60}")
    elif not errors:
        print(f"\n{'=' * 60}")
        print("PASS: All hard checks passed (warnings noted above)")
        print(f"{'=' * 60}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    # --- File existence checks ---
    missing = [p for p in (ENTERPRISE_OKRS, STRATEGY, KPI_CONTRACTS, PLANNING_INDEX) if not p.exists()]
    if missing:
        for p in missing:
            print(f"FAIL: Required file not found: {p.relative_to(REPO_ROOT)}")
        return 1

    print(f"Loading {ENTERPRISE_OKRS.relative_to(REPO_ROOT)} ...")
    okrs_data = load_yaml(ENTERPRISE_OKRS)
    print(f"Loading {STRATEGY.relative_to(REPO_ROOT)} ...")
    strategy_data = load_yaml(STRATEGY)
    print(f"Loading {KPI_CONTRACTS.relative_to(REPO_ROOT)} ...")
    kpi_data = load_yaml(KPI_CONTRACTS)
    print(f"Loading {PLANNING_INDEX.relative_to(REPO_ROOT)} ...")
    index_data = load_yaml(PLANNING_INDEX)

    for label, data in (
        ("enterprise_okrs.yaml", okrs_data),
        ("platform-strategy-2026.yaml", strategy_data),
        ("control_room_kpis.yaml", kpi_data),
        ("planning_system_index.yaml", index_data),
    ):
        if data is None:
            errors.append(f"{label} parsed to None (empty file?)")

    if errors:
        _report(errors, warnings)
        return 1

    # --- Build lookup sets ---
    # KPI IDs from the canonical registry
    registry_kpi_ids: set[str] = {
        kpi.get("id") for kpi in kpi_data.get("kpis", []) if kpi.get("id")
    }

    # Strategic objective IDs from enterprise_okrs.yaml
    strategic_obj_ids: set[str] = {
        obj.get("id")
        for obj in okrs_data.get("strategic_objectives", [])
        if obj.get("id")
    }

    # KPI IDs referenced via kpi_ref anywhere in enterprise_okrs.yaml
    okr_kpi_refs: set[str] = set()

    for obj in okrs_data.get("strategic_objectives", []):
        for kr in obj.get("key_results", []):
            ref = kr.get("kpi_ref")
            if ref:
                okr_kpi_refs.add(ref)

    for okr in okrs_data.get("canonical_okrs", []):
        for kr in okr.get("key_results", []):
            ref = kr.get("kpi_ref")
            if ref:
                okr_kpi_refs.add(ref)

    # KPI IDs from platform-strategy-2026.yaml kpis[].id
    strategy_kpi_ids: set[str] = {
        kpi.get("id")
        for kpi in strategy_data.get("kpis", [])
        if kpi.get("id")
    }

    # Layer IDs from planning_system_index.yaml
    index_layer_ids: set[str] = {
        layer.get("id")
        for layer in index_data.get("layers", [])
        if layer.get("id")
    }

    # --- Check 1: KPI foreign keys ---
    print("\nCheck 1: KPI foreign keys (kpi_ref → control_room_kpis.yaml) ...")
    check1_errors: list[str] = []

    for obj in okrs_data.get("strategic_objectives", []):
        obj_id = obj.get("id", "<unknown>")
        for kr in obj.get("key_results", []):
            ref = kr.get("kpi_ref")
            if ref and ref not in registry_kpi_ids:
                check1_errors.append(
                    f"strategic_objectives[{obj_id}] key_result kpi_ref '{ref}' "
                    f"not found in control_room_kpis.yaml"
                )

    for okr in okrs_data.get("canonical_okrs", []):
        okr_id = okr.get("id", "<unknown>")
        for kr in okr.get("key_results", []):
            ref = kr.get("kpi_ref")
            if ref and ref not in registry_kpi_ids:
                check1_errors.append(
                    f"canonical_okrs[{okr_id}] key_result kpi_ref '{ref}' "
                    f"not found in control_room_kpis.yaml"
                )

    if check1_errors:
        errors.extend(check1_errors)
        for msg in check1_errors:
            print(f"  FAIL: {msg}")
    else:
        print(f"  PASS ({len(okr_kpi_refs)} kpi_ref values all resolve)")

    # --- Check 2: Parent objective integrity ---
    print("\nCheck 2: Parent objective integrity (parent_objectives → strategic_objectives) ...")
    check2_errors: list[str] = []

    for okr in okrs_data.get("canonical_okrs", []):
        okr_id = okr.get("id", "<unknown>")
        for parent_ref in okr.get("parent_objectives", []):
            if parent_ref not in strategic_obj_ids:
                check2_errors.append(
                    f"canonical_okrs[{okr_id}] parent_objectives contains '{parent_ref}' "
                    f"which is not a valid strategic_objectives[].id"
                )

    if check2_errors:
        errors.extend(check2_errors)
        for msg in check2_errors:
            print(f"  FAIL: {msg}")
    else:
        total_parents = sum(
            len(okr.get("parent_objectives", []))
            for okr in okrs_data.get("canonical_okrs", [])
        )
        print(f"  PASS ({total_parents} parent_objectives references all resolve)")

    # --- Check 3: KPI index consistency ---
    print("\nCheck 3: KPI index consistency (kpi_index keys → strategic_objectives, values → kpis) ...")
    check3_errors: list[str] = []

    kpi_index = okrs_data.get("kpi_index", {})
    if not isinstance(kpi_index, dict):
        check3_errors.append("kpi_index is not a dict/mapping")
    else:
        for obj_key, kpi_list in kpi_index.items():
            if obj_key not in strategic_obj_ids:
                check3_errors.append(
                    f"kpi_index key '{obj_key}' is not a valid strategic_objectives[].id"
                )
            if not isinstance(kpi_list, list):
                check3_errors.append(
                    f"kpi_index[{obj_key}] value is not a list"
                )
                continue
            for kpi_val in kpi_list:
                if kpi_val not in registry_kpi_ids:
                    check3_errors.append(
                        f"kpi_index[{obj_key}] contains '{kpi_val}' "
                        f"which is not a valid KPI ID in control_room_kpis.yaml"
                    )

    if check3_errors:
        errors.extend(check3_errors)
        for msg in check3_errors:
            print(f"  FAIL: {msg}")
    else:
        total_index_entries = sum(
            len(v) for v in kpi_index.values() if isinstance(v, list)
        )
        print(
            f"  PASS ({len(kpi_index)} objective keys, "
            f"{total_index_entries} KPI entries all valid)"
        )

    # --- Check 4: KPI namespace overlap (WARN only) ---
    print("\nCheck 4: KPI namespace overlap (strategy kpis vs enterprise_okrs kpi_refs) [WARN] ...")

    if not strategy_kpi_ids:
        warnings.append(
            "platform-strategy-2026.yaml has no kpis[].id entries — overlap check skipped"
        )
        print("  WARN: No strategy KPI IDs found — skipping overlap check")
    elif not okr_kpi_refs:
        warnings.append(
            "enterprise_okrs.yaml has no kpi_ref values — overlap check skipped"
        )
        print("  WARN: No kpi_ref values found in enterprise_okrs.yaml — skipping overlap check")
    else:
        overlap = strategy_kpi_ids & okr_kpi_refs
        strategy_only = strategy_kpi_ids - okr_kpi_refs
        okr_only = okr_kpi_refs - strategy_kpi_ids

        if not overlap:
            msg = (
                f"No KPI ID overlap between platform-strategy-2026.yaml kpis[].id "
                f"({sorted(strategy_kpi_ids)}) and enterprise_okrs.yaml kpi_refs "
                f"({sorted(okr_kpi_refs)}). "
                f"Strategy OBJ-001..007 and operational obj_A..E are complementary layers."
            )
            warnings.append(msg)
            print(f"  WARN: {msg}")
        else:
            print(
                f"  PASS ({len(overlap)} overlapping KPI IDs; "
                f"{len(strategy_only)} strategy-only; "
                f"{len(okr_only)} okr-only — complementary layers)"
            )
            if strategy_only:
                print(f"    strategy-only: {sorted(strategy_only)}")
            if okr_only:
                print(f"    okr-only: {sorted(okr_only)}")

    # --- Check 5: Planning index crosswalk integrity (WARN only) ---
    print("\nCheck 5: Planning index crosswalk integrity [WARN] ...")

    crosswalks = index_data.get("crosswalks", [])
    if not crosswalks:
        warnings.append("planning_system_index.yaml has no crosswalks — integrity check skipped")
        print("  WARN: No crosswalks found — skipping check")
    else:
        crosswalk_issues: list[str] = []
        for i, cw in enumerate(crosswalks):
            for side in ("from", "to"):
                ref = cw.get(side, "")
                if not isinstance(ref, str) or not ref:
                    crosswalk_issues.append(
                        f"crosswalks[{i}].{side} is missing or not a string"
                    )
                    continue
                # Extract the layer ID: take the first segment before "." or "["
                # e.g. "strategy.objectives[].id" → "strategy"
                # e.g. "platform/data/contracts/control_room_kpis.yaml" → treat as external ref
                segment = ref.split(".")[0].split("[")[0].strip()
                # Skip obvious path-like or glob references
                if "/" in segment or segment == "*":
                    continue
                if segment and segment not in index_layer_ids:
                    crosswalk_issues.append(
                        f"crosswalks[{i}].{side} = '{ref}': "
                        f"layer segment '{segment}' not in known layer IDs "
                        f"{sorted(index_layer_ids)}"
                    )

        if crosswalk_issues:
            for msg in crosswalk_issues:
                warnings.append(msg)
                print(f"  WARN: {msg}")
        else:
            print(
                f"  PASS ({len(crosswalks)} crosswalk entries; "
                f"all resolvable layer references match known layer IDs)"
            )

    _report(errors, warnings)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
