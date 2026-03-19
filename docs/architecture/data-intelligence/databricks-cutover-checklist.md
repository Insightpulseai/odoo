# Databricks Workspace Cutover Checklist

## `notion-ppm` → `finance-ppm` Secret Scope Rename

> This is a **workspace config cutover**, not just a code rename.
> Code-side rename is complete. This checklist covers the workspace-side actions.

---

## Pre-Cutover Status

| Item | Status |
|------|--------|
| Active code references renamed to `finance-ppm` | DONE |
| Bundle/job/resource configs renamed | DONE |
| SQL injection risk mitigated (identifier validation + value sanitization) | DONE |
| Parameterized query execution (ideal end-state) | DEFERRED |
| Databricks Bicep hardened (VNet/diagnostics params) | DONE |
| Service principal contract created | DONE |
| Workspace secret scope renamed | **BLOCKED — requires workspace action** |

---

## 1. Pre-Cutover Freeze

- [ ] Confirm no active code/config references to `notion-ppm` remain
- [ ] Confirm no active jobs are mid-run in the target environment
- [ ] Confirm workspace host/profile for the target environment
- [ ] Inventory current contents of `notion-ppm` scope

## 2. Scope-Type Decision

Determine the backend of `notion-ppm`:

| Type | Action |
|------|--------|
| **Databricks-backed** | Recreate secrets inside new scope |
| **Azure Key Vault-backed** | Rebind new scope to Key Vault path/permissions |

## 3. Inventory Old Scope

Capture:
- [ ] Scope name: `notion-ppm`
- [ ] Scope backend type (Databricks or Key Vault)
- [ ] All secret keys in the scope
- [ ] All ACLs / scope permissions
- [ ] All jobs, pipelines, notebooks referencing it
- [ ] All service principals / run-as identities depending on it

**Do NOT delete the old scope yet.**

## 4. Create New Scope

- [ ] Create scope: `finance-ppm`
- [ ] Verify name constraints (alphanumerics, `-`, `_`, `@`, `.`)
- [ ] Verify uniqueness in workspace

## 5. Recreate Secret Contents

For every key in `notion-ppm`:
- [ ] Create same key in `finance-ppm`
- [ ] Preserve exact key names
- [ ] Preserve environment-specific values
- [ ] Verify all expected keys exist in `finance-ppm`

## 6. Reapply ACLs / Permissions

- [ ] Managers/admins
- [ ] Job run identities
- [ ] Service principals (especially `finance-ppm-service-principal`)
- [ ] Groups/users with read or manage access

## 7. Validate Bundle/Config References

Re-check all source-managed references:
- [ ] `infra/databricks/databricks.yml` — bundle name, SP name
- [ ] `infra/databricks/resources/jobs.yml` — 5 secret scope refs
- [ ] `infra/databricks/resources/permissions/uc_grants.yml` — SP ref
- [ ] `infra/databricks/notebooks/bronze/ingest_notion.py` — 4 `dbutils.secrets.get()` calls
- [ ] Any DAB variables/substitutions deriving scope names

## 8. Validate Bundle Before Deploy

- [ ] `databricks bundle validate` passes
- [ ] Target/environment resolution succeeds
- [ ] Job/resource config inspection clean
- [ ] Zero `notion-ppm` references in validated output

## 9. Runtime Smoke Checks

- [ ] Notebook reads a secret from `finance-ppm`
- [ ] Job run using `finance-ppm` succeeds
- [ ] Pipeline/resource using `finance-ppm` resolves
- [ ] Service principal / run-as path works
- [ ] UC grants / downstream auth assumptions valid

## 10. Rollback Posture

Until proven:
- [ ] Keep `notion-ppm` intact
- [ ] Do not delete old secrets/scope
- [ ] Record which workloads are switched
- [ ] Only remove old scope after validation + quiet period

## 11. Evidence to Capture

Store in `docs/evidence/<YYYYMMDD-HHMM>/finance-ppm-cutover/`:
- [ ] Old scope inventory
- [ ] New scope creation proof
- [ ] Key parity checklist
- [ ] ACL parity checklist
- [ ] Bundle validation result
- [ ] Successful job/notebook/pipeline evidence
- [ ] Final "zero active `notion-ppm` references" scan

## 12. Cutover Completion Criteria

All must be true:
- [ ] `finance-ppm` exists in target workspace
- [ ] All required keys present
- [ ] ACLs/permissions re-applied
- [ ] Bundle validation passes
- [ ] Runtime smoke tests pass
- [ ] No active source or deployed config references `notion-ppm`
- [ ] Old scope retained only as rollback safety

## Post-Cutover Cleanup

After observation window:
- [ ] Delete or archive `notion-ppm` scope
- [ ] Remove rollback-only references
- [ ] Update runbooks/SSOT
- [ ] Add CI grep check to fail if `notion-ppm` reappears in active code

---

## Security Language Note

The SQL injection hardening applied to `databricks_writer.py` uses **strict identifier validation** and **safe value sanitization**. This **materially reduces** injection risk but is not equivalent to true **parameterized statement execution**. The correct audit language is:

> SQL injection risk mitigated/hardened significantly; parameterized query execution remains the ideal end-state.

---

## Related

- Code rename: `infra/databricks/`, `.continue/rules/finance-ppm.yaml`
- Identity contract: `ssot/data-intelligence/identity.yaml`
- Repo split plan: `docs/architecture/data-intelligence/repo-split-plan.md`
- Portfolio scorecard: `ssot/agent-platform/portfolio_scorecard.yaml`
