# CI/CD Security Hardening Checklist

> Production-grade security requirements for GitHub Actions workflows
> **Status**: P0 - Required before production deployment
> **Last Updated**: 2026-03-05

---

## Table of Contents

1. [Authentication & Authorization](#authentication--authorization)
2. [Secrets Management](#secrets-management)
3. [Network Security](#network-security)
4. [Runner Security](#runner-security)
5. [Workflow Security](#workflow-security)
6. [Audit & Compliance](#audit--compliance)
7. [Implementation Checklist](#implementation-checklist)

---

## Authentication & Authorization

### OIDC Authentication (Required)

**Status**: 🔴 **CRITICAL - Must implement before production**

GitHub Actions supports OIDC (OpenID Connect) for keyless authentication to cloud providers and services. This eliminates the need for long-lived credentials.

#### Benefits
- ✅ No long-lived secrets in GitHub Secrets
- ✅ Short-lived tokens with automatic rotation
- ✅ Fine-grained permissions per workflow
- ✅ Audit trail of all authentication attempts

#### Implementation

**1. Configure Supabase OIDC Trust**

```sql
-- Create OIDC provider in Supabase
-- File: supabase/migrations/20260305000000_oidc_github_actions.sql

CREATE TABLE IF NOT EXISTS auth.oidc_providers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  issuer TEXT NOT NULL UNIQUE,
  audience TEXT NOT NULL,
  jwks_uri TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO auth.oidc_providers (issuer, audience, jwks_uri)
VALUES (
  'https://token.actions.githubusercontent.com',
  'insightpulseai-odoo',
  'https://token.actions.githubusercontent.com/.well-known/jwks'
);

-- Create GitHub Actions service role
CREATE ROLE github_actions_role;
GRANT USAGE ON SCHEMA ops TO github_actions_role;
GRANT SELECT, INSERT, UPDATE ON ops.workflow_runs TO github_actions_role;
GRANT SELECT ON vault.secrets TO github_actions_role;
```

**2. Workflow OIDC Configuration**

```yaml
# File: .github/workflows/_reusable-oidc-auth.yml
name: Reusable OIDC Authentication

on:
  workflow_call:
    outputs:
      supabase_token:
        description: "Short-lived Supabase access token"
        value: ${{ jobs.authenticate.outputs.token }}

permissions:
  id-token: write  # Required for OIDC
  contents: read

jobs:
  authenticate:
    runs-on: ubuntu-latest
    outputs:
      token: ${{ steps.auth.outputs.token }}
    steps:
      - name: Get OIDC Token
        id: oidc
        run: |
          OIDC_TOKEN=$(curl -H "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" \
            "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=insightpulseai-odoo" \
            | jq -r '.value')
          echo "::add-mask::$OIDC_TOKEN"
          echo "oidc_token=$OIDC_TOKEN" >> $GITHUB_OUTPUT

      - name: Exchange for Supabase Token
        id: auth
        run: |
          SUPABASE_TOKEN=$(curl -X POST \
            "${{ secrets.SUPABASE_URL }}/auth/v1/token?grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer" \
            -H "Content-Type: application/json" \
            -H "apikey: ${{ secrets.SUPABASE_ANON_KEY }}" \
            -d "{\"assertion\": \"${{ steps.oidc.outputs.oidc_token }}\"}" \
            | jq -r '.access_token')
          echo "::add-mask::$SUPABASE_TOKEN"
          echo "token=$SUPABASE_TOKEN" >> $GITHUB_OUTPUT
```

**3. Usage in Workflows**

```yaml
# Example workflow using OIDC
name: Secure Workflow with OIDC

on: push

permissions:
  id-token: write
  contents: read

jobs:
  authenticate:
    uses: ./.github/workflows/_reusable-oidc-auth.yml

  deploy:
    needs: authenticate
    runs-on: self-hosted
    steps:
      - name: Fetch secrets from Vault
        env:
          SUPABASE_TOKEN: ${{ needs.authenticate.outputs.supabase_token }}
        run: |
          # Fetch secrets from Supabase Vault
          SECRETS=$(curl -X POST \
            "${{ secrets.SUPABASE_URL }}/rest/v1/rpc/get_workflow_secrets" \
            -H "Authorization: Bearer $SUPABASE_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"workflow_name": "${{ github.workflow }}"}')

          # Export as environment variables (masked)
          echo "::add-mask::$SECRETS"
          echo "$SECRETS" | jq -r 'to_entries[] | "\(.key)=\(.value)"' >> $GITHUB_ENV
```

### Least Privilege Principles

**Workflow Permissions** (defaults to read-only):

```yaml
permissions:
  contents: read        # Read repository content
  id-token: write       # OIDC token generation (required)
  pull-requests: write  # Comment on PRs (if needed)
  issues: write         # Create issues (if needed)
  # All other permissions: none (default)
```

**Service Account Matrix**:

| Service Account | Permissions | Usage | Rotation |
|----------------|-------------|-------|----------|
| `github_actions_odoo_deploy` | SSH to DO droplet, restart Odoo | Deployment workflows | Monthly |
| `github_actions_plane_sync` | Plane API read/write | Issue creation, status updates | Monthly |
| `github_actions_n8n_trigger` | n8n webhook POST | Workflow orchestration | Monthly |
| `github_actions_slack_notify` | Slack API post to specific channels | Notifications | Monthly |
| `github_actions_vault_read` | Supabase Vault SELECT | Secret retrieval | Weekly |

---

## Secrets Management

### Architecture: Supabase Vault → Workflow Injection

**Principle**: Never store secrets in GitHub Secrets directly. Use GitHub Secrets only for:
1. `SUPABASE_URL` (public anyway)
2. `SUPABASE_ANON_KEY` (low privilege, public in client apps)

All sensitive credentials stored in Supabase Vault with OIDC-authenticated access.

### Vault Schema

```sql
-- File: supabase/migrations/20260305000001_vault_schema.sql

CREATE SCHEMA IF NOT EXISTS vault;

CREATE TABLE vault.secrets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  value TEXT NOT NULL,  -- Encrypted at rest by Supabase
  description TEXT,
  service TEXT NOT NULL,  -- e.g., 'odoo', 'plane', 'n8n'
  rotation_policy TEXT DEFAULT 'monthly',  -- 'weekly', 'monthly', 'never'
  last_rotated_at TIMESTAMPTZ DEFAULT now(),
  created_by TEXT DEFAULT current_user,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Row-Level Security (RLS)
ALTER TABLE vault.secrets ENABLE ROW LEVEL SECURITY;

-- Only github_actions_role can read secrets
CREATE POLICY github_actions_read_secrets
  ON vault.secrets
  FOR SELECT
  TO github_actions_role
  USING (true);

-- Audit trail
CREATE TABLE vault.secret_access_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  secret_id UUID REFERENCES vault.secrets(id),
  accessed_by TEXT NOT NULL,  -- GitHub workflow name
  accessed_at TIMESTAMPTZ DEFAULT now(),
  ip_address INET,
  jwt_claims JSONB  -- OIDC token claims for audit
);

-- Function to log access
CREATE OR REPLACE FUNCTION vault.log_secret_access()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO vault.secret_access_log (secret_id, accessed_by, jwt_claims)
  VALUES (NEW.id, current_user, current_setting('request.jwt.claims', true)::jsonb);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER log_secret_access_trigger
  AFTER SELECT ON vault.secrets
  FOR EACH ROW
  EXECUTE FUNCTION vault.log_secret_access();
```

### Secret Retrieval Function

```sql
-- File: supabase/migrations/20260305000002_vault_functions.sql

CREATE OR REPLACE FUNCTION vault.get_workflow_secrets(workflow_name TEXT)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  secrets_json JSONB;
BEGIN
  -- Verify caller is authenticated via OIDC
  IF current_setting('request.jwt.claims', true)::jsonb->>'iss' != 'https://token.actions.githubusercontent.com' THEN
    RAISE EXCEPTION 'Unauthorized: OIDC authentication required';
  END IF;

  -- Retrieve secrets as JSON
  SELECT jsonb_object_agg(name, value)
  INTO secrets_json
  FROM vault.secrets
  WHERE service = SPLIT_PART(workflow_name, '-', 1);  -- e.g., 'odoo-deploy' → 'odoo'

  RETURN secrets_json;
END;
$$;

-- Grant execution to github_actions_role
GRANT EXECUTE ON FUNCTION vault.get_workflow_secrets TO github_actions_role;
```

### Populating Vault (One-Time Setup)

```bash
#!/bin/bash
# File: scripts/ci/populate-vault.sh

set -euo pipefail

SUPABASE_URL="${SUPABASE_URL}"
SUPABASE_SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY}"

# Function to add secret
add_secret() {
  local name="$1"
  local value="$2"
  local service="$3"
  local description="$4"

  curl -X POST \
    "$SUPABASE_URL/rest/v1/vault.secrets" \
    -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
    -H "Content-Type: application/json" \
    -H "Prefer: return=minimal" \
    -d "{
      \"name\": \"$name\",
      \"value\": \"$value\",
      \"service\": \"$service\",
      \"description\": \"$description\"
    }"
}

# Odoo deployment secrets
add_secret "ODOO_SSH_PRIVATE_KEY" "$(cat ~/.ssh/id_rsa_odoo_deploy)" "odoo" "SSH key for DO droplet deployment"
add_secret "ODOO_DB_PASSWORD" "$ODOO_DB_PASSWORD" "odoo" "PostgreSQL password for Odoo database"

# Plane API secrets
add_secret "PLANE_API_KEY" "$PLANE_API_KEY" "plane" "Plane API key for issue creation"
add_secret "PLANE_WORKSPACE_SLUG" "fin-ops" "plane" "Plane workspace slug"
add_secret "PLANE_PROJECT_ID" "dd0b3bd5-43e8-47ab-b3ad-279bb15d4778" "plane" "BIR project ID"

# n8n secrets
add_secret "N8N_WEBHOOK_SECRET" "$N8N_WEBHOOK_SECRET" "n8n" "n8n webhook authentication secret"

# Slack secrets
add_secret "SLACK_BOT_TOKEN" "$SLACK_BOT_TOKEN" "slack" "Slack bot token for notifications"

# Anthropic API (for AI workflows)
add_secret "ANTHROPIC_API_KEY" "$ANTHROPIC_API_KEY" "ai" "Claude API key for test generation"

echo "✅ Vault populated successfully"
```

### Secret Rotation Automation

```yaml
# File: .github/workflows/rotate-secrets.yml
name: Rotate Secrets

on:
  schedule:
    - cron: '0 0 1 * *'  # Monthly on 1st at midnight
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

jobs:
  rotate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Authenticate with OIDC
        id: auth
        uses: ./.github/workflows/_reusable-oidc-auth.yml

      - name: Rotate secrets
        env:
          SUPABASE_TOKEN: ${{ steps.auth.outputs.token }}
        run: |
          # Call Supabase Edge Function for rotation
          curl -X POST \
            "${{ secrets.SUPABASE_URL }}/functions/v1/rotate-secrets" \
            -H "Authorization: Bearer $SUPABASE_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"rotation_policy": "monthly"}'

      - name: Notify on failure
        if: failure()
        run: |
          # Send Slack alert
          curl -X POST "${{ secrets.SLACK_WEBHOOK_URL }}" \
            -H "Content-Type: application/json" \
            -d '{"text": "❌ Secret rotation failed - manual intervention required"}'
```

---

## Network Security

### Firewall Rules (DO Droplet)

```bash
#!/bin/bash
# File: scripts/ci/configure-firewall.sh

# Allow only GitHub Actions IP ranges
GITHUB_META=$(curl -s https://api.github.com/meta | jq -r '.actions[]')

# Flush existing rules
ufw --force reset

# Default deny
ufw default deny incoming
ufw default allow outgoing

# Allow SSH from specific IPs only (replace with your IPs)
ufw allow from YOUR_ADMIN_IP to any port 22

# Allow GitHub Actions runners
for ip in $GITHUB_META; do
  ufw allow from "$ip" to any port 22 comment "GitHub Actions"
done

# Allow HTTP/HTTPS (for Odoo, n8n)
ufw allow 80/tcp
ufw allow 443/tcp

# Allow PostgreSQL only from localhost
ufw allow from 127.0.0.1 to any port 5432

# Enable firewall
ufw --force enable

echo "✅ Firewall configured for GitHub Actions"
```

### Network Isolation

**Docker Network Configuration**:

```yaml
# File: docker-compose.prod.yml
version: '3.8'

networks:
  odoo_internal:
    driver: bridge
    internal: true  # No external access
  odoo_external:
    driver: bridge

services:
  odoo:
    networks:
      - odoo_internal
      - odoo_external
    # Only nginx has external access

  postgres:
    networks:
      - odoo_internal  # No external access

  nginx:
    networks:
      - odoo_external
    ports:
      - "80:80"
      - "443:443"
```

---

## Runner Security

### Ephemeral Runners (Required)

Self-hosted runners must be ephemeral (one job per runner lifecycle).

**Benefits**:
- ✅ Clean state for each job (no artifacts from previous jobs)
- ✅ Reduced attack surface (no persistent state)
- ✅ Automatic cleanup (no manual maintenance)

**Implementation**:

```bash
#!/bin/bash
# File: scripts/ci/setup-ephemeral-runner.sh

set -euo pipefail

RUNNER_VERSION="2.311.0"
RUNNER_ARCH="linux-x64"
GITHUB_OWNER="Insightpulseai"
GITHUB_REPO="odoo"

# Fetch runner registration token (via GitHub API)
REGISTRATION_TOKEN=$(curl -X POST \
  -H "Authorization: token $GITHUB_PAT" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$GITHUB_OWNER/$GITHUB_REPO/actions/runners/registration-token" \
  | jq -r '.token')

# Download runner
mkdir -p /opt/actions-runner && cd /opt/actions-runner
curl -o actions-runner-linux-x64.tar.gz -L \
  "https://github.com/actions/runner/releases/download/v$RUNNER_VERSION/actions-runner-$RUNNER_ARCH-$RUNNER_VERSION.tar.gz"
tar xzf ./actions-runner-linux-x64.tar.gz

# Configure runner (ephemeral mode)
./config.sh \
  --url "https://github.com/$GITHUB_OWNER/$GITHUB_REPO" \
  --token "$REGISTRATION_TOKEN" \
  --name "odoo-runner-$(hostname)" \
  --labels "odoo,n8n,plane,self-hosted,linux,x64" \
  --work "_work" \
  --ephemeral \
  --unattended

# Install as systemd service
sudo ./svc.sh install
sudo ./svc.sh start

echo "✅ Ephemeral runner configured and started"
```

### Runner Hardening

```bash
#!/bin/bash
# File: scripts/ci/harden-runner.sh

# Disable unnecessary services
systemctl disable bluetooth
systemctl disable cups
systemctl disable avahi-daemon

# Apply CIS benchmark settings
apt install -y aide
aide --init
mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# Configure automatic security updates
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

# Limit sudo access
echo "github_runner ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/bin/systemctl restart odoo" > /etc/sudoers.d/github_runner

# Disable root login
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd

echo "✅ Runner hardened"
```

### Health Monitoring

```yaml
# File: .github/workflows/runner-health-check.yml
name: Runner Health Check

on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes

jobs:
  health:
    runs-on: self-hosted
    steps:
      - name: Check runner health
        run: |
          # CPU usage
          CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)

          # Memory usage
          MEM=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')

          # Disk usage
          DISK=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)

          # Export metrics to Supabase
          curl -X POST \
            "${{ secrets.SUPABASE_URL }}/rest/v1/ops.metrics" \
            -H "Authorization: Bearer ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}" \
            -H "Content-Type: application/json" \
            -d "{
              \"runner_name\": \"$RUNNER_NAME\",
              \"cpu_usage\": $CPU,
              \"memory_usage\": $MEM,
              \"disk_usage\": $DISK,
              \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
            }"

          # Alert if thresholds exceeded
          if (( $(echo "$CPU > 80" | bc -l) )); then
            echo "⚠️ High CPU usage: $CPU%"
          fi

          if (( $(echo "$MEM > 90" | bc -l) )); then
            echo "⚠️ High memory usage: $MEM%"
          fi
```

---

## Workflow Security

### Input Validation

```yaml
# Always validate user inputs
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Validate module name
        run: |
          MODULE_NAME="${{ github.event.inputs.module_name }}"

          # Only allow alphanumeric, underscore, hyphen
          if ! [[ "$MODULE_NAME" =~ ^[a-z0-9_-]+$ ]]; then
            echo "❌ Invalid module name: $MODULE_NAME"
            exit 1
          fi

          # Prevent path traversal
          if [[ "$MODULE_NAME" == *".."* ]] || [[ "$MODULE_NAME" == *"/"* ]]; then
            echo "❌ Path traversal detected"
            exit 1
          fi
```

### Dependency Scanning

```yaml
# File: .github/workflows/security-scan.yml
name: Security Scan

on:
  pull_request:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 1'  # Weekly

jobs:
  sast:
    name: Static Analysis (SAST)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Bandit (Python SAST)
        run: |
          pip install bandit
          bandit -r addons/ipai -f json -o bandit-report.json

      - name: Upload SAST results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: bandit-report.json

  dependency-check:
    name: Dependency Vulnerabilities
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Safety (Python dependencies)
        run: |
          pip install safety
          safety check --json --file requirements.txt

      - name: OWASP Dependency Check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'odoo'
          path: '.'
          format: 'JSON'

  secrets-scan:
    name: Secret Scanning
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: TruffleHog Secret Scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
```

---

## Audit & Compliance

### Workflow Execution Logging

```sql
-- File: supabase/migrations/20260305000003_workflow_audit.sql

CREATE TABLE ops.workflow_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_name TEXT NOT NULL,
  run_id BIGINT NOT NULL,
  run_number INTEGER NOT NULL,
  event TEXT NOT NULL,
  status TEXT NOT NULL,  -- 'queued', 'in_progress', 'completed', 'failed', 'cancelled'
  started_at TIMESTAMPTZ NOT NULL,
  completed_at TIMESTAMPTZ,
  duration_seconds INTEGER,
  actor TEXT NOT NULL,
  repository TEXT NOT NULL,
  branch TEXT,
  commit_sha TEXT,
  secrets_accessed TEXT[],  -- Array of secret names accessed
  runner_name TEXT,
  logs_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Index for querying
CREATE INDEX idx_workflow_runs_status ON ops.workflow_runs(status);
CREATE INDEX idx_workflow_runs_started ON ops.workflow_runs(started_at DESC);
CREATE INDEX idx_workflow_runs_actor ON ops.workflow_runs(actor);

-- RLS policy (read-only for analytics)
ALTER TABLE ops.workflow_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY analytics_read_workflow_runs
  ON ops.workflow_runs
  FOR SELECT
  TO authenticated
  USING (true);
```

### Logging Pattern (in workflows)

```yaml
- name: Log workflow execution
  if: always()
  env:
    SUPABASE_TOKEN: ${{ needs.authenticate.outputs.supabase_token }}
  run: |
    curl -X POST \
      "${{ secrets.SUPABASE_URL }}/rest/v1/ops.workflow_runs" \
      -H "Authorization: Bearer $SUPABASE_TOKEN" \
      -H "Content-Type: application/json" \
      -H "Prefer: return=minimal" \
      -d "{
        \"workflow_name\": \"${{ github.workflow }}\",
        \"run_id\": ${{ github.run_id }},
        \"run_number\": ${{ github.run_number }},
        \"event\": \"${{ github.event_name }}\",
        \"status\": \"${{ job.status }}\",
        \"started_at\": \"${{ github.event.head_commit.timestamp }}\",
        \"actor\": \"${{ github.actor }}\",
        \"repository\": \"${{ github.repository }}\",
        \"branch\": \"${{ github.ref_name }}\",
        \"commit_sha\": \"${{ github.sha }}\",
        \"runner_name\": \"$RUNNER_NAME\",
        \"logs_url\": \"${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}\"
      }"
```

### Compliance Reporting

```yaml
# File: .github/workflows/compliance-report.yml
name: Compliance Report

on:
  schedule:
    - cron: '0 9 * * 1'  # Weekly on Monday 9 AM
  workflow_dispatch:

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - name: Generate compliance report
        run: |
          # Fetch workflow execution data
          REPORT=$(curl -X POST \
            "${{ secrets.SUPABASE_URL }}/rest/v1/rpc/generate_compliance_report" \
            -H "Authorization: Bearer ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{"start_date": "2026-03-01", "end_date": "2026-03-07"}')

          # Send to Plane as documentation issue
          curl -X POST \
            "${{ secrets.PLANE_API_URL }}/workspaces/${{ secrets.PLANE_WORKSPACE_SLUG }}/projects/${{ secrets.PLANE_PROJECT_ID }}/issues/" \
            -H "X-API-Key: ${{ secrets.PLANE_API_KEY }}" \
            -H "Content-Type: application/json" \
            -d "{
              \"name\": \"Weekly Compliance Report - $(date +%Y-%m-%d)\",
              \"description_html\": \"$REPORT\",
              \"state\": \"backlog\",
              \"priority\": \"low\",
              \"labels\": [\"compliance\", \"automation\"]
            }"
```

---

## Implementation Checklist

### Phase 1: Foundation (P0 - Week 1)

- [ ] **OIDC Configuration**
  - [ ] Create Supabase OIDC provider
  - [ ] Implement reusable OIDC auth workflow
  - [ ] Test token exchange with sample workflow
  - [ ] Document OIDC setup in runbook

- [ ] **Vault Setup**
  - [ ] Create vault schema in Supabase
  - [ ] Implement RLS policies
  - [ ] Create `get_workflow_secrets` function
  - [ ] Populate vault with production secrets
  - [ ] Test secret retrieval in workflow

- [ ] **Network Security**
  - [ ] Configure firewall rules on DO droplet
  - [ ] Implement Docker network isolation
  - [ ] Whitelist GitHub Actions IP ranges
  - [ ] Test SSH access from GitHub Actions

### Phase 2: Runner Security (P0 - Week 2)

- [ ] **Ephemeral Runners**
  - [ ] Install Actions runner on DO droplet
  - [ ] Configure ephemeral mode
  - [ ] Setup systemd service with auto-restart
  - [ ] Test runner lifecycle (job → cleanup)

- [ ] **Runner Hardening**
  - [ ] Apply CIS benchmark settings
  - [ ] Configure automatic security updates
  - [ ] Limit sudo access for runner user
  - [ ] Disable unnecessary services

- [ ] **Health Monitoring**
  - [ ] Implement runner health check workflow
  - [ ] Export metrics to Supabase
  - [ ] Setup alerting for high resource usage
  - [ ] Test failover to GitHub-hosted runners

### Phase 3: Workflow Security (P1 - Week 3)

- [ ] **Input Validation**
  - [ ] Add validation to all workflow_dispatch inputs
  - [ ] Implement path traversal prevention
  - [ ] Sanitize all external inputs

- [ ] **Dependency Scanning**
  - [ ] Setup Bandit for Python SAST
  - [ ] Configure Safety for dependency checks
  - [ ] Integrate OWASP Dependency Check
  - [ ] Setup TruffleHog for secret scanning

- [ ] **Error Handling**
  - [ ] Implement retry logic with exponential backoff
  - [ ] Add timeout protection to all jobs
  - [ ] Configure fallback workflows for failures

### Phase 4: Audit & Compliance (P2 - Week 4)

- [ ] **Logging**
  - [ ] Create ops.workflow_runs table
  - [ ] Implement logging in all workflows
  - [ ] Setup log retention policy (90 days)

- [ ] **Compliance Reporting**
  - [ ] Create compliance report generator
  - [ ] Schedule weekly compliance reports
  - [ ] Integrate with Plane for documentation

- [ ] **Secret Rotation**
  - [ ] Implement automated secret rotation
  - [ ] Schedule monthly rotation workflow
  - [ ] Test rotation for all secret types

### Phase 5: Validation (Week 5)

- [ ] **End-to-End Testing**
  - [ ] Test complete OIDC → Vault → Workflow flow
  - [ ] Verify ephemeral runner lifecycle
  - [ ] Test secret rotation workflow
  - [ ] Validate audit logging completeness

- [ ] **Security Audit**
  - [ ] External security review (if budget allows)
  - [ ] Penetration testing of runner infrastructure
  - [ ] Review all RLS policies in Supabase

- [ ] **Documentation**
  - [ ] Complete runbooks for all procedures
  - [ ] Document incident response procedures
  - [ ] Create training materials for team

---

## Security Contacts

**Security Team**:
- Email: security@insightpulseai.com
- Slack: #security-alerts
- Plane: Security project (create for tracking)

**Incident Response**:
1. Immediately revoke compromised credentials in Vault
2. Notify security team via Slack
3. Create incident issue in Plane
4. Follow incident response runbook (docs/security/INCIDENT_RESPONSE.md)

---

## References

- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [OIDC with GitHub Actions](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [Supabase Security Best Practices](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [OWASP Top 10 CI/CD Security Risks](https://owasp.org/www-project-top-10-ci-cd-security-risks/)

---

**Last Updated**: 2026-03-05
**Status**: 🔴 P0 - Required implementation before production deployment
**Next Action**: Implement OIDC authentication and Vault setup (Phase 1)
