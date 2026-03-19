# Odoo Copilot Precursor Target

## Objective

Build the reusable core copilot shell before building specialist sub-agents.

## Why first

This creates:

- One canonical Odoo entry point
- One provider integration surface (Foundry)
- One tool policy surface
- One audit/event model
- One specialist attachment model

Without this, each specialist becomes its own root runtime, duplicating context/tool/audit logic and requiring unraveling later.

## Minimum precursor features

| Feature | Purpose |
|---------|---------|
| Systray/chat entry | Odoo-native user interaction surface |
| Structured request/response contract | Deterministic, benchmarkable I/O |
| User/company/session context | Tenant-safe, multi-company aware |
| Foundry provider adapter | Single integration point for Azure AI Foundry |
| Safe read-only tool registry | Allowlisted tools, no writes by default |
| Audit/event logging | Every tool call traced with user, model, method, timestamp |
| Specialist routing hook | Deterministic handoff to domain packs (TaxPulse, etc.) |

## Explicit exclusions

- Autonomous posting
- Autonomous filing
- Unrestricted write tools
- Final tax recommendation authority
- Free-form workflow automation

## First specialist after precursor

**TaxPulse** — Philippine tax/BIR compliance specialist pack.

Attaches via the specialist handoff hook, not as a replacement for the core shell.

## Build order

### Phase A — Core Precursor

Ship:

- Systray/chat entry
- Foundry bridge
- Read-only tools (record lookup, document search, policy lookup)
- Structured responses
- Audit trail
- Specialist handoff stub

### Phase B — TaxPulse on top

Ship:

- Tax exception review (flag + explain)
- Rule-source citation (grounded in BIR rates/rules)
- Audit note generation
- Human escalation path
- Fail-closed on unresolved ATC codes

## Core Benchmark

The core marketplace benchmark for the Odoo Copilot precursor is **SAP Joule**.

SAP Joule represents the general enterprise copilot shell: transactional, navigational, informational, grounded enterprise assistance. This is the correct benchmark for the precursor core.

AvaTax remains the benchmark for the TaxPulse specialist layer, not for the precursor shell.

| Layer | Product | Primary Benchmark | Secondary Benchmark |
|-------|---------|-------------------|---------------------|
| Core copilot shell | Odoo Copilot Precursor | SAP Joule | Notion 3.0 |
| Tax specialist | TaxPulse | AvaTax | — |
| Platform operations | Odoo on Azure | SAP on Azure | — |

## Secondary Benchmark: Notion 3.0

Notion 3.0 is the secondary benchmark for the precursor. It benchmarks the precursor as an **agentic workspace shell**:

- Multi-step work product generation (up to 20 min autonomous, hundreds of pages)
- Cross-tool search and synthesis
- Document/database creation
- Personalization via memory/instruction page
- Future specialist/custom-agent model (scheduled, trigger-based)

SAP Joule remains the primary ERP/business-system benchmark. Notion 3.0 adds the **knowledge-work and agentic orchestration** dimension that Joule doesn't cover.

Source: [Introducing Notion 3.0](https://www.notion.com/blog/introducing-notion-3-0)

## Current Implementation Status

The core precursor runtime exists in `agent-platform/` and is verified locally with mock Foundry path.

| Capability | Status |
|-----------|--------|
| Runtime contracts | Done |
| Orchestrator + asset loading | Done |
| Mock Foundry client | Done |
| Advisory-mode enforcement | Done |
| Audit event emission | Done |
| Smoke tests (6/6) | Pass |
| TypeScript build | Pass |
| Real Foundry integration | Blocked (endpoint not configured) |
| Real AI Search grounding | Blocked (index not populated) |
| Odoo systray/discuss module | Not started |
| Azure DevOps release gate | Not started |
| Benchmark execution | Not started |

**Next blocker is no longer "build the precursor." It is cloud integration + Odoo UI + release governance.**

## SSOT references

- Precursor definition: `ssot/agents/odoo_copilot_precursor.yaml`
- Copilot target state: `spec/copilot-target-state/prd.md`
- TaxPulse specialist: `spec/tax-pulse-sub-agent/prd.md`
- Benchmark: `ssot/evals/copilot_marketplace_benchmark.yaml`
- Agent production reality: `docs/architecture/AGENT_PRODUCTION_REALITY.md`

---

*Created: 2026-03-18*
