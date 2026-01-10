# Deterministic Troubleshooting Framework for Odoo CE 18.0

**Purpose**: Make Odoo errors "definitive" (file + line + module + DB + request) instead of "guess-it".

**Key Principle**: Every error must resolve to an **Error Envelope JSON** with exact culprit identification and verification steps.

---

## Quick Start

### When an Error Occurs

```bash
# 1. Capture evidence immediately
bash scripts/incident_snapshot.sh

# 2. Review logs in docs/incidents/<timestamp>/
cd docs/incidents/<timestamp>/
grep -E "ERROR|CRITICAL|Traceback" odoo_docker_logs.txt

# 3. If frontend error, reproduce with debug assets
open "https://erp.insightpulseai.net/web?debug=assets"

# 4. Create Error Envelope JSON (see template below)
# 5. Apply minimal fix (OCA-style)
# 6. Verify and commit
```

---

## 1. Structured Logging Setup

### Odoo Configuration

Add to `/etc/odoo/odoo.conf`:

```ini
[options]
; Core logging
log_level = info
log_handler = :INFO

; Targeted debug (without excessive noise)
log_handler = odoo.http:INFO,odoo.sql_db:INFO,odoo.modules.loading:INFO,odoo.addons.base.models.ir_asset:DEBUG,werkzeug:INFO

; Persistent log file
logfile = /var/lib/odoo/odoo.log

; Enable stack traces only during incident investigation
; (comment out for normal operation)
; dev_mode = all
```

**Why `ir_asset:DEBUG`?** - SCSS/JS asset compilation failures become "file+line" definitive.

**Apply changes:**

```bash
ssh root@178.128.112.214
docker exec odoo-prod bash -lc 'nano /etc/odoo/odoo.conf'
# Edit log_handler line
docker restart odoo-prod
```

### nginx Request Correlation

Add to nginx config (`/etc/nginx/conf.d/default.conf` or equivalent):

```nginx
map $request_id $reqid {
    default $request_id;
}

server {
    # ... existing config ...

    location / {
        proxy_set_header X-Request-ID $reqid;
        add_header X-Request-ID $reqid always;

        # ... rest of proxy config ...
    }
}
```

**Why?** - Enables browser error → server log correlation via `X-Request-ID` header.

**Apply changes:**

```bash
ssh root@178.128.112.214
docker exec nginx-prod-v2 nginx -s reload
```

---

## 2. Error Envelope Standard

### JSON Schema

Every incident must produce an Error Envelope JSON for AI agent processing:

```json
{
  "timestamp_utc": "2026-01-11T03:45:22Z",
  "db": "odoo",
  "url": "https://erp.insightpulseai.net/web/expenses?debug=assets",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "symptom": "UI style compilation failed",
  "server_error_signature": "Undefined variable $o-brand-primary",
  "culprit": {
    "module": "ipai_theme_tbwa_backend",
    "file": "static/src/scss/theme.scss",
    "line": 123
  },
  "fix_plan": [
    "patch scss import order",
    "clear assets attachments",
    "restart",
    "verify /web/login"
  ],
  "verification": [
    "curl https://erp.insightpulseai.net/web/login returns 200",
    "no scss errors in logs for 10 minutes",
    "visual parity check passes"
  ]
}
```

### Template

Save incident/<timestamp>/error_envelope.json:

```json
{
  "timestamp_utc": "",
  "db": "odoo",
  "url": "",
  "request_id": "",
  "symptom": "",
  "server_error_signature": "",
  "culprit": {
    "module": "",
    "file": "",
    "line": null
  },
  "fix_plan": [],
  "verification": []
}
```

---

## 3. Pattern Matchers (Fast Triage)

### SCSS/CSS Compilation Errors

**Log Signature**:
```
DEBUG odoo.addons.base.models.ir_asset: Undefined variable $o-brand-primary
```

