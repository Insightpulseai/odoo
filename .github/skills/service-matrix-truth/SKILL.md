# service-matrix-truth

**Impact tier**: P2 -- Quality / Accuracy

## Purpose

Close the inventory accuracy gap where the service matrix (`infra/ssot/azure/
service-matrix.yaml`) lists nginx:alpine stub containers as "active" services.
The benchmark audit found: Auth Gateway (svc_004), MCP Coordinator (svc_005),
and OCR Service (svc_006) are all nginx:alpine stubs with no functional
implementation, yet they appear as `status: active` / `promotion_state: live`.
This creates false confidence in the platform's operational surface.

## When to Use

- Auditing the service matrix for truth alignment.
- Preparing for a go-live readiness review where service status matters.
- Reconciling Azure resource inventory with actual deployed workloads.
- Removing phantom services from monitoring and alerting.

## Required Evidence (inspect these repo paths first)

| Path | What to look for |
|------|-----------------|
| `infra/ssot/azure/service-matrix.yaml` | Services with `note:` containing "Stub" or "nginx:alpine" |
| `infra/ssot/azure/resources.yaml` | ACA entries for stub services |
| `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` | Service verification line items |
| `docs/audits/ODOO_AZURE_ENTERPRISE_BENCHMARK.md` | Inventory accuracy gap row |

## Microsoft Learn MCP Usage

Run at least these three queries:

1. `microsoft_docs_search("Azure Container Apps list revisions active image")`
   -- retrieves how to verify what image is actually running in an ACA app.
2. `microsoft_docs_search("Azure Resource Graph query container apps image")`
   -- retrieves ARG queries to audit deployed container images at scale.
3. `microsoft_docs_search("Azure well-architected operational excellence inventory")`
   -- retrieves WAF guidance on maintaining accurate service inventories.

## Workflow

1. **Inspect repo** -- Read `service-matrix.yaml`. Identify every service with
   `note:` containing "Stub", "nginx:alpine", or "Replace with". List them.
2. **Query MCP** -- Run the three searches. Capture ACA revision inspection
   commands and ARG query syntax for image verification.
3. **Compare** -- For each stub service, determine: (a) Is there a real
   implementation planned? (b) What is the target image? (c) What is the
   timeline? If no implementation is planned, the service should be marked
   `status: stub` or `status: placeholder`, not `active`.
4. **Patch** -- Update `service-matrix.yaml`:
   - Change stub services from `status: active` to `status: stub`.
   - Change `promotion_state: live` to `promotion_state: placeholder`.
   - Add `target_image:` field documenting what will replace nginx:alpine.
   - Add `target_date:` field if a timeline exists.
   Update `resources.yaml` to match.
5. **Verify** -- No nginx:alpine service has `status: active`. All stub
   services are clearly marked. Go-live checklist distinguishes real services
   from placeholders.

## Outputs

| File | Change |
|------|--------|
| `infra/ssot/azure/service-matrix.yaml` | Stub status correction |
| `infra/ssot/azure/resources.yaml` | Lifecycle alignment |
| `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` | Service verification criteria |
| `docs/evidence/<stamp>/service-matrix-truth/` | Before/after diff, MCP excerpts |

## Completion Criteria

- [ ] No service with `note:` containing "Stub" or "nginx:alpine" has
      `status: active`.
- [ ] Stub services use `status: stub` or `status: placeholder`.
- [ ] Stub services have `promotion_state: placeholder` (not `live`).
- [ ] Each stub service documents its `target_image` and `target_date`.
- [ ] `resources.yaml` lifecycle fields match `service-matrix.yaml` status.
- [ ] Go-live checklist distinguishes between real and placeholder services.
- [ ] Evidence directory contains the before/after YAML diff.
