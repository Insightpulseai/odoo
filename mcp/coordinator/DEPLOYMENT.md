# MCP Coordinator Deployment Guide

## Prerequisites

1. **DigitalOcean Access Token**
   - Go to: https://cloud.digitalocean.com/account/api/tokens
   - Create new token with read/write access
   - Update `~/.zshrc`:
     ```bash
     export DO_ACCESS_TOKEN="dop_v1_xxxxx"
     ```
   - Source: `source ~/.zshrc`

2. **Supabase Service Role Key**
   - Already configured in environment
   - Verify: `echo ${SUPABASE_SERVICE_ROLE_KEY:0:20}`

3. **Coordinator API Key**
   - Generate secure key: `openssl rand -hex 32`
   - Will be configured in DO App Platform dashboard

## Deployment Steps

### 1. Authenticate with DigitalOcean

```bash
doctl auth init --access-token "$DO_ACCESS_TOKEN"
doctl auth list  # Verify authentication
```

### 2. Create the App

```bash
cd /Users/tbwa/odoo-ce
doctl apps create --spec mcp/coordinator/infra/do/mcp-coordinator.yaml \
  --format ID,Spec.Name,DefaultIngress
```

**Expected Output:**
```
ID                                    Name              Default Ingress
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  mcp-coordinator   https://mcp-coordinator-xxxxx.ondigitalocean.app
```

### 3. Configure Secrets (via Dashboard)

1. Go to: https://cloud.digitalocean.com/apps/[APP_ID]/settings
2. Navigate to: App-Level Environment Variables
3. Add/Update secrets:
   - `COORDINATOR_API_KEY`: Generate with `openssl rand -hex 32`
   - `SUPABASE_SERVICE_ROLE_KEY`: Copy from `$SUPABASE_SERVICE_ROLE_KEY`
4. Trigger redeployment

### 4. Monitor Deployment

```bash
# Get app ID from step 2
APP_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Watch deployment progress
doctl apps list-deployments $APP_ID --format ID,Phase,Progress

# View logs
doctl apps logs $APP_ID --follow
```

### 5. Verify Health

```bash
# Get the app URL from step 2 output
APP_URL="https://mcp-coordinator-xxxxx.ondigitalocean.app"

# Test health endpoint
curl -s "$APP_URL/health" | jq

# Test status endpoint (requires API key from step 3)
curl -s -H "X-API-Key: YOUR_COORDINATOR_API_KEY" "$APP_URL/status" | jq
```

**Expected Health Response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "targets": ["odoo_prod", "odoo_lab"]
}
```

### 6. Configure DNS

1. **Get App URL** from deployment output (step 2)
2. **Add CNAME record** in DNS provider:
   - Name: `mcp`
   - Type: `CNAME`
   - Value: `mcp-coordinator-xxxxx.ondigitalocean.app` (without https://)
   - TTL: `3600`

3. **Add Domain in DO Dashboard**:
   - Go to: App → Settings → Domains
   - Add domain: `mcp.insightpulseai.net`
   - Verify DNS propagation: `dig mcp.insightpulseai.net`

4. **Enable HTTPS**:
   - DO automatically provisions Let's Encrypt SSL
   - Wait 5-10 minutes for certificate

### 7. Update MCP Server Configs

After DNS is configured, update the production MCP server config:

```bash
cd /Users/tbwa/odoo-ce

# Update odoo-erp.yaml with production URL
vim mcp/servers/odoo-erp.yaml
# Change: url: https://mcp.insightpulseai.net
```

## Testing Production Deployment

### Test Routing

```bash
# Generate test query
cat > /tmp/mcp-test.json << 'EOF'
{
  "query": "How do I file BIR 1601-C for Finance SSC?",
  "context": {
    "finance-ssc": true
  }
}
EOF

# Test routing endpoint
curl -s -X POST https://mcp.insightpulseai.net/route \
  -H "X-API-Key: YOUR_COORDINATOR_API_KEY" \
  -H "Content-Type: application/json" \
  --data @/tmp/mcp-test.json | jq
```

**Expected Response:**
```json
{
  "data": {...},
  "routing": {
    "target": "odoo_prod",
    "reason": "Finance SSC context requires production data",
    "confidence": 0.95
  }
}
```

### Test Aggregation

```bash
cat > /tmp/mcp-aggregate.json << 'EOF'
{
  "query": "List all Odoo skills",
  "context": {}
}
EOF

