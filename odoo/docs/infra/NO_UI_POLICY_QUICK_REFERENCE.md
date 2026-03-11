# No-UI Policy Quick Reference

**Philosophy**: Clicking buttons in a browser is manual labor. Running commands is automation.

**Last Updated**: 2026-02-04

---

## Quick Start

```bash
# 1. Install all CLI tools
make install-cli-tools

# 2. Verify installation
make verify-cli-tools

# 3. See all available commands
make help
```

---

## The CLI Arsenal

| Layer | Tool | Install | Auth | Docs |
|-------|------|---------|------|------|
| **Code/Identity** | `gh` | `brew install gh` | `gh auth login` | [GitHub CLI](https://cli.github.com) |
| **Infrastructure** | `doctl` | `brew install doctl` | `doctl auth init` | [DigitalOcean CLI](https://docs.digitalocean.com/reference/doctl/) |
| **DNS** | `doctl` | Same as above | Same as above | [DNS Guide](./DNS_DELEGATION_SQUARESPACE_TO_DO.md) |
| **Frontend** | `vercel` | `npm i -g vercel` | `vercel login` | [Vercel CLI](https://vercel.com/docs/cli) |
| **Database** | `supabase` | `brew install supabase` | `supabase login` | [Supabase CLI](https://supabase.com/docs/guides/cli) |
| **Containers** | `docker` | [Docker Desktop](https://docker.com) | N/A | [Docker CLI](https://docs.docker.com/engine/reference/commandline/cli/) |

---

## Common Workflows

### DNS Management (No Squarespace UI!)

```bash
# List all DNS records
make dns-list

# Add new DNS record
make dns-add SUB=api IP=178.128.112.214

# Create preview environment
make dns-preview BRANCH=feature/new-ui
# → Creates: preview-feature-new-ui.insightpulseai.com

# Backup DNS configuration
make dns-backup

# Export to Terraform
make dns-export-terraform
```

### GitHub Operations

```bash
# List repositories
make gh-repos

# List open issues
make gh-issues

# Create issue
make gh-issue-create TITLE="Fix bug" BODY="Description here"

# List pull requests
make gh-prs
```

### Infrastructure Management

```bash
# List all DigitalOcean resources
make infra-list

# Export infrastructure state
make infra-export
```

### God Mode (Full Stack Provisioning)

```bash
# Provision complete app in ONE command
make provision-full-app NAME=my-app SUB=api

# Result:
# - DNS: api.insightpulseai.com → 178.128.112.214
# - Ready for deployment
```

---

## DNS Delegation Workflow

**One-Time Setup** (requires Squarespace UI - unavoidable):

```bash
# 1. Setup domain in DigitalOcean
make dns-setup

# 2. Migrate existing records
make dns-migrate

# 3. Show nameserver delegation instructions
make dns-delegate

# 4. (Manual) Log into Squarespace and change nameservers to:
#    - ns1.digitalocean.com
#    - ns2.digitalocean.com
#    - ns3.digitalocean.com

# 5. Wait 2-6 hours for propagation

# 6. Verify delegation is complete
make dns-verify-delegation
```

**After Delegation** (100% CLI):

```bash
# Everything is now CLI-manageable!
make dns-add SUB=staging IP=178.128.112.214
make dns-preview BRANCH=feature/ui
# etc.
```

---

## Google Workspace Bridge

### Strategy Docs → Markdown

```bash
# 1. Stakeholder writes in Google Docs
# 2. Extensions → Docs to Markdown → Convert
# 3. Paste into spec file
vim spec/my-feature/prd.md

# 4. Commit to Git
git add spec/my-feature/prd.md
git commit -m "feat(spec): Add requirements from stakeholder doc"
git push
```

### Quick BI Dashboard

```bash
# 1. Install SQL Connector add-on in Google Sheets
# 2. Connect to Supabase:
#    Host: db.spdtwktxdalcfigzeqrz.supabase.co
#    Database: postgres
#    User: postgres
#    Password: [from .env]

# 3. Run queries:
SELECT product_id, inventory_quantity 
FROM stock_quant 
WHERE inventory_quantity < 10;

# 4. Set auto-refresh: Every 1 hour
```

### Diagrams → Git

```bash
# 1. Create diagram in draw.io
# 2. Export as PNG + XML
# 3. Commit to repo
./scripts/docs/import-diagram.sh diagram.png system-architecture
```

---

## Anti-Patterns (Never Do This)

### ❌ Manual DNS Changes in Squarespace
```
Wrong: Log into Squarespace → DNS Settings → Add record
Right: make dns-add SUB=api IP=178.128.112.214
```

### ❌ Task Management Outside GitHub
```
Wrong: Create tasks in MeisterTask/Trello
Right: gh issue create --title "Fix bug" --body "Description"
```

### ❌ Manual Status Updates in Reports
```
Wrong: Update "Status: Done" in Google Docs manually
Right: Paste GitHub Issue URL → Smart Links auto-updates
```

### ❌ Leaving Specs Only in Google Docs
```
Wrong: Requirements live only in Google Docs
Right: Convert to Markdown → Commit to spec/
```

---

## Automation Patterns

### CI/CD (GitHub Actions)

```yaml
# .github/workflows/deploy-preview.yml
- name: Create Preview DNS
  run: ./scripts/dns/create-preview-dns.sh "${{ github.head_ref }}"
  env:
    DIGITALOCEAN_ACCESS_TOKEN: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
```

### n8n Workflow

```javascript
// Create DNS record via DigitalOcean API
{
  "url": "https://api.digitalocean.com/v2/domains/insightpulseai.com/records",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer {{ $env.DIGITALOCEAN_ACCESS_TOKEN }}"
  },
  "body": {
    "type": "A",
    "name": "preview-{{ $json.branch }}",
    "data": "178.128.112.214"
  }
}
```

### Agent System Prompt

```
You have access to infrastructure management via the `make` command.

If the user asks to:
- Create a DNS record → run: make dns-add SUB=<name> IP=<ip>
- Deploy preview environment → run: make dns-preview BRANCH=<branch>
- Provision new app → run: make provision-full-app NAME=<app> SUB=<sub>

Never suggest manual UI steps. Always provide the CLI command.
```

---

## Environment Variables

Required in `.env`:

```bash
# DigitalOcean
DIGITALOCEAN_ACCESS_TOKEN=dop_v1_xxxxx

# GitHub
GITHUB_TOKEN=ghp_xxxxx

# Vercel
VERCEL_TOKEN=xxxxx

# Supabase
SUPABASE_ACCESS_TOKEN=sbp_xxxxx

# Droplet IP (for DNS automation)
DO_DROPLET_IP=178.128.112.214
```

---

## Troubleshooting

### doctl Not Authenticated
```bash
doctl auth init
# Or: export DIGITALOCEAN_ACCESS_TOKEN=dop_v1_xxxxx
```

### DNS Not Propagating
```bash
# Check nameservers
dig insightpulseai.com NS +short

# If still Squarespace, wait 2-6 hours
# DNS propagation can't be forced
```

### Command Not Found
```bash
# Install missing tools
make install-cli-tools

# Verify everything is installed
make verify-cli-tools
```

---

## Documentation Index

| Topic | Document |
|-------|----------|
| **DNS Delegation** | [DNS_DELEGATION_SQUARESPACE_TO_DO.md](./DNS_DELEGATION_SQUARESPACE_TO_DO.md) |
| **Google Workspace** | [GOOGLE_WORKSPACE_BRIDGE.md](./GOOGLE_WORKSPACE_BRIDGE.md) |
| **DNS Scripts** | [scripts/dns/README.md](../../scripts/dns/README.md) |
| **DNS Enhancement** | [DNS_ENHANCEMENT_GUIDE.md](./DNS_ENHANCEMENT_GUIDE.md) |
| **Overall Philosophy** | [../CLAUDE.md](../../CLAUDE.md) |

---

## Time Savings

| Task | Before (UI) | After (CLI) | Improvement |
|------|-------------|-------------|-------------|
| **Create DNS record** | 5 minutes | 2 seconds | 99.3% faster |
| **Preview environment** | 20 minutes | 10 seconds | 99.2% faster |
| **List all DNS** | 2 minutes | 1 second | 99.2% faster |
| **Provision app** | 30 minutes | 15 seconds | 99.2% faster |
| **Status report** | 15 minutes | Auto-updated | 100% saved |

**Total time saved per week**: ~4 hours (assuming 10 DNS changes + 5 deploys)

---

## Next Steps

1. **Install Tools**: `make install-cli-tools`
2. **Delegate DNS**: Follow [DNS_DELEGATION_SQUARESPACE_TO_DO.md](./DNS_DELEGATION_SQUARESPACE_TO_DO.md)
3. **Configure Google Workspace**: Follow [GOOGLE_WORKSPACE_BRIDGE.md](./GOOGLE_WORKSPACE_BRIDGE.md)
4. **Start Automating**: Use `make` commands for all operations
5. **Train Team**: Share this quick reference

---

**Remember**: Every time you open a UI instead of running a command, you're choosing manual labor over automation.

**Goal**: 100% of infrastructure operations via CLI/API by end of Q1 2026.
