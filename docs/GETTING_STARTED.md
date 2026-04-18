# Getting Started — InsightPulse AI

> New developer onboarding index. Follow these steps in order.

---

## Step 1: Understand the Architecture

Read the [canonical platform architecture](architecture/canonical-platform-architecture.md) to understand the three-plane model:

| Plane | Components |
|-------|-----------|
| **Transaction** | Odoo CE 18 + PostgreSQL on Azure Container Apps |
| **Intelligence** | Databricks + Unity Catalog + Azure AI Foundry |
| **Analytics** | Power BI + Fabric (optional) + ADLS |

Key rules: Azure-native only. No Supabase, n8n, Cloudflare, Vercel, or DigitalOcean.

---

## Step 2: Set Up Your Dev Container

Follow the [Dev Container Guide](development/DEV_CONTAINER_GUIDE.md).

### Docker Context Prerequisite

The devcontainer requires a specific Docker context. Choose your runtime:

**Option A: Colima (recommended for macOS)**
```bash
# Install Colima
brew install colima

# Create and start the odoo context
colima start --profile odoo --cpu 4 --memory 8
docker context create colima-odoo --docker "host=unix://$HOME/.colima/odoo/docker.sock"
docker context use colima-odoo
```

**Option B: Docker Desktop**

If you use Docker Desktop and don't want Colima, edit `.devcontainer/devcontainer.json` and remove the `initializeCommand` line. Docker Desktop's default context works without additional setup.

### Verify
```bash
docker context show          # Should show colima-odoo (or default)
code .                       # Open VS Code
# Cmd+Shift+P → "Dev Containers: Reopen in Container"
```

---

## Step 3: Configure Credentials

Follow the [Credential Guide](setup/CREDENTIAL_GUIDE.md) for the secret inventory.

Key secrets (all via Azure Key Vault `kv-ipai-dev-sea`):
- **PostgreSQL**: `PGHOST`, `PGUSER`, `PGPASSWORD`
- **Azure AI**: `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`
- **Zoho SMTP**: `zoho-smtp-user`, `zoho-smtp-password`
- **Doc Intelligence**: `DOC_INTEL_ENDPOINT`

For local dev, copy the env template:
```bash
cp .devcontainer/devcontainer.env.example .devcontainer/devcontainer.env
```

---

## Step 4: Azure AI Foundry Setup

Follow the [Foundry Onboarding Guide](research/foundry-onboarding-guide.md) for:
- `az login` and `azd auth login`
- macOS PATH fix for Apple Silicon
- `DefaultAzureCredential` auth flow
- Model deployment via VS Code extension

---

## Step 5: Pre-Commit Gates

Before every commit, run the three verification scripts:
```bash
./scripts/repo_health.sh     # Repo structure + secrets check
./scripts/spec_validate.sh   # Spec bundle completeness
./scripts/ci_local.sh        # Full local CI gate
```

---

## Step 6: Know Your Workflows

| Command | Purpose |
|---------|---------|
| `docker compose up -d` | Start Odoo + PostgreSQL + Redis |
| `docker compose --profile tools up -d` | Add pgAdmin + Mailpit |
| `docker compose logs -f odoo` | Tail Odoo logs |
| `docker compose exec odoo odoo shell -d odoo_dev` | Odoo Python REPL |

### Claude Code Workflows
| Command | Purpose |
|---------|---------|
| `/project:plan` | Create implementation plan |
| `/project:implement` | Execute plan |
| `/project:verify` | Run verification checks |
| `/project:ship` | Full workflow end-to-end |

---

## Key References

| Doc | Purpose |
|-----|---------|
| [CLAUDE.md](../CLAUDE.md) | Repo-level operating contract |
| [Architecture](architecture/canonical-platform-architecture.md) | Platform architecture (locked) |
| [Azure BOM](architecture/azure-bom-target-state.md) | Target Azure resource map |
| [Azure Inventory](architecture/azure-resource-inventory.md) | Live 63-resource estate |
| [Identity Architecture](architecture/identity-architecture.md) | Entra ID + managed identity |
| [Dev Container Guide](development/DEV_CONTAINER_GUIDE.md) | Local development setup |
| [Credential Guide](setup/CREDENTIAL_GUIDE.md) | Secret inventory |
| [Foundry Onboarding](research/foundry-onboarding-guide.md) | AI Foundry setup |

---

## Common Issues

| Problem | Fix |
|---------|-----|
| `Expected docker context colima-odoo` | See Step 2 above — create the context or remove `initializeCommand` |
| `psql: connection refused` | Wait for `db` service health check; run `docker compose ps` |
| `az login` fails in VS Code | Grant Full Disk Access to VS Code + terminal |
| Port 8069 in use | `lsof -i :8069` to find conflict; change port in `devcontainer.env` |

---

*Last updated: 2026-04-18*
