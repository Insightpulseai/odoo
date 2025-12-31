# fin-workspace Monorepo Structure

## Overview
Single monorepo for all DigitalOcean fin-workspace infrastructure, services, and operational documentation.

## Directory Structure

```text
fin-workspace/
├─ apps/                          # DO App Platform normalized specs (generated)
│  ├─ superset-analytics/         # example
│  │  ├─ do/app.json
│  │  ├─ spec.yaml
│  │  └─ APP.md
│  └─ ...
├─ agents/                        # agent runtime + skills + prompts
│  ├─ skills/
│  ├─ profiles/
│  └─ runtime/
├─ services/                      # deployable services (ocr, agent-service, mcp)
│  ├─ ocr-service/
│  ├─ agent-service/
│  └─ mcp-coordinator/
├─ infra/
│  ├─ doctl/                      # export scripts + snapshots
│  ├─ nginx/                      # reverse proxy configs by host
│  └─ terraform/                  # optional IaC later
├─ inventory/                     # DO snapshots (runs/ + latest symlink)
│  ├─ runs/
│  │  └─ YYYYMMDDTHHMMSSZ/        # timestamped exports
│  │     ├─ apps.list.json
│  │     ├─ apps.<id>.json
│  │     ├─ agents.list.json
│  │     ├─ droplets.list.json
│  │     ├─ domains.list.json
│  │     ├─ domain_records.<domain>.json
│  │     └─ firewalls.list.json
│  └─ latest -> runs/YYYYMMDDTHHMMSSZ/
├─ docs/
│  ├─ ops/
│  │  ├─ conversations/           # conversation index (NNN — YYYY-MM-DD — title.md)
│  │  │  ├─ INDEX.md
│  │  │  ├─ index.json
│  │  │  └─ *.md
│  │  └─ CONVERSATIONS_README.md
│  ├─ NAMING_CONVENTION_EQ_APP_TOOLS.md
│  └─ MONOREPO_STRUCTURE.md (this file)
├─ scripts/
│  ├─ bootstrap_apps_from_inventory.sh
│  └─ new_conversation_entry.sh
└─ .github/workflows/
```

## Key Scripts

### Export DigitalOcean State
```bash
./infra/doctl/export_state.sh
```
- Exports apps, agents, droplets, domains, firewalls
- Creates timestamped snapshot in `inventory/runs/`
- Updates `inventory/latest` symlink

### Bootstrap App Specs
```bash
./scripts/bootstrap_apps_from_inventory.sh
```
- Generates normalized app specs from inventory
- Creates `apps/<slug>/` directories
- Produces `spec.yaml`, `APP.md`, `do/app.json`

### Create Conversation Entry
```bash
./scripts/new_conversation_entry.sh "title" "YYYY-MM-DD"
```
- Auto-increments conversation number (NNN)
- Updates INDEX.md and index.json
- Creates template with frontmatter

## Workflow

1. **Initial Setup**
   ```bash
   ./infra/doctl/export_state.sh
   ./scripts/bootstrap_apps_from_inventory.sh
   ```

2. **Regular Operations**
   - Create conversation entries as needed
   - Re-export DO state weekly or after major changes
   - Re-bootstrap apps when DO inventory changes

3. **Naming Compliance**
   - Follow Equivalent APP TOOLS convention (see `NAMING_CONVENTION_EQ_APP_TOOLS.md`)
   - Use fin-{product}-{component}-{env} pattern
   - Maintain deterministic naming across all resources

## Next Steps

- [ ] Run initial DO export
- [ ] Bootstrap app specs
- [ ] Create agents/ structure
- [ ] Create services/ structure
- [ ] Add Terraform/IaC templates
- [ ] Setup CI/CD workflows
