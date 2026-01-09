# Go-Live Manifest: prod-20260109-1642

**Generated:** January 09, 2026 at 20:19 UTC

---

## Environment Identifiers

| Component | Value |
|-----------|-------|
| **Release Tag** | `prod-20260109-1642` |
| **Commit SHA** | `0b1e86b078b9a2c6562d437f9957577ac3246d04` |
| **Production URL** | https://erp.insightpulseai.net |
| **Database** | `odoo_core` |
| **Docker Image** | `ghcr.io/jgtolentino/odoo-ce:prod-20260109-1642` |

---

## Deployed Artifacts

### Docker Image
- **Registry:** ghcr.io/jgtolentino/odoo-ce
- **Tag:** `prod-20260109-1642`
- **Digest:** See `DEPLOYMENT_PROOFS/docker_image_digest.txt`

### Odoo Modules (Install/Upgrade List)
- ipai/ipai_aiux_chat
- ipai/ipai_document_ai
- ipai/ipai_expense_ocr
- ipai/ipai_theme_aiux
- ipai/ipai_theme_tbwa_backend
- ipai/ipai_ui_brand_tokens
- ipai/ipai_web_theme_tbwa
- ipai_grid_view/__manifest__.py
- ipai_theme_tbwa/__init__.py
- ipai_theme_tbwa/__manifest__.py
- ipai_theme_tbwa/static
- ipai_theme_tbwa/views
- ipai_theme_tbwa_backend/__manifest__.py
- oca/oca.lock.json

### Supabase Migrations
- See `DEPLOYMENT_PROOFS/supabase_migration_status.txt`

### Edge Functions
- auth-bootstrap
- tenant-invite

---

## Health Checks

| Check | Expected | Proof File |
|-------|----------|------------|
| Odoo Web | HTTP 200 | `curl_health_headers.txt` |
| Odoo Init | Exit 0 | `odoo_stop_after_init.log` |
| Database | Connected | `odoo_stop_after_init.log` |

---

## Verification Commands

```bash
# Check Odoo health
curl -sI https://erp.insightpulseai.net/web/health | head -5

# Check Docker image
docker inspect ghcr.io/jgtolentino/odoo-ce:prod-20260109-1642 --format='{{.Id}}'

# Check module state
docker exec odoo-erp-prod odoo shell -d odoo_core -c "print(env['ir.module.module'].search([('state','=','installed')]).mapped('name'))"
```

---

## Rollback Procedure

```bash
# 1. Stop current deployment
docker compose down

# 2. Pull previous image
docker pull ghcr.io/jgtolentino/odoo-ce:latest

# 3. Update docker-compose.yml to use previous tag
# 4. Restart
docker compose up -d

# 5. Verify
curl -sI https://erp.insightpulseai.net/web | head -3
```
