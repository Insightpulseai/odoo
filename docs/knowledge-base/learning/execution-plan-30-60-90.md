# 30/60/90 Day Execution Plan

## Day 1-30: Foundation + First Business Cycles

### Learn
- Double-entry bookkeeping through Odoo lens (not theory — configure it)
- Odoo module architecture: read 10 OCA modules, understand patterns
- Enterprise process taxonomy: map O2C, P2P, R2R in Odoo
- Azure basics: ACA, Key Vault, Entra ID concepts

### Build
- Chart of accounts for PH services company
- 3 ipai_* modules: one model extension, one new model, one glue module
- Full O2C walkthrough on odoo_dev (quote → delivery → invoice → payment)
- Full P2P walkthrough (request → PO → receipt → bill → payment)
- Install and configure all OPRG-plan OCA modules

### Document
- Annotated capability taxonomy (personal notes on gaps)
- O2C and P2P process maps with Odoo model references
- OCA module assessment: what each module adds, quality, gaps
- Knowledge base domain primers for finance, procurement, sales

### Test
- Module scaffolds pass OCA pre-commit
- All modules install on fresh test_* databases
- Process walkthroughs produce correct financial postings
- Can explain 10 SAP-to-Odoo equivalences from memory

### Evidence
- `docs/evidence/YYYYMMDD-HHMM/foundation/` — screenshots, logs, test results
- Working modules committed to `addons/ipai/`
- Process walkthrough documentation

### Reusable IP
- Module scaffold template
- OCA module evaluation checklist
- Process mapping template (business process → Odoo models → OCA modules)

---

## Day 31-60: Enterprise Depth + Platform

### Learn
- Multi-company accounting (intercompany, consolidation concepts)
- Bank reconciliation strategies and automation
- Management accounting (analytic plans, MIS Builder)
- Azure deployment: ACA multi-role, Entra ID OIDC
- RBAC design: SoD principles, role hierarchy

### Build
- Multi-company setup with intercompany transactions
- Automated bank reconciliation with matching rules
- Period close procedure (accruals, lock, reports)
- MIS Builder management reports (P&L by cost center, project profitability)
- ACA deployment with web/worker/cron roles
- Entra ID OIDC integration
- SoD matrix enforced via Odoo groups + record rules
- First REST API endpoint with proper auth
- queue_job integration for async processing

### Document
- Month-end close playbook
- Multi-company configuration guide
- SoD matrix with group-to-permission mapping
- Deployment runbook
- Integration architecture (Odoo ↔ Azure services)

### Test
- Month-end close produces correct BS, P&L, TB
- Multi-company isolation: Company A cannot see Company B data
- OIDC login works, MFA enforced
- API endpoint responds correctly under load
- Async jobs process and retry on failure

### Evidence
- Financial reports from month-end close
- Multi-company test results
- OIDC login trace
- API test results (Postman/curl)
- Deployment logs from ACA

### Reusable IP
- Month-end close checklist (reusable per period)
- SoD matrix template
- ACA deployment Bicep templates
- API contract template

---

## Day 61-90: AI + Compliance + Implementation Mastery

### Learn
- Azure Document Intelligence models and training
- MCP protocol for ERP agent tools
- PH tax compliance: BIR 2307, SLSP, e-invoicing
- Performance tuning: PostgreSQL query optimization, Odoo worker sizing
- Implementation methodology: fit-gap, data migration, cutover

### Build
- Document Intelligence pipeline: invoice → extracted fields → Odoo vendor bill
- MCP tools: partner lookup, invoice creation, journal entry query
- BIR 2307 withholding tax certificate generation
- SLSP (Summary List of Sales/Purchases) report
- Databricks pipeline: Odoo → JDBC extract → Delta tables → Power BI
- Performance baseline and optimization
- Backup/restore procedure validated

### Document
- AI integration playbook (Document Intelligence, MCP, Copilot)
- PH tax compliance guide
- Data migration toolkit (templates, scripts, validation queries)
- Fit-gap analysis template
- Cutover plan template
- Architecture document (full platform)
- Implementation methodology playbook

### Test
- Document Intelligence: >90% field extraction accuracy on sample invoices
- MCP tools: all tools respond correctly to standard queries
- BIR 2307: correct computation on sample transactions
- Data migration: reconciliation matches 100%
- UAT scenarios: O2C, P2P, R2R all passing
- Performance: page loads <2s, batch processing <30min for 10K records

### Evidence
- Document Intelligence extraction results
- MCP tool test results
- BIR 2307 sample output
- Data migration reconciliation report
- UAT test results
- Performance benchmark report

### Reusable IP
- Document Intelligence pipeline (reusable for new document types)
- MCP tool library
- BIR compliance module
- Data migration toolkit
- Fit-gap analysis template
- Implementation methodology playbook
- Full architecture documentation

---

## Success Criteria at Day 90

| Criterion | Measure |
|-----------|---------|
| **Process coverage** | O2C, P2P, R2R working end-to-end with edge cases |
| **Financial accuracy** | Month-end close produces correct statements |
| **Platform readiness** | ACA deployment with monitoring, OIDC, SoD |
| **AI integration** | Document Intelligence + MCP tools operational |
| **Compliance** | BIR 2307 + SLSP generating correct output |
| **Implementation method** | Fit-gap + migration + cutover templates ready |
| **Knowledge transfer** | All playbooks, checklists, and architecture docs written |
| **Capability maturity** | L2+ across all P1 domains in capability taxonomy |

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| OCA module quality issues at 18.0 | Budget time for porting/fixing; test early |
| PH tax rules complexity | Engage tax advisor; start with most common scenarios |
| Azure deployment complexity | Use existing Bicep templates; iterate on dev environment |
| Performance at scale | Baseline early; profile before optimizing |
| Scope creep into EE-only territory | Stick to capability matrix; document gaps honestly |
