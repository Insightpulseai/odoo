# Repo Topology — Directory Structure & Inventory

> Full directory map, app inventory, and package list for the InsightPulse AI monorepo.

---

## Directory Structure

```
odoo-ce/
├── addons/                    # Odoo modules
│   ├── ipai/                  # IPAI custom modules (69 verified)
│   │   ├── ipai_workspace_core/
│   │   ├── ipai_finance_ppm/
│   │   ├── ipai_ai_core/
│   │   ├── ipai_enterprise_bridge/
│   │   ├── ipai_helpdesk/
│   │   └── ... (69 modules total)
│   ├── ipai_*/                # 41 additional ipai modules at addons/ root (legacy location)
│   ├── OCA/                   # OCA vendor directory (legacy refs)
│   └── oca/                   # OCA modules (hydrated at runtime via gitaggregate, not tracked)
│
├── apps/                      # Applications (9 verified; 2 substantial)
│   ├── ops-console/           # Operations console (substantial)
│   ├── mcp-jobs/              # MCP jobs system (substantial)
│   ├── colima-desktop-ui/     # Desktop UI (minimal)
│   ├── odoo-mobile-ios/       # Mobile app
│   ├── platform/              # Platform app
│   ├── slack-agent/           # Slack agent
│   ├── web/                   # Web frontend (stub)
│   ├── workspace/             # Workspace app
│   └── docs/                  # Docs app
│
├── packages/                  # Shared packages (2 packages)
│   ├── agents/                # Agent framework
│   └── taskbus/               # Task bus system
│
├── spec/                      # Spec bundles (76 total)
│   ├── constitution.md        # Root non-negotiable rules
│   ├── prd.md                 # Root product requirements
│   ├── pulser-master-control/ # Example spec bundle
│   └── ...
│
├── scripts/                   # Automation scripts (1000 files in 86 categories)
│   ├── ci/                    # CI-specific scripts
│   ├── deploy-odoo-modules.sh
│   ├── repo_health.sh
│   ├── spec_validate.sh
│   └── ...
│
├── docker/                    # Docker configurations
│   ├── Dockerfile.seeded
│   ├── Dockerfile.unified
│   └── nginx/
│
├── deploy/                    # Deployment configurations
│   ├── docker-compose.yml     # Production compose
│   └── nginx/
│
├── infra/                     # Infrastructure templates (self-hosted)
│   ├── doctl/                 # DigitalOcean CLI templates
│   ├── superset/              # Apache Superset configs
│   └── terraform/             # Self-hosted infra IaC
│
├── db/                        # Database management
│   ├── schema/                # Schema definitions
│   ├── migrations/            # Migration scripts
│   ├── seeds/                 # Seed data
│   └── rls/                   # Row-level security
│
├── docs/                      # Documentation
│   ├── architecture/
│   ├── data-model/            # DBML, ERD, ORM maps
│   └── ...
│
├── mcp/                       # Model Context Protocol
│   └── servers/               # MCP server implementations
│       └── plane/             # Plane.so integration (1 server — only one implemented)
│
├── odoo19/                    # Canonical Odoo 19 setup (config, scripts, backups)
│
├── .claude/                   # Claude Code configuration
│   ├── project_memory.db      # SQLite config database
│   ├── query_memory.py        # Memory query script
│   ├── settings.json          # Allowed tools config
│   ├── mcp-servers.legacy.json # Legacy MCP catalog (transitional reference)
│   └── commands/              # Slash commands
│
├── .github/workflows/         # CI/CD pipelines (355 workflows)
│
├── docker-compose.yml         # Main compose file
├── package.json               # Node.js monorepo config
├── turbo.json                 # Turbo CI/CD config
└── oca.lock.json             # OCA module lock
```

---

## External Memory (Just-in-Time Retrieval)

Project configuration is stored in SQLite to reduce context usage:

```bash
python .claude/query_memory.py config       # Supabase/DB config
python .claude/query_memory.py arch         # Architecture components
python .claude/query_memory.py commands     # All commands
python .claude/query_memory.py rules        # Project rules
python .claude/query_memory.py deprecated   # Deprecated items
python .claude/query_memory.py all          # Everything
```

---

*Last updated: 2026-03-16*
