# IPAI Ship PRD — Odoo 18 CE + OCA Essentials + AIUX + AskAI (Self-Hosted)

**Version:** 1.1.0
**Date:** 2026-01-08
**Owner:** InsightPulse AI
**Status:** Draft → Review → Approved

---

## 0) Decision (what we ship / what we do NOT ship)

### Ship

1) **Odoo 18 Community Edition** (self-hosted) as the ERP core
2) **OCA "essentials"** for base + accounting + sales (+ a small curated set of productivity/ops modules)
3) **AIUX Design System** as the UX layer for:
   - Odoo 18 CE theme module (`ipai_theme_aiux`)
   - React widget package (`@insightpulse/ask-ai`)
   - Tokens package (`@insightpulse/design-tokens`)
4) **AskAI (self-hosted)**: an internal AI widget + API that replaces Enterprise-only "AI Agent Studio/IAP AI" features without using Odoo SA proprietary modules.
5) **Document Intelligence (OCR)**: self-hosted OCR service for document extraction

### Do NOT ship

- **Odoo 19 "AI / AI Documents / AI Livechat / AI Auto Install / AI Text Draft …"** modules from Odoo S.A.
  - They're **19.0** series and typically sit behind **Enterprise/IAP** flows and upsell hooks.
  - We are self-hosted Odoo, not shipping AI agent using Odoo SA 19 → so they're out.

---

## 1) Product goal

Deliver a production-grade **Odoo 18 CE + OCA** ERP that:
- feels like modern AI tools (Claude/ChatGPT-like warmth + split panes + assistant patterns),
- avoids Enterprise/IAP/upsell friction,
- is operationally stable (assets never 500),
- supports email deliverability (Mailgun domain verification runbook included),
- provides self-hosted document intelligence (OCR),
- stays upgradeable and deterministic.

---

## 2) Compatibility targets

- **Odoo:** 18.0 CE
- **OCA:** 18.0 branches only (pin by commit/tag)
- **Frontend:** AIUX theme works on Odoo webclient (OWL) + optional React embed surfaces
- **OCR Service:** Self-hosted (188.166.237.231 or internal network)

---

## 3) Ship scope: "ERP Essentials" bill of materials

### 3.1 Odoo CE core apps (installable)

- Base / Contacts / Users & Access
- Sales + CRM (CE)
- Accounting / Invoicing (CE)
- Inventory / Purchase (if required for the org)
- Discuss (optional; keep "AskAI" separate as a widget, not embedded into Discuss)

### 3.2 OCA essentials (curated)

> Exact list should be pinned by repository + commit (avoid "floating latest").

**Base/UX/Tech**
- `web` usability + UI fixes (minimal, stable modules)
- `server-tools` (safe utilities only)
- `queue` / job tooling if you need background processing
- `mail` helpers if needed for outgoing mail reliability

**Accounting**
- OCA accounting enhancements that do **not** conflict with CE accounting engine
- EDI/localization only if relevant (PH localization handled via custom)

**Sales**
- OCA sales workflow helpers (portal search/order UX, quotation usability, etc.)

### 3.3 IPAI custom modules

| Module | Purpose |
|--------|---------|
| `ipai_theme_aiux` | Theme + widget hooks |
| `ipai_ask_ai` | Server-side AI endpoints, auth, logging, rate limits |
| `ipai_aiux_chat` | Chat widget OWL component |
| `ipai_document_ai` | OCR integration + document extraction |
| `ipai_expense_ocr` | Expense receipt OCR + duplicate detection |
| Finance/closing stack | Already in repo |

---

## 4) AI scope (Enterprise offset strategy)

### 4.1 What we replicate (without Odoo SA 19 AI)

- **Drafting**: email/sms/notes text suggestions
- **Summaries**: chatter/thread summary, record summary (SO, Invoice, Bill)
- **Smart actions**: "create task", "generate follow-up", "extract key fields from text"
- **Document assist**: extract fields from PDFs via OCR service

