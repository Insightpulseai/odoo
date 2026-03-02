#!/usr/bin/env python3
"""
validate_skills_registry.py
CI validator for ssot/agents/skills.yaml

Usage:
    python3 scripts/ci/validate_skills_registry.py [--ssot-path PATH]
        [--tools-path PATH] [--schema-path PATH] [--check-docs DIRS]

Exit codes:
    0 — PASS (registry is valid)
    1 — FAIL (schema errors found)

Failure mode: CI.SKILLS_REGISTRY_INVALID
Runbook:      docs/runbooks/failures/CI.SKILLS_REGISTRY_INVALID.md
"""

import sys
import re
import argparse
from pathlib import Path

# ── Try to import PyYAML (available in ubuntu-latest GH runners) ──────────
try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# Schema definition (inline — no external jsonschema dep required)
# ─────────────────────────────────────────────────────────────────────────────

VALID_EXECUTORS      = {"vercel_sandbox", "do_runner", "supabase_edge_fn"}
VALID_STATES         = {"PLAN", "PATCH", "VERIFY", "PR", "MONITOR"}
VALID_STATUSES       = {"active", "deprecated", "experimental"}
REQUIRED_SKILL_KEYS  = {
    "id", "name", "description", "executor", "max_duration_s",
    "tags", "state_machine", "owner", "status",
    # Added in schema v1.1 (MAF parity P0):
    "allowed_tools", "security",
}

REQUIRED_SECURITY_KEYS = {
    "path_traversal_guard",
    "symlink_guard",
    "metadata_escaping",
    "max_skill_body_bytes",
}

# Shorthand citation labels without adjacent URLs/paths are forbidden.
# Pattern matches e.g. "[C1]", "[C12]", "[C-1]" as standalone refs.
CITATION_LABEL_PATTERN = re.compile(r"\[C-?\d+\]")
# A "safe" citation has an http/https URL or a repo-relative path in the same line.
CITATION_SAFE_PATTERN  = re.compile(r"(https?://\S+|`[a-zA-Z0-9_./-]+\.[a-zA-Z]{2,5}`)")

# ─────────────────────────────────────────────────────────────────────────────
# Tool registry loader
# ─────────────────────────────────────────────────────────────────────────────

def load_tool_registry(tools_path: Path) -> tuple[set[str], dict[str, list[str]]]:
    """
    Returns (tool_ids, allowed_in_skills_map).
    allowed_in_skills_map: {tool_id -> list of skill ids that may use it}
    ["*"] in YAML means all skills are allowed.
    """
    if not tools_path.exists():
        print(f"ERROR: Tool registry not found at {tools_path}")
        print(f"       Create ssot/tools/registry.yaml before running this validator.")
        sys.exit(1)

    with tools_path.open() as f:
        try:
            doc = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"ERROR: YAML parse error in {tools_path}: {e}")
            sys.exit(1)

    tools = doc.get("tools", [])
    tool_ids: set[str] = set()
    allowed_map: dict[str, list[str]] = {}

    for tool in tools:
        tid = tool.get("id", "")
        if tid:
            tool_ids.add(tid)
            allowed_map[tid] = tool.get("allowed_in_skills", ["*"])

    return tool_ids, allowed_map


# ─────────────────────────────────────────────────────────────────────────────
# Per-skill validation
# ─────────────────────────────────────────────────────────────────────────────

