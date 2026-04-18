# M365 Declarative Agent -- PRD

> Wave 2 companion to the Pulser SaaS marketplace offer (Wave 1).

---

## Problem

Wave 1 ships Pulser SaaS to the Microsoft Commercial Marketplace (Aug-Sep
2026). Customers land on Pulser's web UI. But buyers' users live in Microsoft
365 -- Outlook, Teams, Copilot Chat. Without an M365 surface, daily usage
competes with the user's actual work environment.

The M365 declarative agent closes that gap: users discover and invoke Pulser
from inside Copilot Chat and Teams, without context switching.

## Users

| Persona | Need |
|---|---|
| Odoo end-user (ops, finance, marketing teams) | "Ask about my project P&L without leaving Teams" |
| Approver (manager, controller) | "Get a summary of pending approvals when opening Copilot Chat" |
| Admin | "Install Pulser agent for my whole tenant with one click" |
| Microsoft seller (at demo time) | "Show the customer that Pulser works natively in M365" |

## Functional Requirements

1. **Two declarative agents published to M365 Agent Store**
   - `pulser-project-to-profit` -- project operations + finance reconciliation
   - `pulser-record-to-report` -- month-end close + R2R guidance

2. **API plugin bridge** -- `ai-plugin.json` points at Pulser SaaS API; all
   reads/writes go through there.

3. **Authentication** -- OAuth 2.0 on the API plugin; user's delegated token
   propagated to Pulser; Pulser validates SaaS subscription active.

4. **Dual-catalog** -- published to M365 Agent Store AND available as
   sideloadable app package for design-partner tenants.

5. **Admin consent flow** -- tenant admin approves the agent once; end-users
   don't see consent prompts after that.

6. **Graceful degrade** -- if the user's tenant isn't a Pulser SaaS
   subscriber, the agent responds with a sign-up link to the marketplace
   listing.

7. **No mutations in-surface** -- every write operation returns a link to
   Pulser SaaS with the action pre-filled; user completes there with
   maker-checker gate.

## Non-Functional Requirements

- **Latency**: first response from agent <= 3 s; streaming after
- **Accuracy**: grounded responses only; hallucination rate <= 5% on eval
- **Cost**: Foundry inference cost per invocation <= $0.05 at Wave 2 scale
- **Security**: Content Safety enabled on all prompts and responses
- **Accessibility**: WCAG AA-compliant cards and responses

## Out of Scope

- Additional declarative agents beyond the two listed (Wave 3+ decision)
- Custom Teams bot (use declarative agent pattern, not bot framework)
- Power Platform connector (separate deliverable if/when Business Apps
  designation is pursued)
- Offline / disconnected mode (agent requires active tenant + Pulser SaaS
  subscription)

## Dependencies

- Wave 1 Pulser SaaS published and transactable (hard dependency)
- Pulser API exposing the endpoints used by `ai-plugin.json`
- Entra Agent ID registration for both agents (deadline 2026-05-01)
- M365 Agent Store access via ISV Success partner center profile
- Content Safety resource in Foundry project `ipai-copilot-resource`

## Acceptance

- Both agents pass M365 Agent Store certification (Wave 2 target: Q4 2026)
- "Pulser Project-to-Profit" visible in Copilot Chat agent picker
- Demo query "Summarize outstanding AP invoices for Company IPAI" returns
  grounded Odoo data within 3 s
- Demo query "Approve invoice INV-2026-100" returns a card with deep-link to
  Pulser SaaS for maker-checker completion
- Installation via Teams admin center completes in under 5 minutes for a
  tenant with pre-existing Pulser SaaS subscription

## Success Metrics (first 90 days post-Wave 2 publish)

- 50% of Wave 1 SaaS customers install the declarative agent
- Agent invocations per active user per week >= 3
- Completion rate of cross-surface flows (agent -> SaaS link -> action) >= 40%
