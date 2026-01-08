# Kickoff → Go-Live Checklist (CE/OCA/IPAI)

## Overview

This checklist provides a **deterministic, automation-first** path from project kickoff to production go-live for Odoo 18 CE + OCA + IPAI implementations. Every step is designed to be CI-verifiable.

**Target Stack:**
- Odoo 18 CE
- OCA modules (pinned via submodules)
- IPAI custom modules (v1.1.0 ship bundle)
- DigitalOcean infrastructure

---

## 0) Definition of Done

Before starting, ensure these are locked:

- [x] Target scope locked (modules + features to ship)
- [x] Environments defined: `dev`, `staging`, `prod`
- [x] Deterministic build + deploy path exists (tag → deploy)
- [x] "Green gates" required before prod deploy
- [x] Rollback plan tested (tag rollback + DB restore)

**Ship Bundle Reference:** `aiux_ship_manifest.yml` v1.1.0

---

## 1) Kickoff (Day 0–2)

### 1.1 Scope + Governance

| Task | Status | Verification |
|------|--------|--------------|
| Ship manifest finalized (modules + install order + gates) | [ ] | `cat aiux_ship_manifest.yml` |
| RACI: Owner, Implementer, Ops, Finance SME, Approver | [ ] | Documented in PRD |
| Change control: "scope change requires PRD bump + manifest bump" | [ ] | Process documented |

### 1.2 Repo + Release Control

| Task | Status | Verification |
|------|--------|--------------|
| Main branch protected (required checks + linear history + no force push) | [ ] | GitHub Settings |
| Release tags enabled (`prod-YYYYMMDD-HHMM` or semver) | [ ] | `git tag -l` |
| WHAT_SHIPPED + GO_LIVE_MANIFEST docs generated per deploy | [ ] | Template exists |

### 1.3 Infrastructure Decision

Pick one architecture:

| Option | When to Use | Status |
|--------|-------------|--------|
| **Single-node** (fast ship) | MVP, fast iteration | [ ] |
| **Split** (recommended) | Production stability | [ ] |
| **K8s** (later) | Only if operators + monitoring ready | [ ] |

**Recommended for v1.1.0:** Single-node with managed Postgres upgrade path.

---

## 2) Architecture Baseline (Day 2–5)

### 2.1 Networking / Edge

| Task | Status | Verification Command |
|------|--------|----------------------|
| DNS records set (A/AAAA/CNAME) | [ ] | `dig erp.insightpulseai.net` |
| TLS termination defined (nginx + Certbot) | [ ] | `curl -I https://erp.insightpulseai.net` |
| WebSocket support verified (`/websocket`, `/longpolling`) | [ ] | See PREVENT_502.md |
| `proxy_mode = True` configured | [ ] | Check `odoo.conf` |

### 2.2 Data Layer

| Task | Status | Verification Command |
|------|--------|----------------------|
| Postgres version fixed (16-alpine) | [ ] | `docker compose exec db psql -V` |
| Daily full backup configured | [ ] | Check backup script/cron |
| Restore test executed (staging) | [ ] | Documented proof |

### 2.3 Storage

| Task | Status | Verification Command |
|------|--------|----------------------|
| Filestore persistence (volume) | [ ] | `docker volume ls \| grep filestore` |
| Backup to object storage (Spaces) | [ ] | Check sync script |
| Attachment strategy: filestore (default) | [ ] | System parameter check |

### 2.4 Observability

| Task | Status | Verification Command |
|------|--------|----------------------|
| Health endpoints present (`/web/health`) | [ ] | `curl localhost:8069/web/health` |
| Logs shipped (rotation configured) | [ ] | Check log volume |
| Alerts: 502/504, crash loop, DB saturation | [ ] | Alert rules documented |

---

## 3) Build & Dependency Control (Week 1)

### 3.1 OCA Locking

| Task | Status | Verification Command |
|------|--------|----------------------|
| OCA repos pinned (submodules + lock file) | [ ] | `cat oca.lock.json` |
| Dependency graph recorded | [ ] | Check PRD module list |

### 3.2 CI "Green Gates"

