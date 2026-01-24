# Repository Map

## Primary Repositories

| Repo | Purpose | Key Paths |
|------|---------|-----------|
| `odoo-ce` | Odoo CE + OCA + IPAI modules | `addons/ipai/`, `spec/`, `mcp/` |
| `pulser-agent-framework` | Agent runtime + memory | `packages/`, `apps/` |
| `pulser-mcp` | MCP surfaces + tool routers | `servers/`, `coordinator/` |
| `.github` | Org-wide workflows + templates | `workflows/`, `ISSUE_TEMPLATE/` |

## odoo-ce Structure

```
odoo-ce/
├── addons/ipai/              # 80+ IPAI custom modules
├── apps/                     # 20 applications
├── packages/                 # Shared packages
├── spec/                     # 32 feature spec bundles
├── mcp/servers/              # MCP server implementations
├── supabase/                 # Migrations + Edge Functions
├── n8n/workflows/            # Automation workflows
├── scripts/                  # 160+ automation scripts
└── memory/packs/             # LLM context packs
```

## Module Naming (OCA-style)

| Domain | Prefix | Examples |
|--------|--------|----------|
| AI | `ipai_ai_*` | `ipai_ai_agents`, `ipai_ai_core` |
| Finance | `ipai_finance_*` | `ipai_finance_ppm`, `ipai_finance_bir_compliance` |
| Platform | `ipai_platform_*` | `ipai_platform_workflow`, `ipai_platform_audit` |
| Workspace | `ipai_workspace_*` | `ipai_workspace_core` |

## Key Integration Points

- **Supabase**: Control plane, ops memory, webhook handling
- **n8n**: Workflow automation, event routing
- **Mattermost**: ChatOps, notifications
- **GitHub Actions**: CI/CD, deployment gates
