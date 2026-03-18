# Finance Solution Architecture

> MB-700-style solution architecture mapping for the InsightPulse AI platform.
> Because the runtime is Odoo CE (not Dynamics 365 F&O), this document maps
> MB-700 solution-architect expectations to Odoo CE + OCA + ipai_* equivalents.
>
> Ref: https://learn.microsoft.com/en-us/credentials/certifications/exams/mb-700/
> Cross-references:
>   - `odoo/.claude/rules/ee-parity.md` (parity strategy)
>   - `docs/architecture/UNIFIED_TARGET_ARCHITECTURE.md` (platform architecture)
>   - `ssot/governance/azdo-execution-hierarchy.yaml` (OBJ-002 Epic)

---

## 1. Solution Strategy

### Platform Choice Rationale

| Dimension | Dynamics 365 F&O | InsightPulse AI (Odoo CE) |
|-----------|-------------------|---------------------------|
| Licensing | Per-user, per-app | Zero license cost (CE + OCA) |
| Customization | ISV / extensions | `ipai_*` modules (full source control) |
| Hosting | Microsoft-managed SaaS | Self-hosted on Azure (ACA + managed PG) |
| AI/Copilot | D365 Copilot (built-in) | Azure AI Foundry agents (governed) |
| Analytics | Power BI embedded | Databricks + Superset + Tableau Cloud |
| Compliance | Built-in localization | `ipai_bir_tax_compliance` (Philippine BIR) |
| Source control | Limited (LCS) | Full Git-based SSOT |

**Strategic decision**: Odoo CE was chosen for cost minimization and full source control.
Enterprise-grade capabilities are achieved via `CE + OCA + ipai_* + Azure + Databricks > EE`.

---

## 2. MB-700 Domain Mapping

MB-700 tests solution architects on 6 domains. Here is how each maps to the Odoo CE stack:

### 2.1 Architect Solutions (20-25%)

| MB-700 Expectation | Odoo CE Equivalent |
|--------------------|-------------------|
| Define solution architecture | `docs/architecture/UNIFIED_TARGET_ARCHITECTURE.md` |
| Solution components | Odoo CE core + 56 OCA must-have + 69 `ipai_*` modules |
| Integration architecture | `docs/architecture/ADLS_ETL_REVERSE_ETL_ARCHITECTURE.md` |
| Data migration strategy | `scripts/migrate-pg-to-azure.sh` + Odoo XML/CSV import |
| Testing strategy | `odoo/.claude/rules/testing.md` (disposable DB per test) |

### 2.2 Define Solution Strategy (20-25%)

| MB-700 Expectation | Odoo CE Equivalent |
|--------------------|-------------------|
| Identify business requirements | `spec/*/prd.md` (76 spec bundles) |
| Propose solution components | OCA-first: Config → OCA → Delta (`ipai_*`) |
| Define application lifecycle | `ssot/governance/operating-model.yaml` (AzDo + GitHub) |
| Define migration/cutover | Not yet required (greenfield) |
| Propose governance model | `ssot/governance/platform-constitution.yaml` |

### 2.3 Manage Implementation (15-20%)

| MB-700 Expectation | Odoo CE Equivalent |
|--------------------|-------------------|
| Manage development activities | `ssot/governance/azdo-execution-hierarchy.yaml` |
| ALM / environment strategy | 3 canonical DBs: `odoo_dev`, `odoo_staging`, `odoo` |
| Define testing strategy | Disposable `test_<module>` DBs, 5-class failure taxonomy |
| Manage quality / performance | CI gates (355 workflows), SSOT validators |

### 2.4 Manage Data (10-15%)

| MB-700 Expectation | Odoo CE Equivalent |
|--------------------|-------------------|
| Data model design | Odoo ORM models + `ipai_*` extensions |
| Data migration | XML/CSV seed data + `odoo-bin -i` |
| Data integration | Extract API (ETL), JSON-2 API (reverse ETL) |
| Data governance | `docs/contracts/DATA_AUTHORITY_CONTRACT.md` |

### 2.5 Implement Security (5-10%)

| MB-700 Expectation | Odoo CE Equivalent |
|--------------------|-------------------|
| Security architecture | `odoo/.claude/rules/security-baseline.md` |
| Role-based access | Odoo groups + `ir.model.access.csv` per module |
| Data security | RLS via Odoo record rules (`ir.rule`) |
| Integration security | API keys + managed identity + Key Vault |

