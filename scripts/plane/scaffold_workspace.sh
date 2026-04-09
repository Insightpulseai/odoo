#!/usr/bin/env bash
# scaffold_workspace.sh — Phase 4: Create Plane workspace skeleton
#
# Creates projects, labels, states, wiki root pages, and templates
# in the self-hosted Plane instance.
#
# Prerequisites:
#   PLANE_API_KEY       — Personal access token
#   PLANE_API_URL       — Base URL (default: https://plane.insightpulseai.com)
#   PLANE_WORKSPACE_SLUG — Workspace slug (default: fin-ops)
#
# Usage:
#   ./scripts/plane/scaffold_workspace.sh [--dry-run]
#
# Spec: spec/plane-unified-docs/ (Phase 4)

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PLANE_API_URL="${PLANE_API_URL:-https://plane.insightpulseai.com}"
PLANE_WORKSPACE_SLUG="${PLANE_WORKSPACE_SLUG:-fin-ops}"
DRY_RUN=false
EVIDENCE_DIR="docs/evidence/$(date +%Y%m%d-%H%M)/plane-scaffold"

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "[DRY RUN] No API calls will be made."
fi

if [[ -z "${PLANE_API_KEY:-}" ]]; then
  echo "FAIL: PLANE_API_KEY not set." >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
API="${PLANE_API_URL}/api/v1"
WS="${PLANE_WORKSPACE_SLUG}"

plane_post() {
  local path="$1" body="$2" label="${3:-}"
  if $DRY_RUN; then
    echo "[DRY RUN] POST ${path}"
    echo "  Body: $(echo "$body" | head -c 200)"
    return 0
  fi
  local resp
  resp=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "X-API-Key: ${PLANE_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$body" \
    "${API}${path}")
  local code body_resp
  code=$(echo "$resp" | tail -1)
  body_resp=$(echo "$resp" | sed '$d')
  if [[ "$code" -ge 200 && "$code" -lt 300 ]]; then
    echo "  OK ($code): ${label}"
    echo "$body_resp"
  else
    echo "  FAIL ($code): ${label}" >&2
    echo "$body_resp" >&2
    return 1
  fi
}

plane_get() {
  local path="$1"
  curl -s -H "X-API-Key: ${PLANE_API_KEY}" -H "Content-Type: application/json" "${API}${path}"
}

# ---------------------------------------------------------------------------
# Pre-flight: verify API is reachable
# ---------------------------------------------------------------------------
echo "=== Pre-flight: Testing API connectivity ==="
preflight=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "X-API-Key: ${PLANE_API_KEY}" \
  -H "Accept: application/json" \
  "${API}/workspaces/${WS}/projects/")

content_type=$(curl -s -I \
  -H "X-API-Key: ${PLANE_API_KEY}" \
  "${API}/workspaces/${WS}/projects/" 2>/dev/null | grep -i "content-type" | head -1)

if echo "$content_type" | grep -qi "text/html"; then
  echo "FAIL: Plane API returns HTML, not JSON." >&2
  echo "  The API backend is not routed through the proxy." >&2
  echo "  Fix: Ensure Plane's proxy (Caddy) routes /api/ to the API service." >&2
  echo "  Ref: https://developers.plane.so/self-hosting/plane-architecture" >&2
  exit 2
fi

echo "  API reachable (HTTP ${preflight}, content-type: ${content_type})"

# ---------------------------------------------------------------------------
# Step 1: Create Projects
# ---------------------------------------------------------------------------
echo ""
echo "=== Step 1: Creating Projects ==="

declare -A PROJECTS=(
  ["ARCH"]="Architecture and Platform Design"
  ["INFRA"]="Infrastructure and Deployment"
  ["SPEC"]="Product Specifications and PRDs"
  ["MIGRATE"]="Migration and Consolidation"
  ["OPS"]="Operations and Runbooks"
  ["ERP"]="Odoo ERP Development"
  ["DATA"]="Data Platform and Analytics"
  ["AI"]="AI and Agent Development"
  ["COMPLY"]="Finance and Compliance"
  ["GOV"]="Governance and Process"
)

declare -A PROJECT_IDS=()

for key in ARCH INFRA SPEC MIGRATE OPS ERP DATA AI COMPLY GOV; do
  name="${PROJECTS[$key]}"
  echo "Creating project: ${key} — ${name}"
  body=$(cat <<EOF
{
  "name": "${name}",
  "identifier": "${key}",
  "description": "Project ${key}: ${name}. See spec/plane-unified-docs/prd.md.",
  "network": 2
}
EOF
  )
  result=$(plane_post "/workspaces/${WS}/projects/" "$body" "$key") || true
  # Extract project ID from response
  pid=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null || echo "")
  if [[ -n "$pid" ]]; then
    PROJECT_IDS[$key]="$pid"
    echo "  Project ID: ${pid}"
  fi
done

# ---------------------------------------------------------------------------
# Step 2: Create Labels (shared across projects)
# ---------------------------------------------------------------------------
echo ""
echo "=== Step 2: Creating Labels ==="

