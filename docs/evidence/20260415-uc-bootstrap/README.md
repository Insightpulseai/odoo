# Evidence — Unity Catalog bootstrap on dbw-ipai-dev

**Stamp:** 2026-04-15
**Workspace:** `dbw-ipai-dev` (https://adb-7405608559466577.17.azuredatabricks.net)
**Workspace ID:** 7405608559466577
**Subscription:** Microsoft Azure Sponsorship (`eba824fb-332d-4623-9dfb-2c9f7ee83f4e`)
**RG:** `rg-ipai-dev-ai-sea`
**SKU:** Premium (UC requires Premium ✓)
**Closes:** Issue 28 (`docs/backlog/open-issues-20260415.md`)

## What was deployed

### Catalogs (3 IPAI environments)

| Catalog | Type | storage_root |
|---|---|---|
| `ipai_dev` | MANAGED | `abfss://gold@stipaidevlake.dfs.core.windows.net/ipai_dev` |
| `ipai_staging` | MANAGED | `abfss://gold@stipaidevlake.dfs.core.windows.net/ipai_staging` |
| `ipai_prod` | MANAGED | `abfss://gold@stipaidevlake.dfs.core.windows.net/ipai_prod` |
| `odoo_erp` | FOREIGN | (pre-existing — Lakehouse Federation → `pg-ipai-odoo`) |

### Schemas (5 per catalog, 15 total IPAI schemas)

Each of the 3 catalogs above has:
- `bronze` — raw Odoo-shaped landing
- `silver` — cleaned, typed, Odoo naming preserved
- `gold` — CDM-projected entities per `platform/contracts/cdm-entity-map.yaml`
- `metrics` — canonical metric views per `docs/architecture/semantic-layer.md §1`
- `features` — ML feature store (Phase 3 fine-tune corpus)

Plus auto-created: `default`, `information_schema` (UC standard).

## Verification (run to confirm)

```bash
WS_URL="adb-7405608559466577.17.azuredatabricks.net"
TOKEN=$(az account get-access-token --resource 2ff814a6-3304-4ab8-85cb-cd0e6f879c1d --query accessToken -o tsv)

# List IPAI catalogs
curl -sS -H "Authorization: Bearer $TOKEN" "https://$WS_URL/api/2.1/unity-catalog/catalogs" \
  | python3 -c "import sys,json; r=json.load(sys.stdin); [print(c['name']) for c in r.get('catalogs',[]) if c['name'].startswith('ipai_')]"

# List schemas in ipai_dev
curl -sS -H "Authorization: Bearer $TOKEN" \
  "https://$WS_URL/api/2.1/unity-catalog/schemas?catalog_name=ipai_dev" \
  | python3 -m json.tool
```

## What was NOT deployed (deferred to other issues)

- **Bronze ingestion** — needs Databricks DLT pipeline reading from `pg-ipai-odoo` via the `odoo_erp` FOREIGN_CATALOG (separate task; Issue 26 CDM export covers Gold side)
- **First metric views** (`dso_daily`, `dpo_daily`, `filing_on_time_rate`) — DDL is locked in `docs/architecture/semantic-layer.md §2.1` but views can't be created until Gold has data
- **Role assignments** (`agent_reader_ipai` per agent MI) — separate task; needs Issue 28's role assignment block
- **Fabric mirror** — Issue 27, separate

## Open follow-ups (now unblocked)

- Issue 26 — CDM export pipeline can target `ipai_dev.gold.*` directly
- Issue 28 — schema bootstrap done; metric views + role assignments remain
- Issue 27 — Fabric mirror can shortcut to `stipaidevlake/gold/<catalog>/`

## Bootstrap method

Direct REST API calls to Databricks Unity Catalog endpoints — no CI/CD, no Bicep template, no `terraform apply`. Per user directive 2026-04-15 "ignore ci/cd for now build directly to deploy."

Auth: `DefaultAzureCredential` → Databricks resource (`2ff814a6-3304-4ab8-85cb-cd0e6f879c1d`) → bearer token to `adb-*.azuredatabricks.net/api/2.1/unity-catalog/*`.

No secrets in this evidence file. No state stored outside Databricks UC + this audit log.
