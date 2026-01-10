# Installation Guide

## Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Node.js 18+ (for tooling)
- Git

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/jgtolentino/odoo-ce.git
cd odoo-ce
```

### 2. Start Stack

```bash
# Start core services
docker compose up -d

# Wait for PostgreSQL to be ready
docker compose logs -f postgres

# Initialize modules
docker compose --profile ce-init up
docker compose --profile init up
```

### 3. Access Odoo

- **Core**: http://localhost:8069
- **Marketing**: http://localhost:8070
- **Accounting**: http://localhost:8071

Default credentials: `admin` / `admin`

## Module Installation

### IPAI Modules

```bash
# Deploy IPAI modules
./scripts/deploy-odoo-modules.sh

# Or manually via Odoo
# 1. Go to Apps
# 2. Update Apps List
# 3. Search for "ipai"
# 4. Install desired modules
```

### Required Environment Variables

For AI Agents (`ipai_ai_agents`):

```bash
# Required
IPAI_LLM_API_KEY=sk-...

# Supabase (for RAG)
IPAI_SUPABASE_URL=https://<project>.supabase.co
IPAI_SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Optional
IPAI_LLM_BASE_URL=https://api.openai.com/v1
IPAI_LLM_MODEL=gpt-4o-mini
```

### Install Order

For best results, install modules in this order:

1. `ipai_dev_studio_base` (base dependencies)
2. `ipai_workspace_core` (core workspace)
3. `ipai_ai_agents` (AI functionality)
4. `ipai_approvals` (approval workflows)
5. Other IPAI modules as needed

## Tooling Setup

### ipai_module_gen

```bash
cd tools/ipai_module_gen
pip install -e .

# Generate modules from capability map
ipai-gen --spec spec/ipai-odoo18-enterprise-patch/capability_map.yaml
```

### diagramflow

```bash
cd tools/diagramflow
pip install -e .

# Convert Mermaid to BPMN/draw.io
diagramflow docs/diagrams/example.mmd
```

## Development Setup

### Local Python

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Node.js Workspaces

```bash
# Install with pnpm
pnpm install

# Run development server
npm run dev:runner
```

## Troubleshooting

### Module Not Found

```bash
# Ensure module is in addons path
docker compose exec odoo-core ls /mnt/extra-addons/ipai/

# Update module list
docker compose exec odoo-core odoo -d odoo_core -u base
```

### Database Issues

```bash
# Check PostgreSQL status
docker compose ps postgres
docker compose logs postgres

# Connect directly
docker compose exec postgres psql -U odoo -d odoo_core
```

### Permission Errors

```bash
# Fix addon permissions
chmod -R 755 addons/ipai/
```

## Next Steps

1. [Configure AI Agents](Configuration#ai-agents)
2. [Set up Approval Types](Configuration#approvals)
3. [Explore Capabilities](Home#capabilities)
