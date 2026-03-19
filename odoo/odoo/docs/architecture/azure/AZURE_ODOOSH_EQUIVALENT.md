# Azure-Native Odoo.sh Equivalent — Target State

> Odoo.sh is the **capability benchmark**, not the implementation target.
> Azure is the **deployment surface**. This document codifies the behavior
> on top of Azure primitives to deliver Odoo.sh-style workflows with
> Azure-grade identity, networking, observability, and governance.
>
> SSOT twin: `ssot/governance/azure-odoosh-equivalent.yaml`

---

## 1. Design Doctrine

**Odoo.sh gives you platform behavior. Azure gives you platform primitives.
Our job is to codify the behavior on top of the primitives.**

What to copy from Odoo.sh:
- Every commit builds, tests run, promotion gates exist
- Branch-based environments (dev / staging / production)
- Staging refreshed from sanitized production snapshots
- Shell/log access, mail capture, non-prod safety controls
- Backup/restore in scripted workflows, not ad-hoc
- Custom domain + TLS + monitoring + KPIs

What **not** to copy (Odoo.sh platform constraints, not features):
- No long-lived daemon processes → Azure supports sidecars/queues
- No system package installs → Azure supports custom images
- No PostgreSQL extensions → Azure Flexible Server supports extensions
- Constrained cron runtime → Azure supports background jobs
- Single worker on non-prod → Azure supports custom scaling
- No custom infra topology → Azure supports full network control

---

## 2. Canonical Naming

### Databases (underscores — canonical, never renamed)

- `odoo_dev` — clean control development database
- `odoo_dev_demo` — auxiliary development showroom/demo database (not a separate environment)
- `odoo_staging` — staging rehearsal database
- `odoo` — production database

### Environments (hyphens — Azure resource/infra labels only)

- `dev` hosts `odoo_dev` and may also host `odoo_dev_demo`
- `staging` hosts `odoo_staging`
- `production` hosts `odoo`

Database names are canonical and must not be renamed to hyphenated environment labels.
Hyphenated forms such as `odoo-dev`, `odoo-staging`, and `odoo-production` may be used
only for Azure resource or environment naming where needed.

### Banned names (never use)

- `odoo_prod` — use `odoo`
- `odoo_core` — deprecated
- `odoo_stage` — use `odoo_staging`
- `odoo_dev_clean` — use `odoo_dev`

---

## 3. Platform Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        CONTROL PLANE                              │
│  GitHub (source) → Azure DevOps / GitHub Actions (CI/CD)          │
│  Entra ID (identity) → Key Vault (secrets)                        │
└───────────────────────────┬──────────────────────────────────────┘
                            │ deploy / promote / rollback
┌───────────────────────────▼──────────────────────────────────────┐
│                        RUNTIME PLANE                              │
│                                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │   DEV env   │  │ STAGING env │  │  PROD env   │               │
│  │ ACA / VM    │  │ ACA / VM    │  │ ACA / VM    │               │
│  │ odoo_dev    │  │ odoo_staging│  │ odoo        │               │
│  │ mail: sink  │  │ mail: sink  │  │ mail: Zoho  │               │
│  │ cron: off   │  │ cron: gated │  │ cron: live  │               │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘               │
│         │                │                │                       │
│  ┌──────▼────────────────▼────────────────▼──────┐               │
│  │  Azure Database for PostgreSQL Flexible Server │               │
│  │  (per-env databases, same or separate servers) │               │
│  └───────────────────────────────────────────────┘               │
│                                                                    │
│  Azure Blob Storage (filestore, backups, artifacts)               │
│  Azure Container Registry (Odoo images)                           │
└───────────────────────────┬──────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                      EDGE / ROUTING                               │
│  Cloudflare DNS (authoritative) → Azure Front Door (TLS/WAF)     │
│  erp.insightpulseai.com → prod                                    │
│  erp-staging.insightpulseai.com → staging                         │
│  erp-dev.insightpulseai.com → dev                                 │
└──────────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                     OBSERVABILITY                                 │
│  Azure Monitor → Log Analytics → Application Insights             │
│  Dashboards + Alerts + Deployment Evidence                        │
└──────────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                      AI / COPILOT PLANE                           │
│  Microsoft Foundry → AI Gateway → Evaluation Gates → Publish      │
│  Odoo bridge API (ipai_enterprise_bridge)                         │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Odoo.sh Feature Parity Matrix

### Capability mapping