### 4.2 What we explicitly avoid

- Anything requiring Odoo IAP billing
- Odoo SA "AI" modules (19.x) and their auto-installs
- Upsell banners / enterprise home marketing tiles

### 4.3 AskAI architecture (self-hosted)

- **UI:** AIUX widget (pill → popup → sidepanel)
- **API:** `/api/ai/chat` (your contract)
- **Context injection:** model/res_id/view_type + safe record snippets
- **Auth:** reuse Odoo session + CSRF + groups
- **Telemetry:** minimal (counts + latency), no content exfiltration by default

**Mode Types (Canonical):**
```typescript
type Mode = 'minimize' | 'popup' | 'sidepanel';
```

| Mode | Description |
|------|-------------|
| `minimize` | Collapsed pill, tooltip on hover |
| `popup` | Floating chat window (400x500px) |
| `sidepanel` | Docked side panel, resizable |

**IMPORTANT:** Use `sidepanel`, NOT `fullscreen`.

### 4.4 Document Intelligence (OCR) — Ship Scope (Self-Hosted)

#### Goal

Provide **self-hosted OCR + document understanding** that replaces Enterprise "Documents AI" style capabilities, using **your existing OCR service** (droplet: `188.166.237.231`) and your own APIs—no Odoo SA 19 AI modules, no IAP.

#### What we ship

1) **OCR Service (existing)**
   - Runs as a standalone HTTP service (containerized)
   - Accepts file uploads or object-storage URLs
   - Returns:
     - extracted text (plain + normalized)
     - layout blocks (optional: bbox/lines)
     - entities/fields (optional: invoice totals, vendor, dates)
     - confidence scores

2) **Odoo Module: `ipai_document_ai`**
   - Adds "Document Upload" action on relevant models (Bills, Invoices, Expenses, Purchase Orders, Contracts)
   - Sends docs to OCR service
   - Stores results as:
     - attachment + extracted text
     - structured JSON payload
     - optional suggested field mappings
   - Provides a review UI (approve/apply suggestions)

3) **API Contract + Runbook**
   - `ops/runbooks/ocr_service.md`
   - `docs/architecture/OCR_PIPELINE.md`

### 4.5 Expense OCR — Ship Scope (Self-Hosted)

#### Goal

Provide **expense receipt scanning + extraction** with **duplicate detection** that complements the general Document Intelligence stack.

#### What we ship

1) **Odoo Module: `ipai_expense_ocr`**
   - Extends `hr.expense` with OCR capabilities
   - Adds "Scan Receipt" action on expense forms
   - Sends receipt images to OCR service
   - Extracts: merchant, date, amount, currency, tax
   - **Duplicate detection**: SHA256 hash prevents duplicate submissions
   - Queue-based async processing

2) **Extracted Fields**

   | Field | Description | Confidence Threshold |
   |-------|-------------|---------------------|
   | `merchant_name` | Store/vendor name | 0.70 |
   | `receipt_date` | Transaction date | 0.85 |
   | `total_amount` | Total paid | 0.85 |
   | `currency` | Currency code | 0.80 |
   | `tax_amount` | Tax/VAT amount | 0.75 |
   | `payment_method` | Cash/Card/etc | 0.60 |

3) **Workflow States**

   ```
   queued → processing → extracted|needs_review|failed → applied
   ```

   - **queued**: Waiting for OCR processing
   - **processing**: Being extracted
   - **extracted**: High-confidence results ready
   - **needs_review**: Low confidence (<0.70), manual review required
   - **applied**: Fields applied to expense
   - **failed**: Extraction failed

4) **Duplicate Detection**
   - SHA256 hash computed on receipt upload
   - Compared against recent expenses (configurable window, default 90 days)
   - Warning displayed if duplicate found
   - User can override and submit anyway

5) **Runbook**
   - `ops/runbooks/expenses_ocr_runbook.md`

