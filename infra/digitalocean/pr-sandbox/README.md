# DigitalOcean PR Sandbox (Ephemeral)

Creates ephemeral DigitalOcean droplets per PR for isolated testing environments.

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    GitHub Actions                          │
├────────────────────────────────────────────────────────────┤
│  PR Open/Sync → do-pr-sandbox.yml → Terraform Apply        │
│  PR Close     → do-pr-sandbox.yml → Terraform Destroy      │
│  Cron (6h)    → do-sandbox-janitor.yml → TTL Cleanup       │
└────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│                   DigitalOcean                             │
├────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │ VPC: pr-{number}-{branch}-vpc                       │   │
│  │   ┌───────────────────────────────────────────────┐ │   │
│  │   │ Droplet: pr-{number}-{branch}-droplet         │ │   │
│  │   │   - Ubuntu 22.04                              │ │   │
│  │   │   - Docker + docker-compose                   │ │   │
│  │   │   - Clone repo at PR branch                   │ │   │
│  │   │   - Start Odoo stack                          │ │   │
│  │   │   - Ports: 22, 80, 443, 8069-8071            │ │   │
│  │   └───────────────────────────────────────────────┘ │   │
│  │   ┌───────────────────────────────────────────────┐ │   │
│  │   │ Firewall: pr-{number}-{branch}-fw             │ │   │
│  │   └───────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

## Usage

### Automatic (PR Lifecycle)

1. **PR Opened/Updated**: Sandbox created automatically when PR touches:
   - `addons/**`
   - `docker-compose.yml`
   - `docker/**`
   - `infra/digitalocean/**`

2. **PR Closed**: Sandbox destroyed automatically.

3. **TTL Expiry**: Janitor workflow runs every 6 hours to clean up droplets older than 24 hours.

### Manual

```bash
# Trigger sandbox creation
gh workflow run do-pr-sandbox.yml -f action=create -f pr_number=123

# Check status
gh workflow run do-pr-sandbox.yml -f action=status

# Destroy sandbox
gh workflow run do-pr-sandbox.yml -f action=destroy -f pr_number=123

# Run janitor (dry run)
gh workflow run do-sandbox-janitor.yml -f dry_run=true
```

### Local Terraform

```bash
cd infra/digitalocean/pr-sandbox

# Export DO token
export DIGITALOCEAN_TOKEN="your_token"

# Initialize
terraform init

# Create sandbox
terraform apply -var="pr_number=123" -var="branch_name=feat/my-feature"

# Get outputs
terraform output

# Destroy
terraform destroy -var="pr_number=123" -var="branch_name=feat/my-feature"
```

## Configuration

### Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `pr_number` | (required) | Pull request number |
| `branch_name` | (required) | Git branch name |
| `repo_name` | `odoo-ce` | Repository name |
| `ttl_hours` | `24` | Auto-destroy after N hours |
| `droplet_size` | `s-2vcpu-4gb` | Droplet size slug |
| `region` | `nyc3` | DigitalOcean region |

### Required Secrets

| Secret | Description |
|--------|-------------|
| `DIGITALOCEAN_TOKEN` | DO API token with droplet/VPC/firewall permissions |

## Outputs

| Output | Description |
|--------|-------------|
| `droplet_id` | Droplet ID for cleanup |
| `droplet_ip` | Public IPv4 address |
| `sandbox_url` | Odoo URL (http://{ip}:8069) |
| `ssh_command` | SSH connection command |
| `ttl_expiry` | Expected TTL expiry time |

## Cost Control

- **TTL**: Default 24 hours, configurable via `ttl_hours`
- **Size**: Small droplet by default (`s-2vcpu-4gb` ~$24/mo)
- **Janitor**: Runs every 6 hours to catch orphans
- **PR Close**: Immediate cleanup on PR close

Estimated cost per sandbox: ~$0.03/hour (24h = ~$0.72)

## Comparison: Vercel Sandbox vs DO Sandbox

| Feature | Vercel Sandbox | DO Sandbox |
|---------|----------------|------------|
| **Best for** | Web/Next.js apps | Full-stack/system tests |
| **Compute** | Ephemeral functions | Full VM (Docker) |
| **Startup** | ~1 second | ~2-3 minutes |
| **Cost** | Usage-based | Hourly ($0.03/h) |
| **Network** | Vercel edge | Public IP + firewall |
| **Use case** | AI code validation | Odoo stack testing |

Use Vercel Sandbox for web-native ephemeral compute; use DO Sandbox for full-stack integration testing.
