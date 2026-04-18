# M365 Declarative Agent -- Constitution

> Non-negotiable invariants for the Pulser M365 surface (Copilot Chat / Teams).
> Wave 2 companion to the Wave 1 Pulser SaaS marketplace offer.

---

## Purpose

The **Pulser M365 Declarative Agent** is the M365-surface layer of the Pulser
three-protocol architecture (per platform Invariant #10a). It exposes Pulser
capabilities inside Microsoft 365 surfaces (Copilot Chat, Teams, Outlook) via
Microsoft's declarative agent runtime. It does **not** replace Pulser's
custom-engine runtime; it is a channel.

---

## Core Invariants

### 1. Surface Layer Only, Not a Second Product

The declarative agent is how M365 users discover and invoke Pulser. The
system-of-action remains Pulser SaaS (Wave 1). The agent:
- Accepts user intent in Copilot Chat / Teams
- Translates to Pulser API calls via the bundled `ai-plugin.json`
- Returns results and links the user back to Pulser SaaS for transactional
  actions that require maker-checker approval

The declarative agent never holds business state, never mutates Odoo directly,
never bypasses Pulser's policy gates.

### 2. Channel Via Agent365 SDK, Not A2A

Per platform Invariant #10a (three-protocol model), this surface uses the
Microsoft **Agent365 SDK** protocol layer for M365-user-facing
discovery/invocation/auth. Non-M365 surfaces (Odoo chatter, Slack, Claude
Code) continue to speak A2A directly to the Pulser orchestrator.

### 3. Two Agents, Not More

Scope discipline at publish:

| Agent | Purpose | Source file |
|---|---|---|
| `pulser-project-to-profit` | Odoo project operations + finance reconciliation | `agents/pulser-surface/appPackage/declarativeAgent.json` |
| `pulser-record-to-report` | Month-end close + record-to-report guidance | `agents/pulser-surface/appPackage/declarativeAgent_r2r.json` |

Additional declarative agents are a Wave 3+ conversation. More agents at
publish multiplies certification surface, audit overhead, and user confusion
without revenue acceleration.

### 4. Same Policy Gates as Pulser SaaS

Every declarative agent action that touches Odoo state goes through Pulser's
approval bands (A-E) and Content Safety moderation. The agent runtime cannot
disable these gates. If Microsoft's declarative agent engine cannot express a
required Pulser safety check, the action is unavailable in the M365 surface
(link out to Pulser SaaS instead).

### 5. Published To M365 Agent Store, Not Commercial Marketplace

Wave 1's Pulser SaaS ships to the Microsoft Commercial Marketplace. The
declarative agent ships to the **Microsoft 365 Agent Store** (different
surface, different cert pipeline, different discovery). They are linked: the
agent listing references the SaaS offer; the SaaS listing references the
agent.

### 6. Entra Agent ID Identity

Each declarative agent gets an Entra Agent ID (per Microsoft's own pattern
for Security Copilot Entra agents). Identities:
- `pulser-project-to-profit` → dedicated MI
- `pulser-record-to-report` → dedicated MI

These identities authenticate calls to the Pulser API plugin endpoint.
Aligned with the 2026-05-01 Entra Agent ID registration deadline.

### 7. No Customer Data In Agent Context

The declarative agent instructions and `ai-plugin.json` do not contain
customer data. All customer data is fetched at invocation time via the API
plugin with the user's delegated token. Nothing about any tenant's Odoo
state exists in the agent manifest.

### 8. Dual-Tenant Registration Pattern

Target deployment: IPAI tenant (primary publisher) + design-partner tenants
(e.g., TBWA\\SMP) as custom catalogs. This enables side-loaded testing
without waiting for M365 Agent Store cert on every iteration.

---

## Success Criteria

- Users in Copilot Chat discover "Pulser Project-to-Profit" in agent list
- Query "what's the P&L position of Project Alpha?" returns grounded Odoo data
- Every mutating action (create invoice, approve expense) routes user to
  Pulser SaaS landing page rather than executing in-line
- Agent published to M365 Agent Store by end-Q4 2026 (90 days after Wave 1
  publish)

---

## Non-Goals

- Replacing Pulser SaaS's own chat surface (no Copilot-only customers)
- Becoming a Teams bot with arbitrary messaging capabilities (use declarative
  agent runtime only)
- Supporting tenants without Pulser SaaS subscription (agent is locked to SaaS
  subscribers)
- Exposing Pulser's full multi-agent orchestrator in the M365 surface (the
  supervisor + specialists stay behind the API plugin boundary)
