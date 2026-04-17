# InsightPulse AI

Umbrella monorepo for the InsightPulse AI platform: Odoo CE 18 ERP, agent platform, data intelligence, and web surfaces -- all running on Azure.

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
| `automations/` | Azure Logic Apps / Functions workflows |
| `design/` | Shared design tokens and assets |
| `docs/` | Architecture, runbooks, evidence, guides |
| `infra/` | Azure IaC, DNS, Databricks bundles |
| `odoo/` | Odoo runtime sub-tree (config, Docker, deployment) |
| `spec/` | Spec bundles (constitution, PRD, plan, tasks per feature) |
| `ssot/` | Intended-state truth files for platform and ERP |
| `web/` | Web surfaces and public-facing apps |

Ownership boundaries: [`ssot/repo/ownership-boundaries.yaml`](ssot/repo/ownership-boundaries.yaml)

## Architecture

Odoo CE 18 is the transactional system of record. Databricks + Unity Catalog is the governed analytics plane. Microsoft Foundry hosts agent applications. Azure Container Apps (behind Azure Front Door) is the runtime surface. Azure DNS provides authoritative DNS; Zoho handles outbound mail.

Details: [`docs/architecture/target-state/UNIFIED.md`](docs/architecture/target-state/UNIFIED.md) | [`docs/architecture/target-state/PLATFORM.md`](docs/architecture/target-state/PLATFORM.md)

## Status

**Lifecycle:** Reference architecture + accelerator proving, moving into industry solution packaging.

| Surface | URL | Status |
|---------|-----|--------|
| Odoo ERP | erp.insightpulseai.com | ✅ Live (pending DNS) |
| Corporate site | www.insightpulseai.com | ✅ Live (pending DNS) |
| PrismaLab | prismalab.insightpulseai.com | ✅ Live (pending DNS) |
| W9 Studio | www.w9studio.net | ✅ Live (pending DNS) |
| Databricks One | adb-7405608559466577.17.azuredatabricks.net/one | ✅ Gold + 2 Genie spaces |

- Maturity checkpoint: [`docs/architecture/MATURITY_CHECKPOINT.md`](docs/architecture/MATURITY_CHECKPOINT.md)
- Baseline to target state: [`docs/architecture/baseline-to-target-state.md`](docs/architecture/baseline-to-target-state.md)
- Docs index: [`docs/INDEX.md`](docs/INDEX.md)

## Environments

| Environment | GitHub | Azure Pipelines | Azure resources |
|---|---|---|---|
| `ipai-dev` | Branch protection | Auto-deploy on merge | Sponsored sub (eba824fb) |
| `ipai-staging` | Branch protection | 1 approval gate | Same sub (staging RGs) |
| `ipai-prod` | Branch protection | 2 approvals + business hours | Prod sub (when provisioned) |

## Assistant Surfaces

| Surface | Description |
|---------|-------------|
| Pulser | Guided operating assistant (finance, close, compliance) |
| Tax Guru | PH BIR tax compliance specialist |
| Genie (Databricks) | NL analytics over gold marts (2 spaces live) |
| Document Intelligence | Invoice/receipt/form extraction (docai-ipai-dev) |

Details: [`docs/product/surface-blueprint.md`](docs/product/surface-blueprint.md)

## Key Constraints

- **CE + OCA only** -- no Odoo Enterprise modules, no odoo.com IAP
- **Module philosophy**: Config first, then OCA, then custom `ipai_*` bridges
- **Azure-native** -- Container Apps, Front Door, Key Vault, Entra ID (target)
- **Databricks governs analytics** -- Fabric complements but does not replace
- **MCP required** for reusable agent tools; stateless agent design

## Documentation Index

| Topic | Location |
|-------|----------|
| Target architecture | [`docs/architecture/target-state/UNIFIED.md`](docs/architecture/target-state/UNIFIED.md) |
| Odoo on Azure target state | [`docs/architecture/odoo/ON_AZURE_TARGET_STATE.md`](docs/architecture/odoo/ON_AZURE_TARGET_STATE.md) |
| Odoo runtime contract | [`docs/architecture/odoo/RUNTIME.md`](docs/architecture/odoo/RUNTIME.md) |
| Agent platform | [`docs/architecture/agents/PLATFORM.md`](docs/architecture/agents/PLATFORM.md) |
| Assistant surfaces | [`docs/architecture/agents/ASSISTANT_SURFACES.md`](docs/architecture/agents/ASSISTANT_SURFACES.md) |
| Data platform | [`docs/architecture/data/ENTERPRISE_DATA_PLATFORM.md`](docs/architecture/data/ENTERPRISE_DATA_PLATFORM.md) |
| Identity and secrets | [`docs/architecture/identity/IDENTITY_AND_SECRETS.md`](docs/architecture/identity/IDENTITY_AND_SECRETS.md) |
| Go-live checklist | [`docs/architecture/GO_LIVE_CHECKLIST.md`](docs/architecture/GO_LIVE_CHECKLIST.md) |
| Delivery evidence | [`docs/evidence/`](docs/evidence/) |
| Runbooks | [`docs/runbooks/`](docs/runbooks/) |
| AI agent instructions | [`CLAUDE.md`](CLAUDE.md) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, branch conventions, and PR process.

## License

LGPL-3.0 -- see [LICENSE](LICENSE).
