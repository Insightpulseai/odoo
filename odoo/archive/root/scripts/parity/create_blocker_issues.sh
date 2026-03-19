#!/usr/bin/env bash
# create_blocker_issues.sh - Create GitHub issues for parity blockers (idempotent)
# Usage: ./scripts/parity/create_blocker_issues.sh
# Environment: REPO_SLUG, AUDIT_JSON, LABEL_BLOCKER, LABEL_PARITY, ASSIGNEE
set -euo pipefail

REPO_SLUG="${REPO_SLUG:-jgtolentino/odoo-ce}"
AUDIT_JSON="${AUDIT_JSON:-reports/parity/ee_parity_audit.json}"
LABEL_BLOCKER="${LABEL_BLOCKER:-ee-parity:blocker}"
LABEL_PARITY="${LABEL_PARITY:-ee-parity}"
ASSIGNEE="${ASSIGNEE:-}"  # optional: set to your GitHub username

if [[ ! -f "$AUDIT_JSON" ]]; then
  echo "ERROR: audit json not found: $AUDIT_JSON" >&2
  echo "Run ./scripts/parity/audit_ee_parity.sh first"
  exit 2
fi

echo "==> Creating GitHub issues for parity blockers"
echo "    Repo: $REPO_SLUG"
echo "    Audit: $AUDIT_JSON"

# Ensure labels exist (best-effort)
ensure_label () {
  local name="$1"
  local color="$2"
  local desc="$3"
  if gh label view "$name" --repo "$REPO_SLUG" >/dev/null 2>&1; then
    echo "    Label exists: $name"
    return 0
  fi
  if gh label create "$name" --repo "$REPO_SLUG" --color "$color" --description "$desc" >/dev/null 2>&1; then
    echo "    Created label: $name"
  else
    echo "    Warning: Could not create label: $name"
  fi
}

ensure_label "$LABEL_PARITY"  "1f6feb" "EE parity tracking"
ensure_label "$LABEL_BLOCKER" "d1242f" "Blocks EE parity progress"

commit="$(jq -r '.commit' "$AUDIT_JSON")"
branch="$(jq -r '.branch' "$AUDIT_JSON")"
repo="$(jq -r '.repo' "$AUDIT_JSON")"

count="$(jq '.blockers | length' "$AUDIT_JSON")"
if [[ "$count" -eq 0 ]]; then
  echo ""
  echo "No blockers in audit. Nothing to create."
  exit 0
fi

echo ""
echo "Found $count blocker(s) to process"

created=0
skipped=0

for i in $(seq 0 $((count-1))); do
  code="$(jq -r ".blockers[$i].code" "$AUDIT_JSON")"
  title="$(jq -r ".blockers[$i].title" "$AUDIT_JSON")"
  detail="$(jq -r ".blockers[$i].detail" "$AUDIT_JSON")"

  issue_title="[EE Parity Blocker] $title ($code)"

  # Idempotency: skip if issue with same title already exists (open or closed)
  existing="$(gh issue list --repo "$REPO_SLUG" --search "\"$issue_title\" in:title" --json number,title,state --limit 20 2>/dev/null | jq -r ".[] | select(.title==\"$issue_title\") | .number" | head -n1 || true)"
  if [[ -n "${existing:-}" ]]; then
    echo "    Skip (exists): #$existing $issue_title"
    ((skipped++))
    continue
  fi

  body="$(cat <<MD
## Blocker Code
\`$code\`

## Context
- Repo: \`$repo\`
- Branch: \`$branch\`
- Commit: \`$commit\`
- Audit file: \`$AUDIT_JSON\`

## Detail
$detail

## Definition of Done
- [ ] Fix root cause
- [ ] Re-run: \`./scripts/parity/audit_ee_parity.sh\`
- [ ] Blocker no longer appears in \`reports/parity/ee_parity_audit.json\`

## Verification Commands
\`\`\`bash
./scripts/parity/audit_ee_parity.sh
cat reports/parity/ee_parity_audit.md
jq '.blockers' reports/parity/ee_parity_audit.json
\`\`\`

## Labels
- \`$LABEL_PARITY\`
- \`$LABEL_BLOCKER\`
MD
)"

  args=(--repo "$REPO_SLUG" --title "$issue_title" --body "$body" --label "$LABEL_PARITY" --label "$LABEL_BLOCKER")
  if [[ -n "${ASSIGNEE}" ]]; then
    args+=(--assignee "$ASSIGNEE")
  fi

  if number="$(gh issue create "${args[@]}" 2>/dev/null | grep -oE '[0-9]+$')"; then
    echo "    Created: #$number $issue_title"
    ((created++))
  else
    echo "    Warning: Failed to create issue for $code"
  fi
done

echo ""
echo "==> Summary"
echo "    Created: $created"
echo "    Skipped (already exist): $skipped"
echo "    Total blockers: $count"
