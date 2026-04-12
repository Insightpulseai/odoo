# Azure Tagging Doctrine — IPAI

**Canonical schema:** [ssot/azure/tagging-standard.yaml](../../ssot/azure/tagging-standard.yaml)
**Policy-as-code:** [infra/azure/policy/tagging-baseline.bicep](../../infra/azure/policy/tagging-baseline.bicep)
**Drift audit:** [scripts/azure/audit-tags.sh](../../scripts/azure/audit-tags.sh)

---

## Executive summary

Azure tags are the load-bearing metadata layer for **cost allocation, governance, automation, and compliance** across IPAI's footprint. This doctrine consolidates:

- Microsoft Cloud Adoption Framework (CAF) Ready tagging guidance (June 2025 refresh)
- FinOps Foundation Framework 2026 — Allocation + Invoicing/Chargeback capabilities
- Azure Policy built-in definitions for tag compliance
- Cost Management tag inheritance mechanics

into a single enforceable schema ready for IPAI's subscription `536d8cf6-89e1-4815-aef3-d5f2c5f4d070`.

## Current state (audit 2026-04-13)

Subscription has **17 unique tag keys** with significant drift:

| Drift class | Example | Impact |
|---|---|---|
| Case collisions | `Environment` (59×), `env` (1), `environment` (4), `ENV` | Cost reports show duplicate rows |
| Semantic collisions | `Owner:ipai`, `owner:jake`, `Owner:platform` | Ownership ambiguous |
| Key synonyms | `Service`, `Stack`, `workload`, `product`, `app` | Same concept, 5 keys |
| Non-canonical values | `CostCenter: platform` (not a GL code) | Can't roll up to finance |
| Managed-by casing | `managedBy`, `ManagedBy`, `managed_by`, `managed-by` | 4 variants |

Two resources also carry operational signals missed by anyone not looking at tags:
- `ipai-copilot-gateway` is marked `quarantine: true` / `retain-until: 2026-05-05` — **schedule for deprecation before May 5**
- `acripaiodoo` has `Environment: Development` (value case drift — should be `env=dev`)

## Three findings that drive the schema

### 1. Azure does not inherit tags by default

Resources do NOT inherit from resource group; resource groups do NOT inherit from subscription. This is the single most-cited source of tag drift. Two remediation paths:

- **Azure Policy `modify` effect** — writes tags onto the actual resource (visible in Resource Graph, Policy compliance, and Cost Management)
- **Cost Management tag inheritance** — writes tags onto usage records only (visible in Cost Analysis / budgets / exports, but NOT on the resource)

**IPAI enables both.** Policy-based inheritance closes the governance gap; Cost Management inheritance closes the cost-reporting gap for resources whose tags don't flow into usage (SQL child types, BotService channels, some network types).

### 2. Not every resource can carry tags

Classic resources, IP Groups, Firewall Policies (no PATCH), Entra app registrations (Graph-only, string-list-not-map), Bot Service channels, SQL child types — all either refuse tags or carry them without propagation.

**Workaround** for untaggable resources: carry metadata in naming convention (`ipai-<app>-<env>-<region>`), place in a dedicated RG, rely on Cost Management inheritance from RG/subscription. Entra apps get a parallel SSOT mirror at `ssot/entra/app-registrations.yaml`.

### 3. CAF Ready and FinOps F2 converge on five tag categories

- **Functional** → `env`, `app`, `region`, `managed-by`, `repo`, `created-date`
- **Classification** → `data-classification`, `criticality`
- **Accounting** → `costcenter`, `project`, `businessunit`
- **Purpose** (optional) → `businessprocess`, `revenueimpact`
- **Ownership** → `owner`, `businessunit`

IPAI's required set matches 1:1 with the CAF required set. See `ssot/azure/tagging-standard.yaml` for the full schema.

## Enforcement plan (3-phase)

### Phase 1 — Stage the policy (no enforcement yet)

```bash
az deployment sub create \
  --location southeastasia \
  --template-file infra/azure/policy/tagging-baseline.bicep \
  --subscription 536d8cf6-89e1-4815-aef3-d5f2c5f4d070 \
  --parameters requiredTagKeys='["env","costcenter","owner"]'
```

