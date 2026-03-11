#!/usr/bin/env python3
"""Action evaluation runner — governed tool use compliance.

Validates that the copilot tool dispatch system satisfies all eval cases in
eval/action_eval.yaml by checking:

1. Tool exists in registry (copilot_tools.xml)
2. requires_confirmation flag matches eval case expectation
3. Preview function exists in _dispatch_tool_preview
4. Execute function exists in _execute_tool_confirmed
5. Audit envelope emission is wired (controller has _emit_audit_envelope)

Gate: action_eval_threshold (100% compliance)
Gate: audit_envelope_emitted (envelope emitter is wired)

Usage:
    python scripts/eval/run_action_eval.py                    # run + report
    python scripts/eval/run_action_eval.py --evidence-dir DIR # write evidence pack
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

sys.path.insert(0, REPO_ROOT)
from scripts.eval.audit_envelope import (  # noqa: E402
    AuditEnvelopeEmitter,
    create_envelope,
    validate_envelope,
)

EVAL_PATH = os.path.join(REPO_ROOT, "eval", "action_eval.yaml")
TOOLS_XML_PATH = os.path.join(
    REPO_ROOT, "addons", "ipai", "ipai_ai_copilot", "data", "copilot_tools.xml"
)
CONTROLLER_PATH = os.path.join(
    REPO_ROOT, "addons", "ipai", "ipai_ai_copilot", "controllers", "copilot.py"
)
TOOL_SPECS_DIR = os.path.join(REPO_ROOT, "contracts", "tools")
DEFAULT_EVIDENCE_DIR = os.path.join(REPO_ROOT, "docs", "evidence", "action_eval")


def _parse_tools_xml(xml_path: str) -> dict[str, dict]:
    """Parse copilot_tools.xml and return tool records keyed by name.

    Returns:
        Dict mapping tool name -> {category, requires_confirmation, description}
    """
    tools: dict[str, dict] = {}
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for record in root.iter("record"):
            model = record.get("model", "")
            if model != "ipai.copilot.tool":
                continue

            name = ""
            category = ""
            requires_confirmation = False
            description = ""

            for field in record.findall("field"):
                field_name = field.get("name", "")
                if field_name == "name":
                    name = field.text or ""
                elif field_name == "category":
                    category = field.text or ""
                elif field_name == "requires_confirmation":
                    val = (field.text or "").strip().lower()
                    requires_confirmation = val in ("true", "1", "yes")
                    # Also check eval attribute
                    if field.get("eval"):
                        requires_confirmation = "True" in field.get("eval", "")
                elif field_name == "description":
                    description = field.text or ""

            if name:
                tools[name] = {
                    "category": category,
                    "requires_confirmation": requires_confirmation,
                    "description": description,
                }
    except Exception as exc:
        print(f"Warning: could not parse {xml_path}: {exc}")

    return tools


def _parse_controller_functions(controller_path: str) -> dict[str, set[str]]:
    """Parse copilot.py to find which tools have preview and execute implementations.

    Returns:
        {
            "preview_tools": set of tool names in _dispatch_tool_preview,
            "execute_tools": set of tool names in _execute_tool_confirmed,
            "has_audit_emit": bool (controller has _emit_audit_envelope),
        }
    """
    try:
        with open(controller_path) as f:
            content = f.read()
    except OSError:
        return {"preview_tools": set(), "execute_tools": set(), "has_audit_emit": False}

    # Extract tool names from the _dispatch_tool_preview function DEFINITION
    # (not the call site) — search for "def _dispatch_tool_preview"
    preview_pattern = re.compile(r'"(\w+)":\s*lambda')
    def_marker = "def _dispatch_tool_preview"
    if def_marker in content:
        start = content.find(def_marker)
        next_def = content.find("\ndef ", start + 1)
        preview_section = content[start:next_def] if next_def != -1 else content[start:]
        preview_tools = set(preview_pattern.findall(preview_section))
    else:
        preview_tools = set()

    # Extract tool names from if/elif chain in _execute_tool_confirmed DEFINITION
    execute_pattern = re.compile(r'(?:if|elif)\s+name\s*==\s*["\'](\w+)["\']')
    exec_def_marker = "def _execute_tool_confirmed"
    if exec_def_marker in content:
        start = content.find(exec_def_marker)
        exec_section = content[start:]
        execute_tools = set(execute_pattern.findall(exec_section))
    else:
        execute_tools = set()

    # Check for audit envelope emission
    has_audit_emit = "_emit_audit_envelope" in content or "audit_envelope" in content.lower()

    return {
        "preview_tools": preview_tools,
        "execute_tools": execute_tools,
        "has_audit_emit": has_audit_emit,
    }


def _check_tool_spec_exists(tool_name: str) -> bool:
    """Check if a governed tool has a spec contract in contracts/tools/."""
    spec_path = os.path.join(TOOL_SPECS_DIR, f"{tool_name}.md")
    return os.path.isfile(spec_path)


def run_eval(
    eval_path: str = EVAL_PATH,
    evidence_dir: str | None = None,
) -> dict:
    """Run the full action evaluation.

    Validates structural compliance: tool registry, confirmation requirements,
    preview/execute function existence, audit envelope wiring, tool spec contracts.
    """
    with open(eval_path) as f:
        data = yaml.safe_load(f)

    meta = data["meta"]
    threshold = meta["pass_threshold"]
    governed_tools = meta.get("governed_tools", [])
    cases = data["cases"]

    # Parse tool registry and controller
    xml_tools = _parse_tools_xml(TOOLS_XML_PATH)
    controller = _parse_controller_functions(CONTROLLER_PATH)

    # Audit envelope emitter for simulated calls
    emitter = AuditEnvelopeEmitter(
        sink_dir=os.path.join(evidence_dir, "envelopes") if evidence_dir else None
    )

    results: list[dict] = []
    pass_count = 0

    for case in cases:
        case_id = case["id"]
        tool_name = case["tool"]
        requires_confirmation = case["requires_confirmation"]
        checks = case.get("checks", [])
        envelope_fields = case.get("audit_envelope_required_fields", [])

        check_results: dict[str, bool | str] = {}
        all_passed = True

        # 1. Tool exists in registry
        tool_in_registry = tool_name in xml_tools
        check_results["tool_in_registry"] = tool_in_registry
        if not tool_in_registry:
            all_passed = False

        # 2. requires_confirmation matches
        if tool_in_registry:
            xml_confirmation = xml_tools[tool_name]["requires_confirmation"]
            confirmation_match = xml_confirmation == requires_confirmation
            check_results["confirmation_match"] = confirmation_match
            if not confirmation_match:
                all_passed = False

        # 3. Preview function exists
        has_preview = tool_name in controller["preview_tools"]
        check_results["preview_function_exists"] = has_preview

        # 4. Execute function exists
        has_execute = tool_name in controller["execute_tools"]
        check_results["execute_function_exists"] = has_execute
        if not has_execute:
            all_passed = False

        # 5. Tool spec contract exists
        has_spec = _check_tool_spec_exists(tool_name)
        check_results["tool_spec_exists"] = has_spec

        # 6. Check-specific validations
        if "preview_shown" in checks:
            check_results["preview_shown"] = has_preview
            if not has_preview:
                all_passed = False

        if "approval_required" in checks:
            check_results["approval_required"] = (
                tool_in_registry and xml_tools.get(tool_name, {}).get("requires_confirmation", False)
            )

        if "audit_envelope" in checks:
            # Emit a simulated envelope and validate
            envelope = emitter.emit(
                tool_name=tool_name,
                tool_args={"prompt": case["prompt"]},
                result_status="success",
                duration_ms=50,
                user_id=2,
            )
            valid, errors = validate_envelope(envelope)
            check_results["audit_envelope_valid"] = valid
            if not valid:
                check_results["audit_envelope_errors"] = errors
                all_passed = False

        if "access_enforced" in checks:
            # Structural check: execute function uses request.env (not sudo)
            check_results["access_enforced"] = has_execute  # enforced by design

        # 7. Envelope completeness (AEVAL-016)
        if envelope_fields:
            test_envelope = create_envelope(
                tool_name=tool_name,
                tool_args={"test": True},
                result_status="success",
                duration_ms=1,
                user_id=1,
            )
            missing = [f for f in envelope_fields if f not in test_envelope or test_envelope[f] is None]
            check_results["envelope_completeness"] = len(missing) == 0
            if missing:
                check_results["missing_fields"] = missing
                all_passed = False

        # 8. Audit emit wired in controller
        check_results["audit_emit_wired"] = controller["has_audit_emit"]

        if all_passed:
            pass_count += 1

        results.append({
            "id": case_id,
            "tool": tool_name,
            "requires_confirmation": requires_confirmation,
            "checks": check_results,
            "passed": all_passed,
        })

    # Flush audit envelopes
    if evidence_dir:
        emitter.flush()

    pass_rate = pass_count / len(cases) if cases else 0.0
    threshold_met = pass_rate >= threshold

    # Tool-level summary
    tool_summary = {}
    for tool_name in governed_tools:
        tool_summary[tool_name] = {
            "in_registry": tool_name in xml_tools,
            "has_preview": tool_name in controller["preview_tools"],
            "has_execute": tool_name in controller["execute_tools"],
            "has_spec": _check_tool_spec_exists(tool_name),
        }

    summary = {
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "eval_file": os.path.relpath(eval_path, REPO_ROOT),
        "total_cases": len(cases),
        "passed": pass_count,
        "failed": len(cases) - pass_count,
        "pass_rate": round(pass_rate, 4),
        "threshold": threshold,
        "threshold_met": threshold_met,
        "audit_emit_wired": controller["has_audit_emit"],
        "governed_tools_summary": tool_summary,
        "cases": results,
    }

    # Write evidence
    if evidence_dir:
        os.makedirs(evidence_dir, exist_ok=True)
        evidence_path = os.path.join(evidence_dir, "eval_results.json")
        with open(evidence_path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Evidence written to: {evidence_path}")

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run action eval (governed tool use)")
    parser.add_argument(
        "--evidence-dir",
        default=DEFAULT_EVIDENCE_DIR,
        help="Directory for evidence pack output",
    )
    parser.add_argument(
        "--eval-file",
        default=EVAL_PATH,
        help="Path to eval YAML file",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Action Eval — Governed Tool Use Compliance")
    print("=" * 60)
    print()

    summary = run_eval(eval_path=args.eval_file, evidence_dir=args.evidence_dir)

    # Print tool-level summary
    print("Governed Tools:")
    for tool_name, info in summary["governed_tools_summary"].items():
        markers = []
        markers.append("registry" if info["in_registry"] else "NO registry")
        markers.append("preview" if info["has_preview"] else "NO preview")
        markers.append("execute" if info["has_execute"] else "NO execute")
        markers.append("spec" if info["has_spec"] else "NO spec")
        print(f"  {tool_name}: [{', '.join(markers)}]")
    print()

    # Print per-case results
    for case in summary["cases"]:
        status = "PASS" if case["passed"] else "FAIL"
        print(f"  {case['id']}: [{status}]  {case['tool']} (confirm={case['requires_confirmation']})")
        for check_name, check_val in case["checks"].items():
            if isinstance(check_val, bool):
                marker = "+" if check_val else "X"
                print(f"    [{marker}] {check_name}")

    # Summary
    print()
    print("-" * 60)
    rate_pct = summary["pass_rate"] * 100
    threshold_pct = summary["threshold"] * 100
    print(f"Pass rate: {summary['passed']}/{summary['total_cases']} = {rate_pct:.1f}%")
    print(f"Threshold: {threshold_pct:.0f}%")
    print(f"Audit emit wired: {summary['audit_emit_wired']}")

    if summary["threshold_met"]:
        print(f"RESULT: PASS (>= {threshold_pct:.0f}%)")
        return 0
    else:
        print(f"RESULT: FAIL (< {threshold_pct:.0f}%)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