| Odoo.sh Capability | Azure Target Equivalent | Owner Repo | Status |
|--------------------|------------------------|------------|--------|
| Every commit builds | Pipeline trigger on push/PR | `odoo` | Partial — CI exists, deploy gate missing |
| Branch test environments | Preview/staging environments per branch | `infra` | Planned |
| Staging from prod-like data | Staging refresh workflow from sanitized prod backup | `odoo` + `infra` | Planned |
| Shell access | `az ssh`, ACA exec, or VM/container shell | `infra` | Available |
| Logs in browser | Azure Monitor + Log Analytics + App Insights | `infra` | Planned |
| Automated test builds | CI pipeline + Odoo test matrix | `odoo` | Partial |
| Shareable branch environments | Preview environments with unique URLs | `infra` | Planned |
| Mail catcher in non-prod | SMTP sink (MailHog/Mailpit) on dev/staging | `odoo` | Planned |
| Backup / restore | Scripted backup + restore workflow | `odoo` + `infra` | Partial |
| Custom domain + TLS | Cloudflare + Front Door + managed certs | `infra` | Active |
| Monitoring / KPIs | Dashboards + alerts + deployment evidence | `infra` | Planned |
| Promote dev → staging → prod | Approval gates in pipeline | `odoo` + `infra` | Planned |
| Rollback | Previous image/migration rollback workflow | `odoo` + `infra` | Planned |
| Dependency/addons discovery | `addons.manifest.yaml` + CI validation | `odoo` | Active |
| Cron controls per env | Env-specific `ir.cron` activation | `odoo` | Planned |

### Persona parity requirements

| Persona | Minimum Requirements | Status |
|---------|---------------------|--------|
| **Developer** | PR build, test logs, shell access, deterministic addons loading, preview env per branch | Partial |
| **Tester** | Staging refresh from prod snapshot, mail capture, safe non-prod integrations, shareable URLs | Planned |
| **PM** | Promote dev→staging→prod, deployment history, rollback, approval gates | Planned |
| **Sysadmin** | Backups, restore, health dashboards, alerting, domain/TLS, runtime evidence, audited secrets | Partial |

---

## 5. Environment Model

### Per-environment contract

| Property | dev | staging | production |
|----------|-----|---------|------------|
| Database | `odoo_dev` | `odoo_staging` | `odoo` |
| Odoo workers | 1 | 2 | 4+ |
| Mail transport | MailHog sink (port 1025) | MailHog sink (port 1025) | Zoho SMTP (port 587) |
| Cron (`ir.cron`) | Disabled by default | Gated (manual enable) | Live |
| External integrations | Sandbox / mock | Sandbox / mock | Live |
| Payment providers | Test mode | Test mode | Live |
| Data source | Seed data or dev fixtures | Sanitized prod snapshot | Live data |
| Backup cadence | None (disposable) | Daily (7-day retention) | Daily (30-day retention) + PITR |
| Public URL | `erp-dev.insightpulseai.com` | `erp-staging.insightpulseai.com` | `erp.insightpulseai.com` |
| TLS | Front Door managed | Front Door managed | Front Door managed |
| Access | Developers only | Dev + QA + PM | All authorized users |
| `list_db` | `False` | `False` | `False` |

### Non-prod safety controls

```yaml
# config/environments/staging.yaml (example)
mail:
  transport: mailhog
  host: mailhog
  port: 1025
  catch_all: true       # All outbound mail captured, never delivered

cron:
  mode: gated            # ir.cron records created inactive
  whitelist:             # Only these crons run in staging
    - mail.mail_send
    - base.ir_cron_scheduler

integrations:
  payment_providers: test_mode
  sms_gateway: disabled
  external_apis: sandbox_only

data:
  refresh_source: production_sanitized
  pii_masking: true
  refresh_cadence: weekly
```

---

## 6. CI/CD Pipeline Architecture

### Pipeline stages

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Commit  │───▶│  Build   │───▶│   Test   │───▶│  Stage   │───▶│  Deploy  │
│  (push)  │    │  Image   │    │  Matrix  │    │  Promote │    │  Target  │
└─────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │              │               │               │               │
     │         Dockerfile      Unit tests      Approval gate    ACA revision
     │         + addons       Integration       (manual for     or VM deploy
     │         manifest       Lint / type       staging/prod)
     │                        Odoo --test-enable
     │                        Spec validation
     │
     └── PR → dev env auto-deploy
         merge to main → staging gate
         staging approved → production gate
```

### Build contract

```yaml
# Pipeline: build-odoo-image
trigger:
  branches: [main, 'feat/*', 'fix/*']

steps:
  - checkout
  - resolve_addons:        # Parse addons.manifest.yaml
      base: /opt/odoo/addons
      custom: /workspaces/odoo/addons/ipai
      oca: /workspaces/odoo/addons/oca
  - docker_build:
      dockerfile: docker/Dockerfile.unified
      registry: acripaidev.azurecr.io
      tag: "${GIT_SHA}"
  - test_matrix:
      database: test_${MODULE}
      modules: [changed_modules]
      flags: --stop-after-init --test-enable
  - lint:
      - black --check addons/ipai/
      - flake8 addons/ipai/
      - python3 -m py_compile
  - spec_validate:
      - ./scripts/spec_validate.sh
      - ./scripts/repo_health.sh
  - push_image:
      condition: all_tests_pass
