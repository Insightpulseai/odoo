#!/usr/bin/env bash
# verify_integration_backbone.sh — Validate integration backbone components
# Usage: ./scripts/integration/verify_integration_backbone.sh
set -euo pipefail

PASS=0
FAIL=0

check() {
  local desc="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== Integration Backbone Verification ==="
echo ""

# 1. Migration file exists
echo "[1/6] Migration artifacts"
check "Migration SQL exists" test -f supabase/migrations/20260308000001_integration_backbone_events.sql

# 2. Edge Function files exist
echo "[2/6] Edge Functions"
check "event-fanout/index.ts exists" test -f supabase/functions/event-fanout/index.ts
check "approval-worker/index.ts exists" test -f supabase/functions/approval-worker/index.ts
check "odoo-webhook/index.ts exists" test -f supabase/functions/odoo-webhook/index.ts
check "ops-ingest/index.ts exists" test -f supabase/functions/ops-ingest/index.ts

# 3. Odoo bridge has correlation_id
echo "[3/6] Odoo bridge correlation_id propagation"
check "ipai_webhook.py has correlation_id param" grep -q "correlation_id" addons/ipai/ipai_enterprise_bridge/utils/ipai_webhook.py
check "project_task has correlation_id" grep -q "correlation_id" addons/ipai/ipai_enterprise_bridge/models/project_task_integration.py
check "hr_expense has correlation_id" grep -q "correlation_id" addons/ipai/ipai_enterprise_bridge/models/hr_expense_integration.py
check "odoo-webhook reads x-correlation-id" grep -q "x-correlation-id" supabase/functions/odoo-webhook/index.ts

# 4. GitHub Actions event emission
echo "[4/6] GitHub Actions event emission"
check "emit-ops-event action exists" test -f .github/actions/emit-ops-event/action.yml
check "deploy-production emits events" grep -q "emit-ops-event" .github/workflows/deploy-production.yml
check "deploy-odoo-prod emits events" grep -q "emit-ops-event" .github/workflows/deploy-odoo-prod.yml

# 5. Slack approval wiring
echo "[5/6] Slack approval wiring"
check "taskbus has resolveInteraction" grep -q "resolveInteraction" apps/slack-agent/server/lib/taskbus.ts
check "interactive.post uses resolveInteraction" grep -q "resolveInteraction" apps/slack-agent/server/routes/api/slack/interactive.post.ts
check "taskbus has approval_approve route" grep -q "approval_approve" apps/slack-agent/server/lib/taskbus.ts

# 6. SSOT + contracts
echo "[6/6] SSOT and contracts"
check "event_routes.yaml exists" test -f ssot/integrations/event_routes.yaml
check "TASK_QUEUE_CONTRACT.md exists" test -f docs/contracts/TASK_QUEUE_CONTRACT.md
check "AUDIT_EVENTS_CONTRACT.md exists" test -f docs/contracts/AUDIT_EVENTS_CONTRACT.md

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
