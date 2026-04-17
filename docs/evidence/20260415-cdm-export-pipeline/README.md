# Evidence — Odoo → CDM Gold Export Pipeline deployed

**Stamp:** 2026-04-15
**Closes (partial):** Issue 26 — CDM export pipeline code committed + deployed to Databricks; first run not yet triggered.

## What shipped

| Artifact | Path | Status |
|---|---|---|
| Pipeline README | `data-intelligence/pipelines/odoo_cdm_export/README.md` | ✅ |
| DLT Python source | `data-intelligence/pipelines/odoo_cdm_export/pipeline.py` | ✅ Uploaded to Databricks `/Shared/ipai/cdm_export/pipeline` |
| CDM manifest generator | `data-intelligence/pipelines/odoo_cdm_export/cdm_manifest_generator.py` | ✅ Uploaded to Databricks `/Shared/ipai/cdm_export/cdm_manifest_generator` |
| Databricks job config | `data-intelligence/pipelines/odoo_cdm_export/job.yml` | ✅ Reference config |
| DLT pipeline (Databricks UC) | `pipeline_id: 3495d54a-bfc9-47aa-9fc5-517f190e430b` | ✅ Created (development mode, serverless) |

## Pipeline metadata

- Name: `ipai-odoo-cdm-export`
- Pipeline ID: `3495d54a-bfc9-47aa-9fc5-517f190e430b`
- Workspace: `dbw-ipai-dev` (https://adb-7405608559466577.17.azuredatabricks.net)
- Catalog: `ipai_dev`
- Target schema (for DLT): `bronze` (Silver + Gold tables live under catalog via `@dlt.table` targeting)
- Compute: Serverless
- Mode: Development (set to production after first clean run)
- Channel: CURRENT
- Photon: Enabled

## Entity coverage — Phase 1

| CDM entity | Odoo source | Discriminator |
|---|---|---|
| Invoice | account.move | move_type='out_invoice' |
| VendorInvoice | account.move | move_type='in_invoice' |
| Payment | account.payment | — |
| BankStatementLine | account.bank.statement.line | — |
| Account | res.partner | is_company=true |
| Contact | res.partner | is_company=false |

Full ~35-entity Phase 2 expansion: same pipeline, add more `@dlt.table` blocks per `platform/contracts/cdm-entity-map.yaml`.

## Next steps (to trigger first run)

```bash
TOKEN=$(az account get-access-token --resource 2ff814a6-3304-4ab8-85cb-cd0e6f879c1d --query accessToken -o tsv)
WS="https://adb-7405608559466577.17.azuredatabricks.net"
PIPELINE_ID="3495d54a-bfc9-47aa-9fc5-517f190e430b"

# Trigger first run
curl -sS -X POST -H "Authorization: Bearer $TOKEN" \
  "$WS/api/2.0/pipelines/$PIPELINE_ID/updates" \
  -d '{"full_refresh": true}' \
  -H "Content-Type: application/json"

# Check status
curl -sS -H "Authorization: Bearer $TOKEN" \
  "$WS/api/2.0/pipelines/$PIPELINE_ID" \
  | python3 -m json.tool | head -40
```

## Known issues to watch on first run

1. **`path=` arg conflict on Gold tables** — current pipeline.py specifies explicit `path=abfss://gold@stipaidevlake.../Entity` on Gold `@dlt.table` decorators. `ipai_dev` catalog's storage_root is already set to that same location. On first run this may error with "path conflicts with catalog-managed storage" — remove the `path=` args and let UC manage Gold tables under catalog storage.
2. **`odoo_erp` FOREIGN_CATALOG data availability** — pipeline reads from `odoo_erp.public.account_move` etc. If Lakehouse Federation to `pg-ipai-odoo` isn't populated for the target tables (or RBAC isn't granted to the DLT service principal), the run fails.
3. **CDM manifest generator is a separate notebook** — needs job orchestration (via `job.yml` tasks OR Databricks Workflows) to run AFTER the DLT pipeline succeeds.

## Verification after first successful run

```sql
-- From Databricks SQL Warehouse or ipai_dev catalog
SHOW TABLES IN ipai_dev.gold;

SELECT COUNT(*) FROM ipai_dev.gold.Invoice;
SELECT COUNT(*) FROM ipai_dev.gold.Payment;
SELECT COUNT(*) FROM ipai_dev.gold.BankStatementLine;

-- Check ADLS for CDM manifests
-- (after cdm_manifest_generator notebook run)
```

```bash
az storage blob list \
  --account-name stipaidevlake \
  --container-name gold \
  --prefix ipai_dev/ \
  --auth-mode login -o table | head -20
```

## Downstream unblocks (now possible)

- **Issue 27 — Fabric capacity provisioning + `fcipaidev` workspace**: can shortcut directly to `ipai_dev.gold` via UC
- **Issue 28 continuation — Metric views** (DSO, DPO, filing_on_time_rate): can now define over populated Gold tables
- **Fabric Data Agent**: wraps `ipai_dev.gold` + `ipai_dev.metrics` for M365 Copilot Analyst consumption
- **Power BI semantic model**: direct-query over `ipai_dev.gold`

## Related

- `platform/contracts/cdm-entity-map.yaml` — entity mapping SSOT
- `docs/architecture/cdm-odoo-mapping.md` — full mapping doc
- `docs/architecture/semantic-layer.md` — UC metrics positioning
- `docs/evidence/20260415-uc-bootstrap/` — prerequisite UC catalog+schema creation

---

*Evidence locked 2026-04-15.*