**DevTools Signature**:
```
Failed to load resource: the server responded with a status of 500 (INTERNAL SERVER ERROR)
Request URL: https://erp.insightpulseai.net/web/assets/...web.assets_backend...
```

**Matcher Rule**:
- Look for `odoo.addons.base.models.ir_asset` lines
- Keywords: `scss`, `Undefined variable`, `File to import not found`, `@use`, `@import`
- Extract module from path: `/mnt/extra-addons/<module>/static/src/scss/<file>`

**Autofix Steps**:
1. Identify culprit file from logs
2. Verify ownership and readability (UID 100:GID 101)
3. Patch SCSS (import order / variable define / remove @use)
4. Clear `ir_attachment` web.assets cache
5. Restart + verify

### JavaScript Runtime Errors

**DevTools Signature** (Console):
```
Uncaught TypeError: Cannot read property 'foo' of undefined
    at Object.<anonymous> (ipai_workspace_core.js:234:15)
```

**Matcher Rule**:
- Reproduce with `?debug=assets` to get real file paths
- Right-click error → "Reveal in Sources" for exact line
- Check Network tab for failed `/web/assets/...` requests

**Autofix Steps**:
1. Fix JS error in module file
2. Clear assets cache
3. Restart + verify in Console

### XML View Parse Errors

**Log Signature**:
```
ERROR odoo.modules.loading: Failed to load module ipai_finance_ppm: ParseError while parsing /mnt/extra-addons/ipai/ipai_finance_ppm/views/finance_kanban_views.xml:45
```

**Matcher Rule**:
- Look for `odoo.modules.loading` + `ParseError`
- Extract module, file, line from path

**Autofix Steps**:
1. Fix XML syntax (common: `<list>` not `<tree>` in Odoo 18)
2. Upgrade module: `odoo -d odoo -u <module> --stop-after-init`
3. Verify in UI + logs clean

### RPC/API Errors

**DevTools Signature** (Network tab):
```
POST /web/dataset/call_kw/res.partner/search_read
Status: 500 Internal Server Error
Response: {"error": {"data": {...}, "message": "..."}}
```

**Matcher Rule**:
- Filter Network tab by `call_kw`
- Find red (failed) request
- Correlate to server stack trace via `X-Request-ID`

**Autofix Steps**:
1. Identify model/method from RPC payload
2. Find Python traceback in server logs
3. Fix Python error in module
4. Upgrade module
5. Verify RPC call succeeds

### Python Import/Registry Errors

**Log Signature**:
```
ERROR odoo.modules.registry: Failed to load registry for db odoo
Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/odoo/modules/registry.py", line 89, in new
    odoo.modules.load_modules(registry._db, force_demo, status, update_module)
  File "/mnt/extra-addons/ipai/ipai_workspace_core/__init__.py", line 5, in <module>
    from . import models
ImportError: cannot import name 'WorkspaceNode' from 'models'
```

**Matcher Rule**:
- Look for `odoo.modules.registry` + `ImportError` / `ModuleNotFoundError`
- Extract module from traceback path

**Autofix Steps**:
1. Fix `__init__.py` import ordering / dependency
2. Verify `__manifest__.py` dependencies are correct
3. Upgrade module
4. Verify registry loads cleanly

---

## 4. Chrome DevTools Workflow

### Reproduce with Debug Assets

**Always** reproduce errors with:

```
https://erp.insightpulseai.net/web?debug=assets
```

**Why?** - Odoo serves individual JS/CSS files instead of a single bundle, so DevTools shows **real file paths**.

### Standard Investigation Steps

1. **Open DevTools** → Console tab
2. **Reproduce error** (navigate, click, form submit, etc.)
3. **Right-click error** → "Reveal in Sources" (shows exact file + line)
4. **Network tab** → filter by `web.assets`:
   - Find red (failed) request
   - Open Response/Preview (often contains stack trace)
   - Copy `X-Request-ID` response header (if configured)
5. **Copy evidence**:
   - Request URL (includes db/debug params)
   - X-Request-ID (for server log correlation)
   - Stack trace or error message

