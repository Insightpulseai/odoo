# fin-workspace Setup Guide

## Quick Start

### 1. Export DigitalOcean State
```bash
cd ~/
./infra/doctl/export_state.sh
```

This creates:
- `inventory/runs/YYYYMMDDTHHMMSSZ/` (timestamped snapshot)
- `inventory/latest/` (symlink to most recent)

### 2. Bootstrap App Specs
```bash
./scripts/bootstrap_apps_from_inventory.sh
```

This creates normalized specs for each DO app:
- `apps/<slug>/do/app.json` (raw DO spec)
- `apps/<slug>/spec.yaml` (normalized metadata)
- `apps/<slug>/APP.md` (human-readable summary)

### 3. Create Conversation Entry (Optional)
```bash
./scripts/new_conversation_entry.sh "DOLE submission checklist" "2025-12-22"
```

This creates:
- Auto-incremented entry: `docs/ops/conversations/001 — 2025-12-22 — DOLE submission checklist.md`
- Updates `INDEX.md` and `index.json`

## Files Created

### Core Documentation
- `docs/NAMING_CONVENTION_EQ_APP_TOOLS.md` - Naming standards
- `docs/MONOREPO_STRUCTURE.md` - Repository structure
- `docs/ops/CONVERSATIONS_README.md` - Conversation indexing guide
- `docs/FIN_WORKSPACE_SETUP.md` - This file

### Scripts
- `infra/doctl/export_state.sh` - DO inventory export
- `scripts/bootstrap_apps_from_inventory.sh` - App spec generator
- `scripts/new_conversation_entry.sh` - Conversation entry creator

### Data Files
- `docs/ops/conversations/INDEX.md` - Human-readable conversation index
- `docs/ops/conversations/index.json` - Machine-readable conversation index

## Naming Convention Summary

### Pattern
`{platform}.{product}.{component}.{env}.{region}.{purpose}`

### Products
- core, erp, ocr, mcp, superset, agents, orchestration

### Environments
- dev | stg | prod

### Regions
- sgp1 | blr1 | fra1

### Examples
**DO Apps:**
- fin-erp-odoo-saas-prod
- fin-ocr-ocr-service-prod
- fin-mcp-coordinator-prod
- fin-analytics-superset-prod

**DO Agents:**
- fin-agents-agt-kubernetes-genius-prod
- fin-agents-agt-agent-prod

**Droplets:**
- fin-erp-dro-odoo-prod-sgp1
- fin-ocr-dro-ocr-prod-sgp1

**Domains:**
- erp.insightpulseai.com
- superset.insightpulseai.com
- mcp.insightpulseai.com
- ocr.insightpulseai.com
- agents.insightpulseai.com

## Next Steps

1. **Initial Export**
   ```bash
   ./infra/doctl/export_state.sh
   ls -la inventory/latest/
   ```

2. **Bootstrap Apps**
   ```bash
   ./scripts/bootstrap_apps_from_inventory.sh
   ls -la apps/
   ```

3. **Create First Conversation Entry**
   ```bash
   ./scripts/new_conversation_entry.sh "Initial fin-workspace setup" "$(date +%Y-%m-%d)"
   ```

4. **Commit Changes**
   ```bash
   git add docs/ infra/ scripts/ apps/
   git commit -m "chore(fin-workspace): add Equivalent APP TOOLS naming + DO inventory tooling + conversation index"
   ```

## Maintenance

### Weekly Operations
```bash
# Re-export DO state
./infra/doctl/export_state.sh

# Re-bootstrap if apps changed
./scripts/bootstrap_apps_from_inventory.sh
```

### Per-Change Operations
```bash
# Document significant changes
./scripts/new_conversation_entry.sh "title" "$(date +%Y-%m-%d)"
```

## Verification

### Check Scripts Are Executable
```bash
ls -la infra/doctl/export_state.sh
ls -la scripts/bootstrap_apps_from_inventory.sh
ls -la scripts/new_conversation_entry.sh
```

All should show `-rwx--x--x` or similar execute permissions.

### Check Directory Structure
```bash
tree -L 2 docs/ infra/ scripts/
```

Expected output:
```
docs/
├── ops/
│   ├── conversations/
│   └── CONVERSATIONS_README.md
├── NAMING_CONVENTION_EQ_APP_TOOLS.md
├── MONOREPO_STRUCTURE.md
└── FIN_WORKSPACE_SETUP.md

infra/
└── doctl/
    └── export_state.sh

scripts/
├── bootstrap_apps_from_inventory.sh
└── new_conversation_entry.sh
```

## Troubleshooting

### "doctl not authenticated"
```bash
doctl auth init
```

### "missing jq"
```bash
brew install jq
```

### "permission denied"
```bash
chmod +x infra/doctl/export_state.sh
chmod +x scripts/bootstrap_apps_from_inventory.sh
chmod +x scripts/new_conversation_entry.sh
```

### "inventory/latest not found"
Run the export script first:
```bash
./infra/doctl/export_state.sh
```
