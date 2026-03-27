# InsightPulseAI Documentation

> Navigation index for the documentation surface. See [architecture/README.md](architecture/README.md) for the 18-topic architecture directory.

## Architecture

| Topic | Path | Description |
|-------|------|-------------|
| Index | [architecture/](architecture/) | Full directory index with 18 topic subdirectories |
| Target state | [architecture/target-state/](architecture/target-state/) | Platform, Azure, org, finance target architectures |
| Agents | [architecture/agents/](architecture/agents/) | Copilot, factory, benchmarks, skills |
| Azure | [architecture/azure/](architecture/azure/) | DevOps, pipelines, service mapping, BOM |
| Odoo | [architecture/odoo/](architecture/odoo/) | Runtime, upstream, copilot modules, OAuth |
| Data | [architecture/data/](architecture/data/) | Medallion, Databricks, ETL, schema governance |
| Connectors | [architecture/connectors/](architecture/connectors/) | Onboarding standard (3-mode) and modes reference |
| Identity | [architecture/identity/](architecture/identity/) | Entra, secrets, governance |
| Integration | [architecture/integration/](architecture/integration/) | n8n, A2A, MCP, cloud, FAL |
| Security | [architecture/security/](architecture/security/) | Runtime authority, retrieval policy |
| SaaS | [architecture/saas/](architecture/saas/) | Tenancy, billing, multitenancy, offerings |
| Operations | [architecture/operations/](architecture/operations/) | Reliability, DevSecOps, release, delivery |
| Governance | [architecture/governance/](architecture/governance/) | Repo boundaries, org topology, file taxonomy |
| Tax | [architecture/tax/](architecture/tax/) | BIR compliance, TaxPulse migration |
| AI | [architecture/ai/](architecture/ai/) | Foundry, document intelligence, landing zone |
| Marketing | [architecture/marketing/](architecture/marketing/) | Agency stack, analytics, creative provider |
| ADRs | [architecture/adr/](architecture/adr/) | Architecture Decision Records |
| Docs platform | [architecture/docs-platform/](architecture/docs-platform/) | Documentation platform architecture |
| W9 Studio | [architecture/w9-studio/](architecture/w9-studio/) | W9 Studio project (Wix, website) |

## Governance & Contracts

- [Governance policies](governance/) — Agent policies, naming, branding
- [Contracts](contracts/) — Cross-boundary authority contracts (DNS, email, SSOT)
- [Skills](skills/) — Agent skill packs (iOS wrapper, Odoo copilot)

## Operations

- [Runbooks](runbooks/) — Operational procedures and incident response
- [Audits](audits/) — Security, compliance, and documentation audits
- [Evidence](evidence/) — Deployment and verification evidence packs

## Specifications

- [Spec bundles](../spec/) — Feature specification kits (76 bundles)
- [Templates](../templates/) — Spec kit templates (agent, connector-onboarding)

## SSOT

- [SSOT registry](../ssot/) — Machine-readable intended state (platform, ERP)
- [Infra SSOT](../infra/ssot/) — Infrastructure intended state (Azure, DNS)

## CI/CD

- [Docs pipeline](azure-pipelines.yml) — Azure DevOps validation and publish pipeline
- Validates: internal links, spec bundles, terminology, architecture structure
