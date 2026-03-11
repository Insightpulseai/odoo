# GitHub Enterprise Integration with Plane-Odoo-n8n Stack

> Leveraging GitHub Enterprise features for enhanced automation, security, and compliance

---

## GitHub Enterprise Features for Your Integration

### 1. **GitHub Apps for Enterprise** (Primary Integration Method)

**What You're Using**:
- `pulser-hub` GitHub App (webhook-based integration)
- Organization-wide installation (`Insightpulseai` org)

**Enterprise Advantages**:
- ✅ **Organization-level permissions**: Install once, works across all repos
- ✅ **Fine-grained access tokens**: Scope permissions per integration
- ✅ **Webhook reliability**: Enterprise SLA guarantees
- ✅ **Audit logging**: Complete event trail in GitHub Enterprise audit log

**Configuration for n8n Workflow**:
```json
{
  "github_enterprise": {
    "api_url": "https://api.github.com",
    "app_id": "[pulser-hub app ID]",
    "installation_id": "[org installation ID]",
    "private_key": "[RSA key from GitHub App]",
    "webhook_secret": "[HMAC secret for signature verification]"
  }
}
```

---

### 2. **GitHub Actions Integration**

**Use Case**: CI/CD triggers for Plane-Odoo sync

**Enterprise Features**:
- ✅ **Self-hosted runners**: Run workflows on your DigitalOcean infrastructure
- ✅ **Required workflows**: Enforce sync validation before PR merge
- ✅ **Workflow templates**: Standardize Plane issue creation across repos

**Example Workflow** (`.github/workflows/plane-sync-on-pr.yml`):
```yaml
name: Sync PR to Plane

on:
  pull_request:
    types: [opened, reopened, labeled]

jobs:
  create-plane-issue:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.labels.*.name, 'needs-planning')

    steps:
      - name: Create Plane Issue via n8n
        uses: distributhor/workflow-webhook@v3
        with:
          webhook_url: ${{ secrets.N8N_WEBHOOK_URL }}
          webhook_secret: ${{ secrets.N8N_WEBHOOK_SECRET }}
          data: |
            {
              "source": "github_actions",
              "pr_number": "${{ github.event.pull_request.number }}",
              "pr_title": "${{ github.event.pull_request.title }}",
              "pr_url": "${{ github.event.pull_request.html_url }}",
              "labels": ${{ toJson(github.event.pull_request.labels) }},
              "repository": "${{ github.repository }}"
            }

      - name: Comment PR with Plane Link
        uses: actions/github-script@v7
        with:
          script: |
            const { data: { plane_issue_url } } = await fetch(
              process.env.N8N_WEBHOOK_URL,
              { method: 'GET', headers: { 'Authorization': `Bearer ${process.env.N8N_WEBHOOK_SECRET}` } }
            );

            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `✅ Plane issue created: ${plane_issue_url}`
            });
```

---

### 3. **GitHub Enterprise Security Features**

**Relevant for Your Stack**:

#### A. **Secret Scanning**
- Prevents accidental commit of `PLANE_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- Custom patterns for Odoo credentials (**requires GitHub Advanced Security - GHAS**)
- Push protection blocks commits with secrets

**Configuration** (requires GHAS):
```yaml
# .github/secret_scanning.yml (custom patterns require GHAS)
custom_patterns:
  - name: "Plane API Key"
    pattern: "plane_api_[a-f0-9]{32}"

  - name: "Supabase Service Role Key"
    pattern: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+"

  - name: "Odoo Password"
    pattern: "ODOO_PASSWORD=[\\w@#$%^&*()_+=-]+"
