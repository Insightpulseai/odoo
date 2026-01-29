#!/usr/bin/env bash
# =============================================================================
# OCA Addon Inventory Generator
# =============================================================================
# Scans fetched OCA repositories and generates inventory files.
#
# Outputs:
#   docs/oca/ADDON_INVENTORY.json  - Full inventory with paths
#   docs/oca/ADDON_NAMES.txt       - Simple module name list
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Generating OCA addon inventory..."

mkdir -p "$ROOT_DIR/docs/oca"

python3 - <<'PY'
import os
import pathlib
import json

root = pathlib.Path(".")

# Scan multiple locations for OCA modules
search_paths = [
    pathlib.Path("third_party/oca"),
    pathlib.Path("addons/oca"),
    pathlib.Path("external-src"),
]

addons = []
for base_path in search_paths:
    if not base_path.exists():
        continue

    for repo in base_path.glob("*"):
        if not repo.is_dir():
            continue
        if repo.is_symlink() and not repo.resolve().exists():
            continue

        # Look for modules in repo root and repo/addons/
        search_dirs = [repo]
        if (repo / "addons").is_dir():
            search_dirs.insert(0, repo / "addons")

        for search_dir in search_dirs:
            try:
                for item in search_dir.iterdir():
                    if item.is_dir() and (item / "__manifest__.py").exists():
                        addons.append({
                            "name": item.name,
                            "path": str(item.relative_to(root)),
                            "repo": repo.name,
                            "source": str(base_path)
                        })
            except PermissionError:
                pass

# Deduplicate by module name (prefer third_party/oca)
seen = {}
for a in sorted(addons, key=lambda x: (0 if "third_party" in x["source"] else 1, x["name"])):
    if a["name"] not in seen:
        seen[a["name"]] = a

addons_sorted = sorted(seen.values(), key=lambda x: (x["repo"], x["name"]))

# Write JSON inventory
inventory_path = pathlib.Path("docs/oca/ADDON_INVENTORY.json")
inventory_path.write_text(json.dumps({
    "count": len(addons_sorted),
    "sources": list(set(a["source"] for a in addons_sorted)),
    "addons": addons_sorted
}, indent=2))
print(f"Wrote {inventory_path} with {len(addons_sorted)} addons")

# Write simple names list
names_path = pathlib.Path("docs/oca/ADDON_NAMES.txt")
names_path.write_text("\n".join(sorted(set(a["name"] for a in addons_sorted))) + "\n")
print(f"Wrote {names_path}")

# Write repo summary
repos = {}
for a in addons_sorted:
    repos.setdefault(a["repo"], []).append(a["name"])

summary_path = pathlib.Path("docs/oca/REPO_SUMMARY.md")
with open(summary_path, "w") as f:
    f.write("# OCA Repository Summary\n\n")
    f.write(f"**Total Addons:** {len(addons_sorted)}\n\n")
    for repo_name in sorted(repos.keys()):
        modules = repos[repo_name]
        f.write(f"## {repo_name} ({len(modules)} modules)\n\n")
        for m in sorted(modules)[:20]:  # First 20
            f.write(f"- `{m}`\n")
        if len(modules) > 20:
            f.write(f"- ... and {len(modules) - 20} more\n")
        f.write("\n")
print(f"Wrote {summary_path}")
PY

echo "Done."