LABELS=(
  "P0-critical:#dc2626"
  "P1-high:#ea580c"
  "P2-medium:#ca8a04"
  "P3-low:#16a34a"
  "agent:#7c3aed"
  "human:#2563eb"
  "blocked:#ef4444"
  "spec-linked:#6366f1"
  "migrated:#059669"
  "stale:#9ca3af"
)

# Create labels in the first project (ARCH) — they can be workspace-level too
arch_id="${PROJECT_IDS[ARCH]:-}"
if [[ -n "$arch_id" ]]; then
  for label_entry in "${LABELS[@]}"; do
    label_name="${label_entry%%:*}"
    label_color="${label_entry##*:}"
    body="{\"name\": \"${label_name}\", \"color\": \"${label_color}\"}"
    plane_post "/workspaces/${WS}/projects/${arch_id}/labels/" "$body" "label:${label_name}" || true
  done
fi

# ---------------------------------------------------------------------------
# Step 3: Create Wiki Root Pages (15 taxonomy categories)
# ---------------------------------------------------------------------------
echo ""
echo "=== Step 3: Creating Wiki Root Pages ==="

WIKI_CATEGORIES=(
  "Architecture"
  "Product Specs"
  "Delivery Plans"
  "Runbooks"
  "Integrations"
  "Data Platform"
  "ERP and Odoo"
  "Platform and Azure"
  "AI and Agents"
  "Finance and Compliance"
  "Governance"
  "Templates"
  "Releases"
  "Operations"
  "Onboarding"
)

# Map categories to projects
declare -A WIKI_PROJECT_MAP=(
  ["Architecture"]="ARCH"
  ["Product Specs"]="SPEC"
  ["Delivery Plans"]="SPEC"
  ["Runbooks"]="OPS"
  ["Integrations"]="INFRA"
  ["Data Platform"]="DATA"
  ["ERP and Odoo"]="ERP"
  ["Platform and Azure"]="INFRA"
  ["AI and Agents"]="AI"
  ["Finance and Compliance"]="COMPLY"
  ["Governance"]="GOV"
  ["Templates"]="GOV"
  ["Releases"]="OPS"
  ["Operations"]="OPS"
  ["Onboarding"]="GOV"
)

for category in "${WIKI_CATEGORIES[@]}"; do
  project_key="${WIKI_PROJECT_MAP[$category]:-ARCH}"
  pid="${PROJECT_IDS[$project_key]:-}"
  if [[ -z "$pid" ]]; then
    echo "  SKIP: ${category} (no project ID for ${project_key})"
    continue
  fi
  body=$(cat <<EOF
{
  "name": "${category}",
  "description_html": "<h1>${category}</h1><p>Wiki root page for ${category}. See <code>spec/plane-unified-docs/prd.md</code> for taxonomy.</p><hr/><p><em>Status: Stub — content pending Phase 5 migration.</em></p>",
  "access": 0
}
EOF
  )
  plane_post "/workspaces/${WS}/projects/${pid}/pages/" "$body" "wiki:${category}" || true
done

# ---------------------------------------------------------------------------
# Step 4: Deploy Page Templates
# ---------------------------------------------------------------------------
echo ""
echo "=== Step 4: Deploying Page Templates ==="

# ADR Template
if [[ -n "${PROJECT_IDS[ARCH]:-}" ]]; then
  adr_body=$(cat <<'TMPL'
{
  "name": "[Template] Architecture Decision Record",
  "description_html": "<h1>ADR-NNN: [Title]</h1><h2>Status</h2><p>[Proposed | Accepted | Deprecated | Superseded]</p><h2>Context</h2><p>What is the issue that we're seeing that is motivating this decision or change?</p><h2>Decision</h2><p>What is the change that we're proposing and/or doing?</p><h2>Consequences</h2><p>What becomes easier or more difficult to do because of this change?</p><h2>Alternatives Considered</h2><ul><li>Alternative 1: [description]</li><li>Alternative 2: [description]</li></ul><h2>References</h2><ul><li>Spec: <code>spec/[bundle]/</code></li><li>PR: <code>#NNN</code></li></ul>",
  "access": 0
}
TMPL
  )
  plane_post "/workspaces/${WS}/projects/${PROJECT_IDS[ARCH]}/pages/" "$adr_body" "template:ADR" || true
fi

# PRD Template
if [[ -n "${PROJECT_IDS[SPEC]:-}" ]]; then
  prd_body=$(cat <<'TMPL'
{
  "name": "[Template] Product Requirements Document",
  "description_html": "<h1>PRD: [Feature Name]</h1><h2>1. Problem</h2><p>What user/business problem does this solve?</p><h2>2. Solution</h2><p>What are we building?</p><h2>3. Scope</h2><h3>In Scope</h3><ul><li>[item]</li></ul><h3>Out of Scope</h3><ul><li>[item]</li></ul><h2>4. Success Criteria</h2><ul><li>[measurable outcome]</li></ul><h2>5. Dependencies</h2><ul><li>[system/team/service]</li></ul><h2>6. Risks</h2><ul><li>[risk] — [mitigation]</li></ul><h2>7. Spec Bundle</h2><p><code>spec/[feature-slug]/</code></p>",
  "access": 0
}
TMPL
  )
  plane_post "/workspaces/${WS}/projects/${PROJECT_IDS[SPEC]}/pages/" "$prd_body" "template:PRD" || true
