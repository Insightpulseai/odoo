#!/usr/bin/env python3
"""
Filesystem-based Odoo Module Inventory Scanner

Scans all addon directories for __manifest__.py files, parses them,
cross-references against config/addons.manifest.yaml (OCA must-haves),
and produces a complete inventory of CE + OCA + IPAI modules.

Does NOT require a running Odoo instance. Works offline on the repo.

Usage:
    python scripts/scan_module_inventory.py
    python scripts/scan_module_inventory.py --output docs/audits/module_inventory

Outputs:
    - inventory_scan_<timestamp>.json  (machine)
    - inventory_scan_<timestamp>.csv   (spreadsheet)
    - inventory_scan_<timestamp>.md    (human)
    - latest_scan.json                 (pointer)
"""

import ast
import csv
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Addon search paths (order = Odoo addons_path priority)
ADDON_PATHS = [
    ("ce_core", REPO_ROOT / "odoo" / "addons"),  # CE core (if checked out)
    ("oca", REPO_ROOT / "addons" / "oca"),
    ("ipai", REPO_ROOT / "addons" / "ipai"),
]

# Additional ipai_* modules at addons/ root (legacy location)
LEGACY_IPAI_ROOT = REPO_ROOT / "addons"

MANIFEST_YAML = REPO_ROOT / "config" / "addons.manifest.yaml"


# ---------------------------------------------------------------------------
# Manifest Parsing
# ---------------------------------------------------------------------------


def parse_manifest(manifest_path):
    """Parse an Odoo __manifest__.py and return its dict."""
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()
        return ast.literal_eval(content)
    except (SyntaxError, ValueError):
        # Try extracting the dict from the file
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Find the dict literal
            tree = ast.parse(content, mode="eval")
            return ast.literal_eval(compile(tree, manifest_path, "eval"))
        except Exception:
            return None
    except Exception:
        return None


def classify_origin(module_name, module_path, author=""):
    """Classify module origin based on path and author."""
    path_str = str(module_path)
    if "/addons/ipai/" in path_str or module_name.startswith("ipai_"):
        return "ipai"
    if "/addons/oca/" in path_str:
        return "oca"
    author_lower = (author or "").lower()
    if "odoo community association" in author_lower or "oca" in author_lower:
        return "oca"
    return "ce_core"


def classify_installable(manifest):
    """Determine if module is installable."""
    if manifest is None:
        return "unknown"
    installable = manifest.get("installable", True)
    if installable:
        return "installable"
    return "not_installable"


def has_tests(module_dir):
    """Check if module has test files."""
    tests_dir = module_dir / "tests"
    if not tests_dir.is_dir():
        return False
    test_files = list(tests_dir.glob("test_*.py"))
    return len(test_files) > 0


def count_models(module_dir):
    """Count Python model files."""
    models_dir = module_dir / "models"
    if not models_dir.is_dir():
        return 0
    return len(list(models_dir.glob("*.py")) - {models_dir / "__init__.py"})


def count_views(module_dir):
    """Count XML view files."""
    views_dir = module_dir / "views"
    if not views_dir.is_dir():
        return 0
    return len(list(views_dir.glob("*.xml")))


# ---------------------------------------------------------------------------
# OCA Must-Have Cross-Reference
# ---------------------------------------------------------------------------


def load_oca_manifest():
    """Load OCA must-have modules from addons.manifest.yaml."""
    must_haves = {}
    all_repos = []

    if not MANIFEST_YAML.exists():
        return must_haves, all_repos

    try:
        # Simple YAML parsing without pyyaml dependency
        with open(MANIFEST_YAML, "r") as f:
            content = f.read()

        # Extract must_have modules per repo using basic parsing
        current_repo = None
        in_must_have = False
        in_repos = False

        for line in content.split("\n"):
            stripped = line.strip()

            if stripped.startswith("- repo:"):
                current_repo = stripped.split(":", 1)[1].strip()
                all_repos.append(current_repo)
                in_must_have = False
            elif stripped == "must_have:":
                in_must_have = True
            elif in_must_have and stripped.startswith("- "):
                mod_name = stripped[2:].strip()
                # Remove inline comments
                if "#" in mod_name:
                    mod_name = mod_name.split("#")[0].strip()
                if mod_name:
                    must_haves[mod_name] = current_repo
            elif in_must_have and not stripped.startswith("- "):
                in_must_have = False

    except Exception as e:
        print(f"Warning: could not parse {MANIFEST_YAML}: {e}", file=sys.stderr)

    return must_haves, all_repos


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------