### Example: SCSS Compilation Error

```
1. Navigate to: https://erp.insightpulseai.net/web?debug=assets
2. See error: "Style compilation failed"
3. DevTools Console: Error loading stylesheet
4. Network tab:
   Request URL: https://erp.insightpulseai.net/web/assets/.../web.assets_backend.min.css
   Status: 500 (INTERNAL SERVER ERROR)
   X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
5. Server logs:
   grep "550e8400-e29b-41d4-a716-446655440000" docs/incidents/<timestamp>/odoo_logfile_tail.txt
   DEBUG odoo.addons.base.models.ir_asset: Undefined variable $o-brand-primary in ipai_theme_tbwa_backend/static/src/scss/theme.scss:123
```

---

## 5. AI Agent Playbook

### Standard Operating Prompt

Use this for all AI-assisted troubleshooting:

```text
You are Odoo Incident Response Agent.

Goal: Produce a definitive root cause (module/file/line) and apply the minimal OCA-style fix.

Rules:
- Never guess. If no file+line is found, increase logging and reproduce with debug=assets.
- Always output an Error Envelope JSON to docs/incidents/<timestamp>/error_envelope.json.
- Only patch ipai_* modules. Never edit OCA vendor code in place; override or patch deterministically.
- After any fix: clear web.assets attachments, restart, verify with curl + log scan.

Steps:
1) Collect evidence:
   - Run scripts/incident_snapshot.sh
   - docker logs (odoo-prod, nginx-prod-v2)
   - /var/lib/odoo/odoo.log
   - X-Request-ID if available

2) If frontend error:
   - Reproduce with https://erp.insightpulseai.net/web?debug=assets
   - Capture console + network failing request
   - Copy X-Request-ID from response headers

3) Identify culprit module/file/line from logs using pattern matchers

4) Implement minimal fix (OCA-style):
   - Only edit ipai_* modules
   - No hot-edits to OCA vendor code
   - Follow Odoo 18 conventions

5) Rebuild assets:
   - Delete ir_attachment web.assets:
     psql "$POSTGRES_URL" -c "DELETE FROM ir_attachment WHERE name LIKE 'web.assets_%';"
   - Restart: docker restart odoo-prod

6) Verify:
   - curl https://erp.insightpulseai.net/web/login returns 200
   - No SCSS/Traceback in logs for 5 minutes
   - Visual parity check passes (if UI change)

7) Commit:
   - Incident snapshot to docs/incidents/<timestamp>/
   - Error Envelope JSON
   - Minimal fix patch only (no unrelated changes)
```

### Autofix Loop (Safe in OCA-Style)

```python
def autofix_odoo_error(error_envelope):
    """
    Safe autofix loop for known error classes.

    Args:
        error_envelope: Error Envelope JSON dict

    Returns:
        bool: True if fixed, False if requires manual intervention
    """
    error_class = classify_error(error_envelope['server_error_signature'])

    if error_class == 'SCSS_COMPILE':
        return autofix_scss_compile(error_envelope)
    elif error_class == 'XML_PARSE':
        return autofix_xml_parse(error_envelope)
    elif error_class == 'PYTHON_IMPORT':
        return autofix_python_import(error_envelope)
    elif error_class == 'RPC_ERROR':
        return autofix_rpc_error(error_envelope)
    else:
        print(f"Unknown error class: {error_class}")
        print("Manual intervention required.")
        return False

def autofix_scss_compile(envelope):
    """
    Autofix SCSS compilation errors.

    Steps:
    1. Verify file ownership (UID 100:GID 101)
    2. Patch SCSS (import order / variable define)
    3. Clear assets cache
    4. Restart + verify
    """
    module = envelope['culprit']['module']
    file = envelope['culprit']['file']
    line = envelope['culprit']['line']

    print(f"Fixing SCSS error in {module}/{file}:{line}")

    # 1. Verify ownership
    verify_ownership(module)

    # 2. Patch SCSS
    patch_scss(module, file, line, envelope['server_error_signature'])

    # 3. Clear assets
    clear_web_assets()

    # 4. Restart
    restart_odoo()

    # 5. Verify
    return verify_no_scss_errors()
```

