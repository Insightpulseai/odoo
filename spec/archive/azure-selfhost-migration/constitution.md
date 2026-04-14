# Azure Self-Host Migration -- Constitution

> Non-negotiable rules governing the managed Supabase to Azure self-host cutover.
> Source: `spdtwktxdalcfigzeqrz` (cloud) to `4.193.100.31` (Azure VM, 14 Docker services).

---

## Source of Truth

| Role | System | Identifier |
|------|--------|------------|
| **Active source** | Managed Supabase (cloud) | Project `spdtwktxdalcfigzeqrz` |
| **Migration target** | Azure self-hosted VM | `4.193.100.31` (Docker Compose, 14 services + n8n) |
| **Migration workflow** | GitHub Actions | `.github/workflows/supabase-self-host-migration.yml` |
| **Consumer manifest** | Repo | `platform/supabase/cutover/consumers.yaml` |
| **Seed evidence** | Repo | `docs/architecture/SEED_DATA_INVENTORY.md` |
| **Migration manifests** | Repo | `ssot/migration/*.yaml` |

---

## Rules

### R1: No VM-to-ACA/AKS replatforming in the same cutover

The Azure VM (`4.193.100.31`) is the landing zone for this migration. The VM stays as-is; only data moves. Runtime replatforming to Azure Container Apps or AKS is a **separate program** that may only begin after parity is proven and the managed Supabase project is decommissioned. Any PR that introduces ACA/AKS resource definitions during migration phases 1--5 must be rejected.

### R2: Seed canonicalization before replay

Raw copies of seed data are banned. The seed inventory (`SEED_DATA_INVENTORY.md`) documents 6 duplicate groups. Only canonical seed sources (per `ssot/migration/seed_canonical_map.yaml`) are replayed to the target. The canonical map must be consumed and resolved before any seed data is written to the target database. Duplicate and deprecated sources are excluded at the script level, not by manual filtering.

### R3: All n8n workflows imported disabled first

Every n8n workflow is imported with `active: false`. No exceptions. Enablement happens in controlled waves after smoke testing each wave:

| Wave | Scope | Prerequisite |
|------|-------|-------------|
| 1 | Health / control plane | Import verification complete |
| 2 | Read-only / observability | Wave 1 stable for 1h |
| 3 | Business automation (sync, project) | Wave 2 stable for 1h |
| 4 | Finance / BIR | Wave 3 stable for 2h |
| 5 | Write-path / deployment | Wave 4 stable for 4h |

### R4: Machine-verifiable parity -- every gate has a script, no manual checks

No migration phase is considered complete without machine-readable evidence produced by a script. Human eyeball confirmation is not a valid gate. Required evidence per phase:

| Check | Method | Tolerance |
|-------|--------|-----------|
| Table row counts | `SELECT count(*) FROM <table>` source vs target | Within 1% |
| Critical table integrity | Keyed checksum (MD5 of ordered PKs + critical columns) | Exact match |
| Edge function health | HTTP GET to each function endpoint | 200 OK |
| Scheduler presence | `SELECT * FROM cron.job` source vs target | Exact count match |
| Workflow import | n8n API list all workflows, assert `active: false` | 100% disabled |
| Consumer endpoints | Health check on all 8 consumers post-rewire | All pass |

### R5: Rollback always available -- cloud Supabase stays read-only until cutover verified

The managed Supabase project remains the active source until cutover verification passes all gates. At any point before final decommission, traffic can be reverted by repointing endpoints back to `spdtwktxdalcfigzeqrz.supabase.co`. The cloud project must not be paused, scaled down, or decommissioned until the 7-day soak period completes with zero incidents.

Rollback trigger thresholds:
- Any critical consumer health check fails post-cutover
- Data parity drift >1% on any monitored table
- >3 edge function failures in 1 hour
- n8n workflow error rate >10% in first 24h

### R6: No plaintext secrets in migration artifacts -- Azure Key Vault only, mask in CI logs

All secrets resolve from Azure Key Vault (`kv-ipai-dev`) at runtime. Migration scripts use `az keyvault secret show` or environment variables injected by GitHub Actions. Connection strings, API keys, JWT secrets, and passwords must never appear in:
- Script source code
- CI workflow logs (use `::add-mask::` in GitHub Actions)
- Migration evidence files
- Commit messages or PR descriptions

---

## Migration Order (Strict)

1. Schema (extensions, roles, grants, DDL)
2. Reference data / seeds (canonical sources only)
3. Transactional tables (PK/FK order preserved)
4. Storage / objects (bucket metadata + files)
5. Edge Functions (deploy to self-hosted Deno runtime)
6. Schedulers / pg_cron (import disabled, enable by wave)
7. n8n workflows (import disabled, enable by wave)
8. Cutover (freeze source, delta replay, repoint endpoints)

---

## Reconciliation Plane

Databricks serves as the **reconciliation plane** for post-migration data validation and drift detection. It is explicitly **not** the operational cutover plane. Databricks queries compare source and target states; it does not participate in data movement or consumer rewiring.

---

## Separation of Concerns

**Migration** (phases 1--5) and **enablement** (post-cutover n8n waves) are separate workstreams with separate gates. Migration is complete when all data and functions are present on the target. Enablement is complete when all consumers and workflows are operational. These must not be conflated in planning, execution, or reporting.