| Gate | Workflow | Status |
|------|----------|--------|
| Lint + formatting | `ci.yml` | [ ] |
| No Enterprise/IAP guardrails | `repo-structure.yml` | [ ] |
| Install/upgrade test | `aiux-ship-gate.yml` | [ ] |
| Seed drift checks | `seeds-validate.yml` | [ ] |
| Data-model drift checks | `spec-and-parity.yml` | [ ] |

### 3.3 Artifact Strategy

| Task | Status | Verification |
|------|--------|--------------|
| Built image tagged and reproducible | [ ] | GHCR image exists |
| Deployment uses a tag (never "latest") | [ ] | Check compose file |

---

## 4) Functional Readiness (Week 1–2)

### 4.1 Core Odoo Config

| Task | Status | Verification Command |
|------|--------|----------------------|
| Base settings: timezone, locale, company | [ ] | Odoo UI / shell |
| Outgoing email configured (Mailgun) | [ ] | Test email send |
| Users/roles created (least privilege) | [ ] | User audit |
| Audit trail enabled | [ ] | Check mail tracking |

### 4.2 IPAI Modules Ready

| Module | Status | Verification |
|--------|--------|--------------|
| `ipai_theme_aiux` | [ ] | `odoo shell -c "env['ir.module.module'].search([('name','=','ipai_theme_aiux'),('state','=','installed')])"` |
| `ipai_aiux_chat` | [ ] | Same pattern |
| `ipai_ask_ai` | [ ] | Same pattern |
| `ipai_document_ai` | [ ] | Same pattern |
| `ipai_expense_ocr` | [ ] | Same pattern |

### 4.3 Integrations Ready

| Integration | Runbook | Status | Test Command |
|-------------|---------|--------|--------------|
| Mailgun | `ops/runbooks/mailgun_domain_verification.md` | [ ] | SMTP test |
| Sinch SMS | `ops/runbooks/sinch_setup.md` | [ ] | API test |
| OCR Service | `ops/runbooks/ocr_service.md` | [ ] | Health check |

---

## 5) Data Migration & Cutover (Week 2)

### 5.1 Data Plan

| Task | Status | Notes |
|------|--------|-------|
| Data sources identified | [ ] | CSV/legacy ERP/Sheets |
| Mapping sheet complete | [ ] | Source → target model/field |
| Import scripts deterministic | [ ] | Same input → same output |
| Import idempotent | [ ] | Can rerun without duplicates |

### 5.2 Migration Dry Run

| Task | Status | Verification |
|------|--------|--------------|
| Full import into staging | [ ] | Import log |
| Record counts validated | [ ] | Count comparison |
| Business sign-off on staging | [ ] | Sign-off document |

### 5.3 Cutover Strategy

Pick one:

| Strategy | Description | Status |
|----------|-------------|--------|
| Big bang | Short downtime, full switch | [ ] |
| Phased | Modules/users in waves | [ ] |
| Parallel run | Legacy + new until close | [ ] |

---

## 6) Security & Compliance (Week 2)

### 6.1 Access Control

| Task | Status | Verification |
|------|--------|--------------|
| Admin credentials rotated | [ ] | Last rotation date |
| Service credentials in secret store only | [ ] | No secrets in repo |
| DB access restricted (private network/firewall) | [ ] | Connection test |

### 6.2 Odoo Hardening

| Task | Status | Verification Command |
|------|--------|----------------------|
| `dbfilter` configured | [ ] | Check `odoo.conf` |
| Longpolling/websocket proper routing | [ ] | See nginx config |
| File upload limits set | [ ] | `client_max_body_size` |
| Reverse-proxy timeouts configured | [ ] | `proxy_read_timeout 720s` |

### 6.3 Compliance (PH)

| Task | Status | Notes |
|------|--------|-------|
| PH tax/close workflows verified | [ ] | Against BIR checklist |
| Calendar/holidays validated | [ ] | Due date accuracy |

---

## 7) Performance & Reliability (Go-Live Readiness)

### 7.1 Load/Smoke Tests

| Task | Status | Target |
|------|--------|--------|
| Concurrent user smoke test | [ ] | 50–200 users |
| Queue throughput tested | [ ] | OCR/AI jobs |
| Postgres connection pool tuned | [ ] | `max_connections` |