```

**Note**: Standard secret scanning (GitHub's built-in patterns) is available for all public repos and private repos with GitHub Advanced Security enabled. Custom patterns require GHAS.

#### B. **Dependabot for Odoo Modules**
- Monitors Python dependencies in `addons/ipai/*/requirements.txt`
- Auto-creates PRs for security updates
- Integrates with Plane via n8n workflow

**Configuration** (`.github/dependabot.yml`):
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/addons/ipai/ipai_bir_plane_sync"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "python"
      - "security"

  - package-ecosystem: "npm"
    directory: "/mcp/servers/plane"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "nodejs"
      - "mcp-server"
```

#### C. **Code Scanning (CodeQL)**
- Security analysis for TypeScript MCP servers
- Python security checks for Odoo modules
- Results sync to Plane as security backlog

**n8n Workflow Integration**:
```
GitHub CodeQL Alert Created
  ↓
n8n Webhook Trigger
  ↓
Create Plane Issue (security backlog, priority: urgent)
  ↓
Create Odoo Task (if compliance-related)
  ↓
Slack #security Channel Notification
  ↓
GitHub: Add comment with Plane issue link
```

---

### 4. **GitHub Projects vs Plane.so**

**Strategic Decision**: Use **Plane** as primary project management, GitHub Projects as auxiliary

| Feature | GitHub Projects | Plane.so | Recommendation |
|---------|----------------|----------|----------------|
| Issue tracking | ✅ Native | ✅ Enhanced | Use Plane (richer features) |
| Roadmaps | ✅ Basic | ✅ Advanced | Use Plane (cycles, modules) |
| Custom fields | ✅ Limited | ✅ Extensive | Use Plane |
| API access | ✅ GraphQL | ✅ REST | Both (via n8n) |
| Self-hosted | ❌ No | ✅ Yes | Plane (data sovereignty) |
| Code integration | ✅ Native | ⚠️ Via sync | GitHub (but sync to Plane) |

**Integration Strategy**:
- GitHub Issues: Development task tracking (technical details, code refs)
- Plane Issues: Project management, business context, OKRs
- n8n: Keep both in sync
- Odoo: ERP compliance and billing

---

### 5. **GitHub API Rate Limits**

**Rate limits vary by authentication type and product tier:**
- **Unauthenticated requests**: 60 requests/hour
- **Authenticated requests (PAT/OAuth)**: 5,000 requests/hour
- **GitHub App (installation token)**: 5,000 requests/hour per installation
- **Enterprise Cloud with IP allowlist**: Rate limits may be higher (contact GitHub)

**Note**: Rate limits are per-user for OAuth/PAT, per-installation for GitHub Apps

**Optimization for n8n Workflows**:
```javascript
// n8n HTTP Request node configuration
{
  "url": "https://api.github.com/repos/Insightpulseai/odoo/issues",
  "headers": {
    "Authorization": "Bearer {{ $credentials.githubEnterpriseToken }}",
    "X-GitHub-Api-Version": "2022-11-28",
    "Accept": "application/vnd.github+json"
  },
  "options": {
    "rateLimitHandling": {
      "enabled": true,
      "maxRetries": 3,
      "backoffStrategy": "exponential"
    }
  }
}
```

**Rate Limit Monitoring** (Supabase Edge Function):
```typescript
// Check GitHub API rate limit before bulk operations
const rateLimitResponse = await fetch('https://api.github.com/rate_limit', {
  headers: { 'Authorization': `Bearer ${GITHUB_TOKEN}` }
});

const { resources } = await rateLimitResponse.json();
const { core } = resources;

if (core.remaining < 100) {
  const resetTime = new Date(core.reset * 1000);
  console.warn(`GitHub API rate limit low: ${core.remaining} remaining, resets at ${resetTime}`);
  // Implement backoff or queue mechanism
}
```

---

### 6. **GitHub Enterprise Webhooks (Advanced)**

**Standard Webhook Events** (already using):
- `issues` (opened, closed, labeled)
- `pull_request` (opened, merged, review_requested)
- `issue_comment` (created)

**Additional Events** (require specific features/permissions):
- `repository` events (created, deleted, archived) → Requires repo admin permissions
- `organization` events (member_added, member_removed) → Requires org owner access
- `security_advisory` events (published, updated) → Requires security advisory permissions
- `code_scanning_alert` → Requires GitHub Advanced Security (GHAS)
- `secret_scanning_alert` → Requires GitHub Advanced Security (GHAS)

**Use Cases**:
- `repository.created` → Auto-add to Plane workspace
- `organization.member_added` → Sync to Odoo user management
- `security_advisory.published` → Create Plane security backlog item

**Webhook Delivery Reliability**:

**Architecture**:
```
GitHub Webhook → Ingestion → Persistence → Enqueue → Processing → Retry/Dedupe
```

**Implementation Flow**:

1. **Signature Verification** (Supabase Edge Function):
```typescript
// supabase/functions/ops-github-webhook-ingest/index.ts
import { createHmac } from "https://deno.land/std@0.168.0/node/crypto.ts"

serve(async (req) => {
  const signature = req.headers.get("x-hub-signature-256")
  const payload = await req.text()

  // Verify webhook signature
  const webhookSecret = Deno.env.get("GITHUB_WEBHOOK_SECRET")
  const expectedSig = `sha256=${createHmac("sha256", webhookSecret).update(payload).digest("hex")}`

  if (signature !== expectedSig) {
    return new Response("Invalid signature", { status: 401 })
  }

  const event = JSON.parse(payload)
  // Continue to step 2...
})
```

2. **Persist to Audit Trail**:
```typescript
// Write to ops.github_webhook_deliveries IMMEDIATELY
const { data, error } = await supabaseClient
  .from('ops.github_webhook_deliveries')
  .insert({
    delivery_id: req.headers.get("x-github-delivery"),
    event_type: req.headers.get("x-github-event"),
    payload: event,
    received_at: new Date().toISOString(),
    status: 'received' // Not 'processed' yet
  })
```

3. **Enqueue for Processing**:
```typescript
// Enqueue to ops.task_queue for async processing
await supabaseClient
  .from('ops.task_queue')
  .insert({
    task_type: 'github_webhook_processing',
    payload: { delivery_id: deliveryId },
    priority: eventPriority(event), // High priority for security alerts
    scheduled_at: new Date().toISOString()
  })

// Return 200 OK immediately - GitHub requires fast ACK
return new Response(JSON.stringify({ queued: true }), { status: 200 })
```

4. **Background Processing** (separate worker):
```typescript
// Worker polls ops.task_queue every 5 seconds
const tasks = await supabaseClient
  .from('ops.task_queue')
  .select('*')
  .eq('status', 'pending')
  .order('priority', { ascending: false })
  .limit(10)

for (const task of tasks) {
  // Dedupe check
  const existing = await checkIfAlreadyProcessed(task.payload.delivery_id)
  if (existing) {
    await markTaskComplete(task.id)
    continue
  }

  // Process webhook (trigger n8n, create Plane issue, etc.)
  await processWebhook(task.payload.delivery_id)
}
```

5. **Retry Logic**:
```typescript
// If processing fails, retry with exponential backoff
if (processingError) {
  const retryCount = task.retry_count || 0
  const backoffSeconds = Math.pow(2, retryCount) * 60 // 1m, 2m, 4m, 8m...

  await supabaseClient
    .from('ops.task_queue')
    .update({
      retry_count: retryCount + 1,
      scheduled_at: new Date(Date.now() + backoffSeconds * 1000).toISOString(),
      last_error: processingError.message
    })
    .eq('id', task.id)
}
```

**Fallback Mechanism**:
- If n8n is down, webhooks still persist to Supabase
- Worker will retry when n8n comes back online
- GitHub redelivery attempts (if Edge Function fails): automatic retry for up to 3 days
- Manual redelivery: GitHub webhook settings → Recent Deliveries → "Redeliver"

---

### 7. **GitHub Enterprise Support for Odoo Development**

**Use Cases**:

#### A. **OCA Module Development Workflow**
```
1. Create GitHub issue: "Port OCA module X to Odoo 19"
2. GitHub Actions: Check OCA compatibility
3. n8n: Create Plane issue (development backlog)
4. Developer: Work on module in feature branch
5. PR created: n8n updates Plane issue status
6. PR merged: n8n creates Odoo task for QA testing
7. GitHub Release: n8n syncs to Plane milestone completion
```

#### B. **BIR Compliance Documentation**
```
GitHub Wiki (per repo)
  ↓
n8n: Extract BIR-related docs
  ↓
Odoo: Create bir.compliance.document records
  ↓
Plane: Link to compliance issues
  ↓
Supabase: Store searchable index
```

---

### 8. **GitHub Enterprise + Copilot for Business**

**Relevant for Your Stack**:
- ✅ **Copilot Chat**: Context-aware code suggestions for Odoo modules
- ✅ **Code review assistance**: Automated PR reviews for Python/TypeScript
- ✅ **Documentation generation**: Auto-generate docstrings for Odoo methods

**Integration Point**:
```
Developer writes Odoo module with Copilot
  ↓
Push to GitHub
  ↓
GitHub Actions: Run tests + OCA compliance check
  ↓
n8n: Sync to Plane (code review task)
  ↓
Reviewer uses Copilot Chat for review
  ↓
PR approved: n8n updates Odoo task status
```

---

## Implementation Checklist

### Phase 1: GitHub Enterprise Setup (If Not Already Done)

- [ ] Verify GitHub Enterprise organization: `Insightpulseai`
- [ ] Enable required features:
  - [ ] GitHub Apps
  - [ ] GitHub Actions (with self-hosted runners)
  - [ ] Secret scanning (with custom patterns)
  - [ ] Dependabot
  - [ ] Code scanning (CodeQL)
- [ ] Configure organization-level webhooks
- [ ] Set up audit log streaming to Supabase

### Phase 2: GitHub App Configuration

- [ ] Review `pulser-hub` GitHub App permissions:
  - [ ] Issues: Read & Write
  - [ ] Pull Requests: Read & Write
  - [ ] Webhooks: Subscribe to events
  - [ ] Metadata: Read
- [ ] Update webhook URL to point to n8n:
  - Primary: `https://n8n.insightpulseai.com/webhook/github-plane-sync`
  - Fallback: `https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/github-webhook-handler`
- [ ] Configure webhook secret (store in Supabase Vault)
- [ ] Install app on all `Insightpulseai` repositories

### Phase 3: GitHub Actions Integration

- [ ] Create workflow templates in `.github/workflow-templates/`:
  - [ ] `plane-sync.yml`: Auto-sync PRs to Plane
  - [ ] `bir-compliance-check.yml`: Validate BIR-related changes
  - [ ] `odoo-module-test.yml`: Test Odoo modules before merge
- [ ] Configure organization secrets:
  - [ ] `N8N_WEBHOOK_URL`
  - [ ] `N8N_WEBHOOK_SECRET`
  - [ ] `PLANE_API_KEY`
  - [ ] `SUPABASE_SERVICE_ROLE_KEY`

### Phase 4: Security Configuration

- [ ] Enable secret scanning push protection
- [ ] Configure custom secret patterns (Plane, Supabase, Odoo)
- [ ] Set up Dependabot for Python and Node.js dependencies
- [ ] Enable CodeQL analysis for TypeScript and Python
- [ ] Create n8n workflow: CodeQL alerts → Plane security issues

### Phase 5: n8n Workflow Updates

- [ ] Update `plane-odoo-github-sync.json` with GitHub Enterprise specifics
- [ ] Add GitHub Actions webhook trigger node
- [ ] Add rate limit monitoring
- [ ] Add fallback webhook handling (Supabase Edge Function)
- [ ] Test end-to-end with GitHub Enterprise events

---

## GitHub Enterprise API Integration Examples

### 1. **List All Organization Repositories** (for Plane workspace mapping)

```javascript
// n8n HTTP Request node
{
  "url": "https://api.github.com/orgs/Insightpulseai/repos",
  "method": "GET",
  "headers": {
    "Authorization": "Bearer {{ $credentials.githubEnterpriseToken }}",
    "Accept": "application/vnd.github+json"
  },
  "qs": {
    "type": "all",
    "sort": "updated",
    "per_page": 100
  }
}
```

**Use Case**: Sync all repos to Plane projects, create Odoo project records.

### 2. **Create Issue with Custom Properties** (Enterprise-only)

```javascript
// n8n GitHub node
{
  "resource": "issue",
  "operation": "create",
  "repository": "Insightpulseai/odoo",
  "title": "[BIR] {{ $json.form_type }} Filing Due {{ $json.deadline_date }}",
  "body": "Synced from Odoo BIR deadline #{{ $json.odoo_id }}",
  "labels": ["bir:filing", "compliance", "priority:high"],
  "assignees": ["finance-team"],
  "custom_fields": {
    "odoo_id": {{ $json.odoo_id }},
    "plane_issue_id": "{{ $json.plane_issue_id }}",
    "deadline": "{{ $json.deadline_date }}"
  }
}
```

### 3. **Search Issues with Advanced Filters** (for Plane sync validation)

```javascript
// n8n HTTP Request node
{
  "url": "https://api.github.com/search/issues",
  "method": "GET",
  "qs": {
    "q": "org:Insightpulseai label:bir:filing is:open",
    "sort": "created",
    "order": "desc"
  }
}
```

---

## Monitoring & Observability

### GitHub Enterprise Audit Log → Supabase

**Use Case**: Complete audit trail of all GitHub Enterprise events

**Supabase Edge Function** (`github-audit-log-ingest`):
```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  const auditEvent = await req.json()

  // Store in Supabase ops.platform_events
  const { data, error } = await supabaseClient
    .from('ops.platform_events')
    .insert({
      event_type: `github.${auditEvent.action}`,
      source_system: 'github_enterprise',
      event_data: auditEvent,
      timestamp: new Date(auditEvent.created_at).toISOString(),
      correlation_id: auditEvent.request_id
    })

  return new Response(JSON.stringify({ success: !error }))
})
```

**GitHub Enterprise Configuration**:
```
Settings → Audit Log Streaming
Endpoint: https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/github-audit-log-ingest
Format: JSON
Events: All
```

---

## Cost Optimization

### GitHub Enterprise Pricing Considerations

**Features Included**:
- ✅ Unlimited private repositories
- ✅ GitHub Actions (50,000 minutes/month)
- ✅ GitHub Packages (50GB storage)
- ✅ Advanced security features
- ✅ Premium support

**n8n Workflow Optimizations**:
1. **Batch API calls**: Reduce GitHub API requests by batching updates
2. **Webhook-first**: Use webhooks instead of polling
3. **Self-hosted runners**: Use DigitalOcean droplets for Actions (cheaper than GitHub-hosted)
4. **Cache dependencies**: Reduce package download time

---

## Next Steps

1. ✅ **Review GitHub Enterprise features** (you're here)
2. ⏳ **Verify `pulser-hub` app configuration** (check app permissions)
3. ⏳ **Update n8n workflow** with GitHub Enterprise API specifics
4. ⏳ **Configure GitHub Actions workflows** (plane-sync, bir-compliance-check)
5. ⏳ **Enable security features** (secret scanning, Dependabot, CodeQL)
6. ⏳ **Test end-to-end** (GitHub → Plane → Odoo → Slack)

---

## Resources

| Resource | URL |
|----------|-----|
| GitHub Enterprise Docs | https://docs.github.com/enterprise-cloud@latest |
| GitHub Apps Docs | https://docs.github.com/apps |
| GitHub Actions Docs | https://docs.github.com/actions |
| GitHub API Reference | https://docs.github.com/rest |
| GitHub Enterprise Support | https://enterprise.github.com/support |
| n8n GitHub Node Docs | https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.github/ |

---

**Last Updated**: 2026-03-05
**Status**: GitHub Enterprise integration documented, ready for configuration
**Next Action**: Verify `pulser-hub` app settings and update n8n workflow