### 2.6 Implement AI/Copilot (5-10%)

| MB-700 Expectation | Odoo CE Equivalent |
|--------------------|-------------------|
| AI/Copilot integration | `ipai_ai_copilot` → Azure AI Foundry agent |
| AI governance | Foundry guardrails + advisory-only policy |
| AI tool execution | MCP tool layer + Odoo FastAPI endpoints |

---

## 3. Finance Process Scope

### In Scope

| Process | Module(s) | Status |
|---------|-----------|--------|
| Chart of Accounts | `account` (core) | Active |
| AP / AR | `account` + `ipai_ap_expense_capture` | Active / In development |
| Bank reconciliation | `account_reconcile_oca` (OCA) | Active |
| Financial reporting | `mis_builder` + `account_financial_report` (OCA) | Active |
| Asset management | `account_asset_management` (OCA) | Active |
| Tax compliance (BIR) | `ipai_bir_tax_compliance` | Active |
| Expense capture | `ipai_ap_expense_capture` + Document Intelligence | In development |
| Cost/revenue spreading | `account_spread_cost_revenue` (OCA) | Planned |

### Out of Scope

| Process | Reason |
|---------|--------|
| Payroll | Not yet in EE parity scope (deferred) |
| Fixed asset depreciation (complex) | OCA module covers basic; advanced deferred |
| Multi-currency revaluation | Core Odoo handles basic; advanced deferred |
| Intercompany transactions | Single-company model (CONST scope) |
| Budgeting (advanced) | `account_move_budget` (OCA) covers basic needs |

---

## 4. Implementation Lifecycle

```
Phase 1: Foundation          Phase 2: Core Finance       Phase 3: Intelligence
─────────────────           ──────────────────          ────────────────────
• Odoo CE 19 runtime        • OCA finance modules       • Foundry copilot
• Azure hosting (ACA)       • ipai_* bridges            • Document Intelligence
• PostgreSQL managed        • BIR tax compliance        • Databricks analytics
• Identity baseline         • Bank reconciliation       • Expense capture
• CI/CD governance          • Financial reporting       • Predictive models
```

### Environment Strategy

| Environment | Database | Purpose | Refresh Cadence |
|------------|----------|---------|-----------------|
| Development | `odoo_dev` | Feature development | Continuous |
| Demo | `odoo_dev_demo` | Stakeholder demos, showroom | On-demand |
| Staging | `odoo_staging` | Pre-production validation | Per release |
| Production | `odoo` | Live operations | — |
| Test | `test_<module>` | Disposable per-module testing | Per test run |

---

## 5. Testing Governance

### Test Classification (5 classes)

| Classification | Meaning | Action |
|---------------|---------|--------|
| `passes locally` | Init and tests clean | Mark as compatible |
| `init only` | Installs but has no tests | Note; cannot claim tested |
| `env issue` | Fails due to test env | Re-run with adjusted env |
| `migration gap` | Incomplete 19.0 migration | Report upstream |
| `real defect` | Functional failure | Fix or report with traceback |

### Test Approach by Layer

| Layer | Test Type | Tool | Evidence |
|-------|----------|------|----------|
| Odoo modules | Unit + integration | `odoo-bin --test-enable` | `docs/evidence/<stamp>/test.log` |
| API endpoints | Integration | FastAPI test client | CI logs |
| Foundry agents | Evaluation | Foundry evaluations (planned) | Foundry dashboard |
| Data pipelines | Data quality | Great Expectations (planned) | Pipeline logs |
| Infrastructure | Validation | CI validators (`scripts/ci/`) | CI output |

---

## 6. AI/Copilot Boundaries

| Capability | Agent | Mode | Constraint |
|-----------|-------|------|-----------|
| Ask (search/RAG) | `ipai-odoo-copilot-azure` | Read-only | No write operations |
| Author (drafting) | `ipai-odoo-copilot-azure` | Draft creation | Human review required |
| Livechat (visitor Q&A) | `ipai-odoo-copilot-azure` | Advisory only | No PII access |
| Transact (CRUD) | `ipai-odoo-copilot-azure` | Bounded writes | Audit trail mandatory |

Full agent architecture: `docs/architecture/AI_CONSOLIDATION_FOUNDRY.md`

---

*Last updated: 2026-03-17*
