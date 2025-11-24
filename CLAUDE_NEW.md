# InsightPulse Odoo (Delta Architecture)

## 🏗 System Context
- **Core:** Odoo 18 Community Edition (Dockerized).
- **Strategy:** "Smart Customization" (Inheritance only).
- **Modules:** Located in `addons/`.
    - `ipai_finance_ppm`: Finance, Projects, WBS.
    - `ipai_equipment`: Asset management (Cheqroom parity).
    - `ipai_payment_payout`: Stripe integration.

## 🛡️ Coding Rules (Strict)
1.  **Inheritance:** NEVER modify Odoo core files. Always use `_inherit` in Python and `xpath` in XML.
2.  **Manifest:** Always include `depends` when inheriting a module.
3.  **XML IDs:** Use `module_name.unique_id`. Do not overwrite existing IDs.
4.  **Linting:** All code must pass `pre-commit run --all-files` before completion.

## 🛠️ Tool Usage & Commands
- **Start/Restart:** `make up` / `make restart`
- **Update Module:** `make update MODULE=ipai_finance_ppm` (Updates DB schema + XML).
- **Check Logs:** `make logs`
- **Shell Access:** `make shell` (For python-level debugging).

## 🧠 Memory Bank (Configuration)
- **Keycloak SSO:** configured via `auth_oidc`.
- **OCR:** configured via `ocr.service.endpoint` System Param.
- **n8n:** configured via `payout.n8n.webhook`.

## 🔧 Development Environment

### VS Code Configuration
- **Settings:** `.vscode/settings.json` (Black formatting, Pylance, XML validation)
- **Debugging:** `.vscode/launch.json` (Docker attach on port 5678)
- **Path Mappings:** Local `addons/` → Container `/mnt/extra-addons`

### Database Configuration
- **Production Password:** `odoo` (consider changing for security)
- **Container:** `odoo-db-1` (not `odoo-db`)
- **Connection Test:** `docker exec odoo-db-1 psql -U odoo -d odoo -c 'SELECT version();'`

### CLI Helper
- **Script:** `scripts/erp_config_cli.sh`
- **Usage:** `./scripts/erp_config_cli.sh <command>`
- **Commands:** `test-db`, `update-param`, `reset-password`, `show-config`

## 📚 Documentation
- **Configuration Guide:** `INSIGHTPULSE_ERP_CONFIGURATION_GUIDE.md`
- **Troubleshooting:** `POSTGRES_PASSWORD_SOLUTION.md`
- **Summary:** `ERP_CONFIGURATION_SUMMARY.md`

## 🚀 Quick Commands

```bash
# Test database connectivity
./scripts/erp_config_cli.sh test-db

# Update system parameter
./scripts/erp_config_cli.sh update-param web.base.url https://erp.insightpulseai.net

# Emergency password reset
./scripts/erp_config_cli.sh reset-password new_secure_password

# Show current configuration
./scripts/erp_config_cli.sh show-config
```

## 🔒 Security Notes
- Current database password: `odoo` (recommend changing for production)
- All API keys stored in System Parameters
- Emergency CLI access available via Odoo shell
- GitHub Actions deployment with proper secrets

## 📋 Verification Checklist
- [ ] Database connectivity working
- [ ] Import scripts executing successfully
- [ ] VS Code debugging configured
- [ ] CLI helper script functional
- [ ] All documentation up to date
