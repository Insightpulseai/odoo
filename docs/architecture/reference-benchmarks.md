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

**Role:** Benchmark for enterprise ERP landscape architecture on Azure.

**What we benchmark against:**

- Environment separation and landing-zone discipline (dev / non-prod / prod / DR)
- HA/DR topology and resilience patterns (Pacemaker clusters, zone-redundant storage, cross-region DR)
- Storage architecture quality (tiered storage, workload-appropriate choices)
- Network isolation and ingress posture (delegated subnets, NSGs, WAF/Front Door)
- Identity integration with Microsoft Entra ID (managed identities, SSO, fence agent auth)
- IaC automation discipline (Terraform + Ansible via SAP Deployment Automation Framework)
- Platform observability and monitoring (Azure Monitor for SAP solutions — OS, DBMS, application stack)

**Source:** [SAP on Azure workload documentation](https://learn.microsoft.com/en-us/azure/sap/workloads/get-started)

**Our canonical implementation:** Odoo CE 19 on Azure Container Apps.

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

## Canonical runtime target

SAP on Azure is the benchmark for enterprise ERP landscape shape and operating discipline; Odoo on Azure remains the implementation target.

Odoo on Azure remains the actual implementation target for ERP, finance, project, and compliance workloads. Benchmarks inform architecture quality but do not replace the canonical stack.

## Cross-references

- `docs/architecture/idea-to-release-pipeline.md` — end-to-end delivery pipe
- `docs/architecture/platform_delivery_contract.md` — tooling consistency
- `ssot/governance/platform-constitution.yaml` — platform non-negotiables

---

*Last updated: 2026-03-17*