def validate_skill(
    skill: dict,
    index: int,
    tool_ids: set[str],
    allowed_map: dict[str, list[str]],
) -> list[str]:
    """Return list of error messages for a single skill entry."""
    errors = []
    prefix = f"skills[{index}]"

    # Required keys
    for key in REQUIRED_SKILL_KEYS:
        if key not in skill:
            errors.append(f"{prefix}.{key}: required field missing")

    if errors:  # stop early — remaining checks need the fields
        return errors

    # id: non-empty kebab-case
    sid = skill["id"]
    if not isinstance(sid, str) or not sid.strip():
        errors.append(f"{prefix}.id: must be a non-empty string")
    elif not re.match(r"^[a-z][a-z0-9-]+$", sid):
        errors.append(f"{prefix}.id: must match ^[a-z][a-z0-9-]+$ (got '{sid}')")

    # name
    if not isinstance(skill["name"], str) or not skill["name"].strip():
        errors.append(f"{prefix}.name: must be a non-empty string")

    # executor
    if skill["executor"] not in VALID_EXECUTORS:
        errors.append(
            f"{prefix}.executor: must be one of {sorted(VALID_EXECUTORS)}"
            f" (got '{skill['executor']}')"
        )

    # max_duration_s
    mds = skill["max_duration_s"]
    if not isinstance(mds, int) or mds < 1 or mds > 3600:
        errors.append(f"{prefix}.max_duration_s: must be integer 1–3600 (got {mds!r})")

    # tags
    if not isinstance(skill["tags"], list):
        errors.append(f"{prefix}.tags: must be a list")

    # state_machine
    sm = skill["state_machine"]
    if not isinstance(sm, list) or len(sm) == 0:
        errors.append(f"{prefix}.state_machine: must be a non-empty list")
    else:
        for j, state in enumerate(sm):
            if state not in VALID_STATES:
                errors.append(
                    f"{prefix}.state_machine[{j}]: '{state}' is not one of "
                    f"{sorted(VALID_STATES)}"
                )
        # Order must be a subsequence of PLAN→PATCH→VERIFY→PR→MONITOR
        canonical_order = ["PLAN", "PATCH", "VERIFY", "PR", "MONITOR"]
        last_idx = -1
        for state in sm:
            if state in canonical_order:
                idx = canonical_order.index(state)
                if idx <= last_idx:
                    errors.append(
                        f"{prefix}.state_machine: states must appear in order "
                        f"PLAN→PATCH→VERIFY→PR→MONITOR (got {sm})"
                    )
                    break
                last_idx = idx

    # status
    if skill["status"] not in VALID_STATUSES:
        errors.append(
            f"{prefix}.status: must be one of {sorted(VALID_STATUSES)}"
            f" (got '{skill['status']}')"
        )

    # owner
    if not isinstance(skill["owner"], str) or not skill["owner"].strip():
        errors.append(f"{prefix}.owner: must be a non-empty string")

    # ── allowed_tools cross-reference ────────────────────────────────────────
    allowed_tools = skill.get("allowed_tools", [])
    if not isinstance(allowed_tools, list):
        errors.append(f"{prefix}.allowed_tools: must be a list")
    else:
        for tool_id in allowed_tools:
            if tool_id == "__none__":
                continue
            if tool_id not in tool_ids:
                errors.append(
                    f"{prefix}.allowed_tools: '{tool_id}' not found in "
                    f"ssot/tools/registry.yaml — add the tool entry or remove the reference"
                )
            else:
                # Check that this skill is permitted to use this tool
                permitted = allowed_map.get(tool_id, ["*"])
                if permitted != ["*"] and sid not in permitted:
                    errors.append(
                        f"{prefix}.allowed_tools: tool '{tool_id}' does not list "
                        f"skill '{sid}' in its allowed_in_skills "
                        f"(permitted: {permitted})"
                    )

    # ── security block ────────────────────────────────────────────────────────
    sec = skill.get("security", {})
    if not isinstance(sec, dict):
        errors.append(f"{prefix}.security: must be a mapping")
    else:
        for key in REQUIRED_SECURITY_KEYS:
            if key not in sec:
                errors.append(
                    f"{prefix}.security.{key}: required field missing "
                    f"(see ssot/agents/interface_schema.yaml for defaults)"
                )
        # Type checks for known fields
        bool_keys = ["path_traversal_guard", "symlink_guard", "metadata_escaping"]
        for bk in bool_keys:
            if bk in sec and not isinstance(sec[bk], bool):
                errors.append(f"{prefix}.security.{bk}: must be a boolean (got {sec[bk]!r})")
        if "max_skill_body_bytes" in sec:
            msbb = sec["max_skill_body_bytes"]
            if not isinstance(msbb, int) or msbb < 1:
                errors.append(
                    f"{prefix}.security.max_skill_body_bytes: must be a positive integer"
                    f" (got {msbb!r})"
                )

    return errors


# ─────────────────────────────────────────────────────────────────────────────
# Citation label checker for docs
# ─────────────────────────────────────────────────────────────────────────────