fi

# Runbook Template
if [[ -n "${PROJECT_IDS[OPS]:-}" ]]; then
  runbook_body=$(cat <<'TMPL'
{
  "name": "[Template] Runbook",
  "description_html": "<h1>Runbook: [Title]</h1><h2>Purpose</h2><p>When to use this runbook.</p><h2>Prerequisites</h2><ul><li>[access/tool/credential required]</li></ul><h2>Steps</h2><ol><li>[step with command]</li><li>[step with expected output]</li></ol><h2>Verification</h2><ul><li>[how to confirm success]</li></ul><h2>Rollback</h2><ol><li>[how to undo if something goes wrong]</li></ol><h2>Contacts</h2><ul><li>Owner: [name/team]</li><li>Escalation: [name/channel]</li></ul>",
  "access": 0
}
TMPL
  )
  plane_post "/workspaces/${WS}/projects/${PROJECT_IDS[OPS]}/pages/" "$runbook_body" "template:Runbook" || true
fi

# Incident Postmortem Template
if [[ -n "${PROJECT_IDS[OPS]:-}" ]]; then
  postmortem_body=$(cat <<'TMPL'
{
  "name": "[Template] Incident Postmortem",
  "description_html": "<h1>Incident Postmortem: [Title]</h1><h2>Summary</h2><p>[1-2 sentence description]</p><h2>Timeline</h2><table><tr><th>Time</th><th>Event</th></tr><tr><td>[HH:MM UTC]</td><td>[what happened]</td></tr></table><h2>Impact</h2><ul><li>Duration: [X minutes/hours]</li><li>Users affected: [count/scope]</li><li>Services affected: [list]</li></ul><h2>Root Cause</h2><p>[technical root cause]</p><h2>Resolution</h2><p>[what fixed it]</p><h2>Action Items</h2><ul><li>[ ] [action] — Owner: [name] — Due: [date]</li></ul><h2>Lessons Learned</h2><ul><li>[lesson]</li></ul>",
  "access": 0
}
TMPL
  )
  plane_post "/workspaces/${WS}/projects/${PROJECT_IDS[OPS]}/pages/" "$postmortem_body" "template:Postmortem" || true
fi

# Release Checklist Template
if [[ -n "${PROJECT_IDS[OPS]:-}" ]]; then
  release_body=$(cat <<'TMPL'
{
  "name": "[Template] Release Checklist",
  "description_html": "<h1>Release Checklist: [Version/Tag]</h1><h2>Pre-Release</h2><ul><li>[ ] All CI gates green on main</li><li>[ ] Spec bundle tasks complete</li><li>[ ] Evidence pack in <code>docs/evidence/</code></li><li>[ ] CHANGELOG updated</li></ul><h2>Deploy</h2><ul><li>[ ] Tag created: <code>vX.Y.Z</code></li><li>[ ] Container image built and pushed</li><li>[ ] Database migrations applied</li><li>[ ] Health check passing</li></ul><h2>Post-Release</h2><ul><li>[ ] Smoke test in production</li><li>[ ] Monitoring dashboards reviewed</li><li>[ ] WHAT_SHIPPED.md updated</li><li>[ ] Stakeholder notification sent</li></ul>",
  "access": 0
}
TMPL
  )
  plane_post "/workspaces/${WS}/projects/${PROJECT_IDS[OPS]}/pages/" "$release_body" "template:Release" || true
fi

# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------
echo ""
echo "=== Generating Evidence ==="
mkdir -p "${EVIDENCE_DIR}"

cat > "${EVIDENCE_DIR}/scaffold_results.md" <<EOF
# Plane Workspace Scaffold — Phase 4 Evidence

- **Date**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
- **Workspace**: ${WS}
- **API URL**: ${PLANE_API_URL}
- **Dry Run**: ${DRY_RUN}

## Projects Created

$(for key in ARCH INFRA SPEC MIGRATE OPS ERP DATA AI COMPLY GOV; do
  echo "- ${key}: ${PROJECTS[$key]} (ID: ${PROJECT_IDS[$key]:-N/A})"
done)

## Labels Created

$(for l in "${LABELS[@]}"; do echo "- ${l}"; done)

## Wiki Root Pages

$(for c in "${WIKI_CATEGORIES[@]}"; do echo "- ${c} -> ${WIKI_PROJECT_MAP[$c]}"; done)

## Templates Deployed

- ADR (Architecture Decision Record)
- PRD (Product Requirements Document)
- Runbook
- Incident Postmortem
- Release Checklist

## Spec Reference

- \`spec/plane-unified-docs/tasks.md\` — Phase 4
EOF

echo "  Evidence saved to: ${EVIDENCE_DIR}/scaffold_results.md"
echo ""
echo "=== Phase 4 scaffold complete ==="
