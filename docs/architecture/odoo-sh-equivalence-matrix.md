# Odoo.sh Equivalence Matrix — Azure Target

**Rev:** 2026-04-16
**Authority:** `infra/ssot/odoo/odoo-saas-minimum-bom.yaml`

---

## Purpose

Map Odoo.sh service guarantees to their Azure equivalents. Copy the **operating model**, not the UI.

---

## Equivalence matrix

| Odoo.sh feature | Azure equivalent | Required now | Later | Repo owner | IPAI status |
|---|---|---|---|---|---|
| **Git-driven build/deploy** | GitHub + Azure Pipelines → ACR → ACA revision | ✅ | | infra | Partial (ACR build works, pipeline not gated) |
| **Isolated container runtime** | ACA container per revision | ✅ | | infra | ✅ Live |
| **Auto dependency install** | `pip install` + `apt-get` in Dockerfile | ✅ | | docker | ✅ In image |
| **Web + Worker + Cron topology** | 3 ACA apps (web/worker/cron) | ✅ | | infra | ✅ Live |
| **Managed PostgreSQL** | Azure PG Flexible Server | ✅ | | infra | ✅ Live (pg-ipai-odoo) |
| **Backup + PITR** | PG Flex 7-35 day retention + PITR | ✅ | | infra | ✅ 7-day (extend at go-live) |
| **Restore drill** | Restore to new PG server + validate | ✅ | | infra | ❌ Not executed |
| **Domain + HTTPS** | ACA custom domain + managed TLS cert | ✅ | | infra | ✅ erp.insightpulseai.com |
| **Proxy/forwarded-proto** | ACA ingress + proxy_mode=True | ✅ | | infra | 🟡 Works but http:// leak (addon fix) |
| **Shell / log access** | ACA console logs + `az containerapp logs` | ✅ | | infra | ✅ Working |
| **Real-time logs** | Log Analytics / Azure Monitor | | ✅ | infra | ❌ Not configured |
| **Secrets management** | Azure Key Vault | ✅ | | infra | 🟡 KV exists, PG password still plaintext |
| **Branch → environment mapping** | Git branch → pipeline → ACA revision | | ✅ | infra | ❌ Not automated |
| **Staging environment** | Duplicate ACA topology + odoo_staging DB | | ✅ | infra | ❌ Not deployed |
| **Dev environment** | Local Docker (Colima) + odoo_dev DB | ✅ | | odoo | ✅ Colima profile exists |
| **Mail safety (non-prod)** | Mail catcher / SMTP disabled in staging | | ✅ | odoo | ❌ Not implemented |
| **Integration sandboxing** | Disabled payment/marketplace in staging | | ✅ | odoo | ❌ Not implemented |
| **Cron safety (non-prod)** | max_cron_threads=0 in dev/staging web | | ✅ | odoo | ❌ Not implemented |
| **Monitoring / alerts** | Azure Monitor + App Insights | | ✅ | infra | ❌ Not configured |
| **CI pipeline (lint/test)** | Azure Pipelines | ✅ | | infra | 🟡 Definitions exist, no proven runs |
| **Deploy gate (review/approve)** | Pipeline environment approvals | | ✅ | infra | ❌ Not configured |
| **Addon path management** | addons_path in odoo.conf (build-time) | ✅ | | docker | ✅ In image |
| **OCA submodule support** | Git submodules or hydrated in image | ✅ | | docker | ✅ In Dockerfile |

---

## Scorecard

| Category | Items | Done | Partial | Missing |
|---|---|---|---|---|
| **Must reproduce now** | 13 | 8 | 3 | 2 |
| **Reproduce later** | 9 | 1 | 0 | 8 |
| **Total** | 22 | 9 | 3 | 10 |

**41% complete, 55% with partials counted.**

---

## Priority gap closure (shortest path to Odoo.sh parity)

### Wave 1 — Required now, missing

1. **Restore drill** — execute PG PITR to a test server, validate data, document
2. **Secrets to KV** — move PG password from ACA env to Key Vault secretRef

### Wave 2 — Required now, partial

3. **CI pipeline proven run** — trigger Azure Pipeline, verify image build + deploy
4. **Proxy/HTTPS clean** — wire AFD or verify ACA forwarded-proto; remove SSO addon
5. **Secrets audit** — enumerate all KV secrets, verify completeness

### Wave 3 — Later, high value

6. **Staging environment** — deploy second ACA topology + odoo_staging DB
7. **Log Analytics** — wire ACA → Log Analytics workspace
8. **Mail safety** — mail catcher for staging/dev
9. **Deploy gate** — pipeline environment approvals before prod

### Wave 4 — Later, nice to have

10. **Branch → env automation**
11. **Integration sandboxing**
12. **Monitoring dashboards**
13. **Cron safety controls**

---

## What NOT to copy from Odoo.sh

- Odoo.sh browser UI/UX
- Drag-and-drop branch promotion
- Odoo.sh-specific container restrictions
- Odoo.sh hosting abstractions
- Any Odoo.sh IAP dependency

---

## Clean target state

| Environment | Topology | Database | Integrations | Mail |
|---|---|---|---|---|
| **Dev** | Local Docker (Colima) | odoo_dev (local) | All disabled | Console only |
| **Staging** | ACA web+worker+cron | odoo_staging (Azure PG) | Sandboxed | Mail catcher |
| **Production** | ACA web+worker+cron | odoo (Azure PG) | Live | Zoho SMTP |

---

## Anchors

- `infra/ssot/odoo/odoo-saas-minimum-bom.yaml`
- `infra/ssot/odoo/odoo-saas-recommended-bom.yaml`
- `ssot/odoo/environment-contract.yaml`
- `docker/Dockerfile.prod`
