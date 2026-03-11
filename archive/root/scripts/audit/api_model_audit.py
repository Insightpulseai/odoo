#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
api_model_audit.py — @api.model_create_multi Audit for IPAI Modules

Scans all addons/ipai/*/models/*.py files, finds create() method
definitions on Odoo models, and classifies each as:

  ALREADY_CORRECT  — already uses @api.model_create_multi with vals_list
  SAFE_AUTO_FIX    — simple create() with only sequence gen / field defaulting
  MANUAL_REVIEW    — has post-create logic (event emission, external calls, etc.)

Outputs JSON report to stdout and to docs/evidence/<date>/api_model_audit.json.
Exit code is always 0 (audit only, not a gate).
"""

import ast
import json
import os
import sys
from datetime import datetime
from pathlib import Path


# Indicators of post-create side effects that require manual review
POST_CREATE_INDICATORS = [
    "_emit",
    "send_",
    "post(",
    "message_post",
    "webhook",
    "requests.",
    "notify",
    "signal",
    "event",
    "publish",
    "broadcast",
    "dispatch",
    "trigger",
    "external",
    "api_call",
    "slack",
    "mail",
]


def find_ipai_model_files(repo_root: str) -> list[str]:
    """Find all Python files under addons/ipai/*/models/."""
    ipai_dir = Path(repo_root) / "addons" / "ipai"
    if not ipai_dir.exists():
        return []
    results = []
    for module_dir in sorted(ipai_dir.iterdir()):
        if not module_dir.is_dir():
            continue
        models_dir = module_dir / "models"
        if not models_dir.exists():
            continue
        for py_file in sorted(models_dir.glob("*.py")):
            if py_file.name == "__init__.py":
                continue
            results.append(str(py_file))
    return results


def get_decorator_names(decorators: list[ast.expr]) -> list[str]:
    """Extract decorator name strings from AST decorator list."""
    names = []
    for dec in decorators:
        if isinstance(dec, ast.Attribute):
            # e.g., api.model or api.model_create_multi
            if isinstance(dec.value, ast.Name) and dec.value.id == "api":
                names.append(f"api.{dec.attr}")
        elif isinstance(dec, ast.Name):
            names.append(dec.id)
        elif isinstance(dec, ast.Call):
            # e.g., @api.model_create_multi() — unlikely but handle it
            if isinstance(dec.func, ast.Attribute):
                if isinstance(dec.func.value, ast.Name) and dec.func.value.id == "api":
                    names.append(f"api.{dec.func.attr}")
    return names


def has_vals_list_param(func_node: ast.FunctionDef) -> bool:
    """Check if the create method uses vals_list as its parameter name."""
    args = func_node.args
    # args.args includes 'self' as first, then positional params
    if len(args.args) >= 2:
        param_name = args.args[1].arg
        return param_name == "vals_list"
    return False


def get_source_lines(filepath: str) -> list[str]:
    """Read source lines from file."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()


def analyze_create_body(func_node: ast.FunctionDef, source_lines: list[str]) -> str:
    """
    Analyze the body of a create() method to determine if it is safe to auto-fix.

    Returns:
        'SAFE_AUTO_FIX' — only does sequence generation or simple field defaulting
                          before calling super().create(vals), no post-create side effects
        'MANUAL_REVIEW' — has post-create logic, event emission, external API calls, etc.
    """
    # Extract the raw source of the function body for pattern matching
    start_line = func_node.lineno - 1
    end_line = func_node.end_lineno if hasattr(func_node, "end_lineno") and func_node.end_lineno else start_line + 20
    body_source = "".join(source_lines[start_line:end_line]).lower()

    # Check for post-create side effect indicators
    for indicator in POST_CREATE_INDICATORS:
        if indicator.lower() in body_source:
            return "MANUAL_REVIEW"

    # Analyze the AST structure
    # Pattern: safe create() methods assign to a local before super().create()
    # and then just return the result. They don't do anything after super().
    super_call_found = False
    post_super_statements = []

    for i, stmt in enumerate(func_node.body):
        # Check if this statement contains a super().create() call
        has_super = _contains_super_create(stmt)
        if has_super:
            super_call_found = True
            # Everything after this statement is "post-create"
            post_super_statements = func_node.body[i + 1:]
            break

    if not super_call_found:
        # No super().create() call found — unusual, needs manual review
        return "MANUAL_REVIEW"

    # If there are statements after super().create() (besides a bare return),
    # it needs manual review
    if post_super_statements:
        # Filter out bare return statements
        non_return = [
            s for s in post_super_statements
            if not (isinstance(s, ast.Return) and s.value is None)
        ]
        if non_return:
            return "MANUAL_REVIEW"

    # Check if super().create() result is stored and then used in post-create logic
    # Pattern: task = super().create(vals) ... self._emit(task, ...) → MANUAL_REVIEW
    # Pattern: return super().create(vals) → SAFE_AUTO_FIX
    for stmt in func_node.body:
        if isinstance(stmt, ast.Assign) and _contains_super_create(stmt):
            # Result is assigned to a variable — check if variable is used later
            # in non-return statements
            target_names = set()
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    target_names.add(target.id)
            # Check subsequent statements for usage of the variable
            idx = func_node.body.index(stmt)
            for later_stmt in func_node.body[idx + 1:]:
                if isinstance(later_stmt, ast.Return):
                    # return <var> is fine
                    continue
                # Any other usage of the assigned variable means post-create logic
                later_source = ast.dump(later_stmt)
                for name in target_names:
                    if name in later_source:
                        return "MANUAL_REVIEW"

    return "SAFE_AUTO_FIX"


