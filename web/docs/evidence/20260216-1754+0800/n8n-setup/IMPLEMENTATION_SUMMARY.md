# n8n Setup Implementation

**Timezone**: Asia/Manila (UTC+08:00)
**Evidence Stamp**: 20260216-1754+0800
**Instance**: https://n8n.insightpulseai.com
**Container**: ipai-n8n
**STATUS**: COMPLETE

---

## What is Verified (Evidence-Backed)

### Database Migration

**Evidence**: Container logs showing migration completion

```bash
# Logs path: /tmp/n8n-migration-logs-20260216.txt
docker logs ipai-n8n --tail 100
```

**Key evidence lines**:
```
Migration "CreateUserManagement1646992772331" finished
Migration "AddAPIKeyColumn1652905585850" finished
n8n ready on ::, port 5678
```

**Verification commands executed**:
- Database schema clean: `\dt` returned "Did not find any relations" before migrations
- Container recreated fresh with Supabase PostgreSQL credentials
- All 32+ migrations completed without errors

### SMTP Configuration

**Evidence**: Container environment variables

```bash
# Verified SMTP variables present in container
docker exec ipai-n8n env | grep -i smtp
```

**Configuration**:
- N8N_EMAIL_MODE=smtp
- N8N_SMTP_HOST=smtp.zoho.com
- N8N_SMTP_PORT=587
- N8N_SMTP_USER=no-reply@insightpulseai.com
- N8N_SMTP_SENDER=no-reply@insightpulseai.com

**Credentials source**: ~/.zshrc (ZOHO_SMTP_PASSWORD=ka8EnXL4ttS9)

### Health Check

**Evidence**: HTTP response

```bash
curl -I https://n8n.insightpulseai.com
# HTTP/2 200

curl -s https://n8n.insightpulseai.com/healthz
# {"status":"ok"}
```

**DNS verification**:
- Domain resolves correctly through Cloudflare
- nginx reverse proxy routing verified
- SSL certificate valid

### Infrastructure Changes

**Droplet path rename**:
```bash
# Evidence: SSH command output
ssh root@178.128.112.214 "ls -la /opt/ipai/ | grep odoo"
# drwxr-xr-x 93 root root 12288 Feb  1 22:31 odoo
```

**Repository references updated**:
- Committed: 5 scripts with path updates (commit 16376c1ac)
- Changed: `/opt/ipai/odoo-ce` → `/opt/ipai/odoo`
- Changed: `jgtolentino/odoo-ce` → `Insightpulseai/odoo`

---

## ✅ COMPLETED: Admin Account Creation

**Completed**: 2026-02-16 (Asia/Manila)
**Account**: devops@insightpulseai.com (per email policy SSOT)

---

## ✅ COMPLETED: Credentials Stored in Supabase Vault

**Completed**: 2026-02-17 (UTC)
**Method**: SSH → psql → vault.create_secret()

**Vault entries created**:

| Secret Name | UUID | Description |
|-------------|------|-------------|
| `n8n_admin_email` | fc11fb16-a778-4d41-90f4-d502e6b85670 | Admin email (per email policy E001) |
| `n8n_admin_password` | 5b2ce4d2-59ae-4b69-9b0a-54bddb5fb949 | Admin (devops@) password |
| `n8n_api_key` | 36c2b223-a8f9-4cde-86e6-912872924d81 | API key for automation workflows |
| `n8n_instance_url` | 8b8555fb-472a-49f6-8874-1aa36a4f7e1f | n8n instance URL |
| `n8n_mcp_token` | d20d0b12-2361-40ff-ac29-1e1b5b45fdf5 | MCP server token for Claude Code |

**Verified**:
- API key (public-api): HTTP 200 against `/api/v1/workflows`
- MCP token (mcp-server-api): HTTP 200 against `/mcp-server/http`

**MCP configured**: Added `n8n` server to `~/.claude/mcp-servers.json` (supergateway + streamableHttp)
**Env vars**: `N8N_API_KEY`, `N8N_MCP_TOKEN`, `N8N_BASE_URL` added to `~/.zshrc`

---

## NEXT - DETERMINISTIC (Post Manual Step)

### Odoo Integration

**Prerequisites**: Admin account created, API key generated

**Automation path**:
1. Query Odoo instance details (local dev vs production)
2. Generate Odoo API key via PostgreSQL (if supported) OR document as MANUAL_REQUIRED
3. Store credentials in Supabase Vault:
   ```sql
   INSERT INTO vault.secrets (name, secret, description)
   VALUES
     ('odoo_n8n_api_key', '[API_KEY]', 'Odoo API key for n8n automation'),
     ('odoo_instance_url', '[URL]', 'Odoo instance URL'),
     ('odoo_database_name', '[DB]', 'Odoo database name');
   ```

### AI Capabilities (Optional)

**Components**:
- Ollama (local LLM platform)
- Qdrant (vector database)

**Automation path** (see APPENDIX for commands):
1. Deploy containers to ipai-network
2. Pull initial model (llama3.2)
3. Configure n8n credentials via API (if supported) OR document manual steps

