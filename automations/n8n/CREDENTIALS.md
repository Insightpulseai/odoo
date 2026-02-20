# n8n Credential Names — InsightPulse AI

This file documents the **required n8n credential names** for all canonical workflows.
Create these in n8n UI → Settings → Credentials before activating any workflow.

---

## Odoo

| Credential Name | Type | Used By |
|----------------|------|---------|
| `Odoo API` | Odoo | All Odoo workflows |

**Configuration**:
- Site URL: `https://erp.insightpulseai.com`
- API Key: from Odoo → Settings → Users → `n8n@insightpulseai.com` → Preferences → Developer API Keys
- (Create `n8n@insightpulseai.com` user in Odoo with restricted Technical/CRM/Accounting read-only access)

---

## Supabase

| Credential Name | Type | Used By |
|----------------|------|---------|
| `Supabase IPAI` | Supabase | Any workflow reading/writing Supabase tables |

**Configuration**:
- Host: `https://spdtwktxdalcfigzeqrz.supabase.co`
- Service Role Secret: from Supabase Vault → `SUPABASE_SERVICE_ROLE_KEY`

---

## Superset

Superset does not have a native n8n credential type. The `superset-cache-refresh.json`
workflow uses **n8n Environment Variables** (set in n8n UI → Settings → Variables):

| Variable Name | Value |
|--------------|-------|
| `SUPERSET_URL` | `https://superset.insightpulseai.com` |
| `SUPERSET_USERNAME` | `admin` |
| `SUPERSET_PASSWORD` | (from Superset admin password — store in n8n env, not hardcode) |

---

## GitHub

| Credential Name | Type | Used By |
|----------------|------|---------|
| `GitHub IPAI` | GitHub (OAuth2 or PAT) | CI/CD workflows |

---

## Notes

- **Never** put credentials directly in workflow JSON files
- All workflow JSON files in `workflows/` use credential names by reference only
- Credentials are configured per-instance in the n8n UI and stored encrypted in n8n's database
- The n8n instance is at `https://n8n.insightpulseai.com`

---

*Last updated: 2026-02-20*