---

## 6. Common Error Classes & Fixes

### Class: Permission Denied

**Symptom**:
```
PermissionError: [Errno 13] Permission denied: '/mnt/extra-addons/ipai_theme_tbwa/__manifest__.py'
```

**Root Cause**: Files owned by wrong user (not UID 100:GID 101)

**Fix**:
```bash
ssh root@178.128.112.214
chown -R 100:101 /opt/odoo-ce/repo/addons/ipai_theme_tbwa
chmod -R 755 /opt/odoo-ce/repo/addons/ipai_theme_tbwa
docker restart odoo-prod
```

**Prevention**: Update `scripts/deploy-odoo-modules.sh` to auto-fix permissions after rsync

### Class: SCSS Variable Undefined

**Symptom**:
```
DEBUG odoo.addons.base.models.ir_asset: Undefined variable $o-brand-primary in ipai_theme_tbwa_backend/static/src/scss/theme.scss:123
```

**Root Cause**: SCSS variable used before definition or missing import

**Fix**:
1. Add variable definition at top of file
2. Or fix import order (ensure variable file imported first)

**Verification**:
```bash
curl -sI https://erp.insightpulseai.net/web/login | head -1
# Should return: HTTP/2 200
```

### Class: XML View Parse Error (Odoo 18 Migration)

**Symptom**:
```
ERROR odoo.modules.loading: ParseError while parsing .../views/finance_kanban_views.xml:45
lxml.etree.XMLSyntaxError: Opening and ending tag mismatch: tree line 10 and list
```

**Root Cause**: Odoo 18 changed `<tree>` to `<list>` for list views

**Fix**:
```xml
<!-- Before (Odoo 17) -->
<record id="view_finance_list" model="ir.ui.view">
    <field name="arch" type="xml">
        <tree>
            ...
        </tree>
    </field>
</record>

<!-- After (Odoo 18) -->
<record id="view_finance_list" model="ir.ui.view">
    <field name="arch" type="xml">
        <list>
            ...
        </list>
    </field>
</record>
```

**Verification**:
```bash
ssh root@178.128.112.214
docker exec odoo-prod odoo -d odoo -u ipai_finance_ppm --stop-after-init
# Should complete without ParseError
```

---

## 7. Incident Documentation Template

### Directory Structure

```
docs/incidents/<timestamp_utc>/
├── metadata.json              # Auto-generated by incident_snapshot.sh
├── docker_ps.txt              # Container status
├── odoo_docker_logs.txt       # Odoo container logs
├── nginx_docker_logs.txt      # nginx container logs
├── odoo_logfile_tail.txt      # /var/lib/odoo/odoo.log
├── odoo_conf.txt              # Odoo config (sanitized)
├── mounts.json                # Docker mounts
├── error_envelope.json        # Error Envelope (manual)
├── fix.patch                  # Minimal fix patch (optional)
└── POST_MORTEM.md             # Analysis (manual)
```

### POST_MORTEM.md Template

```markdown
# Incident: <Brief Description>

**Date**: <timestamp_utc>
**Severity**: Critical | High | Medium | Low
**Impact**: <User-facing impact>
**Resolution Time**: <Time to fix>

## Timeline

- **HH:MM UTC**: Incident detected
- **HH:MM UTC**: Evidence collected (incident_snapshot.sh)
- **HH:MM UTC**: Root cause identified
- **HH:MM UTC**: Fix applied
- **HH:MM UTC**: Verification passed
- **HH:MM UTC**: Incident resolved

## Root Cause

<Definitive module/file/line with explanation>

## Error Envelope

```json
<Paste error_envelope.json>
```

## Fix Applied

<Describe minimal fix>

## Verification

- [ ] curl /web/login returns 200
- [ ] No errors in logs for 10 minutes
- [ ] Visual parity check passes (if UI change)
- [ ] Affected functionality tested manually

## Prevention

<How to prevent recurrence>

## Lessons Learned

<What we learned>
```