curl -s -X POST https://mcp.insightpulseai.net/aggregate \
  -H "X-API-Key: YOUR_COORDINATOR_API_KEY" \
  -H "Content-Type: application/json" \
  --data @/tmp/mcp-aggregate.json | jq
```

## Troubleshooting

### Build Fails

**Check build logs:**
```bash
doctl apps logs $APP_ID --type BUILD
```

**Common issues:**
- Missing dependencies in `requirements.txt` → Add to file
- Dockerfile syntax errors → Verify locally with `docker build`

### Runtime Errors

**Check runtime logs:**
```bash
doctl apps logs $APP_ID --type RUN --follow
```

**Common issues:**
- Missing environment variables → Check App Platform dashboard
- Supabase connection errors → Verify `SUPABASE_SERVICE_ROLE_KEY`
- Port binding issues → Ensure `http_port: 8766` in spec

### Health Check Fails

**Symptoms:**
- App shows "Deploying" indefinitely
- Health check endpoint returns 503

**Debug:**
```bash
# Check if container is listening on port 8766
doctl apps logs $APP_ID | grep "Uvicorn running"

# Test internal health endpoint
doctl apps logs $APP_ID | grep "/health"
```

**Fix:**
- Verify `HEALTHCHECK` in Dockerfile
- Ensure FastAPI app binds to `0.0.0.0:8766`
- Check startup time (increase `initial_delay_seconds` if needed)

### DNS Not Resolving

**Check DNS propagation:**
```bash
dig mcp.insightpulseai.net
nslookup mcp.insightpulseai.net
```

**Wait time:**
- CNAME changes: 5-60 minutes
- First-time DNS: up to 24 hours (rare)

**Verify with curl:**
```bash
curl -v https://mcp.insightpulseai.net/health
# Should return HTTP 200 + JSON response
```

## Rollback

If deployment fails, rollback to previous version:

```bash
# List deployments
doctl apps list-deployments $APP_ID

# Get previous deployment ID
PREVIOUS_DEPLOYMENT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Rollback
doctl apps create-deployment $APP_ID --deployment-id $PREVIOUS_DEPLOYMENT_ID
```

## Monitoring

### View Metrics

```bash
# App metrics (via dashboard)
open "https://cloud.digitalocean.com/apps/$APP_ID/metrics"
```

**Key Metrics:**
- CPU usage (should be <30% average)
- Memory usage (should be <400MB for basic-xxs)
- HTTP requests/second
- HTTP error rate (should be <1%)

### Logs

```bash
# Real-time logs
doctl apps logs $APP_ID --follow

# Last 100 lines
doctl apps logs $APP_ID --tail 100

# Filter by type
doctl apps logs $APP_ID --type RUN --follow
```

## Scaling

If needed, upgrade instance size:

```bash
# Edit spec file
vim mcp/coordinator/infra/do/mcp-coordinator.yaml
# Change: instance_size_slug: basic-xs  # 1GB RAM, $10/month

# Update app
doctl apps update $APP_ID --spec mcp/coordinator/infra/do/mcp-coordinator.yaml
```

## Security

### Rotate Coordinator API Key

```bash
# Generate new key
NEW_KEY=$(openssl rand -hex 32)

# Update in DO dashboard
# Apps → [APP_ID] → Settings → Environment Variables
# Update: COORDINATOR_API_KEY

# Redeploy
doctl apps create-deployment $APP_ID --force-rebuild

# Update local clients
echo "export COORDINATOR_API_KEY='$NEW_KEY'" >> ~/.zshrc
source ~/.zshrc
```

### Rotate Supabase Key

**DO NOT rotate service role key unless absolutely necessary.**

If rotation is required:
1. Generate new service role key in Supabase dashboard
2. Update DO App Platform environment variable
3. Update local `~/.zshrc`
4. Redeploy coordinator

## Next Steps

After successful deployment:

1. ✅ Coordinator deployed and healthy
2. ✅ DNS configured and resolving
3. ✅ HTTPS enabled
4. 📝 Test routing with production MCP servers
5. 📝 Update VS Code workspace configs
6. 📝 Monitor for 24 hours
7. 📝 Proceed to Phase 3 (DO Advisor)

---

**Deployment Date**: TBD (awaiting DO token refresh)
**Deployed By**: Claude Code
**App Platform Region**: San Francisco (sfo)
**Instance Size**: basic-xxs (512MB RAM, $5/month)
