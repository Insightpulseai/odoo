# Directory Structure
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

```
odoo/
├── addons/                    # Odoo modules
│   ├── ipai/                  # IPAI custom modules (43 modules)
│   │   ├── ipai_ai_agent_builder/   # AI agent builder
│   │   ├── ipai_ai_tools/           # AI tool integrations
│   │   ├── ipai_auth_oidc/          # OIDC authentication
│   │   ├── ipai_design_system/      # Design system core
│   │   ├── ipai_enterprise_bridge/  # EE parity bridge
│   │   ├── ipai_finance_ppm/        # Finance PPM
│   │   ├── ipai_helpdesk/           # Helpdesk module
│   │   ├── ipai_hr_payroll_ph/      # PH payroll
│   │   ├── ipai_ops_connector/      # Operations connector
│   │   ├── ipai_sign/               # Digital signatures
│   │   └── ...                      # 33 more modules
│   ├── OCA/                   # OCA community modules (12 repos)
│   └── oca/                   # OCA submodules
│
├── apps/                      # Applications (28 apps)
│   ├── pulser-runner/         # Automation runner
│   ├── control-room/          # Control plane UI
│   ├── control-room-api/      # Control plane API
│   ├── bi-architect/          # BI analytics
│   ├── mcp-coordinator/       # MCP coordination
│   ├── web/                   # Web frontend
│   ├── ai-control-plane/      # AI control plane
│   ├── odoo-developer-agent/  # Odoo dev agent
│   ├── superset-analytics/    # Superset BI integration
│   └── ...                    # 19 more apps
│
├── packages/                  # Shared packages (8 packages)
│   ├── agent-core/            # Core agent framework
│   ├── github-app/            # GitHub App integration
│   ├── ipai-design-tokens/    # Design system tokens
│   ├── agentic-codebase-crawler/ # Codebase analysis
│   ├── config/                # Shared configuration
│   ├── env-config/            # Environment config
│   ├── saas-types/            # SaaS type definitions
│   └── supabase/              # Supabase client
│
├── spec/                      # Spec bundles (62+ feature specs)
│   ├── constitution.md        # Root non-negotiable rules
│   ├── prd.md                 # Root product requirements
│   ├── pulser-master-control/ # Example spec bundle
│   └── ...
│
├── scripts/                   # Automation scripts (550+ files, 43 categories)
│   ├── ci/                    # CI-specific scripts
│   ├── ci_gate/               # CI gate checks
│   ├── audit/                 # Audit scripts
│   ├── backup/                # Backup utilities
│   ├── db/                    # Database management
│   ├── deploy/                # Deployment scripts
│   ├── health/                # Health checks
│   ├── infra-discovery/       # Infrastructure discovery
│   ├── odoo/                  # Odoo-specific scripts
│   ├── parity/                # EE parity validation
│   ├── seeds/                 # Seed data management
│   ├── supabase/              # Supabase utilities
│   └── ...                    # 31 more categories
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
├── infra/                     # Infrastructure templates (26 subdirectories)
│   ├── doctl/                 # DigitalOcean CLI templates
│   ├── superset/              # Apache Superset configs
│   ├── terraform/             # Self-hosted infra IaC
│   └── ...
│
├── db/                        # Database management
│   ├── schema/                # Schema definitions
│   ├── migrations/            # Migration scripts
│   ├── seeds/                 # Seed data
│   └── rls/                   # Row-level security
│
├── docs/                      # Documentation (67+ categories)
│   ├── architecture/
│   ├── data-model/            # DBML, ERD, ORM maps
│   ├── ee_parity_map/         # Enterprise parity tracking
│   ├── evidence/              # Deployment evidence packs
│   ├── infra/                 # Infrastructure docs
│   ├── parity/                # Parity analysis
│   ├── security/              # Security documentation
│   └── ...
│
├── mcp/                       # Model Context Protocol
│   ├── coordinator/           # MCP routing & aggregation
│   └── servers/               # MCP server implementations (11 servers)
│       ├── odoo-erp-server/          # Odoo ERP integration
│       ├── digitalocean-mcp-server/  # DO infrastructure
│       ├── superset-mcp-server/      # BI platform
│       ├── vercel-mcp-server/        # Deployments
│       ├── pulser-mcp-server/        # Agent orchestration
│       ├── speckit-mcp-server/       # Spec enforcement
│       ├── mcp-jobs/                 # Jobs & observability backend
│       ├── agent-coordination-server/ # Agent coordination
│       └── memory-mcp-server/        # Persistent memory
│
├── odoo19/                    # Canonical Odoo 19 setup (recommended)
│   ├── compose.yaml           # Project-specific compose
│   ├── config/                # Version-controlled Odoo config
│   ├── scripts/               # Odoo19-specific scripts
│   └── backups/               # Database backups
│
├── n8n/                       # n8n workflow templates
│
├── .claude/                   # Claude Code configuration
│   ├── project_memory.db      # SQLite config database
│   ├── query_memory.py        # Memory query script
│   ├── settings.json          # Allowed tools config
│   ├── mcp-servers.json       # MCP server configuration
│   └── commands/              # Slash commands
│
├── .github/workflows/         # CI/CD pipelines (153 workflows)
│
├── docker-compose.yml         # Main compose file
├── docker-compose.dev.yml     # Dev overrides
├── docker-compose.shell.yml   # Shell access compose
├── package.json               # Node.js monorepo config
├── turbo.json                 # Turbo CI/CD config
└── oca.lock.json             # OCA module lock
```