def _contains_super_create(node: ast.AST) -> bool:
    """Check if an AST node contains a super().create(...) call."""
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func = child.func
            if isinstance(func, ast.Attribute) and func.attr == "create":
                if isinstance(func.value, ast.Call):
                    if isinstance(func.value.func, ast.Name) and func.value.func.id == "super":
                        return True
    return False


def audit_file(filepath: str) -> list[dict]:
    """Audit a single Python file for create() method patterns."""
    results = []
    try:
        source_lines = get_source_lines(filepath)
        source = "".join(source_lines)
        tree = ast.parse(source, filename=filepath)
    except (SyntaxError, UnicodeDecodeError) as exc:
        results.append({
            "file": filepath,
            "line": 0,
            "class": "N/A",
            "classification": "PARSE_ERROR",
            "reason": f"Could not parse file: {exc}",
        })
        return results

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        class_name = node.name
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            if item.name != "create":
                continue

            decorators = get_decorator_names(item.decorator_list)
            line_no = item.lineno

            # Already uses @api.model_create_multi
            if "api.model_create_multi" in decorators:
                if has_vals_list_param(item):
                    results.append({
                        "file": filepath,
                        "line": line_no,
                        "class": class_name,
                        "classification": "ALREADY_CORRECT",
                        "reason": "Uses @api.model_create_multi with vals_list parameter",
                    })
                else:
                    results.append({
                        "file": filepath,
                        "line": line_no,
                        "class": class_name,
                        "classification": "MANUAL_REVIEW",
                        "reason": "Has @api.model_create_multi but parameter is not named vals_list",
                    })
                continue

            # Uses @api.model — needs classification
            if "api.model" in decorators:
                classification = analyze_create_body(item, source_lines)
                if classification == "SAFE_AUTO_FIX":
                    reason = (
                        "Simple create() with @api.model — only does pre-create "
                        "field defaulting/sequence generation before super().create(vals)"
                    )
                else:
                    reason = (
                        "create() with @api.model has post-create logic or side effects "
                        "that require manual review for @api.model_create_multi migration"
                    )
                results.append({
                    "file": filepath,
                    "line": line_no,
                    "class": class_name,
                    "classification": classification,
                    "reason": reason,
                })
                continue

            # No decorator at all — unusual but flag it
            results.append({
                "file": filepath,
                "line": line_no,
                "class": class_name,
                "classification": "MANUAL_REVIEW",
                "reason": "create() override without @api.model or @api.model_create_multi decorator",
            })

    return results


def main():
    # Determine repo root — script lives at scripts/audit/api_model_audit.py
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent

    model_files = find_ipai_model_files(str(repo_root))

    all_results = []
    for filepath in model_files:
        file_results = audit_file(filepath)
        all_results.extend(file_results)

    # Build report
    summary = {
        "ALREADY_CORRECT": 0,
        "SAFE_AUTO_FIX": 0,
        "MANUAL_REVIEW": 0,
        "PARSE_ERROR": 0,
    }
    for r in all_results:
        classification = r["classification"]
        if classification in summary:
            summary[classification] += 1

    report = {
        "audit_date": datetime.now().isoformat(),
        "repo_root": str(repo_root),
        "files_scanned": len(model_files),
        "create_methods_found": len(all_results),
        "summary": summary,
        "results": all_results,
    }

    # Output to stdout
    report_json = json.dumps(report, indent=2)
    print(report_json)

    # Write to evidence directory
    date_str = datetime.now().strftime("%Y%m%d")
    evidence_dir = repo_root / "docs" / "evidence" / date_str
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_file = evidence_dir / "api_model_audit.json"
    with open(evidence_file, "w") as f:
        f.write(report_json)
        f.write("\n")
    print(f"\nReport written to: {evidence_file}", file=sys.stderr)

    # Always exit 0 — audit only
    sys.exit(0)


if __name__ == "__main__":
    main()
