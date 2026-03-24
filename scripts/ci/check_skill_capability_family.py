#!/usr/bin/env python3
"""CI gate: verify every IPAI agent skill under agents/skills/ has a
microsoft_capability_family field in its SKILL.md frontmatter.

Exit 0 = all skills classified.
Exit 1 = one or more skills missing the field.

This script validates IPAI agent skills (agents/skills/), NOT Claude Code
skills (.claude/skills/). The microsoft_capability_family frontmatter is
part of the IPAI skill schema, not the Claude Code skill schema.
"""

import os
import re
import sys

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "agents", "skills")
SKIP_DIRS = {"_template", "_templates", "schema", "__pycache__"}
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
FAMILY_RE = re.compile(r"microsoft_capability_family:\s*[\"']?(.+?)[\"']?\s*$", re.MULTILINE)

# Known Microsoft capability families (validated taxonomy from Learn docs portal)
VALID_FAMILIES = {
    "Azure",
    "Azure / AI",
    "Azure / AI / Document Intelligence",
    "Azure / AI Foundry",
    "Azure / Architecture",
    "Azure / Architecture / Operations",
    "Azure / CLI / Resource Management",
    "Azure / Cloud Adoption Framework",
    "Azure / Container Apps",
    "Azure / Container Registry",
    "Azure / Cost Optimization",
    "Azure / Database",
    "Azure / Database / PostgreSQL",
    "Azure / Databricks",
    "Azure / Deployment",
    "Azure / Developer CLI",
    "Azure / Functions / Developer CLI",
    "Azure / Governance / Security",
    "Azure / Load Testing",
    "Azure / Migration",
    "Azure / Monitor",
    "Azure / Monitor / App Insights",
    "Azure / Networking",
    "Azure / Networking / Container Apps",
    "Azure / Operations",
    "Azure / Reliability",
    "Azure / SaaS Architecture",
    "GitHub / DevOps",
    "GitHub / DevOps / Azure Container Registry",
    "GitHub / DevOps / Azure Deployment",
    "Microsoft 365 / Agents SDK",
    "Microsoft Copilot / Azure AI",
    "Microsoft Entra / Security",
}


# Skill name prefixes that indicate a Microsoft capability family is expected.
# Skills without these prefixes are Odoo/OCA/internal and do not require the field.
MICROSOFT_PREFIXES = (
    "aca-", "azure-", "azd-", "caf-", "copilot-", "databricks-",
    "entra-", "foundry-", "m365-", "saas-", "service-matrix-",
)


def is_microsoft_skill(skill_name: str) -> bool:
    """Return True if the skill name implies a Microsoft capability family."""
    return any(skill_name.startswith(p) for p in MICROSOFT_PREFIXES)


def check_skill(skill_dir: str, skill_name: str) -> tuple[bool, str]:
    """Check a single skill directory for microsoft_capability_family."""
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        if is_microsoft_skill(skill_name):
            return False, f"  FAIL {skill_name}: Microsoft skill missing SKILL.md"
        return True, f"  SKIP {skill_name} (no SKILL.md, non-Microsoft)"

    with open(skill_md) as f:
        content = f.read()

    fm_match = FRONTMATTER_RE.match(content)
    if not fm_match:
        if is_microsoft_skill(skill_name):
            return False, f"  FAIL {skill_name}: no frontmatter in SKILL.md"
        return True, f"  SKIP {skill_name} (no frontmatter, non-Microsoft)"

    family_match = FAMILY_RE.search(fm_match.group(1))
    if not family_match:
        if is_microsoft_skill(skill_name):
            return False, f"  FAIL {skill_name}: missing microsoft_capability_family"
        return True, f"  OK   {skill_name} (non-Microsoft, no family required)"

    family = family_match.group(1).strip()
    if family not in VALID_FAMILIES:
        return False, f"  WARN {skill_name}: unknown family '{family}' (not in validated taxonomy)"

    return True, f"  OK   {skill_name} -> {family}"


def main():
    skills_dir = os.path.abspath(SKILLS_DIR)
    if not os.path.isdir(skills_dir):
        print(f"ERROR: skills directory not found: {skills_dir}")
        sys.exit(1)

    total = 0
    passed = 0
    failed = 0
    skipped = 0
    failures = []

    for entry in sorted(os.listdir(skills_dir)):
        entry_path = os.path.join(skills_dir, entry)
        if not os.path.isdir(entry_path):
            continue
        if entry in SKIP_DIRS or entry.startswith("."):
            continue

        total += 1
        ok, msg = check_skill(entry_path, entry)
        print(msg)
        if "SKIP" in msg:
            skipped += 1
        elif ok:
            passed += 1
        else:
            failed += 1
            failures.append(msg)

    print(f"\n--- Summary ---")
    print(f"Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")

    if failures:
        print(f"\nFailures:")
        for f in failures:
            print(f)
        sys.exit(1)

    print("All skills have microsoft_capability_family classified.")
    sys.exit(0)


if __name__ == "__main__":
    main()
