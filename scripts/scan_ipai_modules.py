#!/usr/bin/env python3
"""
Scan IPAI modules and extract metadata for documentation generation.
"""
import os
import ast
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
IPAI_ROOT = REPO_ROOT / "addons" / "ipai"


def extract_manifest_data(manifest_path):
    """Extract data from __manifest__.py file."""
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Handle both dict and function-based manifests
            if content.strip().startswith("def"):
                return None  # Skip function-based manifests
            manifest = ast.literal_eval(content)
            return manifest
    except Exception as e:
        print(f"Error reading {manifest_path}: {e}")
        return None


def categorize_module(name, manifest):
    """Categorize module by layer based on name and metadata."""
    name_lower = name.lower()
    category = manifest.get("category", "")

    if "workos" in name_lower or "workspace" in name_lower:
        return "WorkOS"
    elif "platform" in name_lower:
        return "Platform"
    elif any(x in name_lower for x in ["finance", "bir", "ppm", "close", "month"]):
        return "Finance"
    elif "crm" in name_lower or "pipeline" in name_lower:
        return "CRM"
    elif "ce_" in name_lower or "branding" in name_lower or "cleaner" in name_lower:
        return "Platform/Utilities"
    elif "industry" in name_lower:
        return "Industry"
    else:
        return "Other"


def scan_module_structure(module_path):
    """Scan module directory structure."""
    structure = {
        "models": [],
        "views": [],
        "security": [],
        "data": [],
        "controllers": [],
        "static": [],
        "wizards": [],
        "reports": [],
        "tests": [],
    }

    for category, patterns in {
        "models": ["models/*.py"],
        "views": ["views/*.xml"],
        "security": ["security/*.csv"],
        "data": ["data/*.xml"],
        "controllers": ["controllers/*.py"],
        "static": ["static/**/*"],
        "wizards": ["wizard/*.py", "wizards/*.py"],
        "reports": ["report/*.py", "report/*.xml"],
        "tests": ["tests/*.py"],
    }.items():
        for pattern in patterns:
            for item in module_path.glob(pattern):
                if item.is_file() and not item.name.startswith("__"):
                    structure[category].append(str(item.relative_to(module_path)))

    return structure


def main():
    """Main scanning function."""
    modules = []

    for module_dir in sorted(IPAI_ROOT.iterdir()):
        if (
            not module_dir.is_dir()
            or module_dir.name.startswith(".")
            or module_dir.name == "__pycache__"
        ):
            continue

        manifest_path = module_dir / "__manifest__.py"
        if not manifest_path.exists():
            continue

        manifest = extract_manifest_data(manifest_path)
        if not manifest:
            continue

        module_name = module_dir.name
        layer = categorize_module(module_name, manifest)
        structure = scan_module_structure(module_dir)

        module_info = {
            "name": module_name,
            "display_name": manifest.get("name", "N/A"),
            "version": manifest.get("version", "18.0.1.0.0"),
            "summary": manifest.get("summary", ""),
            "category": manifest.get("category", "Uncategorized"),
            "layer": layer,
            "author": manifest.get("author", ""),
            "website": manifest.get("website", ""),
            "license": manifest.get("license", "AGPL-3"),
            "depends": manifest.get("depends", []),
            "data": manifest.get("data", []),
            "demo": manifest.get("demo", []),
            "installable": manifest.get("installable", True),
            "application": manifest.get("application", False),
            "auto_install": manifest.get("auto_install", False),
            "structure": structure,
            "path": str(module_dir.relative_to(REPO_ROOT)),
        }

        modules.append(module_info)

    # Group by layer
    by_layer = {}
    for module in modules:
        layer = module["layer"]
        if layer not in by_layer:
            by_layer[layer] = []
        by_layer[layer].append(module)

    # Output results
    output = {
        "total_modules": len(modules),
        "by_layer": {layer: len(mods) for layer, mods in by_layer.items()},
        "layers": by_layer,
        "all_modules": modules,
    }

    output_file = REPO_ROOT / "docs" / "ipai" / "module_scan.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Scanned {len(modules)} modules")
    print("\nBy Layer:")
    for layer in sorted(by_layer.keys()):
        print(f"  {layer}: {len(by_layer[layer])} modules")
        for mod in by_layer[layer]:
            print(f"    - {mod['name']} ({mod['display_name']})")

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
