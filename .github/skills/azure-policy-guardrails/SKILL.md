# azure-policy-guardrails

**Impact tier**: P1 -- Operational Readiness

## Purpose

Close the governance gap where no Azure Policy assignments enforce baseline
guardrails. The benchmark audit found: no tag enforcement policy, no denial of
public PostgreSQL access, no Key Vault requirement policy. Resources can be
created without tags, with public endpoints, and without secrets management.

## When to Use

- Implementing Azure Policy assignments for the IPAI subscription.
- Enforcing tagging standards across resource groups.
- Preventing public database endpoints via policy.
- Requiring Key Vault for secret management.

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `infra/azure/main.bicep` | Existing policy assignment resources |
| `infra/ssot/azure/resources.yaml` | Resource tags, naming patterns |
| `infra/ssot/azure/service-matrix.yaml` | Services that need tag compliance |
| `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` | Policy/governance line items |
| `docs/audits/ODOO_AZURE_ENTERPRISE_BENCHMARK.md` | Policy gap row |

## Microsoft Learn MCP Usage

Run at least these three queries:

1. `microsoft_docs_search("Azure Policy require tag resource group built-in")`
   -- retrieves the built-in policy for requiring tags on resources.
2. `microsoft_docs_search("Azure Policy deny public network access PostgreSQL")`
   -- retrieves policy definitions for denying public PG access.
3. `microsoft_docs_search("Azure Policy audit Key Vault usage secrets")`
   -- retrieves policies requiring KV for secret storage.

Optional:

4. `microsoft_code_sample_search("bicep policy assignment require tag", language="bicep")`
5. `microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/governance/policy/samples/built-in-policies")`

## Workflow

1. **Inspect repo** -- Read Bicep for any existing policy definitions or
   assignments. Check SSOT YAML for tagging conventions. Identify which
   built-in policies are needed.
2. **Query MCP** -- Run the three searches. Capture built-in policy definition
   IDs, assignment Bicep syntax, effect options (Deny vs Audit).
3. **Compare** -- Identify: (a) Are any policies assigned? (b) Do resources
   have consistent tags? (c) Is public PG access allowed? (d) Are secrets
   stored outside Key Vault?
4. **Patch** -- Create `infra/azure/modules/policy-assignments.bicep`:
   - Require `environment` and `owner` tags on resource groups (effect: Deny).
   - Deny public network access on PG Flexible Servers (effect: Deny).
   - Audit resources without Key Vault integration (effect: Audit).
   Start with Audit mode for 7 days, then switch to Deny.
5. **Verify** -- Bicep lints clean. Policy assignment count documented. SSOT
   updated. Go-live checklist includes policy verification.

## Outputs

| File | Change |
|------|--------|
| `infra/azure/modules/policy-assignments.bicep` | Policy assignments (new) |
| `infra/azure/main.bicep` | Wire policy module |
| `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` | Policy verification steps |
| `infra/ssot/azure/resources.yaml` | Policy assignment entries |
| `docs/evidence/<stamp>/azure-policy-guardrails/` | Policy defs, MCP excerpts |

## Completion Criteria

- [ ] At least 3 policy assignments exist in Bicep (tags, public PG, KV).
- [ ] Tag enforcement policy requires `environment` and `owner` on resource groups.
- [ ] Public PG access denial policy targets `Microsoft.DBforPostgreSQL/flexibleServers`.
- [ ] Key Vault audit policy checks for secret references.
- [ ] Policies start in Audit mode with documented plan to switch to Deny.
- [ ] Go-live checklist includes policy compliance check.
- [ ] Evidence directory contains policy definitions and MCP excerpts.