### 4.6 Sinch SMS/Verification — Ship Scope

#### Goal

Provide **SMS messaging + phone verification** capabilities using Sinch as the provider (Enterprise offset for SMS features).

#### What we ship

1) **Integration Points**
   - SMS notifications for expense approvals
   - Phone verification for user onboarding
   - OTP delivery for sensitive operations

2) **Configuration**

   | Environment Variable | Description |
   |---------------------|-------------|
   | `SINCH_API_KEY` | Sinch API key |
   | `SINCH_API_SECRET` | Sinch API secret |
   | `SINCH_PROJECT_ID` | Sinch project ID |
   | `SINCH_SENDER_ID` | Sender ID or phone number |

3) **Runbook**
   - `ops/runbooks/sinch_setup.md`

---

## 5) Canonical runtime (stop asset 500s by making the platform deterministic)

Your current symptom ("assets 500") matches the classic failure mode:
- Odoo points to a DB (`odoo_core`) where module state / web assets bundles are not fully initialized, or
- addons_path changed, so assets build references missing modules, or
- dbfilter/list_db behavior changed, causing the wrong DB to load in some contexts.

### 5.1 Canonical rules

1) **Single canonical DB name** in production: `odoo` (recommended)
2) **Single canonical service DNS** for Postgres inside the docker network: `db` (recommended)
3) **Environment-driven secrets** (no hardcoded db_password in config)
4) **Pinned addons paths** and a single mount strategy:
   - `/mnt/addons/ipai` (your custom)
   - `/mnt/addons/oca` (OCA repos)
   - plus default Odoo addons
5) **dbfilter ON**, **list_db OFF** to prevent accidental DB switching

### 5.2 Canonical `odoo.conf` (prod template)

```ini
[options]
proxy_mode = True

; ---- DB ----
db_host = db
db_port = 5432
db_user = odoo
db_password = ${DB_PASSWORD}
db_name = odoo
dbfilter = ^odoo$
list_db = False

; ---- addons ----
addons_path = /mnt/addons/ipai,/mnt/addons/oca,/usr/lib/python3/dist-packages/odoo/addons

; ---- logging ----
log_level = info

; ---- performance ----
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_time_cpu = 600
limit_time_real = 1200
```

### 5.3 Canonical `docker-compose.prod.yml` (key pieces)

```yaml
services:
  db:
    image: postgres:15
    container_name: odoo-db
    environment:
      POSTGRES_DB: odoo
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    networks: [odoo_backend]

  odoo:
    image: your-odoo-image:18
    depends_on: [db]
    environment:
      DB_PASSWORD: ${DB_PASSWORD}
      OCR_BASE_URL: http://ocr:8000
    volumes:
      - ./addons/ipai:/mnt/addons/ipai
      - ./addons/oca:/mnt/addons/oca
      - ./config/odoo.conf:/etc/odoo/odoo.conf:ro
    networks: [odoo_backend]

  ocr:
    image: your-ocr-image:latest
    container_name: ocr
    ports:
      - "8000:8000"
    networks: [odoo_backend]

networks:
  odoo_backend:
    external: true
```

### 5.4 Deterministic "assets are healthy" acceptance checks

```bash
# inside odoo container
odoo --version

# confirm DB target
python3 - <<'PY'
import os
print("DB_PASSWORD set:", bool(os.getenv("DB_PASSWORD")))
PY

# force web assets rebuild (safe when diagnosing)
odoo -d odoo -u web --stop-after-init

# install/upgrade your theme + core web deps
odoo -d odoo -u ipai_theme_aiux --stop-after-init

# health endpoints (examples)
curl -I https://erp.insightpulseai.net/web/login
curl -I https://erp.insightpulseai.net/web/assets/debug/
```

---

## 6) AIUX Design System

**Ship as-is** with these additions:

* The Odoo theme module MUST NOT depend on enterprise web modules.
* AskAI widget MUST be:
  * a floating pill by default,
  * able to dock as side panel,
  * not tied to Discuss.