### 7.2 "502 Bad Gateway" Prevention Checklist

**Most common causes in Odoo stacks:**

| Cause | Check | Mitigation |
|-------|-------|------------|
| Odoo worker crash loop | Container restart count | Health checks + fast fail |
| Nginx timeout too low | `proxy_read_timeout` | Set to 720s |
| Wrong upstream port | nginx upstream config | Verify 8069/8072 |
| WebSocket misrouted | `/longpolling` location | Explicit upstream |
| DB connection exhaustion | `pg_stat_activity` | Pool tuning |
| Memory pressure (OOM) | `docker stats` | Resource limits |

**See:** `docs/ops/PREVENT_502.md` for detailed mitigations.

---

## 8) Go-Live Execution (T-0)

### 8.1 Final Pre-Flight (ALL must be green)

| Gate | Status | Command |
|------|--------|---------|
| CI gates green on release tag | [ ] | GitHub Actions |
| Staging deploy from same tag succeeded | [ ] | Staging URL test |
| Backup taken right before cutover | [ ] | `pg_dump` timestamp |
| Rollback plan confirmed | [ ] | Tag + DB restore point |

### 8.2 Deploy

```bash
# Deploy release tag to prod
git checkout ship-aiux-v1.1.0
./scripts/deploy/verify_prod.sh
```

**Scripted verification must pass:**

| Check | Expected | Status |
|-------|----------|--------|
| HTTP 200 on `/web/login` | 200/303 | [ ] |
| Module list matches manifest | All installed | [ ] |
| Scheduled jobs running | Active | [ ] |
| Email send test | Delivered | [ ] |
| OCR pipeline test | Processed | [ ] |
| SMS test (if enabled) | Delivered | [ ] |

### 8.3 Announce Go-Live

| Task | Status |
|------|--------|
| Capture proofs (logs, versions, tag, checks) | [ ] |
| Generate WHAT_SHIPPED.md | [ ] |
| Freeze changes for 24–48h (except hotfix) | [ ] |
| Notify stakeholders | [ ] |

---

## 9) Post Go-Live (T+1 to T+14)

### 9.1 Stabilization

| Task | Frequency | Status |
|------|-----------|--------|
| Daily health review | Daily | [ ] |
| Error rate monitoring | Daily | [ ] |
| Queue backlog check | Daily | [ ] |
| Close "known issues" from staging | Once | [ ] |

### 9.2 Operational Runbooks

| Runbook | Path | Verified |
|---------|------|----------|
| Mailgun domain verification | `ops/runbooks/mailgun_domain_verification.md` | [ ] |
| OCR service ops | `ops/runbooks/ocr_service.md` | [ ] |
| Sinch SMS setup | `ops/runbooks/sinch_setup.md` | [ ] |
| Expense OCR ops | `ops/runbooks/expenses_ocr_runbook.md` | [ ] |
| Backup/restore | `docs/ops/production_redeploy_runbook.md` | [ ] |

### 9.3 Release Hygiene

| Task | Status |
|------|--------|
| WHAT_SHIPPED.md generated | [ ] |
| GO_LIVE_MANIFEST.md stored with tag | [ ] |
| Open issues triaged into next sprint | [ ] |

---

## Quick Reference Commands

```bash
# Container health
docker compose -f deploy/docker-compose.prod.yml ps
docker compose -f deploy/docker-compose.prod.yml logs --tail=100 odoo

# Full verification
./scripts/deploy/verify_prod.sh

# Module installation verification
./scripts/aiux/verify_install.sh

# Asset verification
./scripts/aiux/verify_assets.sh
```

---

## Related Documents

- [Ship PRD v1.1.0](docs/prd/IPAI_SHIP_PRD_ODOO18_AIUX.md)
- [Fresh Redeploy PRD](docs/prd/ODOO18_DO_FRESH_REDEPLOY.md)
- [End State Spec](docs/prd/END_STATE_SPEC.json)
- [502 Prevention Guide](docs/ops/PREVENT_502.md)
- [Verification Commands](docs/ops/VERIFICATION_COMMANDS.md)
- [What Shipped Template](docs/ops/WHAT_SHIPPED.template.md)

---

*Last updated: 2026-01-08*
