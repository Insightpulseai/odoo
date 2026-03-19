#!/usr/bin/env python3
"""Validate ssot/governance/planning_system_index.yaml structural integrity.

Checks:
  1. YAML parses without error
  2. Required top-level keys present: schema_version, last_updated, layers, crosswalks, governance
  3. Each layer has required fields: id, name, canonical_file, owner, cadence
  4. Layers with status != "not_on_branch" (or no status): canonical_file exists on disk
     Layers with status == "not_on_branch": print WARNING and skip file-existence check
  5. Layers with a `validator` field: validator script file exists on disk
  6. Layers with a `ci_gate` field: workflow file exists on disk
  7. Layer IDs are unique

Exit 0 on success, 1 on failure.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SSOT_YAML = REPO_ROOT / "ssot" / "governance" / "planning_system_index.yaml"

try:
    import yaml
except ImportError:
    yaml = None


def load_yaml(path: Path) -> dict:
    text = path.read_text()
    if yaml is not None:
        return yaml.safe_load(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print("ERROR: PyYAML not installed and file is not JSON-compatible.")
        print("       Install: pip install pyyaml")
        sys.exit(1)


REQUIRED_TOP_LEVEL = {"schema_version", "last_updated", "layers", "crosswalks", "governance"}
REQUIRED_LAYER_FIELDS = {"id", "name", "canonical_file", "owner", "cadence"}


def _report(errors: list[str]) -> None:
    if errors:
        print(f"\n{'=' * 60}")
        print(f"FAIL: {len(errors)} error(s)")
        print(f"{'=' * 60}")
        for i, e in enumerate(errors, 1):
            print(f"  {i}. {e}")
    else:
        print(f"\n{'=' * 60}")
        print("PASS: All checks passed")
        print(f"{'=' * 60}")


def main() -> int:
    errors: list[str] = []

    if not SSOT_YAML.exists():
        print(f"FAIL: SSOT file not found: {SSOT_YAML}")
        return 1

    # --- Check 1: YAML parses ---
    print(f"Parsing {SSOT_YAML.relative_to(REPO_ROOT)} ...")
    try:
        data = load_yaml(SSOT_YAML)
    except Exception as exc:
        errors.append(f"Check 1: YAML parse error: {exc}")
        _report(errors)
        return 1

    if data is None:
        errors.append("Check 1: YAML parse: FAIL (parsed to None — empty file?)")
        _report(errors)
        return 1
    print("  Check 1: YAML parses: PASS")

    # --- Check 2: Required top-level keys ---
    print("Checking required top-level keys ...")
    present_keys = set(data.keys())
    missing_keys = REQUIRED_TOP_LEVEL - present_keys
    if missing_keys:
        errors.append(
            f"Check 2: required top-level keys missing: {sorted(missing_keys)}"
        )
    else:
        print(f"  Check 2: required top-level keys ({', '.join(sorted(REQUIRED_TOP_LEVEL))}): PASS")

    # --- Check 3: Each layer has required fields ---
    print("Checking layer required fields ...")
    layers = data.get("layers", [])
    if not isinstance(layers, list):
        errors.append("Check 3: `layers` is not a list")
        _report(errors)
        return 1

    layer_field_errors: list[str] = []
    for i, layer in enumerate(layers):
        if not isinstance(layer, dict):
            layer_field_errors.append(f"layers[{i}] is not a dict")
            continue
        layer_id = layer.get("id", f"<index {i}>")
        for field in REQUIRED_LAYER_FIELDS:
            if field not in layer:
                layer_field_errors.append(
                    f"layer '{layer_id}' missing required field: {field}"
                )

    if layer_field_errors:
        for e in layer_field_errors:
            errors.append(f"Check 3: {e}")
    else:
        print(f"  Check 3: all {len(layers)} layers have required fields: PASS")

    # --- Check 4: canonical_file exists on disk (skip not_on_branch) ---
    print("Checking canonical_file existence ...")
    active_layers = 0
    deferred_layers = 0
    file_check_errors: list[str] = []

    for layer in layers:
        if not isinstance(layer, dict):
            continue
        layer_id = layer.get("id", "<unknown>")
        status = layer.get("status", "on_main")
        canonical_file = layer.get("canonical_file", "")

        if status == "not_on_branch":
            deferred_layers += 1
            print(
                f"  Check 4: layer '{layer_id}' ({canonical_file}): "
                f"WARN (status=not_on_branch — skipping file check)"
            )
            continue

        active_layers += 1

        # Handle glob pattern (e.g. spec/*/) — check that base dir exists
        if canonical_file.endswith("/") or "*" in canonical_file:
            base_dir = canonical_file.split("*")[0].rstrip("/")
            target_path = REPO_ROOT / base_dir
            if not target_path.exists():
                file_check_errors.append(
                    f"layer '{layer_id}': base directory for '{canonical_file}' not found: {base_dir}/"
                )
            else:
                print(f"  Check 4: layer '{layer_id}' ({canonical_file}): PASS (dir exists)")
        else:
            target_path = REPO_ROOT / canonical_file
            if not target_path.exists():
                file_check_errors.append(
                    f"layer '{layer_id}': canonical_file not found on disk: {canonical_file}"
                )
            else:
                print(f"  Check 4: layer '{layer_id}' ({canonical_file}): PASS")

    for e in file_check_errors:
        errors.append(f"Check 4: {e}")

    # --- Check 5: validator script exists (if field present) ---
    print("Checking validator script existence ...")
    validator_errors: list[str] = []
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        layer_id = layer.get("id", "<unknown>")
        validator = layer.get("validator")
        if validator is None:
            continue
        validator_path = REPO_ROOT / validator
        if not validator_path.exists():
            validator_errors.append(
                f"layer '{layer_id}': validator script not found: {validator}"
            )
        else:
            print(f"  Check 5: layer '{layer_id}' validator ({validator}): PASS")

    if validator_errors:
        for e in validator_errors:
            errors.append(f"Check 5: {e}")
    elif not any(layer.get("validator") for layer in layers if isinstance(layer, dict)):
        print("  Check 5: no layers have a validator field — skipped")
    elif not validator_errors:
        pass  # individual PASS lines already printed

    # --- Check 6: ci_gate workflow exists (if field present) ---
    print("Checking ci_gate workflow existence ...")
    ci_gate_errors: list[str] = []
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        layer_id = layer.get("id", "<unknown>")
        ci_gate = layer.get("ci_gate")
        if ci_gate is None:
            continue
        ci_gate_path = REPO_ROOT / ci_gate
        if not ci_gate_path.exists():
            ci_gate_errors.append(
                f"layer '{layer_id}': ci_gate workflow not found: {ci_gate}"
            )
        else:
            print(f"  Check 6: layer '{layer_id}' ci_gate ({ci_gate}): PASS")

    if ci_gate_errors:
        for e in ci_gate_errors:
            errors.append(f"Check 6: {e}")
    elif not any(layer.get("ci_gate") for layer in layers if isinstance(layer, dict)):
        print("  Check 6: no layers have a ci_gate field — skipped")

    # --- Check 7: Layer IDs are unique ---
    print("Checking layer ID uniqueness ...")
    seen_ids: set[str] = set()
    duplicate_ids: list[str] = []
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        layer_id = layer.get("id")
        if layer_id is None:
            continue
        if layer_id in seen_ids:
            duplicate_ids.append(layer_id)
        seen_ids.add(layer_id)

    if duplicate_ids:
        errors.append(f"Check 7: duplicate layer IDs: {duplicate_ids}")
    else:
        print(f"  Check 7: layer IDs unique ({len(seen_ids)} layers): PASS")

    # --- Summary ---
    total_layers = len(layers)
    print(f"\nSummary: {total_layers} total layers | {active_layers} active | {deferred_layers} deferred (not_on_branch)")

    _report(errors)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
