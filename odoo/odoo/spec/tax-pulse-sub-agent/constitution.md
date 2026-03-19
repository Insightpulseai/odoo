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
