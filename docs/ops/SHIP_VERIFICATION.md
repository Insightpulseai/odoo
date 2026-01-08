# Ship Verification Runbook

## Hard Rule
This verification **MUST** be executed via Docker (compose exec). Public HTTP checks are necessary but never sufficient.
If Docker steps are skipped, the verification is **INVALID**.

---

## 1. Production: Reproduce Integrity (From Inside Stack)

Run on the droplet (`ssh insightpulse-odoo`):

```bash
cd /opt/odoo-ce || cd ~/odoo-ce

# 1. Check Stack Status
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs --tail=200 odoo
docker compose -f docker-compose.prod.yml logs --tail=200 db

# 2. Internal Connectivity & Assets Check (No Proxy/CDN)
docker compose -f docker-compose.prod.yml exec -T odoo bash -lc \
  "curl -sS -o /dev/null -w '%{http_code}\n' http://localhost:8069/web/login && \
   curl -sS -o /dev/null -w '%{http_code}\n' http://localhost:8069/web/assets/debug/web.assets_backend.js"
```

**Expectation:**
- Login: `200` or `303`
- Assets: `200`
- If Assets returns `500`, proceed to **Section 2 (Hard Reset)**.

---

## 2. Hard Reset & Rebuild Assets (Fastest Fix)

If you are dealing with a sticky 500 error on assets, force a deterministic rebuild.

### 2.1 Dump Config (Verify DB)
```bash
docker compose -f docker-compose.prod.yml exec -T odoo bash -lc "odoo --config=/etc/odoo/odoo.conf --save --stop-after-init || true"
```
*Ensure `db_name` is set to your canonical DB (e.g., `odoo`) if strictly single-DB.*

### 2.2 Force Module Upgrade
This triggers the asset bundle regeneration.
```bash
docker compose -f docker-compose.prod.yml exec -T odoo bash -lc \
  "odoo --stop-after-init -d odoo -u web,base,ipai_theme_aiux,ipai_aiux_chat,ipai_ask_ai,ipai_document_ai,ipai_expense_ocr --log-level=info"
```

### 2.3 Restart & Verify
```bash
docker compose -f docker-compose.prod.yml restart odoo
# Watch logs for startup errors
docker compose -f docker-compose.prod.yml logs -f --tail=200 odoo
```
*Wait for "Odoo is running" / "HTTP service running".*

---

## 3. Deep Diagnosis (If still 500)

If the hard reset fails, capture the exact traceback to identify the failing file (SCSS/JS/Manifest).

### 3.1 Capture Traceback
```bash
# Get the stacktrace around the error
docker compose -f docker-compose.prod.yml logs --tail=500 odoo | grep -nE "assets|scss|bundle|Traceback|ERROR" | tail -200
```

### 3.2 Inspect Manifests
Verify that installed modules declare assets correctly.
```bash
docker compose -f docker-compose.prod.yml exec -T odoo bash -lc \
  "python - <<'PY'\nimport os,glob\nmods=['ipai_theme_aiux','ipai_aiux_chat']\nfor m in mods:\n  p=f'/mnt/addons/ipai/{m}/__manifest__.py'\n  if os.path.exists(p):\n    print('\\n===',m,'===')\n    print(open(p,'r',encoding='utf-8').read())\nPY"
```

---

## 4. Assets Gate (Required Verification)

**PASS** only if ALL conditions are met:
- [ ] `/web/login` returns **200** or **303**.
- [ ] `/web/assets/debug/web.assets_backend.js` returns **200**.
- [ ] `scripts/aiux/verify_assets.sh` (if run locally/remotely) exits **0**.

**FAIL** otherwise.
