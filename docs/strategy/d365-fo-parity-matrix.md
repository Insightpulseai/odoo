# D365 Finance & Operations — Side-by-Side Parity Matrix

> **Locked:** 2026-04-17
> **Authority:** this file maps every D365 F&O category to IPAI's equivalent layer.
> **Companion:** [`lifecycle-maturity-matrix.md`](./lifecycle-maturity-matrix.md)
> **Microsoft ref:** [D365 F&O documentation](https://learn.microsoft.com/dynamics365/fin-ops-core/fin-ops/)
> **Position:** We are productizing the intelligence + guided operations layer first, not the full monolithic ERP suite.

---

## Internal statement

> Relative to the Dynamics 365 Finance & Operations lifecycle, we are currently strongest in the integration, analytics, and intelligence layers, with the implementation and packaged solution layer still being productized. Our current maturity is best described as **reference architecture proven with live telemetry, moving into repeatable finance-operations solution packaging**.

---

## Side-by-side matrix

### 1. Implementation lifecycle

| D365 F&O category | Our equivalent | Maturity | Gap | Next milestone |
|---|---|---|---|---|
| FastTrack onboarding | ISV Success enrollment (MpnId 7097325) | Medium | No structured onboarding playbook for customers | Build customer onboarding checklist |
| Implementation lifecycle | Architecture shaping + reference proving | Strong | Not yet a repeatable rollout motion | Package into vertical offer bundle |
| Preparing for go-live | Feature Ship-Readiness Checklist (5 gates) | Defined | Not executed against live deployment | Execute checklist for R2 first-slice |
| Go-live readiness review | No external reviewer yet | Gap | No FastTrack equivalent | Partner with MS ISV Success for review |

### 2. Integrations

| D365 F&O category | Our equivalent | Maturity | Gap | Next milestone |
|---|---|---|---|---|
| Business events | Odoo webhooks + `ipai-odoo-mcp` (P0 gap) | Emerging | `ipai-odoo-mcp` not yet built | Build the MCP server (Phase 2 per MCP topology) |
| Data entities / OData | OData entity map (`ssot/semantic/odata-entity-map.yaml`) | Strong | OData not yet served (contract only) | Implement OData serving layer |
| Power Automate integration | Azure Functions + Logic Apps (Foundry tools) | Medium | No customer-facing workflow automation yet | Wire Pulser → Foundry → Odoo action loop |
| Dual-write / virtual entities | Lakehouse Federation (`odoo_erp` foreign catalog) | Strong | Zero-copy read works; no write-back | Keep read-only per doctrine |

### 3. Finance domain

| D365 F&O category | Our equivalent | Maturity | Gap | Next milestone |
|---|---|---|---|---|
| General ledger | Odoo CE `account.move` + `account.move.line` | Strong (CE) | No advanced consolidation yet | Add OCA `account_consolidation` when multi-entity |
| Accounts payable | Odoo CE AP + OCA `account_payment_order` | Strong | AP aging mart planned but not populated | Populate `gold_finance_ap_aging` |
| Accounts receivable | Odoo CE AR + `ipai_ar_collections` (planned) | Emerging | AR collections overlay not built yet | Build `ipai_ar_collections` thin delta |
| Cash and bank management | Odoo CE bank + OCA `account_reconcile_oca` | Medium | Cash position mart not populated | Populate `gold_finance_cash_position` |
| Compliance / regulatory | `ipai_bir_tax_compliance` + `ipai_bir_2307` | Emerging | BIR modules partially built; control tower = contract only | Populate `gold_finance_bir_deadline_control` |
| Financial reporting | Databricks gold marts + Genie + dashboards | Strong (architecture) | Gold marts not populated yet | Run DLT → populate gold → create Genie Space |
| Budgets / FP&A | OCA `account_budget_oca` + `ipai_finance_ppm` | Emerging | PPM overlay in dev_ppm catalog | Wire PPM data into gold marts |
| Fixed assets | OCA `account_asset_management` | Available | Not installed/tested | Install when asset management use case materializes |
| Expense management | Odoo CE `hr.expense` + `ipai_expense_liquidation` | Emerging | PH expense liquidation bridge planned | Build `ipai_expense_liquidation` |

### 4. Intelligence layer (IPAI's differentiator)

| D365 F&O category | Our equivalent | Maturity | Gap | Next milestone |
|---|---|---|---|---|
| Analytics | Databricks gold marts + dashboards + Databricks One | **Strong** | Gold tables not populated from live pipeline | Run DLT pipeline |
| Business documents | Evidence packs + workbook-driven workflow data | Medium | No DMS integration yet | Build evidence-pack MCP (Phase 3) |
| Financial reporting | Semantic layer (46 metrics, 16 dims, OData entity map) | **Strong** (architecture) | Not yet materialized as running views | Create UC views from semantic definitions |
| Regulatory reporting | BIR control tower (4 modules, 16 business questions) | **Strong** (model) | Contract-only; not yet live data | Ingest BIR calendar → populate facts |

### 5. Development / administration

| D365 F&O category | Our equivalent | Maturity | Gap | Next milestone |
|---|---|---|---|---|
| Extensibility | `ipai_*` module doctrine (CE → OCA → thin delta) | **Strong** | Module introspection docs incomplete for some modules | Complete MODULE_INTROSPECTION.md per module |
| Continuous delivery | Azure Pipelines (sole CI/CD) | **Strong** | 26 pipeline files defined; not all wired to ADO environments | Wire environment gates |
| Cloud deployment | ACA + Databricks + Foundry on Sponsored sub | **Strong** | Old-sub resources not fully decommissioned | Complete decom (10 apps scaled to zero; delete after 90d) |
| Lifecycle services | SSOT YAML + architecture docs + memory system | Medium | No customer-facing lifecycle portal equivalent | Build demo path for customer onboarding |
| Organization admin | Entra + UC + tag governance + RBAC | Medium | Tag policy not enforced via Azure Policy deny yet | Enable Policy deny for untagged resources |

### 6. Supply chain / HR / other domains

| D365 F&O category | Our equivalent | Maturity | Gap | Next milestone |
|---|---|---|---|---|
| Supply chain management | Odoo CE `stock.*` + `purchase.*` + `mrp.*` | Available (CE) | Not the current vertical focus | Defer until customer demand |
| Human resources | Odoo CE `hr.*` + OCA payroll | Available (CE) | Not the current vertical focus | Defer |
| Commerce / retail | Not in scope | N/A | Not competing on retail | N/A |
| Project management | Odoo CE `project.*` + `ipai_finance_ppm` | Emerging | PPM bridge in progress | Complete `ipai_ppm_bridge` |

---

## Maturity summary

| Layer | Maturity | Rating |
|---|---|---|
| Platform / admin / dev | Medium → Strong | ████████░░ |
| Integration | Medium → Strong | ████████░░ |
| **Analytics / intelligence** | **Strong (differentiator)** | **██████████** |
| Finance domain (ERP) | Emerging → Medium | ██████░░░░ |
| Packaged solution | Emerging | ████░░░░░░ |
| Industry solution packaging | Not finished | ██░░░░░░░░ |

---

## Strategic implication

We are **not** building a monolithic ERP to compete with D365 F&O on breadth.

We are building:

```
Odoo CE + OCA                    = transactional core (80%+ EE parity target)
Databricks + UC + Genie          = intelligence layer (our differentiator)
Pulser + MAF agents              = guided operations layer
ipai_* thin deltas               = PH-specific / vertical bridges only
```

The intelligence layer is where we lead. The ERP layer is where we match (via CE + OCA). The packaging layer is what we're building next.

**Which layer are we productizing first?**

> The intelligence + guided operations layer — not the full traditional monolithic ERP suite.

---

## Commercial framing

For Microsoft conversations:
> We displace D365 F&O for mid-market PH services firms by combining Odoo CE (transaction core) with Databricks (operating intelligence) and Pulser (AI copilot). Our strongest differentiation is the intelligence layer — finance control towers, compliance analytics, and guided close workflows — not raw ERP feature count.

For customer conversations:
> We make finance operations measurable before we automate them. Your close calendar, approval chains, and compliance deadlines become a live control tower — not a static spreadsheet.

---

*Last updated: 2026-04-17*
