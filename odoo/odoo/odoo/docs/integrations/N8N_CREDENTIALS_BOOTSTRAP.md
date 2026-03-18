# n8n Credentials Bootstrap – Finance Stack

Scope: `n8n.insightpulseai.com` – Finance PPM, OCR, CI telemetry workflows

---

## 1. Accounts & Roles

- **Admin user**: `finance-automation-admin`
- Channels:
  - Mattermost: `#finance-alerts`, `#ci-health`
- Systems:
  - Odoo CE 18 (`erp.insightpulseai.com`)
  - n8n (`https://n8n.insightpulseai.com/`)
  - Supabase (finance analytics DB)

---

## 2. API Key Creation

1. Login to n8n as admin.
2. Go to **Settings → API Keys**.
3. Create:
   - `FINANCE_AUTOMATION_KEY`
4. Store in secure vault (1Password / Vaultwarden).

Export template (for local testing only):

```bash
export N8N_API_KEY="YOUR_N8N_API_KEY"
export N8N_BASE_URL="https://n8n.insightpulseai.com"
```

---

## 3. Credential Types

### 3.1 Odoo REST / RPC

* Name: `Odoo ERP – Finance`
* Type: HTTP Request credentials
* Fields:

  * Base URL: `https://erp.insightpulseai.com`
  * Auth: API key / header
  * Header: `X-ODOO-API-KEY: ****`

### 3.2 Mattermost Webhook

* Name: `Mattermost – Finance Alerts`
* Type: Webhook
* Endpoint: `<incoming webhook URL>`
* Channel: `#finance-alerts`

### 3.3 Supabase

* Name: `Supabase – Finance Warehouse`
* Fields:

  * URL: `<SUPABASE_URL>`
  * Key: `<SERVICE_ROLE_KEY>` (only stored in n8n)

---

## 4. Workflows Bound to Credentials

* `Finance PPM Alerts` → Odoo + Mattermost
* `CI Telemetry Router` → GitHub Actions → n8n → Mattermost
* `BIR Deadline Alert` → Supabase + Odoo + Mattermost

Each JSON workflow refers to credential **names**, not raw secrets, so you can safely move them between environments.