def scan_addons_dir(origin, addons_dir):
    """Scan a directory for Odoo modules."""
    modules = []
    if not addons_dir.is_dir():
        return modules

    for item in sorted(addons_dir.iterdir()):
        if not item.is_dir():
            continue
        if item.name.startswith(".") or item.name == "__pycache__":
            continue

        manifest_path = item / "__manifest__.py"
        if not manifest_path.exists():
            # Check for OCA nested repos: addons/oca/<repo>/<module>/
            if origin == "oca":
                for sub in sorted(item.iterdir()):
                    if not sub.is_dir():
                        continue
                    sub_manifest = sub / "__manifest__.py"
                    if sub_manifest.exists():
                        manifest = parse_manifest(sub_manifest)
                        if manifest:
                            modules.append(
                                build_module_entry(
                                    sub.name, sub, manifest, origin, item.name
                                )
                            )
            continue

        manifest = parse_manifest(manifest_path)
        if manifest:
            modules.append(build_module_entry(item.name, item, manifest, origin))

    return modules


def build_module_entry(name, module_dir, manifest, origin, oca_repo=None):
    """Build a module inventory entry."""
    return {
        "name": name,
        "display_name": manifest.get("name", name),
        "version": manifest.get("version", "-"),
        "origin": classify_origin(name, module_dir, manifest.get("author", "")),
        "installable": manifest.get("installable", True),
        "application": manifest.get("application", False),
        "auto_install": manifest.get("auto_install", False),
        "category": manifest.get("category", "Uncategorized"),
        "author": manifest.get("author", ""),
        "license": manifest.get("license", ""),
        "summary": (manifest.get("summary") or "")[:120],
        "depends": manifest.get("depends", []),
        "has_tests": has_tests(module_dir),
        "path": str(module_dir.relative_to(REPO_ROOT)),
        "oca_repo": oca_repo,
    }


def scan_legacy_ipai():
    """Scan for ipai_* modules at addons/ root (legacy location)."""
    modules = []
    if not LEGACY_IPAI_ROOT.is_dir():
        return modules
    for item in sorted(LEGACY_IPAI_ROOT.iterdir()):
        if not item.is_dir() or not item.name.startswith("ipai_"):
            continue
        # Skip if inside addons/ipai/ (already scanned)
        if item.parent.name == "ipai":
            continue
        manifest_path = item / "__manifest__.py"
        if manifest_path.exists():
            manifest = parse_manifest(manifest_path)
            if manifest:
                modules.append(build_module_entry(item.name, item, manifest, "ipai"))
    return modules


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------


def generate_summary(modules, must_haves):
    """Generate summary statistics."""
    by_origin = Counter(m["origin"] for m in modules)
    by_installable = Counter()
    for m in modules:
        if m["installable"]:
            by_installable["installable"] += 1
        else:
            by_installable["not_installable"] += 1

    with_tests = sum(1 for m in modules if m["has_tests"])
    applications = sum(1 for m in modules if m["application"])

    # OCA must-have coverage
    found_must_haves = set()
    missing_must_haves = set()
    module_names = {m["name"] for m in modules}
    for mh in must_haves:
        if mh in module_names:
            found_must_haves.add(mh)
        else:
            missing_must_haves.add(mh)

    return {
        "total_modules": len(modules),
        "by_origin": dict(by_origin),
        "installable": by_installable["installable"],
        "not_installable": by_installable["not_installable"],
        "with_tests": with_tests,
        "applications": applications,
        "oca_must_have_total": len(must_haves),
        "oca_must_have_present": len(found_must_haves),
        "oca_must_have_missing": sorted(missing_must_haves),
    }


def generate_markdown(modules, summary, must_haves):
    """Generate markdown inventory report."""
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Odoo Module Inventory (Filesystem Scan)",
        "",
        f"**Scanned:** {ts} | **Repo:** `{REPO_ROOT.name}`",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total modules scanned | {summary['total_modules']} |",
        f"| Installable | {summary['installable']} |",
        f"| Not installable | {summary['not_installable']} |",
        f"| With tests | {summary['with_tests']} |",
        f"| Applications | {summary['applications']} |",
        "",
        "### By Origin",
        "",
        "| Origin | Count |",
        "|--------|-------|",
    ]
    for origin in ["ce_core", "oca", "ipai"]:
        label = {"ce_core": "CE Core", "oca": "OCA", "ipai": "IPAI"}.get(origin, origin)
        lines.append(f"| {label} | {summary['by_origin'].get(origin, 0)} |")

    # OCA Must-Have Coverage
    lines.extend(
        [
            "",
            "## OCA Must-Have Coverage",
            "",
            f"**Present:** {summary['oca_must_have_present']}/{summary['oca_must_have_total']} "
            f"({100 * summary['oca_must_have_present'] // max(summary['oca_must_have_total'], 1)}%)",
            "",
        ]
    )
    if summary["oca_must_have_missing"]:
        lines.append("### Missing Must-Have Modules")
        lines.append("")
        lines.append("| Module | OCA Repo | Status |")
        lines.append("|--------|----------|--------|")
        for mod in summary["oca_must_have_missing"]:
            repo = must_haves.get(mod, "?")
            lines.append(f"| `{mod}` | {repo} | Not in addons path |")
        lines.append("")

    # Module list by origin
    for origin, label in [
        ("ipai", "IPAI Custom"),
        ("oca", "OCA"),
        ("ce_core", "CE Core"),
    ]:
        origin_mods = [m for m in modules if m["origin"] == origin]
        if not origin_mods:
            continue

        installable = [m for m in origin_mods if m["installable"]]
        not_installable = [m for m in origin_mods if not m["installable"]]

        lines.extend(
            [
                f"## {label} Modules ({len(installable)} installable, {len(not_installable)} disabled)",
                "",
                "| Module | Version | Installable | Tests | Category | Path |",
                "|--------|---------|-------------|-------|----------|------|",
            ]
        )
        for m in origin_mods:
            inst = "Yes" if m["installable"] else "**No**"
            tests = "Yes" if m["has_tests"] else "-"
            must_have_tag = ""
            if m["name"] in must_haves:
                must_have_tag = " (must-have)"
            lines.append(
                f"| `{m['name']}`{must_have_tag} | {m['version']} | {inst} | "
                f"{tests} | {m['category']} | {m['path']} |"
            )
        lines.append("")

    return "\n".join(lines)