---

## 8. Verification Checklist

After every fix, run this checklist:

```bash
# 1. Web endpoint health check
curl -sI https://erp.insightpulseai.net/web/login | head -1
# Expected: HTTP/2 200

# 2. No errors in recent logs (5 minutes)
ssh root@178.128.112.214
docker logs --since 5m odoo-prod 2>&1 | grep -E "ERROR|CRITICAL|Traceback" || echo "No errors found"

# 3. Specific error signature absent
docker logs --since 5m odoo-prod 2>&1 | grep "<ERROR_SIGNATURE>" || echo "Error signature not found (good)"

# 4. Visual parity (if UI change)
node scripts/snap.js --routes="/expenses,/tasks" --base-url="https://erp.insightpulseai.net"
node scripts/ssim.js --routes="/expenses,/tasks" --odoo-version="18.0"
# Expected: SSIM ≥ 0.97 (mobile), ≥ 0.98 (desktop)

# 5. Manual functionality test
# Navigate to affected page, test workflow
```

---

## 9. Known Limitations

### Odoo Asset Pipeline Opacity

- Asset compilation can be opaque unless `debug=assets` and `ir_asset:DEBUG` logging enabled
- Some 400 responses depend on db routing; rely on `/web/login` for health checks
- Server stack traces won't include browser context unless correlated via request IDs

**Workaround**: nginx request-id + server log handlers + incident snapshots

### Multi-Tenant Confusion

- Single-database mode (`dbfilter = ^odoo$`) prevents multi-tenant issues
- Always verify `DB_NAME=odoo` in scripts (not `odoo_core` or other variants)

### External PostgreSQL

- Database is external (DigitalOcean Managed PostgreSQL)
- No local PostgreSQL container to inspect
- Use connection pooler (port 6543) for connections

---

## 10. Quick Reference

### Common Commands

```bash
# Capture incident snapshot
bash scripts/incident_snapshot.sh

# Verify addon permissions
bash scripts/verify-addon-permissions.sh

# Clear web.assets cache
ssh root@178.128.112.214
docker exec odoo-prod bash -lc 'psql "$POSTGRES_URL" -c "DELETE FROM ir_attachment WHERE name LIKE '\''web.assets_%'\'';"'
docker restart odoo-prod

# Check Odoo logs for errors
ssh root@178.128.112.214
docker logs --tail=500 odoo-prod 2>&1 | grep -E "ERROR|CRITICAL|Traceback"

# Upgrade module after fix
ssh root@178.128.112.214
docker exec odoo-prod odoo -d odoo -u <module_name> --stop-after-init
```

### Essential Files

- **Odoo config**: `/etc/odoo/odoo.conf` (in container)
- **Odoo logs**: `/var/lib/odoo/odoo.log` (in container)
- **Addons path**: `/mnt/extra-addons` (in container) = `/opt/odoo-ce/repo/addons` (on host)
- **nginx config**: `/etc/nginx/conf.d/default.conf` (in container)

### Key Identifiers

- **Container**: odoo-prod
- **Database**: odoo (external DigitalOcean Managed PostgreSQL)
- **Odoo user**: UID 100, GID 101
- **Public URL**: https://erp.insightpulseai.net
- **Debug URL**: https://erp.insightpulseai.net/web?debug=assets

---

**Last Updated**: 2026-01-11
**Maintained By**: Odoo DevOps Team
**Related Docs**:
- `docs/architecture/PROD_RUNTIME_SNAPSHOT.md` - Production runtime identifiers
- `docs/architecture/RUNTIME_IDENTIFIERS.md` - Quick reference for canonical names
- `CLAUDE.md` - AI agent operating procedures