def check_citation_labels(doc_dirs: list[Path]) -> list[str]:
    """
    Scan Markdown files for bare citation labels like [C1] or [C-12].
    A label is allowed only if the same line contains a URL or a backtick path.
    Returns a list of violation strings.
    """
    violations = []
    for doc_dir in doc_dirs:
        if not doc_dir.exists():
            continue
        for md_path in sorted(doc_dir.rglob("*.md")):
            try:
                lines = md_path.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue
            for lineno, line in enumerate(lines, start=1):
                if CITATION_LABEL_PATTERN.search(line):
                    if not CITATION_SAFE_PATTERN.search(line):
                        violations.append(
                            f"{md_path}:{lineno}: bare citation label found — "
                            f"add a URL or repo-relative path on the same line\n"
                            f"    {line.strip()}"
                        )
    return violations


# ─────────────────────────────────────────────────────────────────────────────
# Registry validator
# ─────────────────────────────────────────────────────────────────────────────

def validate_registry(
    path: Path,
    tool_ids: set[str],
    allowed_map: dict[str, list[str]],
) -> int:
    """Validate the registry YAML. Returns exit code."""
    if not path.exists():
        print(f"ERROR: {path} not found")
        return 1

    with path.open() as f:
        try:
            doc = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"ERROR: YAML parse error in {path}: {e}")
            return 1

    if not isinstance(doc, dict):
        print(f"ERROR: {path} must be a YAML mapping at the top level")
        return 1

    skills = doc.get("skills")
    if not isinstance(skills, list) or len(skills) == 0:
        print(f"ERROR: {path} must contain a non-empty 'skills' list")
        return 1

    all_errors: list[str] = []
    ids_seen: set[str] = set()

    for i, skill in enumerate(skills):
        if not isinstance(skill, dict):
            all_errors.append(f"skills[{i}]: must be a mapping")
            continue

        # Duplicate ID check
        sid = skill.get("id")
        if sid and sid in ids_seen:
            all_errors.append(f"skills[{i}].id: duplicate id '{sid}'")
        elif sid:
            ids_seen.add(sid)

        all_errors.extend(validate_skill(skill, i, tool_ids, allowed_map))

    if all_errors:
        print(f"FAIL: ssot/agents/skills.yaml schema validation failed")
        print(f"      Failure mode: CI.SKILLS_REGISTRY_INVALID")
        print(f"      Runbook:      docs/runbooks/failures/CI.SKILLS_REGISTRY_INVALID.md")
        print()
        for err in all_errors:
            print(f"  {err}")
        print(f"\n{len(all_errors)} error(s) found in {len(skills)} skill(s)")
        return 1

    print(f"PASS: {len(skills)} skill(s) validated in {path}")
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ssot-path",
        default="ssot/agents/skills.yaml",
        help="Path to skills YAML (default: ssot/agents/skills.yaml)",
    )
    parser.add_argument(
        "--tools-path",
        default="ssot/tools/registry.yaml",
        help="Path to tools registry YAML (default: ssot/tools/registry.yaml)",
    )
    parser.add_argument(
        "--check-docs",
        nargs="*",
        default=["docs/contracts", "spec"],
        metavar="DIR",
        help="Directories to scan for bare citation labels (default: docs/contracts spec)",
    )
    args = parser.parse_args()

    repo_root = Path(".")
    exit_codes: list[int] = []

    # 1. Load tool registry
    tool_ids, allowed_map = load_tool_registry(repo_root / args.tools_path)
    print(f"INFO: Loaded {len(tool_ids)} tool(s) from {args.tools_path}")

    # 2. Validate skills registry
    rc = validate_registry(repo_root / args.ssot_path, tool_ids, allowed_map)
    exit_codes.append(rc)

    # 3. Citation label check
    doc_dirs = [repo_root / d for d in args.check_docs]
    citation_violations = check_citation_labels(doc_dirs)
    if citation_violations:
        print(f"\nFAIL: bare citation labels (e.g. [C1]) without URL/path found:")
        print(f"      Fix: add a URL or repo-relative path on the same line,")
        print(f"      or use the full contract title instead of a shorthand label.")
        print()
        for v in citation_violations:
            print(f"  {v}")
        print(f"\n{len(citation_violations)} citation violation(s) found")
        exit_codes.append(1)
    else:
        dirs_checked = [str(d) for d in doc_dirs if d.exists()]
        print(f"PASS: no bare citation labels in {dirs_checked}")

    sys.exit(max(exit_codes))


if __name__ == "__main__":
    main()