```

### Promotion workflow

```
feature branch → PR → CI green → merge to main
                                      │
                     ┌────────────────▼──────────────────┐
                     │  Deploy to dev (automatic)         │
                     │  erp-dev.insightpulseai.com        │
                     └────────────────┬──────────────────┘
                                      │ manual approval
                     ┌────────────────▼──────────────────┐
                     │  Deploy to staging (gated)         │
                     │  Refresh from sanitized prod       │
                     │  erp-staging.insightpulseai.com    │
                     └────────────────┬──────────────────┘
                                      │ manual approval + evidence
                     ┌────────────────▼──────────────────┐
                     │  Deploy to production (gated)      │
                     │  erp.insightpulseai.com            │
                     │  Evidence pack required            │
                     └───────────────────────────────────┘
```

---

## 7. Backup & Restore

### Backup strategy

| Component | Method | Target | Cadence | Retention |
|-----------|--------|--------|---------|-----------|
| PostgreSQL (prod) | `pg_dump` + PITR | Blob Storage `backups/pg/prod/` | Daily + continuous WAL | 30 days |
| PostgreSQL (staging) | `pg_dump` | Blob Storage `backups/pg/staging/` | Daily | 7 days |
| Filestore (prod) | `azcopy sync` | Blob Storage `backups/filestore/prod/` | Daily | 30 days |
| Odoo config | Git-tracked | `config/` in repo | Every commit | Git history |
| Container images | ACR retention | `acripaidev.azurecr.io` | Per build | 90 days |

### Staging refresh workflow

```bash
#!/bin/bash
# scripts/staging_refresh.sh — Refresh staging from sanitized production

# 1. Dump production (exclude PII columns)
pg_dump -h $PROD_PG_HOST -U $PG_USER -d odoo \
  --exclude-table-data='mail_message' \
  --exclude-table-data='mail_mail' \
  --exclude-table-data='fetchmail_server' \
  -Fc -f /tmp/prod_sanitized.dump

# 2. Restore to staging
pg_restore -h $STAGING_PG_HOST -U $PG_USER -d odoo_staging \
  --clean --if-exists --no-owner -Fc /tmp/prod_sanitized.dump

# 3. Post-restore sanitization
psql -h $STAGING_PG_HOST -U $PG_USER -d odoo_staging <<SQL
  -- Disable outbound mail servers
  UPDATE ir_mail_server SET active = false;
  -- Reset all user passwords to staging default
  UPDATE res_users SET password = 'staging_default' WHERE login != '__system__';
  -- Disable live crons
  UPDATE ir_cron SET active = false WHERE id NOT IN (
    SELECT id FROM ir_cron WHERE cron_name IN ('Mail: Send', 'Scheduler')
  );
  -- Mask PII in partners
  UPDATE res_partner SET
    email = 'staging_' || id || '@example.com',
    phone = '000-000-0000',
    mobile = '000-000-0000'
  WHERE is_company = false;
SQL

# 4. Restart staging container to pick up new data
az containerapp revision restart ...
```

---

## 8. Observability Stack

### Monitoring architecture

```
Odoo container ──┬── stdout/stderr ──► Log Analytics workspace
                 │
                 ├── /web/health ──► Application Insights (availability)
                 │
                 ├── Odoo logs ──► Log Analytics (custom table)
                 │
                 └── PostgreSQL ──► Azure Monitor for PostgreSQL
                                    (query perf, connections, IOPS)

Front Door ──► Access logs + WAF logs ──► Log Analytics

