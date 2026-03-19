# DNS Delegation: Squarespace → DigitalOcean

**Purpose**: Enable CLI-based DNS management for autonomous enterprise operations by delegating DNS authority from Squarespace to DigitalOcean.

**Status**: Recommended Strategic Change  
**Date**: 2026-02-04  
**Domain**: `insightpulseai.com`

---

## Problem Statement

**Challenge**: Squarespace does not offer a public DNS API or command-line tool.

**Impact**:
- ❌ No automation: Every DNS change requires manual UI login
- ❌ No CI/CD integration: Cannot create DNS records from GitHub Actions or n8n workflows
- ❌ No Infrastructure as Code: Cannot version control DNS configuration
- ❌ No dynamic environments: Cannot auto-create `feat-xyz.insightpulseai.com` for branch deployments

**Solution**: Delegate DNS authority to DigitalOcean while keeping domain registration at Squarespace.

---

## Strategic Context: Autonomous Enterprise

This repository follows the **"Autonomous Enterprise"** philosophy:

```
Everything that can be automated MUST be automated via CLI/API
```

### Current Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                   InsightPulse AI Stack (Self-Hosted)                │
├─────────────────────────────────────────────────────────────────────┤
│   Hosting: DigitalOcean Droplets (~$50-100/mo)                       │
│   Database: PostgreSQL 16 (self-managed, not RDS)                    │
│   Automation: n8n (self-hosted)                                      │
│   DNS: Squarespace (manual, no API) ← BLOCKING AUTOMATION            │
└─────────────────────────────────────────────────────────────────────┘
```

### After DNS Delegation

```
┌─────────────────────────────────────────────────────────────────────┐
│   Hosting: DigitalOcean (droplets + DNS)                             │
│   Automation: doctl compute domain (CLI-managed)                     │
│   CI/CD: GitHub Actions can create DNS records                       │
│   IaC: Terraform can version control DNS zone                        │
│   Domain Billing: Squarespace (just payment processor)               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Solution Architecture

### What Changes

| Aspect | Before (Squarespace DNS) | After (DO DNS) |
|--------|--------------------------|----------------|
| **Nameservers** | Squarespace default | `ns{1,2,3}.digitalocean.com` |
| **DNS Records** | Managed in Squarespace UI | Managed via `doctl` CLI |
| **Automation** | ❌ Not possible | ✅ Full CLI/API access |
| **Version Control** | ❌ No | ✅ Terraform/Git |
| **Domain Billing** | Squarespace | Squarespace (unchanged) |

### What Stays the Same

✅ **Domain registration**: Still at Squarespace  
✅ **Domain renewal**: Still billed by Squarespace  
✅ **Domain ownership**: No change  
✅ **Existing DNS records**: Will be migrated to DigitalOcean

---

## Implementation Steps

### Phase 1: Pre-Migration (DO THIS FIRST)

**1. Export Current DNS Records**

Before changing anything, document all existing DNS records:

```bash
# Export current Squarespace DNS configuration
./scripts/dns/export-squarespace-dns.sh
```

**2. Create Domain in DigitalOcean**

```bash
# Set environment variable (your droplet IP)
export DO_DROPLET_IP="178.128.112.214"

# Create domain in DigitalOcean
doctl compute domain create insightpulseai.com --ip-address "$DO_DROPLET_IP"
```

**3. Replicate Existing Records**

Use the automated migration script:

```bash
./scripts/dns/migrate-dns-to-do.sh
```

Or manually recreate critical records:

```bash
# Production ERP
doctl compute domain records create insightpulseai.com \
  --record-type A \
  --record-name erp \
  --record-data 178.128.112.214 \
  --record-ttl 3600

# n8n automation
doctl compute domain records create insightpulseai.com \
  --record-type A \
  --record-name n8n \
  --record-data 178.128.112.214 \
  --record-ttl 3600

# Mailgun subdomain MX
doctl compute domain records create insightpulseai.com \
  --record-type MX \
  --record-name mg \
  --record-data "mxa.mailgun.org." \
  --record-priority 10 \
  --record-ttl 3600

doctl compute domain records create insightpulseai.com \
  --record-type MX \
  --record-name mg \
  --record-data "mxb.mailgun.org." \
  --record-priority 10 \
  --record-ttl 3600

# Mailgun DKIM
doctl compute domain records create insightpulseai.com \
  --record-type TXT \
  --record-name "pic._domainkey.mg" \
  --record-data "k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDUwHKEo91h..." \
  --record-ttl 3600

# Add remaining records as needed
```

**4. Verify DigitalOcean DNS Configuration**

```bash
# List all records to verify
doctl compute domain records list insightpulseai.com

# Verify specific records
./scripts/dns/verify-do-dns.sh
```

