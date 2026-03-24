# InsightPulse AI

Umbrella monorepo for the InsightPulse AI platform: Odoo CE 19 ERP, agent platform, data intelligence, automation workflows, and web surfaces -- all running on Azure.

## Quick Start

```bash
git clone https://github.com/Insightpulseai/odoo.git && cd odoo
docker compose up -d
# Odoo at http://localhost:8069 (database: odoo_dev)
```

Production: [erp.insightpulseai.com](https://erp.insightpulseai.com)

## Repo Map

| Directory | Purpose |
|-----------|---------|
| `addons/ipai/` | Custom IPAI Odoo modules (integration bridges) |
| `agents/` | Agent personas, skills, knowledge bases, workflows |
| `agent-platform/` | Agent runtime and orchestration engine |
| `automations/` | n8n workflow definitions |
| `design/` | Shared design tokens and assets |
| `docs/` | Architecture, runbooks, evidence, guides |
| `infra/` | Azure IaC, DNS, Databricks bundles |
| `odoo/` | Odoo runtime sub-tree (config, Docker, deployment) |
| `spec/` | Spec bundles (constitution, PRD, plan, tasks per feature) |
| `ssot/` | Intended-state truth files for platform and ERP |
| `web/` | Web surfaces and public-facing apps |

Ownership boundaries: [`ssot/repo/ownership-boundaries.yaml`](ssot/repo/ownership-boundaries.yaml)

## Architecture

Odoo CE 19 is the transactional system of record. Databricks + Unity Catalog is the governed analytics plane. Azure AI Foundry hosts agent applications. Azure Container Apps (behind Azure Front Door) is the runtime surface. Cloudflare provides DNS; Zoho handles outbound mail.

Details: [`docs/architecture/UNIFIED_TARGET_ARCHITECTURE.md`](docs/architecture/UNIFIED_TARGET_ARCHITECTURE.md) | [`docs/architecture/PLATFORM_TARGET_STATE.md`](docs/architecture/PLATFORM_TARGET_STATE.md)

## Assistant Surfaces

| Surface | Description | Details |
|---------|-------------|---------|
| Odoo Copilot | ERP chat assistant (Odoo systray) | In-app AI for finance, HR, operations |
| Diva | Tax and compliance advisor | BIR/PH tax workflow guidance |
| Studio Agent | Dev/config copilot | Module scaffolding, OCA selection |
| Azure Genie | Cloud ops assistant | Infrastructure and deployment |
| Document AI | OCR and extraction | Invoice, receipt, document processing |

Details: [`docs/architecture/ASSISTANT_SURFACES.md`](docs/architecture/ASSISTANT_SURFACES.md)

## Key Constraints

- **CE + OCA only** -- no Odoo Enterprise modules, no odoo.com IAP
- **Module philosophy**: Config first, then OCA, then custom `ipai_*` bridges
- **Azure-native** -- Container Apps, Front Door, Key Vault, Entra ID (target)
- **Databricks governs analytics** -- Fabric complements but does not replace
- **MCP required** for reusable agent tools; stateless agent design

## Documentation Index

| Topic | Location |
|-------|----------|
| Target architecture | [`docs/architecture/UNIFIED_TARGET_ARCHITECTURE.md`](docs/architecture/UNIFIED_TARGET_ARCHITECTURE.md) |
| Odoo on Azure target state | [`docs/architecture/INSIGHTPULSEAI_ODOO_ON_AZURE_TARGET_STATE.md`](docs/architecture/INSIGHTPULSEAI_ODOO_ON_AZURE_TARGET_STATE.md) |
| Odoo runtime contract | [`docs/architecture/ODOO_RUNTIME.md`](docs/architecture/ODOO_RUNTIME.md) |
| Agent platform | [`docs/architecture/AGENT_PLATFORM.md`](docs/architecture/AGENT_PLATFORM.md) |
| Assistant surfaces | [`docs/architecture/ASSISTANT_SURFACES.md`](docs/architecture/ASSISTANT_SURFACES.md) |
| Data platform | [`docs/architecture/enterprise_data_platform.md`](docs/architecture/enterprise_data_platform.md) |
| Identity and secrets | [`docs/architecture/identity_and_secrets.md`](docs/architecture/identity_and_secrets.md) |
| Go-live checklist | [`docs/architecture/GO_LIVE_CHECKLIST.md`](docs/architecture/GO_LIVE_CHECKLIST.md) |
| Delivery evidence | [`docs/evidence/`](docs/evidence/) |
| Runbooks | [`docs/runbooks/`](docs/runbooks/) |
| AI agent instructions | [`CLAUDE.md`](CLAUDE.md) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, branch conventions, and PR process.

## License

LGPL-3.0 -- see [LICENSE](LICENSE).