Deploys 5 policy assignments at subscription scope:
1. `ipai-require-env` — deny resources missing `env`
2. `ipai-require-costcenter` — deny resources missing `costcenter`
3. `ipai-require-owner` — deny resources missing `owner`
4. `ipai-rg-require-owner` — deny resource groups missing `owner`
5. `ipai-inherit-rg-{env|costcenter|owner|businessunit|project|data-classification}` — modify (inherit-if-missing) from RG

### Phase 2 — Remediate existing non-compliant resources

After deploy, the policy MIs are granted Contributor to run remediation tasks:

```bash
for tag in env costcenter owner businessunit project data-classification; do
  az policy remediation create \
    --name "remediate-inherit-rg-${tag}-$(date +%Y%m%d)" \
    --policy-assignment "ipai-inherit-rg-${tag}" \
    --resource-discovery-mode ReEvaluateCompliance
done
```

This sweeps existing resources and writes the missing tags from the RG. Does NOT overwrite existing values.

### Phase 3 — Drift detection in CI

Wire `scripts/azure/audit-tags.sh` into:

- GitHub Actions **scheduled run** (twice weekly) — alerts on drift
- GitHub Actions **pre-deploy gate** on `infra/azure/**` changes — blocks deploys that introduce drift
- Evidence bundle writes to `docs/evidence/<stamp>/azure-tags/` for audit trail

Exit code 0 on zero drift, 1 otherwise. Per IPAI operating contract.

## Case-drift cleanup (one-time, manual)

The policy baseline does NOT automatically remove forbidden case-variant keys (`Environment`, `managedBy`, etc.). Remediate manually or via targeted scripts:

```bash
# Find all resources with forbidden keys
bash scripts/azure/audit-tags.sh
# Inspect docs/evidence/<stamp>/azure-tags/drift-forbidden-keys.json
# Then for each affected resource, either:
#  - use az resource tag --operation merge to add the canonical key
#  - use az resource update --remove tags.<ForbiddenKey> to drop the drift
```

## Cost Management companion step (portal, owner-only)

Cost Management tag inheritance is **not available via CLI**. One-time owner step:

1. Portal → Cost Management → Settings → Manage subscription
2. Tag inheritance → Edit → **Enable** "Automatically apply subscription and resource group tags to new usage data"
3. Save — propagation takes 8–24 hours

After enable, `env`, `costcenter`, `owner`, `businessunit` will appear in Cost Analysis `Group by` even for resource types that don't emit tags in their usage records.

## Integration with existing IPAI standards

- **Naming convention** (`ipai-<app>-<env>-<region>`) still applies — tags complement names, don't replace them
- **Secrets policy** — `data-classification: restricted` triggers stricter KV access review in CI
- **SSOT rule #10** (no console-only infra changes) — policy assignments deploy via Bicep; drift audit is scripted
- **Operating contract** — audit output lands in `docs/evidence/<stamp>/azure-tags/`

## Related

- [ssot/azure/tagging-standard.yaml](../../ssot/azure/tagging-standard.yaml) — the canonical schema
- [infra/azure/policy/tagging-baseline.bicep](../../infra/azure/policy/tagging-baseline.bicep) — policy-as-code
- [scripts/azure/audit-tags.sh](../../scripts/azure/audit-tags.sh) — drift detector
- [docs/security/revoke-pat-runbook.md](../security/revoke-pat-runbook.md) — PAT cleanup (prerequisite — tags reference `owner`/`managed-by` which require Entra auth)

## Sources

Microsoft Learn (primary):
- [Define your tagging strategy (CAF Ready, June 2025)](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/resource-tagging)
- [Use tags to organize Azure resources](https://learn.microsoft.com/azure/azure-resource-manager/management/tag-resources)
- [Tag support for Azure resources](https://learn.microsoft.com/azure/azure-resource-manager/management/tag-support)
- [Assign policy definitions for tag compliance](https://learn.microsoft.com/azure/azure-resource-manager/management/tag-policies)
- [Group and allocate costs using tag inheritance](https://learn.microsoft.com/azure/cost-management-billing/costs/enable-tag-inheritance)
- [Group related resources (cm-resource-parent)](https://learn.microsoft.com/azure/cost-management-billing/costs/group-filter#group-related-resources-in-the-resources-view)

FinOps Foundation:
- [Allocation capability](https://www.finops.org/framework/capabilities/allocation/)
- [Invoicing & Chargeback capability](https://www.finops.org/framework/capabilities/invoicing-chargeback/)
- [FinOps Framework 2026](https://www.finops.org/insights/2026-finops-framework/)

---

*Last updated: 2026-04-13*