**Packages shipped**

| Package | Type | Purpose |
|---------|------|---------|
| `@insightpulse/design-tokens` | npm | CSS/SCSS/Tailwind tokens |
| `@insightpulse/ask-ai` | npm | React widget |
| `ipai_theme_aiux` | Odoo | Theme module |
| `ipai_ask_ai` | Odoo | Server endpoints + RBAC + audit log |
| `ipai_aiux_chat` | Odoo | OWL chat widget |
| `ipai_document_ai` | Odoo | OCR integration |

---

## 7) Operational: Mailgun domain verification runbook (production requirement)

### 7.1 Why this is required

Mailgun requires domain verification to send email properly and enable tracking (opens/clicks).

### 7.2 Runbook steps (copy/paste checklist)

See: `ops/runbooks/mailgun_domain_verification.md`

#### Step 1 — Add domain in Mailgun

* Control Panel → **Sending** → **Domains** → **Add New Domain**
* Prefer **subdomain** (e.g., `mail.yourdomain.com`) for deliverability
* Keep the DNS records page open after adding the domain

#### Step 2 — Add DNS records at your DNS host

Mailgun will show the exact values; you add these record types:

**TXT (SPF + DKIM)**
* Add SPF TXT record.
* If SPF already exists for the root domain, **do not add a second SPF**; instead insert `include:mailgun.org` into the existing SPF value between `v=spf1` and `~all`.

**MX (two records)**
* Add both MX records Mailgun provides
* Priority should be **10**

**CNAME (tracking)**
* Add the CNAME record to enable open/click tracking (recommended)

#### Step 3 — Propagation + verification

* DNS propagation may take **24–48 hours**
* Use Mailgun's **"Check DNS Records Now"** button if you want to force a check

### 7.3 Production verification commands (DNS + SMTP)

```bash
# Replace with your domain/subdomain
DOMAIN=mail.yourdomain.com

# SPF
dig +short TXT $DOMAIN | tr -d '"'

# DKIM (Mailgun provides selector/host)
dig +short TXT mx._domainkey.$DOMAIN | tr -d '"'

# MX
dig +short MX $DOMAIN

# CNAME tracking host
dig +short CNAME email.$DOMAIN
```

---

## 8) OCR Service Architecture

### 8.1 Components

- **Odoo 18 CE**
  - Uploads document (attachment)
  - Calls OCR service via internal network/VPN
  - Receives extraction payload
  - Persists output + optional mapped fields

- **OCR Service (188.166.237.231)**
  - `/health`
  - `/v1/ocr/extract`
  - `/v1/ocr/extract-async` (optional)
  - `/v1/ocr/jobs/{id}` (optional)

- **Storage**
  - Option A: Odoo attachments only (simplest)
  - Option B: Object storage bucket + signed URLs (better for large PDFs)

### 8.2 Data flow

1) User uploads PDF/image to Odoo (Attachment)
2) Odoo enqueues OCR job (sync or async)
3) OCR service extracts
4) Odoo stores:
   - `extracted_text`
   - `extraction_json`
   - `confidence`
   - `doc_type` (invoice/receipt/contract/other)
5) UI shows:
   - preview + extracted text
   - suggested fields (vendor/date/total/tax/etc.)
   - "Apply to record" button

### 8.3 OCR API Contract

#### Sync extract

`POST /v1/ocr/extract`

**Request (multipart)**
- `file`: PDF/JPG/PNG
- `options`: JSON string (optional)

