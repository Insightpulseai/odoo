# DNS Automation Scripts

**Purpose**: CLI-based DNS management for `insightpulseai.com` using DigitalOcean.

**Prerequisites**: 
- DNS delegation to DigitalOcean nameservers (see `docs/infra/DNS_DELEGATION_SQUARESPACE_TO_DO.md`)
- `doctl` CLI installed and authenticated
- Environment variable: `DIGITALOCEAN_ACCESS_TOKEN`

---

## Scripts Overview

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup-do-domain.sh` | Initial domain creation in DigitalOcean | One-time setup |
| `migrate-dns-to-do.sh` | Migrate existing records from Squarespace | One-time migration |
| `verify-do-dns.sh` | Verify DNS records in DigitalOcean | Regular verification |
| `verify-delegation-complete.sh` | Check nameserver delegation status | Post-delegation check |
| `create-preview-dns.sh` | Create branch preview DNS records | CI/CD automation |
| `cleanup-preview-dns.sh` | Remove old preview DNS records | Cleanup automation |
| `export-dns-to-terraform.sh` | Export DNS to Terraform format | IaC generation |
| `backup-dns-config.sh` | Backup current DNS configuration | Regular backups |

---

## Quick Start

### 1. Initial Setup

```bash
# Set your DigitalOcean token
export DIGITALOCEAN_ACCESS_TOKEN="dop_v1_xxxxx"

# Verify doctl authentication
doctl account get

# Create domain in DigitalOcean
./scripts/dns/setup-do-domain.sh
```

### 2. Migrate Existing Records

```bash
# Export current Squarespace DNS (manual - save to docs/evidence/)
# Then recreate in DigitalOcean:
./scripts/dns/migrate-dns-to-do.sh
```

### 3. Delegate Nameservers

**Manual step in Squarespace UI:**
- Set nameservers to: `ns1.digitalocean.com`, `ns2.digitalocean.com`, `ns3.digitalocean.com`
- See: `docs/infra/DNS_DELEGATION_SQUARESPACE_TO_DO.md`

### 4. Verify Delegation

```bash
# Wait 2-6 hours, then:
./scripts/dns/verify-delegation-complete.sh
```

---

## Usage Examples

### Add Production Record

```bash
# Add A record for new service
doctl compute domain records create insightpulseai.com \
  --record-type A \
  --record-name api \
  --record-data 178.128.112.214 \
  --record-ttl 3600
```

### Create Staging Environment

```bash
# Create preview for branch 'feature/new-ui'
./scripts/dns/create-preview-dns.sh feature/new-ui

# Result: feat-new-ui.insightpulseai.com → 178.128.112.214
```

### List All Records

```bash
doctl compute domain records list insightpulseai.com
```

### Update Existing Record

```bash
# Get record ID
doctl compute domain records list insightpulseai.com | grep staging

# Update by ID
doctl compute domain records update insightpulseai.com \
  --record-id 123456789 \
  --record-data "new-ip-address"
```

### Delete Record

```bash
doctl compute domain records delete insightpulseai.com \
  --record-id 123456789
```

---

## Automation Patterns

### GitHub Actions

```yaml
# .github/workflows/dns-preview.yml
- name: Create Preview DNS
  run: ./scripts/dns/create-preview-dns.sh "${{ github.head_ref }}"
  env:
    DIGITALOCEAN_ACCESS_TOKEN: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
```

### n8n Workflow

```javascript
// HTTP Request node to DigitalOcean API
{
  "url": "https://api.digitalocean.com/v2/domains/insightpulseai.com/records",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer {{ $env.DIGITALOCEAN_ACCESS_TOKEN }}"
  },
  "body": {
    "type": "A",
    "name": "preview-{{ $json.branch }}",
    "data": "178.128.112.214",
    "ttl": 3600
  }
}
```

### Terraform

```hcl
# infra/terraform/dns.tf
resource "digitalocean_record" "app" {
  domain = "insightpulseai.com"
  type   = "A"
  name   = "app"
  value  = var.droplet_ip
  ttl    = 3600
}
```

---

## Troubleshooting

### doctl Not Authenticated

```bash
# Initialize doctl
doctl auth init

# Or use token directly
export DIGITALOCEAN_ACCESS_TOKEN="dop_v1_xxxxx"
doctl account get
```

### DNS Not Propagating

```bash
# Check nameservers
dig insightpulseai.com NS +short

# If still showing Squarespace, wait 2-6 hours
# DNS propagation is gradual and can't be forced
```

### Record Already Exists

```bash
# List existing records
doctl compute domain records list insightpulseai.com

# Delete old record first
doctl compute domain records delete insightpulseai.com --record-id OLD_ID

# Then create new record
doctl compute domain records create insightpulseai.com ...
```

---

## Best Practices

### Security

✅ **DO**:
- Store `DIGITALOCEAN_ACCESS_TOKEN` in GitHub Secrets / n8n Credentials
- Use scoped tokens (read/write only what's needed)
- Rotate tokens every 90 days

❌ **DON'T**:
- Commit tokens to git
- Share tokens via Slack/email
- Use account-level tokens if scoped tokens work

### Reliability

✅ **DO**:
- Set reasonable TTL values (3600 = 1 hour is good default)
- Back up DNS configuration before major changes
- Test in staging before applying to production records

❌ **DON'T**:
- Set TTL too low (<300 seconds) - causes excessive DNS queries
- Delete records without backup
- Make DNS changes without verification script

### Automation

✅ **DO**:
- Use scripts for common operations
- Version control DNS via Terraform
- Add DNS changes to deployment workflows

❌ **DON'T**:
- Manually create DNS records if script exists
- Skip verification after automated changes
- Run cleanup scripts without dry-run first

---

## References

- **Main Documentation**: `docs/infra/DNS_DELEGATION_SQUARESPACE_TO_DO.md`
- **DigitalOcean API Docs**: https://docs.digitalocean.com/reference/api/api-reference/#tag/Domains
- **doctl Reference**: https://docs.digitalocean.com/reference/doctl/reference/compute/domain/

---

**Last Updated**: 2026-02-04  
**Maintained By**: Infrastructure Team
