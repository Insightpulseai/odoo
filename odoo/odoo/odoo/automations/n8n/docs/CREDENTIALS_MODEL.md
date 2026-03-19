# n8n Credentials Model

**Last Updated:** 2026-02-20
**Policy:** No secrets in git, reference-only in workflow JSON
**SSOT:** Supabase Vault (secrets), n8n encrypted storage (tokens)

---

## Secret Storage Matrix

| **Credential Type** | **Storage Location** | **Rotation** | **Access** |
|--------------------|---------------------|-------------|-----------|
| Odoo credentials | n8n encrypted DB | Manual | n8n workflows only |
| Google OAuth2 | n8n encrypted DB | Auto (refresh token) | n8n workflows only |
| Google Service Account | Supabase Vault | Manual (90d) | n8n + Edge Functions |
| n8n API Key | Supabase Vault | Manual (180d) | CI/automation scripts |
| Supabase keys | Supabase Vault | Never (hardened) | n8n + all services |

---

## Environment Variables (n8n Container)

```bash
# .env (never committed)
N8N_ENCRYPTION_KEY=<generated-key>
N8N_HOST=n8n.insightpulseai.com
N8N_PROTOCOL=https
N8N_PORT=443
WEBHOOK_URL=https://n8n.insightpulseai.com/
GENERIC_TIMEZONE=Asia/Manila

# Integration secrets (referenced from Supabase Vault)
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<from-vault>
ODOO_URL=https://erp.insightpulseai.com
ODOO_DB=odoo
```

---

## Credential Reference in Workflow JSON

**✅ Correct (reference only):**
```json
{
  "credentials": {
    "googleOAuth2Api": "Google OAuth2 - Drive Access",
    "odooApi": "Odoo Production"
  }
}
```

**❌ Forbidden (hardcoded secret):**
```json
{
  "credentials": {
    "googleOAuth2Api": {
      "clientId": "1234-abcd.apps.googleusercontent.com",
      "clientSecret": "GOCSPX-ACTUAL_SECRET_HERE"  // NEVER DO THIS
    }
  }
}
```

---

## CI Secret Scanner Pattern

```bash
# .github/workflows/n8n-secret-scanner.yml
- name: Scan for hardcoded secrets
  run: |
    if grep -r "clientSecret\|private_key\|api_key\|password" automations/n8n/workflows/*.json; then
      echo "❌ Hardcoded secrets detected in workflow JSON"
      exit 1
    fi
```

---

## Cross-References

- **Secret Handling:** `sandbox/dev/CLAUDE.md`
- **Google Credentials:** `docs/integrations/n8n/GOOGLE_CREDENTIALS.md`
- **SSOT Policy:** `spec/odoo-ee-parity-seed/constitution.md` (Article 3: Integration Invariants)