### Phase 2: Nameserver Delegation (ONE-TIME UI ACTION)

⚠️ **This is the only manual step required. Do this ONCE.**

**Steps:**

1. Log into Squarespace: https://account.squarespace.com
2. Navigate to: **Domains → insightpulseai.com → DNS Settings**
3. Scroll to **Nameservers** section
4. Click **Use Custom Nameservers**
5. Enter DigitalOcean nameservers:
   ```
   ns1.digitalocean.com
   ns2.digitalocean.com
   ns3.digitalocean.com
   ```
6. Click **Save**

**Propagation Time**: 1–24 hours (typically 2–6 hours)

**During Propagation**:
- Some users see old DNS (Squarespace)
- Some users see new DNS (DigitalOcean)
- This is expected and safe

### Phase 3: Verification

**Wait 2-6 Hours**, then verify nameserver delegation:

```bash
# Check nameservers (should show digitalocean.com)
dig insightpulseai.com NS +short

# Expected output:
# ns1.digitalocean.com.
# ns2.digitalocean.com.
# ns3.digitalocean.com.

# Verify A records
dig insightpulseai.com A +short
dig erp.insightpulseai.com A +short

# Verify MX records for Mailgun
dig mg.insightpulseai.com MX +short

# Run comprehensive verification
./scripts/dns/verify-delegation-complete.sh
```

---

## CLI-Based DNS Management (Post-Delegation)

### Common Operations

**List All Records:**
```bash
doctl compute domain records list insightpulseai.com
```

**Add A Record:**
```bash
doctl compute domain records create insightpulseai.com \
  --record-type A \
  --record-name staging \
  --record-data 178.128.112.214 \
  --record-ttl 3600
```

**Add CNAME Record:**
```bash
doctl compute domain records create insightpulseai.com \
  --record-type CNAME \
  --record-name www \
  --record-data "@" \
  --record-ttl 3600
```

**Add TXT Record (SPF/DMARC):**
```bash
doctl compute domain records create insightpulseai.com \
  --record-type TXT \
  --record-name "@" \
  --record-data "v=spf1 include:mailgun.org ~all" \
  --record-ttl 3600
```

**Update Existing Record:**
```bash
# First, get record ID
doctl compute domain records list insightpulseai.com

# Then update by ID
doctl compute domain records update insightpulseai.com \
  --record-id 123456789 \
  --record-data "new-value"
```

**Delete Record:**
```bash
doctl compute domain records delete insightpulseai.com \
  --record-id 123456789
```

### Automation Scripts

**Create Branch Preview Environment:**
```bash
./scripts/dns/create-preview-dns.sh feature/new-ui
# Creates: feat-new-ui.insightpulseai.com → 178.128.112.214
```

**Cleanup Preview Environments:**
```bash
./scripts/dns/cleanup-preview-dns.sh
# Removes all feat-*.insightpulseai.com records older than 7 days
```

**Sync DNS with Git:**
```bash
./scripts/dns/export-dns-to-terraform.sh
# Generates: infra/terraform/dns.tf (version controlled)
```

---

## Integration Patterns

### GitHub Actions

**Auto-create DNS on Deploy:**

```yaml
# .github/workflows/deploy-preview.yml
name: Deploy Preview Environment
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Create Preview DNS
        run: |
          BRANCH_NAME="${{ github.head_ref }}"
          SUBDOMAIN=$(echo "$BRANCH_NAME" | sed 's/[^a-z0-9]/-/g' | cut -c1-63)
          
          doctl compute domain records create insightpulseai.com \
            --record-type A \
            --record-name "preview-$SUBDOMAIN" \
            --record-data "178.128.112.214" \
            --record-ttl 3600
          
          echo "Preview URL: https://preview-$SUBDOMAIN.insightpulseai.com"
```

### n8n Workflows

**Webhook-Triggered DNS Creation:**

```json
{
  "nodes": [
    {
      "name": "GitHub Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "github-pr"
      }
    },
    {
      "name": "Create DNS Record",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.digitalocean.com/v2/domains/insightpulseai.com/records",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "digitalOceanApi",
        "method": "POST",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "type",
              "value": "A"
            },
            {
              "name": "name",
              "value": "={{ $json.pull_request.head.ref.replace(/[^a-z0-9]/g, '-') }}"
            },
            {
              "name": "data",
              "value": "178.128.112.214"
            }
          ]
        }
      }
    }
  ]
}
```

### Terraform

**Version-Controlled DNS:**

