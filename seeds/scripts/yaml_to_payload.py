#!/usr/bin/env python3
"""
Convert seed YAML files to JSON payload for Odoo import.

Usage:
    python yaml_to_payload.py > payload.json
    python yaml_to_payload.py --output /path/to/output.json
"""
import argparse
import json
import os
import sys

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def load_yaml(path):
    """Load YAML file, return empty dict if not found."""
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main():
    parser = argparse.ArgumentParser(description="Convert seed YAML to JSON payload")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    parser.add_argument(
        "--seeds-dir",
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        help="Seeds directory path",
    )
    args = parser.parse_args()

    base = args.seeds_dir

    payload = {
        "workstreams": [],
        "templates": [],
        "tasks": [],
        "checklists": [],
        "stc_worklist_types": [],
        "stc_checks": [],
        "stc_scenarios": [],
        "localization_overlays": [],
    }

    # AFC Workstream
    afc_ws = load_yaml(f"{base}/workstreams/afc_financial_close/00_workstream.yaml").get(
        "workstream", {}
    )
    if afc_ws:
        payload["workstreams"].append(
            {
                "code": afc_ws.get("code", "AFC"),
                "name": afc_ws.get("name", "AFC - Advanced Financial Closing"),
                "description": afc_ws.get("description"),
                "sap_anchor": afc_ws.get("sap_anchor"),
                "odoo_anchor": afc_ws.get("odoo_anchor"),
                "active": True,
            }
        )

    # AFC Templates
    for t in load_yaml(f"{base}/workstreams/afc_financial_close/10_templates.yaml").get(
        "templates", []
    ):
        payload["templates"].append(
            {
                "workstream_id": None,  # Resolved on import
                "code": t["code"],
                "name": t["name"],
                "period_type": t.get("period_type", "monthly"),
                "version": t.get("version", "v1"),
                "is_active": t.get("is_active", True),
                "sequence": t.get("sequence", 10),
            }
        )

    # AFC Tasks
    for task in load_yaml(f"{base}/workstreams/afc_financial_close/20_tasks.yaml").get(
        "tasks", []
    ):
        payload["tasks"].append(
            {
                "template_id": None,  # Resolved on import
                "code": task["code"],
                "name": task["name"],
                "category": task.get("category"),
                "phase": task.get("phase"),
                "sequence": task.get("sequence", 10),
                "due_offset_days": task.get("due_offset_days", 0),
                "prep_offset": task.get("prep_offset", 0),
                "review_offset": task.get("review_offset", 0),
                "owner_role": task.get("owner_role"),
                "requires_approval": task.get("requires_approval", False),
                "evidence_required": task.get("evidence_required", True),
                "sap_reference": task.get("sap_reference"),
            }
        )

    # AFC Checklists
    for chk in load_yaml(f"{base}/workstreams/afc_financial_close/30_checklists.yaml").get(
        "checklists", []
    ):
        payload["checklists"].append(
            {
                "task_id": None,  # Resolved on import by task_code match
                "task_code": chk.get("task_id", "").replace("afc_task_", "AFC_"),
                "sequence": chk.get("sequence", 10),
                "label": chk.get("label"),
                "required": chk.get("required", True),
                "evidence_type": chk.get("evidence_type", "file").lower(),
                "notes": chk.get("notes"),
            }
        )

    # STC Workstream
    stc_ws = load_yaml(f"{base}/workstreams/stc_tax_compliance/00_workstream.yaml").get(
        "workstream", {}
    )
    if stc_ws:
        payload["workstreams"].append(
            {
                "code": stc_ws.get("code", "STC"),
                "name": stc_ws.get("name", "STC - SAP Tax Compliance"),
                "description": stc_ws.get("description"),
                "sap_anchor": stc_ws.get("sap_anchor"),
                "odoo_anchor": stc_ws.get("odoo_anchor"),
                "active": True,
            }
        )

        # Extract worklist types from workstream definition
        for wl in stc_ws.get("worklist_types", []):
            payload["stc_worklist_types"].append(
                {
                    "code": wl["code"],
                    "name": wl["name"],
                    "description": wl.get("description"),
                }
            )

    # STC Worklist Types (from separate file if exists)
    for wl in load_yaml(f"{base}/workstreams/stc_tax_compliance/10_worklist_types.yaml").get(
        "worklist_types", []
    ):
        # Avoid duplicates
        if not any(w["code"] == wl["code"] for w in payload["stc_worklist_types"]):
            payload["stc_worklist_types"].append(
                {
                    "code": wl["code"],
                    "name": wl["name"],
                    "description": wl.get("description"),
                }
            )

    # STC Compliance Checks
    for chk in load_yaml(
        f"{base}/workstreams/stc_tax_compliance/20_compliance_checks.yaml"
    ).get("compliance_checks", []):
        payload["stc_checks"].append(
            {
                "workstream_id": None,  # Resolved on import
                "worklist_type_id": None,  # Resolved by worklist_type code
                "worklist_type_code": chk.get("worklist_type"),
                "code": chk["code"],
                "name": chk["name"],
                "description": chk.get("description"),
                "category": chk.get("category"),
                "sequence": chk.get("sequence", 10),
                "severity": chk.get("severity", "med").lower()[:3]
                if chk.get("severity")
                else "med",
                "is_active": chk.get("is_active", True),
                "auto_run": chk.get("auto_run", True),
                "sap_reference": chk.get("sap_reference"),
            }
        )

    # STC Scenarios
    for scn in load_yaml(f"{base}/workstreams/stc_tax_compliance/30_scenarios.yaml").get(
        "scenarios", []
    ):
        payload["stc_scenarios"].append(
            {
                "workstream_id": None,  # Resolved on import
                "code": scn["code"],
                "name": scn["name"],
                "frequency": scn.get("frequency", "monthly").lower(),
                "run_day_offset": scn.get("run_day_offset", 0),
                "sequence": scn.get("sequence", 10),
                "check_codes": scn.get("checks", []),
                "bir_forms": ",".join(scn.get("bir_forms", [])),
                "notes": scn.get("notes"),
                "sap_reference": scn.get("sap_reference"),
            }
        )

    # PH Localization Overlay
    ph_local = load_yaml(f"{base}/workstreams/stc_tax_compliance/60_localization_ph.yaml")

    # BIR Forms as overlays
    for form in ph_local.get("bir_forms", []):
        payload["localization_overlays"].append(
            {
                "country": "PH",
                "workstream_id": None,
                "applies_to_code": form["code"],
                "patch_type": "bir_form",
                "patch_payload": json.dumps(form, ensure_ascii=False),
                "sequence": 10,
                "active": True,
            }
        )

    # Check overlays
    for ovl in ph_local.get("check_overlays", []):
        payload["localization_overlays"].append(
            {
                "country": "PH",
                "workstream_id": None,
                "applies_to_code": ovl.get("applies_to"),
                "patch_type": ovl.get("patch_type", "threshold").replace("_update", ""),
                "patch_payload": json.dumps(ovl.get("patch", {}), ensure_ascii=False),
                "sequence": 20,
                "active": True,
            }
        )

    # Output
    output = json.dumps(payload, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Payload written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
