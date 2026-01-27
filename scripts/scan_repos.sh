#!/usr/bin/env bash
set -euo pipefail

USER="${1:-jgtolentino}"
LIMIT="${LIMIT:-200}"

command -v gh >/dev/null || { echo "gh CLI required"; exit 1; }
gh auth status >/dev/null

echo "Fetching repo inventory for $USER ..."
gh repo list "$USER" --limit "$LIMIT" --source \
  --json name,description,url,visibility,isArchived,isFork,defaultBranchRef,updatedAt,pushedAt,createdAt,stargazerCount,forkCount,issues,primaryLanguage \
  > out/repos_inventory.json

# Extract repo names
python3 -c '
import json
d=json.load(open("out/repos_inventory.json"))
print("\n".join([r["name"] for r in d if not r.get("isFork") and not r.get("isArchived")]))
' > out/repos_names.txt

echo "Checking repo contents (presence of key files/dirs) ..."
rm -f out/repos_files.jsonl
while read -r repo; do
  full="$USER/$repo"
  echo " - $full"
  # List root + common dirs, best-effort
  # Note: API will 404 if repo empty/private to token.
  for path in "" ".github/workflows" "docs" "spec" "architecture" ".devcontainer"; do
    api_path="repos/$full/contents"
    [ -n "$path" ] && api_path="$api_path/$path"
    if gh api "$api_path" >/dev/null 2>&1; then
      echo "{\"repo\":\"$full\",\"path\":\"$path\",\"exists\":true}" >> out/repos_files.jsonl
    else
      echo "{\"repo\":\"$full\",\"path\":\"$path\",\"exists\":false}" >> out/repos_files.jsonl
    fi
  done

  # Probe specific files at root / .github
  for file in "README.md" "LICENSE" "SECURITY.md" "CONTRIBUTING.md" "CODE_OF_CONDUCT.md" ".github/CODEOWNERS" ".github/dependabot.yml"; do
    if gh api "repos/$full/contents/$file" >/dev/null 2>&1; then
      echo "{\"repo\":\"$full\",\"file\":\"$file\",\"exists\":true}" >> out/repos_files.jsonl
    else
      echo "{\"repo\":\"$full\",\"file\":\"$file\",\"exists\":false}" >> out/repos_files.jsonl
    fi
  done

  # Releases/tags metadata
  rel_count="$(gh api "repos/$full/releases" --paginate 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(len(d))' 2>/dev/null || echo 0)"
  tag_count="$(gh api "repos/$full/tags" --paginate 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(len(d))' 2>/dev/null || echo 0)"

  echo "{\"repo\":\"$full\",\"releases\":$rel_count,\"tags\":$tag_count}" >> out/repos_files.jsonl

done < out/repos_names.txt

echo "DONE: out/repos_inventory.json, out/repos_files.jsonl, out/repos_names.txt"