Key Vault ──► Audit logs ──► Log Analytics
```

### Alert rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| Odoo health down | `/web/health` != 200 for 3min | Critical | Slack #ops-alerts |
| PostgreSQL CPU > 80% | 5min sustained | Warning | Slack #ops-alerts |
| Container restart loop | > 3 restarts in 10min | Critical | Slack + PagerDuty |
| Backup failure | Daily backup job fails | Critical | Slack + email |
| Disk usage > 85% | Storage account threshold | Warning | Slack #ops-alerts |
| Failed deployments | Pipeline failure on main | High | Slack #ci-alerts |
| WAF block spike | > 100 blocks in 5min | Warning | Slack #security |

### Dashboard: OdooOps KPIs

| KPI | Source | Target |
|-----|--------|--------|
| Uptime (prod) | App Insights availability | > 99.5% |
| Deploy frequency | Pipeline runs | > 1/week |
| Deploy lead time | Commit → prod | < 4 hours |
| MTTR | Incident → resolution | < 1 hour |
| Test pass rate | CI pipeline | > 95% |
| Backup success rate | Backup job | 100% |
| Secret rotation compliance | Key Vault audit | 100% on schedule |

---

## 9. Identity & Secrets

### Managed identity model

| Service | Identity | Key Vault Access | Purpose |
|---------|----------|-----------------|---------|
| Odoo Container App | `mi-ipai-odoo-dev` | `kv-ipai-dev` | DB creds, SMTP, API keys |
| CI Pipeline | Service Principal | `kv-ipai-dev` | Deploy secrets |
| Backup Job | `mi-ipai-platform-dev` | `kv-ipai-dev` | Storage + DB access |
| Front Door | Managed cert | — | TLS termination |

### Secret rotation schedule

| Secret | Rotation | Method |
|--------|----------|--------|
| PostgreSQL passwords | 90 days | Key Vault auto-rotate → restart container |
| Zoho SMTP credentials | 180 days | Manual rotate → Key Vault → restart |
| API keys (external) | 90 days | Key Vault auto-rotate |
| JWT signing keys | 365 days | Key Vault auto-rotate |
| Container Registry tokens | 90 days | Entra ID managed |

---

## 10. Repo Ownership Matrix

| Capability | Owner Repo | Key Paths |
|------------|-----------|-----------|
| Odoo runtime config | `odoo` | `config/environments/`, `odoo19/` |
| Odoo addons/modules | `odoo` | `addons/ipai/`, `addons/oca/` |
| CI/CD pipelines | `odoo` + `infra` | `.github/workflows/`, `azure-pipelines/` |
| Container images | `odoo` | `docker/Dockerfile.*` |
| Azure infra (IaC) | `infra` | `infra/terraform/`, `infra/bicep/` |
| DNS records | `infra` | `infra/dns/subdomain-registry.yaml` |
| Key Vault config | `infra` | `infra/keyvault/` |
| Monitoring/alerts | `infra` | `infra/monitoring/` |
| Front Door config | `infra` | `infra/frontdoor/` |
| Backup scripts | `ops-platform` | `ops-platform/backup/` |
| Staging refresh | `ops-platform` | `ops-platform/staging/` |
| AI/Copilot bridge | `agents` | `agents/foundry/` |
| Edge functions | `ops-platform` | `ops-platform/supabase/` |

---

## 11. Implementation Phases

### Phase 1: Foundation (current state → baseline)

- [x] Azure Container Apps runtime deployed
- [x] PostgreSQL connectivity established
- [x] Key Vault secrets populated
- [x] Cloudflare DNS → Front Door routing
- [x] CI workflows running (partial)
- [ ] Container Registry (ACR) with automated image builds
- [ ] `config/environments/` per-env config files

### Phase 2: CI/CD Pipeline

- [ ] Build pipeline: commit → image → test → push
- [ ] Deploy pipeline: image → dev (auto) → staging (gated) → prod (gated)
- [ ] Odoo test matrix in CI (`--test-enable` per changed module)
- [ ] Spec validation gate
- [ ] Deployment evidence capture

### Phase 3: Environment Parity

- [ ] Dev environment with mail sink + disabled crons
- [ ] Staging environment with refresh-from-prod workflow
- [ ] Production environment with full observability
- [ ] Preview environments per feature branch (stretch)

### Phase 4: Observability

- [ ] Log Analytics workspace with Odoo container logs
- [ ] Application Insights for `/web/health` availability
- [ ] PostgreSQL monitoring (query perf, connections)
- [ ] Alert rules → Slack integration
- [ ] OdooOps KPI dashboard

### Phase 5: Backup & Restore

- [ ] Daily automated backup (DB + filestore)
- [ ] Staging refresh from sanitized prod
- [ ] Point-in-time restore capability
- [ ] Backup verification (restore test)

### Phase 6: Non-prod Safety

- [ ] Mail catcher (MailHog/Mailpit) on dev/staging
- [ ] Cron gating per environment
- [ ] Integration sandbox mode
- [ ] PII masking in staging refresh

---

## 12. What This Is Not

This is **not** a managed Odoo hosting platform. It is:

- A **codified operating model** for running Odoo 19 CE on Azure
- An **internal platform** for one organization (InsightPulse AI)
- **Self-managed** — we own the runtime, the data, the upgrades
- **Azure-native** — uses Azure primitives, not Odoo.sh abstractions

The tradeoff: more operational responsibility in exchange for
full control over extensions, scaling, networking, identity,
and cost structure.

---

*SSOT: `ssot/governance/azure-odoosh-equivalent.yaml`*
*Last updated: 2026-03-15*
