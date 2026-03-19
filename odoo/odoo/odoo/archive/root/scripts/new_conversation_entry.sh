#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "${ROOT}"

DIR="docs/ops/conversations"
IDX_MD="${DIR}/INDEX.md"
IDX_JSON="${DIR}/index.json"

mkdir -p "${DIR}"
touch "${IDX_MD}"
[[ -f "${IDX_JSON}" ]] || echo "[]" > "${IDX_JSON}"

# args
TITLE="${1:-untitled}"
DATE="${2:-$(date +"%Y-%m-%d")}"

# next number = count(md)+1
n=$(( $(find "${DIR}" -maxdepth 1 -name "*.md" ! -name "INDEX.md" 2>/dev/null | wc -l | tr -d ' ') + 1 ))
NNN="$(printf "%03d" "${n}")"

slug="$(echo "${TITLE}" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')"
FILE="${DIR}/${NNN} — ${DATE} — ${TITLE}.md"

cat > "${FILE}" <<MD
---
scope: ""
inputs: ""
outputs: ""
decisions: ""
next_actions: ""
tags: []
---

# ${NNN} — ${DATE} — ${TITLE}

## Summary

## Evidence / Artifacts

## Notes
MD

# Update human index
{
  echo "- **${NNN} — ${DATE} — ${TITLE}** → \`${FILE}\`"
} >> "${IDX_MD}"

# Update machine index
tmp="$(mktemp)"
jq --arg n "${NNN}" --arg d "${DATE}" --arg t "${TITLE}" --arg f "${FILE}" \
  '. + [{"id":$n,"date":$d,"title":$t,"file":$f}] | sort_by(.id)' \
  "${IDX_JSON}" > "${tmp}"
mv "${tmp}" "${IDX_JSON}"

echo "✅ created: ${FILE}"
