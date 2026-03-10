# ERP Positioning Policy

**Canonical Name**: Odoo CE 19 (Community Edition)
**Hosting**: Self-hosted on DigitalOcean (178.128.112.214)
**Database**: PostgreSQL 16 (local to the droplet, NOT Supabase)

## Prohibited Terms

| Term | Why Prohibited |
|------|---------------|
| Odoo SaaS | We do not use Odoo's SaaS offering; we self-host |
| Odoo.sh | We do not use Odoo's PaaS; we build equivalent features ourselves |
| Odoo Enterprise | We do not license EE; we achieve parity via CE + OCA + ipai_* |
| Odoo Online | We do not use Odoo's managed hosting |
| odoo.com IAP | We do not consume Odoo's paid in-app services |

## Permitted Usage

- **EE Parity comparisons**: "Replaces Odoo Enterprise feature X" is allowed
- **Prohibition statements**: "No Odoo Enterprise modules" is allowed
- **Feature parity tables**: Referencing EE/Odoo.sh features we are replacing is allowed
- **Upstream Odoo documentation** (`docs/kb/odoo19/upstream/`): unmodified reference material

## SAP-Grade Operational Maturity

"SAP-grade Azure maturity" is an operational posture target, not feature parity with SAP:

| SAP-Like Capability | Our Implementation |
|---------------------|-------------------|
| IaC-defined landing zone | Bicep + Terraform (`infra/azure/`, `infra/terraform/`) |
| Governed runtime | Unity Catalog + RBAC (`ssot/databricks/workspace.yaml`) |
| Enterprise identity | Entra ID + Supabase Auth (`ctrl.identity_map`) |
| Release evidence | Evidence bundles (`docs/evidence/YYYYMMDD-HHMM/`) |
| Formal contracts | Spec bundles + SSOT YAML (`spec/`, `ssot/`) |
| Integration backbone | n8n + Supabase sync + MCP (`automations/n8n/`) |
| Cost governance | Self-hosted stack, DigitalOcean-first, FinOps controls |

We target SAP-like operational discipline and governance rigor. We do NOT replicate SAP's product feature set. Odoo CE + OCA + ipai_* covers ERP functionality; Azure + Databricks covers enterprise data/AI maturity.

## Pricing Positioning

| Model | Surface | Description |
|-------|---------|-------------|
| Outcome-based | Professional services | Priced per deliverable/outcome, not per hour |
| Credit-based | Platform usage | Consumption credits for data, AI, automation |

## Cross-References

- Root constitution: `constitution.md` (Section 1.3)
- Agent instructions: `CLAUDE.md` (Critical Rules, Section 4)
- Parity strategy: `docs/ai/EE_PARITY.md`
- Enterprise operating model: `docs/governance/ENTERPRISE_OPERATING_MODEL.md`
- Enterprise OKRs: `ssot/governance/enterprise_okrs.yaml`
