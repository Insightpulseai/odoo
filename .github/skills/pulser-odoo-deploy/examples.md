# pulser-odoo-deploy -- Worked Examples

## Example 1: Module Install Order Validation

**Scenario**: Preparing to install the MVP release scope on the `dev` environment.

**Step 1 -- Read SSOT**:
```yaml
# ssot/odoo/module_install_manifest.yaml  -- expected structure
modules:
  - name: ipai_ai_agent_sources     # no internal deps, install first
    depends: []
    install_order: 1
  - name: ipai_tax_intelligence     # depends on account (CE), install early
    depends: [account]
    install_order: 2
  - name: ipai_expense_wiring       # wires expense to accounting
    depends: [hr_expense, account]
    install_order: 3
  - name: ipai_expense_ops          # operational layer over expense_wiring
    depends: [ipai_expense_wiring]
    install_order: 4
  - name: ipai_hr_expense_liquidation
    depends: [ipai_expense_ops]
    install_order: 5
  - name: ipai_copilot_actions      # action layer, depends on copilot
    depends: [ipai_odoo_copilot]
    install_order: 6
  - name: ipai_odoo_copilot         # core copilot, install before actions
    depends: [mail, bus]
    install_order: 6                # same tier as copilot_actions; install ipai_odoo_copilot first
```

**Step 2 -- Install command**:
```bash
# scripts/odoo/install_mvp_modules.sh
MODULES="ipai_ai_agent_sources,ipai_tax_intelligence,ipai_expense_wiring,\
ipai_expense_ops,ipai_hr_expense_liquidation,ipai_odoo_copilot,ipai_copilot_actions"

python odoo-bin \
  --config /etc/odoo/odoo.conf \
  --database odoo_dev \
  --init "$MODULES" \
  --stop-after-init \
  --no-http
```

**Step 3 -- Gate check**:
```bash
# Exit code must be 0 before promoting to staging
echo "Install exit code: $?"
```

---

## Example 2: ACA Revision Rollback Plan

**Scenario**: Production deployment of `ipai_odoo_copilot` fails. Need to activate
the previous revision within 5 minutes.

**Pre-deployment -- record current revision**:
```bash
PREV_REVISION=$(az containerapp revision list \
  --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev \
  --query "[?properties.active].name | [0]" \
  -o tsv)
echo "Rollback target: $PREV_REVISION"
# Store in docs/release/MVP_SHIP_CHECKLIST.md before promotion
```

**Rollback command** (from MCP query 4):
```bash
# Activate previous revision and shift 100% traffic to it
az containerapp revision activate \
  --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev \
  --revision "$PREV_REVISION"

az containerapp ingress traffic set \
  --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev \
  --revision-weight "$PREV_REVISION=100"
```

**Evidence written to**:
```
docs/evidence/<YYYYMMDD-HHMM>/pulser-odoo-deploy/rollback-plan.md
```

---

## Example 3: Detecting and Blocking a Greenfield Resource Request

**Scenario**: A deploy script proposes creating a new Azure AI Search resource
(`srch-ipai-copilot`) during the MVP deployment run.

**SSOT check**:
```bash
grep -r "srch-ipai-copilot" ssot/azure/runtime_topology.yaml
# Result: (no match)
```

**Decision**: Resource not in SSOT. Deployment blocked.

**Required action before unblocking**:
1. Classify the service in `ssot/azure/runtime_topology.yaml`:
   ```yaml
   optional_services:
     - name: srch-ipai-copilot
       classification: optional
       required_for_mvp: false
       required_when: "grounding enabled for ipai_odoo_copilot RAG"
   ```
2. Get explicit approval (architecture review, `pulser-odoo-architecture` skill).
3. Only then run `az search service create ...` inside the deploy pipeline.

**MCP query that confirmed this pattern**:
```
microsoft_docs_search("Azure Container Apps deploy review existing resources before create")
Result: Best practice is to inspect existing resources with `az resource list`
        before creating. Idempotent creation (`az search service create --if-not-exists`)
        is acceptable only after SSOT classification.
```
