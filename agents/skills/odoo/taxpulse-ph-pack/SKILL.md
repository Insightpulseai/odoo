# Skill: TaxPulse-PH-Pack — Philippine BIR Tax Compliance Module

## Metadata

| Field | Value |
|-------|-------|
| **id** | `taxpulse-ph-pack` |
| **domain** | `finance_ops` |
| **source** | https://github.com/jgtolentino/TaxPulse-PH-Pack |
| **extracted** | 2026-03-15 |
| **applies_to** | odoo, agents, ops-platform |
| **tags** | bir, tax, philippines, compliance, withholding, vat, income-tax, supabase, ai-review |

---

## What It Is

Odoo module automating Philippine BIR tax compliance and multi-agency finance operations. Computes tax from account moves, generates BIR forms, syncs to Supabase, and provides AI-assisted compliance reviews.

**Maintained by**: InsightPulse AI Finance Shared Service Center
**License**: AGPL-3

## Supported BIR Forms

| Form | Type | Description |
|------|------|-------------|
| **1601-C** | Monthly | Withholding tax on compensation + final payments |
| **2550Q** | Quarterly | VAT return |
| **1702-RT** | Annual | Income tax return |

## Multi-Agency Framework

Supports 8 Philippine entities: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB

## Architecture

```
Odoo UI (Forms & Workflows)
    ↓ "Compute from Account Moves"
Python Engine (Tax Computation)
    ↓ Auto-sync on post
Supabase (PostgreSQL)
    ├── tax_pulse_run_log (audit trail)
    ├── BIR form data tables
    └── Edge Function: finance-tax-pulse (AI review)
```

### Three-Tier Model

| Tier | Component | Purpose |
|------|-----------|---------|
| Frontend | Odoo forms + wizards | User interaction, data entry |
| Business Logic | Python engine (`engine/`) | Tax computation from `account.move` |
| Data Warehouse | Supabase PostgreSQL | Cloud sync, AI review, audit trail |

## File Structure

```
TaxPulse-PH-Pack/
├── models/              # Odoo data models
├── engine/              # Tax computation logic
├── packs/ph/            # Philippine-specific modules
├── supabase/            # Migrations + Edge Functions
│   └── migrations/      # 5 SQL files for schema setup
├── specs/               # Technical specifications
├── config/              # Configuration templates
├── scripts/             # Utility automation
├── skills/              # AI skill definitions
├── security/            # Authorization policies
└── addons/ipai_project_brief/  # Project metadata
```

## Installation

```bash
# 1. Clone to Odoo addons path
git clone https://github.com/jgtolentino/TaxPulse-PH-Pack.git

# 2. Install Python dependencies
pip install requests psycopg2-binary

# 3. Apply Supabase migrations (5 SQL files)
# 4. Set environment variables
export SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
export SUPABASE_SERVICE_ROLE_KEY=<from-key-vault>

# 5. Install module in Odoo
odoo-bin -d odoo_dev -i taxpulse_ph_pack --stop-after-init
```

## Workflow

1. Navigate: Accounting → Philippine BIR → select form type
2. Populate fields (entity, period, etc.)
3. Click **"Compute from Account Moves"** — auto-calculates from journal entries
4. Review computed values
5. Confirm and post → auto-syncs to Supabase
6. (Optional) Run AI compliance review via Edge Function

## AI Compliance Review

Calls `finance-tax-pulse` Edge Function with:
- Entity ID
- Date range
- Form types

Returns structured scoring across 5 dimensions:

| Dimension | What It Measures |
|-----------|-----------------|
| **Compliance** | Adherence to BIR rules and deadlines |
| **Numeric accuracy** | Computation correctness |
| **Coverage** | All required forms filed |
| **Timeliness** | Filing vs deadline |
| **Clarity** | Documentation completeness |

Results stored in `tax_pulse_run_log` for audit trail.

## Relationship to Existing BIR Assets

| Existing Asset | TaxPulse-PH-Pack Role |
|---------------|----------------------|
| `ipai_bir_tax_compliance` (Odoo module) | TaxPulse is the **upstream source** — computation engine |
| `ipai_bir_notifications` (alerts) | TaxPulse provides the deadline data that triggers alerts |
| `ipai_bir_plane_sync` (PM sync) | TaxPulse filing status syncs to Plane via this module |
| `bir-tax-filing` (agent skill) | Skill references TaxPulse forms and workflows |
| `bir.ts` (MCP tool) | MCP tools call TaxPulse engine for form generation |
| n8n BIR workflows | Workflows orchestrate TaxPulse operations |
| Supabase Edge Functions | `finance-tax-pulse` is the AI review endpoint |

## Benchmark: TaxPulse vs AvaTax (Avalara)

| Feature | TaxPulse-PH-Pack | AvaTax (Avalara) |
|---------|-----------------|-----------------|
| **Focus** | Philippines BIR (PH-specific) | Global (190+ countries) |
| **Forms** | 36 eBIRForms | N/A (rate engine, not form generator) |
| **Tax types** | EWT, FWT, VAT, income tax, DST | Sales, use, VAT, GST |
| **Computation** | From Odoo `account.move` | Real-time API per transaction |
| **Geolocation** | N/A (PH nationwide) | Rooftop-level (US street address) |
| **Product tax rules** | BIR ATC codes | 330+ product categories |
| **AI review** | 5-dimension compliance scoring | Agentic tax compliance (new) |
| **ERP integration** | Odoo CE 18 native | Dynamics 365, SAP, NetSuite, Shopify |
| **Latency** | Batch (form-level) | 20ms per transaction |
| **Scale** | Multi-entity (8 agencies) | 55B+ API calls/year |
| **Pricing** | Open source (AGPL-3) | $1+/year (Azure Marketplace) |
| **Compliance certification** | Self-certified | SST CSP certified |

### Key Insight

AvaTax and TaxPulse solve **different problems**:
- **AvaTax** = real-time tax rate engine for transactions (point-of-sale, e-commerce)
- **TaxPulse** = compliance reporting engine for filing (BIR forms, deadlines, audits)

They're complementary, not competing. For IPAI:
- Use **TaxPulse** for BIR compliance (form generation, filing, AI review)
- Consider **AvaTax** only if expanding to US/global tax on sales transactions

### AvaTax "Agentic" Features (New 2026)

Avalara now markets "Agentic Tax and Compliance" on Azure Marketplace:
- Real-time tax calculation via API (20ms avg response)
- Continuous rate updates (no manual monitoring)
- SST CSP certification (shifts tax liability in qualifying US states)
- Supports D365, SAP, NetSuite, Shopify, WooCommerce
- $1/year starting price on Azure Marketplace

**IPAI verdict**: Not relevant for Philippine operations. AvaTax has no BIR form generation, no Philippine-specific tax rules, no eBIRForms integration. TaxPulse is the correct tool for IPAI's use case.

## SSOT References

| Document | Path |
|----------|------|
| BIR forms reference | `agents/knowledge-base/bir-compliance/bir-forms-reference.md` |
| BIR filing calendar | `agents/knowledge-base/bir-compliance/bir-filing-calendar.md` |
| Tax SSOT | `odoo/infra/ssot/tax/` |
| Tax Pulse tool contracts | `odoo/infra/ssot/agents/tax_pulse_tool_contracts.yaml` |
| Spec bundle | `documentaion/spec/tax-compliance-ph-odoo/` |
| Agent skill | `agents/skills/bir-tax-filing/SKILL.md` |
| MCP tools | `agents/mcp/servers/odoo-erp-server/src/tools/bir.ts` |
