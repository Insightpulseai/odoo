# AI Agent Troubleshooting Playbook - Odoo SCSS/Asset Errors

**Purpose**: Deterministic troubleshooting protocol for AI agents fixing Odoo asset compilation errors.

**Last Updated**: 2026-01-10

---

## Execution Protocol (No Creative Wandering)

### Phase 1: Evidence Collection (Browser)

**Step 1.1**: Reproduce in browser with debug mode
```bash
URL="https://erp.insightpulseai.com/web?debug=assets"
```

**Step 1.2**: Capture from Chrome DevTools
- **Console**: First error line (exact text)
- **Network**: Failing assets request → Response tab
- **Network**: `X-Request-Id` header value (for server log correlation)
- **Sources**: Search for failing import statement (e.g., `import "tokens"`)

**Step 1.3**: Check for error banner in HTML
```bash
curl -fsS "https://erp.insightpulseai.com/web?debug=assets" | grep -i "style compilation failed"
```

### Phase 2: Evidence Collection (Server)

**Step 2.1**: Run verification gate
```bash
/opt/odoo-ce/repo/scripts/verify_web_assets.sh
```

**Step 2.2**: Extract SCSS/asset errors from logs
```bash
docker logs --tail 500 odoo-prod | grep -E "File to import not found|ir_asset|scss|sass"
```

**Step 2.3**: If X-Request-Id available from browser
```bash
docker logs odoo-prod | grep "<request-id-from-browser>"
```

### Phase 3: Classification (Deterministic Decision Tree)

**Decision Tree**:
```
Is the missing file in /usr/lib/python3/.../odoo/addons/... (core Odoo)?
├─ YES → CLASSIFICATION: Image/Spec Drift
│         ROOT CAUSE: Odoo Docker image version skew
│         FIX PATH: A (Recreate from pinned digest)
│
└─ NO → Is the file in /mnt/extra-addons/... (custom addons)?
        ├─ YES → CLASSIFICATION: Permissions/Ownership
        │         ROOT CAUSE: Files not readable by UID 100:GID 101
        │         FIX PATH: B (Fix permissions)
        │
        └─ NO → CLASSIFICATION: Unknown
                 ESCALATE: Manual investigation required
```

### Phase 4: Fix Application

#### Fix Path A: Image/Spec Drift
```bash
# Recreate container from pinned digest
/opt/odoo-ce/repo/scripts/recreate_odoo_prod.sh

# Verification automatically runs at end of script
```

#### Fix Path B: Permissions/Ownership
```bash
# Fix ownership for custom addons
ssh root@178.128.112.214 "chown -R 100:101 /opt/odoo-ce/repo/addons/ipai*"
ssh root@178.128.112.214 "chmod -R 755 /opt/odoo-ce/repo/addons/ipai*"

# Clear asset cache
docker exec odoo-prod bash -c 'rm -rf /var/lib/odoo/.local/share/Odoo/filestore/*/assets/*'

# Restart container
docker restart odoo-prod

# Wait for startup
sleep 15

# Verify
/opt/odoo-ce/repo/scripts/verify_web_assets.sh
```

### Phase 5: Verification (Must PASS)

**Step 5.1**: Run verification gate
```bash
/opt/odoo-ce/repo/scripts/verify_web_assets.sh
```

**Expected Output**:
```
== 1) Site reachable ==
HTTP/2 200 
== 2) No style compilation banner in HTML (debug=assets) ==
PASS
== 3) No recent SCSS import errors in Odoo logs ==
PASS
== 4) Odoo is serving (internal) ==
PASS
== OK ==
```

**Step 5.2**: Manual browser verification
1. Open `https://erp.insightpulseai.com/web?debug=assets`
2. Check Console for errors
3. Check Network for failed asset requests
4. Verify UI renders properly (no "style compilation failed" banner)

---

## Error Patterns & Quick Fixes

### Pattern 1: "File to import not found: tokens"
```
ERROR: Can't import /usr/lib/python3/.../bootstrap/scss/tokens
CLASSIFICATION: Image/Spec Drift
FIX: /opt/odoo-ce/repo/scripts/recreate_odoo_prod.sh
```

### Pattern 2: "PermissionError: [Errno 13] Permission denied"
```
ERROR: Permission denied: /mnt/extra-addons/ipai_theme_*/...
CLASSIFICATION: Permissions/Ownership
FIX: chown -R 100:101 /opt/odoo-ce/repo/addons/ipai*
```

### Pattern 3: "Undefined variable $o-brand-primary"
```
ERROR: SCSS variable undefined in custom theme
CLASSIFICATION: Theme Configuration
FIX: Check theme SCSS import order, ensure variables loaded before usage
```

---

## Post-Fix Documentation

After successful fix, document in `docs/incidents/<timestamp>.md`:

```markdown
# Incident: SCSS Compilation Failure - <Date>

## Symptom
[Exact error text from browser/logs]

## Root Cause
[Classification from decision tree]

## Fix Applied
[Exact commands executed]

## Verification
[Output of verify_web_assets.sh]

## Prevention
[What was updated to prevent recurrence]
```

---

## Escalation Criteria

Escalate to manual investigation if:
1. Verification gate fails after both Fix Path A and B
2. Error pattern doesn't match known patterns
3. Browser shows errors but server logs are clean
4. Asset compilation succeeds but UI still broken

**Escalation Contact**: Repository owner or DevOps team
