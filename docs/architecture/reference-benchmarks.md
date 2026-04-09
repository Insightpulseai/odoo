# Reference Benchmarks

## Purpose

Document external platforms used as architecture and process benchmarks for the InsightPulseAI platform. These are reference models, not mandatory integrations or systems of record.

## What "benchmark" means

A benchmark is a product or platform whose architecture, process design, or capability model is used as a reference target for comparison and quality calibration.

A benchmark is **not**:

- a required runtime dependency
- a system of record
- a mandatory procurement target
- an integration contract

A benchmark becomes an integration only when an explicit integration contract is created in `docs/contracts/` and registered in `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`.

## Benchmark registry

### SAP on Azure

**Role:** Ops/governance maturity benchmark only. SAP-on-Azure is NOT the application architecture, runtime, or AI benchmark for this platform.

**What we benchmark against (ops/governance maturity only):**

- Environment separation and landing-zone discipline (dev / non-prod / prod / DR)
- HA/DR topology and resilience patterns (Pacemaker clusters, zone-redundant storage, cross-region DR)
- Storage architecture quality (tiered storage, workload-appropriate choices)
- Network isolation and ingress posture (delegated subnets, NSGs, WAF/Front Door)
- Identity integration with Microsoft Entra ID (managed identities, SSO, fence agent auth)
- IaC automation discipline (Terraform + Ansible via SAP Deployment Automation Framework)
- Platform observability and monitoring (Azure Monitor for SAP solutions — OS, DBMS, application stack)

**Source:** [SAP on Azure workload documentation](https://learn.microsoft.com/en-us/azure/sap/workloads/get-started)

**Our canonical implementation:** Odoo CE 18 on Azure Container Apps.

### SAP Concur

**Role:** Benchmark for travel, expense, invoice, and AP operating model.

**What we benchmark against:**

- Connected spend management across expense, travel, and invoice flows
- Employee expense receipt/OCR intake patterns
- AP/invoice automation quality bar
- Tax receipt indicator handling
- Reimbursement/approval workflow design

**Our canonical implementation:** Odoo Expense + Vendor Bills + custom `ipai_*` modules.

### Avalara AvaTax

**Role:** Benchmark for tax calculation and compliance engine capability.

**What we benchmark against:**

- Automated tax calculation across sales/use/VAT/GST
- Jurisdiction-aware rate and rule handling
- Product-specific tax code categories
- Real-time and batch transaction processing
- Compliance certification model (SST CSP)

**Our canonical implementation:** Odoo fiscal positions + BIR tax compliance (`ipai_bir_tax_compliance`).

**Note:** Azure Marketplace AvaTax offer has no plan available for market PH. Do not design around Marketplace procurement as the only path. If AvaTax is later adopted as an integration, use the direct REST API / commercial path.

## Benchmark hierarchy

The platform uses a 4-layer benchmark model. Each layer has its own benchmark authority:

| Layer | Benchmark |
|---|---|
| ERP/application architecture | Odoo CE 18 + OCA + thin-bridge doctrine |
| Cloud runtime | Azure Container Apps Well-Architected guidance |
| AI/copilot runtime | Microsoft Foundry SDK/project model |
| Tax/compliance product ambition | AvaTax-style capability benchmark (PH-first) |
| Ops/governance maturity | SAP-on-Azure seriousness / landing-zone discipline |

SAP-on-Azure governs ops/governance maturity patterns only. It is not the application architecture, runtime, or AI benchmark. Never say "SAP on Azure but with Odoo." The correct framing is: "Azure-native Odoo operating model. Benchmarks: Odoo CE 18 + OCA (application), ACA Well-Architected (runtime), Foundry SDK (AI), AvaTax capability (tax/compliance), SAP-on-Azure (ops maturity only)."

Odoo on Azure remains the actual implementation target for ERP, finance, project, and compliance workloads. Benchmarks inform architecture quality but do not replace the canonical stack.

## Cross-references

- `docs/architecture/idea-to-release-pipeline.md` — end-to-end delivery pipe
- `docs/architecture/platform_delivery_contract.md` — tooling consistency
- `ssot/governance/platform-constitution.yaml` — platform non-negotiables

---

*Last updated: 2026-03-17*
