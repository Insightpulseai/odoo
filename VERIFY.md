# IPAI Verification Commands

Copy/paste verification commands for production deployment.

---

## 1. Design Tokens Package

```bash
# Check tokens files exist
ls -la packages/ipai-design-tokens/

# Expected output:
# tokens.css
# tokens.scss
# tailwind.preset.js
# package.json
```

---

## 2. Token Sync

```bash
# Run sync script
./scripts/sync-tokens.sh

# Verify synced file exists
ls -la addons/ipai_web_theme_chatgpt/static/src/scss/tokens_shared.scss
```

---

## 3. OCA Addons

```bash
# Run bootstrap
./scripts/oca-bootstrap.sh

# Verify repos cloned
ls addons/oca/

# Expected: queue rest-framework server-ux server-tools web
```

---

## 4. Odoo Theme Addon

```bash
# Check theme manifest
cat addons/ipai_web_theme_chatgpt/__manifest__.py | grep -A5 "assets"

# Check assets files exist
ls addons/ipai_web_theme_chatgpt/static/src/scss/
```

---

## 5. Ask AI Chatter Addon

```bash
# Check manifest
cat addons/ipai_ask_ai_chatter/__manifest__.py

# Check security file
cat addons/ipai_ask_ai_chatter/security/ir.model.access.csv
```

---

## 6. Odoo Container Health

```bash
# Check container running
docker compose ps | grep odoo

# Check Odoo HTTP responds
curl -s http://localhost:8069/web/health || echo "Not ready"

# Check logs for errors
docker compose logs --tail=50 odoo-core | grep -i error
```

---

## 7. Mail Queue Status

```bash
docker exec -i odoo-core odoo shell -d odoo_core <<'PY'
outgoing = env['mail.mail'].search_count([('state', '=', 'outgoing')])
sent = env['mail.mail'].search_count([('state', '=', 'sent')])
exception = env['mail.mail'].search_count([('state', '=', 'exception')])
print(f"Outgoing: {outgoing}, Sent: {sent}, Exception: {exception}")
PY
```

---

## 8. SMTP Configuration

```bash
docker exec -i odoo-core odoo shell -d odoo_core <<'PY'
servers = env['ir.mail_server'].search([])
for s in servers:
    print(f"{s.name}: {s.smtp_host}:{s.smtp_port} ({s.smtp_encryption})")
PY
```

---

## 9. Ask AI Configuration

```bash
docker exec -i odoo-core odoo shell -d odoo_core <<'PY'
ICP = env['ir.config_parameter'].sudo()
print("enabled:", ICP.get_param('ipai_ask_ai_chatter.enabled'))
print("api_url:", ICP.get_param('ipai_ask_ai_chatter.api_url'))
print("trigger:", ICP.get_param('ipai_ask_ai_chatter.trigger'))
PY
```

---

## 10. ChatGPT App Widget Build

```bash
# Check dist exists
ls -la apps/ipai-chatgpt-app/web/dist/

# Check single-file size (should be < 500KB)
wc -c apps/ipai-chatgpt-app/web/dist/index.html
```

---

## 11. MCP Server

```bash
# Health check
curl -s http://localhost:8787/ | jq .

# Expected: {"status":"ok","service":"ipai-chatgpt-app-server"}
```

---

## 12. MCP Tools List (with Inspector)

```bash
# Using MCP Inspector
npx @modelcontextprotocol/inspector --server-url http://localhost:8787/mcp --transport http
```

---

## 13. Complete Stack Check

```bash
#!/bin/bash
echo "=== IPAI Stack Verification ==="

# Tokens
[ -f "packages/ipai-design-tokens/tokens.css" ] && echo "✓ Design tokens" || echo "✗ Design tokens missing"

# Theme
[ -f "addons/ipai_web_theme_chatgpt/__manifest__.py" ] && echo "✓ Theme addon" || echo "✗ Theme addon missing"

# Ask AI
[ -f "addons/ipai_ask_ai_chatter/__manifest__.py" ] && echo "✓ Ask AI addon" || echo "✗ Ask AI addon missing"

# OCA queue
[ -d "addons/oca/queue" ] && echo "✓ OCA queue" || echo "✗ OCA queue missing"

# Widget
[ -f "apps/ipai-chatgpt-app/web/package.json" ] && echo "✓ ChatGPT widget" || echo "✗ ChatGPT widget missing"

# MCP Server
[ -f "apps/ipai-chatgpt-app/server/server.js" ] && echo "✓ MCP server" || echo "✗ MCP server missing"

echo ""
echo "=== Container Status ==="
docker compose ps 2>/dev/null || echo "Docker not running"

echo ""
echo "=== Done ==="
```

Save as `verify-stack.sh` and run:
```bash
chmod +x verify-stack.sh
./verify-stack.sh
```

---

## Quick Smoke Test

```bash
# 1. Odoo responds
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web | grep -q 200 && echo "✓ Odoo" || echo "✗ Odoo"

# 2. MCP server responds
curl -s http://localhost:8787/ | grep -q "ok" && echo "✓ MCP" || echo "✗ MCP"

# 3. Theme assets exist
[ -f "addons/ipai_web_theme_chatgpt/static/src/scss/tokens.scss" ] && echo "✓ Theme CSS" || echo "✗ Theme CSS"
```