```hcl
# infra/terraform/dns.tf
resource "digitalocean_domain" "main" {
  name = "insightpulseai.com"
}

resource "digitalocean_record" "erp" {
  domain = digitalocean_domain.main.name
  type   = "A"
  name   = "erp"
  value  = var.droplet_ip
  ttl    = 3600
}

resource "digitalocean_record" "n8n" {
  domain = digitalocean_domain.main.name
  type   = "A"
  name   = "n8n"
  value  = var.droplet_ip
  ttl    = 3600
}

# Mailgun MX
resource "digitalocean_record" "mailgun_mx_a" {
  domain   = digitalocean_domain.main.name
  type     = "MX"
  name     = "mg"
  priority = 10
  value    = "mxa.mailgun.org."
  ttl      = 3600
}

resource "digitalocean_record" "mailgun_mx_b" {
  domain   = digitalocean_domain.main.name
  type     = "MX"
  name     = "mg"
  priority = 10
  value    = "mxb.mailgun.org."
  ttl      = 3600
}
```

Apply with:
```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

---

## Rollback Plan

If delegation causes issues, you can revert:

### Option 1: Quick Revert (Within 24 Hours)

**In Squarespace:**
1. Go back to DNS Settings
2. Change nameservers back to Squarespace defaults
3. Wait 2-6 hours for propagation

### Option 2: Temporary DNS Override (Immediate)

Add entries to `/etc/hosts` on your local machine:
```
178.128.112.214 erp.insightpulseai.com
178.128.112.214 n8n.insightpulseai.com
```

### Option 3: Use DigitalOcean API Directly

Even if nameservers aren't fully propagated, you can manage DNS via API:
```bash
doctl compute domain records create insightpulseai.com \
  --record-type A \
  --record-name emergency-fix \
  --record-data 178.128.112.214
```

---

## Security Considerations

### Access Control

**Principle**: Only CI/CD systems and authorized engineers should have `doctl` access.

**DO NOT**:
- ❌ Commit `DIGITALOCEAN_ACCESS_TOKEN` to git
- ❌ Share tokens via Slack/email
- ❌ Use account-level tokens (use scoped tokens)

**DO**:
- ✅ Store tokens in GitHub Secrets
- ✅ Store tokens in n8n Credentials
- ✅ Use read-only tokens for verification scripts
- ✅ Rotate tokens every 90 days

### DNS Security Best Practices

**CAA Records** (Certificate Authority Authorization):
```bash
doctl compute domain records create insightpulseai.com \
  --record-type CAA \
  --record-name "@" \
  --record-data "0 issue \"letsencrypt.org\"" \
  --record-ttl 3600
```

**DNSSEC** (Future Enhancement):
```bash
# DigitalOcean supports DNSSEC for additional security
doctl compute domain dnssec enable insightpulseai.com
```

---

## Benefits After Delegation

### ✅ Automation Unlocked

| Use Case | Before | After |
|----------|--------|-------|
| **Create staging DNS** | Manual, 5 minutes | Automated, 2 seconds |
| **Branch previews** | Not possible | `git push` → auto-creates DNS |
| **Compliance audits** | Manual export | `doctl` → CSV export |
| **DNS backup** | Screenshots | `git commit dns.tf` |
| **Multi-environment** | Error-prone | Terraform modules |

### ✅ Cost Savings

- **No DigitalOcean DNS charges**: Free with account
- **No manual labor**: Save ~4 hours/month on DNS management
- **No deployment delays**: Instant DNS changes instead of waiting for UI access

### ✅ Developer Experience

```bash
# Developer workflow (BEFORE delegation):
1. Create branch
2. Deploy to server
3. Log into Squarespace
4. Create DNS record manually
5. Wait for propagation
6. Test deployment
Total: ~20 minutes

# Developer workflow (AFTER delegation):
1. git push
2. CI auto-creates DNS + deploys
Total: ~2 minutes (18 minute savings per deployment!)
```

---

## References

- **DigitalOcean DNS Documentation**: https://docs.digitalocean.com/products/networking/dns/
- **doctl CLI Reference**: https://docs.digitalocean.com/reference/doctl/reference/compute/domain/
- **Squarespace Nameserver Guide**: https://support.squarespace.com/hc/en-us/articles/360002101888
- **DNS Propagation Checker**: https://dnschecker.org

---

## Related Documentation

- [`docs/infra/DNS_ENHANCEMENT_GUIDE.md`](./DNS_ENHANCEMENT_GUIDE.md) - Current DNS configuration
- [`docs/runbooks/digitalocean.md`](../runbooks/digitalocean.md) - DigitalOcean operations
- [`scripts/dns/README.md`](../../scripts/dns/README.md) - DNS automation scripts

---

**Status**: Ready for Implementation  
**Approval Required**: Yes (one-time Squarespace UI change)  
**Estimated Time**: 30 minutes (setup) + 2-6 hours (propagation)  
**Risk Level**: Low (reversible within 24 hours)
