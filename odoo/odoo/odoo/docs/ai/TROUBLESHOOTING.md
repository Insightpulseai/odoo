# Troubleshooting
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

## Common Issues

### Module not found

```bash
# Ensure module is in addons path
docker compose exec odoo-core ls /mnt/extra-addons/ipai/

# Update module list
docker compose exec odoo-core odoo -d odoo_core -u base
```

### Database connection issues

```bash
# Check PostgreSQL status
docker compose ps postgres
docker compose logs postgres
```

### Permission errors (SCSS compilation failures)

```bash
# Symptom: "Style compilation failed" errors in Odoo
# Root cause: Addons owned by wrong user, Odoo container can't read SCSS files

# Auto-fix permissions (recommended)
./scripts/verify-addon-permissions.sh

# Manual fix on server
ssh root@178.128.112.214
cd /opt/odoo/repo/addons
chown -R 100:101 ipai ipai_theme_tbwa*
chmod -R 755 ipai ipai_theme_tbwa*
docker restart odoo-prod
```