**Response (JSON)**
```json
{
  "job_id": "optional",
  "doc_type": "invoice",
  "text": "full extracted text",
  "blocks": [
    { "text": "ACME INC", "bbox": [12, 32, 210, 58], "conf": 0.98 }
  ],
  "fields": {
    "vendor_name": { "value": "ACME INC", "conf": 0.93 },
    "invoice_number": { "value": "INV-10021", "conf": 0.89 },
    "invoice_date": { "value": "2026-01-08", "conf": 0.91 },
    "currency": { "value": "PHP", "conf": 0.85 },
    "subtotal": { "value": 1000.0, "conf": 0.87 },
    "tax": { "value": 120.0, "conf": 0.84 },
    "total": { "value": 1120.0, "conf": 0.92 }
  },
  "meta": {
    "pages": 2,
    "engine": "your-ocr-engine",
    "duration_ms": 1432
  }
}
```

#### Health

`GET /health` → `200 OK` with `{"status":"ok"}`

---

## 9) Go-live acceptance criteria (ship gate)

### Platform

- [ ] No `/web/assets/*` 500s under normal mode
- [ ] Odoo loads the intended DB (`odoo`) every time (dbfilter enforced)
- [ ] Theme installs/upgrades cleanly (`ipai_theme_aiux`)
- [ ] OCA essentials install/upgrades cleanly (pinned commit set)

### AskAI

- [ ] Pill → popup → sidepanel modes all work
- [ ] Context is preserved when switching modes
- [ ] RBAC: only allowed groups can call `/api/ai/chat`
- [ ] Logs capture latency + status (not secrets)

### Document AI / OCR

- [ ] OCR service health endpoint responds
- [ ] Document upload + extraction works on Bills/Invoices
- [ ] Extracted fields display with confidence scores
- [ ] "Apply to record" successfully maps fields

### Expense OCR

- [ ] Receipt scan action available on expense forms
- [ ] OCR extraction returns merchant, date, amount fields
- [ ] Duplicate detection flags matching receipts
- [ ] Low-confidence results route to review queue
- [ ] "Apply to expense" successfully maps extracted fields

### Sinch SMS

- [ ] Sinch API credentials configured
- [ ] Test SMS sends successfully
- [ ] Phone verification flow works

### Mailgun

- [ ] Domain verified in Mailgun
- [ ] SPF/DKIM/MX/CNAME present and resolving
- [ ] Outbound mail works from Odoo (test message + logs)

---

## 10) Risks / failure modes (and mitigations)

1. **Assets 500 again** if DB changes or addons_path drifts
   * Mitigation: canonical DB/service names + env-driven config + pinned addons paths + "upgrade web/theme" check commands.

2. **OCA module conflicts**
   * Mitigation: curated essentials only; pin commits; stage upgrades.

3. **Mail deliverability**
   * Mitigation: enforce domain verification + SPF/DKIM + track propagation; keep runbook.

4. **OCR service downtime**
   * Mitigation: health checks + retry queue + graceful degradation (mark as failed, allow retry).

5. **Low confidence OCR results**
   * Mitigation: require manual approval for low-confidence field mappings.

---

## 11) Deliverables (what to commit)

| Path | Purpose |
|------|---------|
| `docs/prd/IPAI_SHIP_PRD_ODOO18_AIUX.md` | This document |
| `addons/ipai/ipai_theme_aiux/` | Theme module |
| `addons/ipai/ipai_ask_ai/` | API + RBAC + logging |
| `addons/ipai/ipai_aiux_chat/` | Chat widget |
| `addons/ipai/ipai_document_ai/` | OCR integration |
| `addons/ipai/ipai_expense_ocr/` | Expense receipt OCR |
| `packages/ipai-design-tokens/` | Design tokens |
| `ops/runbooks/mailgun_domain_verification.md` | Mail setup runbook |
| `ops/runbooks/ocr_service.md` | OCR service runbook |
| `ops/runbooks/sinch_setup.md` | Sinch SMS setup runbook |
| `ops/runbooks/expenses_ocr_runbook.md` | Expense OCR operations |
| `docs/architecture/OCR_PIPELINE.md` | OCR architecture |
| `aiux_ship_manifest.yml` | Shipping manifest |

---

*This PRD is the canonical reference for IPAI shipping. All implementations must conform to these specifications.*