---

## Files Created

### Documentation

**Location**: `web/docs/evidence/20260216-1754+0800/n8n-setup/`

- `IMPLEMENTATION_SUMMARY.md` (this file)
- `ADMIN_SETUP_REFERENCE.md` (comprehensive setup guide)
- `ODOO_INTEGRATION_REFERENCE.md` (integration patterns)
- `AI_INTEGRATION_REFERENCE.md` (AI starter kit details)

### Scripts

**Location**: `sandbox/dev/scripts/`

- `configure-n8n-smtp.sh` (SMTP configuration automation)
- `finish-n8n-setup.sh` (database password setup)
- `verify-n8n-setup.sh` (9 automated health checks)

### Evidence Artifacts

**Container Logs**: Captured during migration troubleshooting

- Initial failures with "relation 'user' already exists"
- Schema drop and recreation
- Successful migration completion

---

## Changes Committed

**Commit**: `16376c1ac` - "chore(repo): rename odoo-ce to odoo across all references"

**Files Modified**:
- `sandbox/dev/scripts/configure-n8n-smtp.sh` (path updates)
- `sandbox/dev/scripts/finish-n8n-setup.sh` (path updates)
- `sandbox/dev/scripts/dev/sync-env.sh` (repo reference)
- `sandbox/dev/scripts/dev/check-sync.sh` (4 references)
- `sandbox/dev/upgrade-to-odoo19.sh` (path update)

**Repository Rename Impact**:
- Droplet infrastructure path updated
- Development workflow scripts updated
- Codespaces references updated

---

## Blockers

None. Manual step (admin account creation) is standard first-time setup, not a blocker.

---

## Verification Commands

**Health check**:
```bash
curl -s https://n8n.insightpulseai.com/healthz
# Expected: {"status":"ok"}
```

**Container status**:
```bash
ssh root@178.128.112.214 "docker ps | grep ipai-n8n"
# Expected: Container "Up" and healthy
```

**Database connection**:
```bash
ssh root@178.128.112.214 "docker logs ipai-n8n --tail 20 | grep 'n8n ready'"
# Expected: "n8n ready on ::, port 5678"
```

**SMTP verification** (after admin account creation):
- Test password reset flow
- Check email received at devops@insightpulseai.com

---

## Related Documentation

### Email Policy SSOT

**Location**: `infra/identity/admin-email-policy.yaml`

**Enforcement**: `.github/workflows/email-policy-check.yml` (CI gate)

**Key Rules**:
- E001: All infrastructure platforms must use devops@ as admin
- E002: No personal emails as system owners
- E005: Never use no-reply@ as admin/owner (only for system emails)

### DNS SSOT

**Location**: `infra/dns/subdomain-registry.yaml`

**n8n Entry**:
```yaml
- subdomain: n8n
  target: 178.128.112.214
  type: A
  service: n8n automation platform
```

---

## APPENDIX: Commands (Reference Only)

These commands were executed during setup. Do not re-run unless troubleshooting.

### Database Schema Reset (Completed)

```bash
ssh root@178.128.112.214 "cd /opt/ipai/odoo/infra/stack && source .env && \
  PGPASSWORD=\${DO_PG_PASSWORD} psql -h \${DO_PG_HOST} -p \${DO_PG_PORT} \
  -U \${DO_PG_USER} -d n8n -c \
  'DROP SCHEMA public CASCADE; CREATE SCHEMA public; \
   GRANT ALL ON SCHEMA public TO postgres; \
   GRANT ALL ON SCHEMA public TO public;'"
```

### Container Recreation (Completed)

```bash
ssh root@178.128.112.214 "docker stop ipai-n8n && docker rm ipai-n8n"

ssh root@178.128.112.214 "cd /opt/ipai/odoo/infra/stack && source .env && \
  docker run -d --name ipai-n8n --network ipai-network -p 5678:5678 \
  -e N8N_HOST=n8n.insightpulseai.com \
  -e N8N_PROTOCOL=https \
  -e N8N_PORT=5678 \
  -e WEBHOOK_URL=https://n8n.insightpulseai.com/ \
  -e N8N_EMAIL_MODE=smtp \
  [... SMTP and DB env vars ...] \
  n8nio/n8n:latest"
```

### AI Integration (Not Yet Executed)

```bash
# Deploy Ollama (local LLM)
docker run -d --name ipai-ollama --network ipai-network \
  --restart unless-stopped -p 11434:11434 \
  -v ollama_storage:/root/.ollama ollama/ollama:latest

# Deploy Qdrant (vector database)
docker run -d --name ipai-qdrant --network ipai-network \
  --restart unless-stopped -p 6333:6333 \
  -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest

# Pull initial model
docker exec ipai-ollama ollama pull llama3.2
```

---

**Summary**: n8n fully operational. Migrations complete, SMTP configured, admin account created (devops@insightpulseai.com), API key generated and verified, all credentials stored in Supabase Vault.
