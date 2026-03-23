# Constitution — Tax Pulse Sub-Agent

> Non-negotiable rules governing the BIR Compliance Pack inside the Odoo Copilot system.

---

## C1: Tax Pulse is a capability pack, not a top-level agent

Tax Pulse attaches to the existing 3-agent + 1-workflow system as the **BIR Compliance Pack**.
It does not create a new prompt agent, runtime, or workflow.
The canonical runtime remains: Advisory, Ops, Actions, Router.

## C2: Odoo 19 CE is the workflow and state engine

All filing lifecycle state lives in Odoo records (`bir.tax.return`, `bir.filing.deadline`, `project.task`).
Tax Pulse tools trigger Odoo state transitions — they do not hold state, invent stages, or maintain a parallel workflow.

Odoo-native primitives are authoritative:
- **Stages** → Draft → Computed → Validated → Approved → Filed → Confirmed
- **Activities** → reminders, approvals, missing-data follow-ups
- **Reporting** → overdue filings, blocked filings, upcoming deadlines
- **Project/service task templates** → recurring BIR/month-end tasks
- **Milestone-style checkpoints** → compute, validate, export, pay, confirm

## C3: BIR knowledge must be grounded in authoritative sources

Tax advice must be grounded in:
- `data/rates/ph_rates_2025.json` — TRAIN law brackets, EWT/FWT ATC codes
- `data/rules/*.rules.yaml` — JSONLogic computation rules
- BIR Revenue Regulations and Revenue Memorandum Circulars (knowledge store)
- Odoo record state (actual return data)

Free-form tax guidance without grounding citation is blocked.

## C4: Tax truth lives in rules, rates, tools, knowledge, and workflow policy

The five layers of tax truth:
1. **Rules** — JSONLogic evaluation (deterministic, auditable)
2. **Rates** — Externalized JSON (versioned, updatable without code changes)
3. **Tools** — Copilot tool contracts (typed inputs/outputs, approval gates)
4. **Knowledge** — BIR regulations, circulars, and compliance guidelines (RAG-grounded)
5. **Workflow policy** — Odoo stages, activities, task templates (operational state)

Prompts alone are never sufficient for tax truth.

## C5: Risky tax actions require approval

Any action that:
- Computes a tax liability
- Generates a filing artifact (eFPS XML, PDF)
- Changes a return state to `filed` or `confirmed`
- Modifies tax rates or rules

must route through the Actions agent with explicit approval gate.
Advisory can explain and inspect. Ops can diagnose. Only Actions can execute.

## C6: No Enterprise Edition dependencies

All computation, reporting, and filing must work on Odoo 19 CE.
No dependency on `account_reports`, `account_accountant`, or any EE module.
OCA modules may be used where they provide CE-compatible alternatives.

## C7: Externalized rates and rules are versioned

`ph_rates_2025.json` and `*.rules.yaml` are versioned by tax year.
When BIR updates rates (e.g., TRAIN law amendments), a new version file is created.
Old versions are retained for historical computation and audit.
The engine loader selects the correct version based on the return's period dates.

## C8: Azure Resource Binding

Tax Pulse uses Azure Document Intelligence for BIR document extraction and classification:

- **Resource**: `data-intel-ph` in resource group `rg-data-intel-ph`
- **Purpose**: Receipt/invoice extraction, BIR form classification, supporting document OCR
- **Flow**: Document Intelligence extracts → structured data feeds into Odoo operational flows → Tax Pulse checks/scenarios evaluate the extracted data
- **Auth**: Managed identity from ACA to Document Intelligence resource

Document Intelligence is an extraction substrate, not a tax-computation authority. All tax logic remains in rules, rates, and Odoo workflow.

## C9: AvaTax as Future Complement

AvaTax (Avalara) is a benchmark-only reference for global tax engine patterns:

- AvaTax is **not available in the PH market** for BIR compliance
- TaxPulse-PH-Pack remains the canonical PH tax core
- Future bridge: `ipai_tax_compliance_bridge` module when a global tax engine integration is justified (e.g., multi-country expansion)
- Until that bridge exists, AvaTax patterns inform design benchmarks only — no runtime dependency, no adapter, no API calls

## C10: Sovos as E-Invoicing Watch Item

Sovos is a global compliance and e-invoicing platform with strong presence in Latin America and the EU.

- Sovos does **not currently cover PH BIR** at depth, but is expanding in APAC
- If BIR mandates electronic invoicing (similar to Brazil's NF-e or Mexico's CFDI), Sovos is the most likely commercial entrant to the PH market
- Tax Pulse must monitor BIR e-invoicing regulatory signals (Revenue Memorandum Circulars, pilot programs)
- If BIR mandates e-invoicing, the response is an **adapter** (`sovos_adapter` behind `ipai_tax_compliance_bridge`), not a replacement for Tax Pulse
- Sovos would handle e-invoicing transmission/certification only — filing lifecycle, approval gates, and tax computation remain in Tax Pulse and Odoo
- No preemptive integration — build the adapter only when a BIR mandate is published or a pilot program is announced
