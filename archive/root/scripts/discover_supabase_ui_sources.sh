#!/usr/bin/env bash
set -euo pipefail

WORK_DIR="/tmp/supabase-ui-discovery"
OUT_DIR="kb/parity"
DOCS_DIR="docs/parity"

mkdir -p "$WORK_DIR" "$OUT_DIR" "$DOCS_DIR"

echo "=== Supabase UI Library Discovery ==="
echo "Step 1: GitHub repository search"

# Search for Supabase UI-related repos
gh search repos "supabase ui library" --limit 50 --json fullName,url,description,stargazersCount > "$WORK_DIR/search_ui_library.json"
gh search repos "supabase blocks" --limit 50 --json fullName,url,description,stargazersCount > "$WORK_DIR/search_blocks.json"
gh search repos "supabase shadcn" --limit 50 --json fullName,url,description,stargazersCount > "$WORK_DIR/search_shadcn.json"
gh search repos "supabase platform kit" --limit 50 --json fullName,url,description,stargazersCount > "$WORK_DIR/search_platform_kit.json"

# Combine and dedupe
python3 -c '
import json, sys
from pathlib import Path

repos = {}
for f in ["search_ui_library.json", "search_blocks.json", "search_shadcn.json", "search_platform_kit.json"]:
    path = Path("/tmp/supabase-ui-discovery") / f
    if path.exists():
        data = json.loads(path.read_text())
        for r in data:
            repos[r["fullName"]] = r

print(json.dumps(list(repos.values()), indent=2))
' > "$WORK_DIR/all_repos.json"

echo "Step 2: Clone and index top repos"

# Get top 10 by stars
python3 -c '
import json
data = json.load(open("/tmp/supabase-ui-discovery/all_repos.json"))
top = sorted(data, key=lambda x: x["stargazersCount"], reverse=True)[:10]
for r in top:
    print(r["fullName"])
' > "$WORK_DIR/top_repos.txt"

# Clone shallow
while read -r repo; do
    echo " - Cloning $repo"
    repo_dir="$WORK_DIR/repos/$(basename $repo)"
    if [ ! -d "$repo_dir" ]; then
        git clone --depth 1 "https://github.com/$repo.git" "$repo_dir" 2>/dev/null || echo "  (skip: clone failed)"
    fi
done < "$WORK_DIR/top_repos.txt"

echo "Step 3: Extract blocks and components"

# Find component/block directories
find "$WORK_DIR/repos" -type d \( -name "components" -o -name "blocks" -o -name "ui" \) 2>/dev/null > "$WORK_DIR/component_dirs.txt" || true

# Extract block names from directories
python3 -c '
import json
from pathlib import Path

blocks = []
dirs_file = Path("/tmp/supabase-ui-discovery/component_dirs.txt")
if dirs_file.exists():
    for line in dirs_file.read_text().strip().split("\n"):
        if not line:
            continue
        p = Path(line)
        repo = p.parts[-4] if len(p.parts) >= 4 else "unknown"
        category = p.name
        for child in p.iterdir():
            if child.is_dir():
                blocks.append({
                    "name": child.name,
                    "category": category,
                    "repo": repo,
                    "path": str(child.relative_to(Path("/tmp/supabase-ui-discovery/repos")))
                })

print(json.dumps(blocks, indent=2))
' > "$WORK_DIR/extracted_blocks.json"

echo "Step 4: Generate inventory JSON"

python3 -c '
import json
from pathlib import Path

all_repos = json.loads(Path("/tmp/supabase-ui-discovery/all_repos.json").read_text())
blocks = json.loads(Path("/tmp/supabase-ui-discovery/extracted_blocks.json").read_text())

inventory = {
    "meta": {
        "generated": "2026-01-27",
        "total_repos_found": len(all_repos),
        "total_blocks_extracted": len(blocks)
    },
    "repositories": all_repos[:20],  # Top 20
    "blocks": blocks[:50]  # Top 50 blocks
}

Path("kb/parity/supabase_ui_library_sources.json").write_text(json.dumps(inventory, indent=2))
'

echo "Step 5: Generate block catalog markdown"

python3 << 'PYTHON'
import json
from pathlib import Path

inv = json.loads(Path("kb/parity/supabase_ui_library_sources.json").read_text())

md = ["# Supabase UI Library - Block Catalog\n"]
md.append(f"**Total Repos Discovered**: {inv['meta']['total_repos_found']}")
md.append(f"**Total Blocks Extracted**: {inv['meta']['total_blocks_extracted']}\n")

md.append("## Discovered Blocks\n")
md.append("| Block Name | Category | Repo | Status | Complexity |")
md.append("|---|---|---|---|---|")

for b in inv["blocks"][:20]:
    md.append(f"| `{b['name']}` | {b['category']} | {b['repo']} | exists | TBD |")

Path("docs/parity/supabase-ui-library_block_catalog.md").write_text("\n".join(md))
PYTHON

echo ""
echo "=== DONE ==="
echo "Outputs:"
echo "  - kb/parity/supabase_ui_library_sources.json"
echo "  - docs/parity/supabase-ui-library_block_catalog.md"
echo ""
echo "Top 20 blocks found:"
python3 -c '
import json
from pathlib import Path
inv = json.loads(Path("kb/parity/supabase_ui_library_sources.json").read_text())
for i, b in enumerate(inv["blocks"][:20], 1):
    print(f"{i}. {b['name']} ({b['category']}) from {b['repo']}")
'