def write_csv(modules, filepath):
    """Write inventory to CSV."""
    fieldnames = [
        "name",
        "display_name",
        "version",
        "origin",
        "installable",
        "application",
        "auto_install",
        "category",
        "author",
        "license",
        "has_tests",
        "depends",
        "path",
        "oca_repo",
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for m in modules:
            row = dict(m)
            row["depends"] = ",".join(row.get("depends", []))
            writer.writerow(row)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Scan filesystem for Odoo module inventory"
    )
    parser.add_argument(
        "--output",
        default="docs/audits/module_inventory",
        help="Output directory",
    )
    args = parser.parse_args()

    print("Scanning Odoo module directories...")

    # Load OCA must-haves
    must_haves, oca_repos = load_oca_manifest()
    print(
        f"  OCA manifest: {len(must_haves)} must-have modules from {len(oca_repos)} repos"
    )

    # Scan all addon paths
    all_modules = []
    for origin, path in ADDON_PATHS:
        mods = scan_addons_dir(origin, path)
        if mods:
            print(f"  {origin}: {len(mods)} modules in {path.relative_to(REPO_ROOT)}")
        all_modules.extend(mods)

    # Scan legacy ipai_* at addons/ root
    legacy = scan_legacy_ipai()
    if legacy:
        print(f"  ipai (legacy): {len(legacy)} modules at addons/ root")
    all_modules.extend(legacy)

    # Deduplicate by name (prefer addons/ipai/ over addons/ root)
    seen = {}
    for m in all_modules:
        if m["name"] not in seen:
            seen[m["name"]] = m
    all_modules = sorted(seen.values(), key=lambda x: (x["origin"], x["name"]))

    # Generate summary
    summary = generate_summary(all_modules, must_haves)

    # Write outputs
    os.makedirs(args.output, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M")

    json_path = os.path.join(args.output, f"inventory_scan_{ts}.json")
    csv_path = os.path.join(args.output, f"inventory_scan_{ts}.csv")
    md_path = os.path.join(args.output, f"inventory_scan_{ts}.md")
    latest_path = os.path.join(args.output, "latest_scan.json")

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "scan_type": "filesystem",
        "repo_root": str(REPO_ROOT),
        "summary": summary,
        "modules": all_modules,
    }
    with open(json_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    with open(latest_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)

    write_csv(all_modules, csv_path)

    md_content = generate_markdown(all_modules, summary, must_haves)
    with open(md_path, "w") as f:
        f.write(md_content)

    # Print summary
    print()
    print("=" * 60)
    print("MODULE INVENTORY SCAN COMPLETE")
    print("=" * 60)
    print(f"Total:          {summary['total_modules']}")
    print(f"  CE Core:      {summary['by_origin'].get('ce_core', 0)}")
    print(f"  OCA:          {summary['by_origin'].get('oca', 0)}")
    print(f"  IPAI:         {summary['by_origin'].get('ipai', 0)}")
    print()
    print(f"Installable:    {summary['installable']}")
    print(f"Not installable:{summary['not_installable']}")
    print(f"With tests:     {summary['with_tests']}")
    print()
    print(
        f"OCA Must-Have:  {summary['oca_must_have_present']}/{summary['oca_must_have_total']} present"
    )
    if summary["oca_must_have_missing"]:
        print(f"  Missing:      {', '.join(summary['oca_must_have_missing'][:10])}")
        if len(summary["oca_must_have_missing"]) > 10:
            print(
                f"                ... and {len(summary['oca_must_have_missing']) - 10} more"
            )
    print()
    print(f"Reports: {json_path}")
    print(f"         {csv_path}")
    print(f"         {md_path}")


if __name__ == "__main__":
    main()
