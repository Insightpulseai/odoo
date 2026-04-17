# GENIE_SPACE_STRATEGY

## Purpose

Genie Spaces are the **natural language question-answering surface** for operating intelligence. They allow business users to ask questions in plain language and receive answers grounded in gold mart data — without writing SQL.

## Principles

1. **Prefer curated gold marts** — Genie Spaces must be backed by gold or curated serving views. Raw bronze/silver exposure is prohibited in steady state.
2. **Bronze-backed pilots are time-limited** — A space may launch on bronze backing during initial domain development, but must be promoted to gold backing within one sprint.
3. **Curated example questions are mandatory** — Every Genie Space must have a defined set of seed example questions (see contracts in `data-intelligence/contracts/serving/genie/`).
4. **Live data only** — No synthetic data, no static snapshots in production or pilot spaces.
5. **One space per domain** — Avoid space sprawl. Each vertical domain has one canonical Genie Space.

## Initial Spaces (3)

### Space 1: IPAI Platform Tracker
- **Domain**: Delivery Intelligence (ADO)
- **Status**: Pilot
- **Backing assets**: `gold_ado_work_item_flow`, `gold_ado_iteration_health`
- **Seed questions**: How many work items are in R2? What is blocked right now? Which owner has the most open items?

### Space 2: Finance Operations
- **Domain**: Finance Operations Intelligence
- **Status**: Planned
- **Backing assets**: `gold_finance_close_workload`, `gold_finance_approval_latency`
- **Seed questions**: Who has the highest month-end workload? Which tasks take the most review time? What close steps are best candidates for automation?

### Space 3: Compliance & Tax
- **Domain**: Tax and Compliance Intelligence
- **Status**: Planned
- **Backing assets**: `gold_tax_deadline_control`, `gold_tax_filing_readiness`
- **Seed questions**: Which BIR filings are at risk this month? Which approvals are bottlenecked? What deadlines need escalation?

## Promotion Rule

A Genie Space is **not production-ready** until:
1. It is backed by a gold mart (not bronze/silver directly)
2. Its contract file exists in `data-intelligence/contracts/serving/genie/`
3. At least 3 seed example questions are defined and verified against live data
4. Access is controlled via Unity Catalog row/column security (where applicable)
