# Microsoft Copilot & Agent Offerings — Platform Gap Analysis

> **Date:** 2026-03-25
> **Source:** Microsoft Copilot landscape research (Mar 2026) mapped against InsightPulse AI target state
> **Current state basis:** `ssot/architecture/services.yaml`, enterprise benchmark audit (2026-03-24)
> **Status:** Analysis document — requires commercial validation

---

## 1. Executive Summary

The InsightPulse AI platform has made **architecturally correct bets** on the three Microsoft offerings that matter most for a pro-code SaaS ERP builder: **Foundry Agent Service** (agent runtime), **Entra ID** (identity), and **Azure OpenAI** (inference). These align with the "no extra charge for agent shell, pay for tokens/tools" model Microsoft now offers.

However, the platform has **no plan for the adjacent offerings** that Microsoft is positioning as the enterprise governance and delivery layer: **Copilot Studio** (low-code agent factory), **Microsoft 365 Copilot surfaces** (enterprise delivery channels), and **Agent 365** (cross-platform agent governance). These gaps matter because enterprise customers will expect agents to appear in Teams/Outlook/M365, not just in a custom web widget.

**Bottom line:** The pro-code foundation is sound. The enterprise delivery and governance surface is missing.

---

## 2. Alignment Scorecard

| # | Microsoft Offering | IPAI Current State | Alignment | Gap Severity | Action Required |
|---|---|---|---|---|---|
| 1 | **Foundry Agent Service** | Pulser agents on Foundry (confirmed doctrine) | **ALIGNED** | None | Continue; wire multi-agent workflows |
| 2 | **Azure OpenAI** | `oai-ipai-dev` deployed, API version 2024-10-01-preview | **ALIGNED** | Low | Upgrade to latest stable API; confirm data residency |
| 3 | **Entra ID** | Spec bundle exists, 72 tasks, 0% started | **PLANNED** | **Critical** | P0 — no production auth without Entra |
| 4 | **Microsoft 365 Copilot surfaces** | Not planned | **MISSING** | High | Plan M365 channel for Pulser agents |
| 5 | **Copilot Studio** | Not planned | **MISSING** | Medium | Evaluate for internal department agents |
| 6 | **Agent 365 governance** | Not planned | **MISSING** | Medium | Track preview; plan adoption when GA |
| 7 | **Security Copilot** | Not planned | **MISSING** | Low | Defer until Defender/Sentinel active |
| 8 | **Dynamics 365 Copilot** | N/A (Odoo is ERP) | **N/A** | None | Not applicable — Odoo is SoR |
| 9 | **GitHub Copilot** | Available (developer tooling) | **ALIGNED** | None | Already in use |
| 10 | **Power BI** | Planned (primary BI) | **ALIGNED** | Medium | Not yet deployed |
| 11 | **Microsoft Fabric** | Mirroring enabled on `pg-ipai-odoo` | **PARTIAL** | Medium | Needs Fabric capacity to complete |
| 12 | **MCP governance** | MCP-first doctrine, `mcp/servers/` exists | **ALIGNED** | Low | Formalize MCP tool registry for Foundry |

---

## 3. Gap Detail

### Gap A: Entra ID — Identity Plane Not Operational (P0)

**Current:** Spec bundle at `spec/entra-identity-migration/` (72 tasks, 5 phases). Zero operational SSO. Benchmark audit confirms "MFA not enforced, Security Defaults OFF."

**Microsoft landscape confirms:** Entra is the **prerequisite** for every Copilot and agent offering. M365 Copilot Chat requires "eligible Entra users." Foundry Agent Service uses Entra for tool auth (including OBO). Agent 365 governance layer is Entra-native. Without Entra, you cannot participate in any Microsoft agent governance.

**Impact:** Blocks items 4, 5, 6, 7 from this scorecard. Blocks production readiness per benchmark.

**Recommendation:** Execute Entra bootstrap as P0. Minimum viable: app registration + OAuth for Odoo + Foundry service principal.

---

### Gap B: No Microsoft 365 Delivery Channel for Pulser (High)

**Current:** Pulser agents deliver via custom web widget (`web/ipai-landing/`) and planned Odoo embedded copilot (`addons/ipai/ipai_ai_copilot/`). No Teams/Outlook/M365 surface.

**Microsoft landscape confirms:** Microsoft positions **declarative agents** and **custom engine agents** as the two paths to appear in M365 Copilot. Custom engine agents (which IPAI would use) can be built with the **Microsoft 365 Agents SDK** and published to Teams, Outlook, and M365 Copilot via **Agents Toolkit**.

**Impact:** Enterprise customers expect agents in Teams/Outlook. A web-only Pulser limits distribution to users who visit the custom portal.

**Recommendation:**
1. Evaluate Microsoft 365 Agents SDK (JS/Python) for wrapping existing Foundry-hosted Pulser agents
2. Publish Ask Pulser as a **custom engine agent** in Teams (requires Entra app registration)
3. Requires M365 Copilot license ($30/user/month) for users accessing via M365 surfaces
4. Add to roadmap as P3 (after Entra and core ERP stabilization)

---

### Gap C: No Copilot Studio Evaluation for Low-Code Agents (Medium)

**Current:** All agent development is pro-code (Foundry Agent Service + Agent Framework). No low-code agent path exists.

**Microsoft landscape confirms:** Copilot Studio is positioned as the **low-code enterprise agent factory** with credit-based pricing ($0.01/credit or $200/mo for 25K credits). It supports DLP policies, connector governance, and publishing to Teams/M365/SharePoint. Copilot Studio is included with M365 Copilot for internal agents.

**Impact:** Department agents (HR policy bot, IT helpdesk, finance FAQ) are faster to build in Copilot Studio than in pro-code. Missing this path means over-engineering simple scenarios.

**Recommendation:**
1. Identify 2-3 internal agent use cases suitable for Copilot Studio (HR policy, IT helpdesk, onboarding)
2. Evaluate whether Copilot Studio included with M365 Copilot covers internal needs
3. Reserve pro-code Foundry for Pulser family (complex orchestration, tool execution, multi-agent)
4. Decision gate: after Entra is operational

---

### Gap D: Agent 365 Governance Layer Not Tracked (Medium)

**Current:** No awareness of Agent 365 in architecture docs or roadmap.

**Microsoft landscape confirms:** Agent 365 (preview) defines an "enterprise capabilities layer" — identity, notifications, observability, governed MCP tool access — that applies to agents regardless of build platform. It supports agent code hosted on Azure, AWS, GCP, or other providers. Introduces "agent blueprint" concept for IT-approved templates.

**Impact:** When Agent 365 goes GA, it becomes the expected governance surface for enterprise agent deployments. Early tracking prevents retrofit.

**Recommendation:**
1. Add Agent 365 to architecture watchlist
2. Ensure Foundry agents use Entra identity (prerequisite for Agent 365 compatibility)
3. Formalize MCP tool registry (`ssot/contracts/tool_contracts.yaml` → Agent 365 compatible format)
4. No immediate action required — preview only

---

### Gap E: Security Copilot Not Planned (Low)

**Current:** No Defender or Sentinel deployment. Observability targets Azure Monitor only.

**Microsoft landscape confirms:** Security Copilot is SCU-metered (provisioned + overage). Embedded in Defender/Sentinel. M365 E5 customers get included capacity.

**Impact:** Low — IPAI is pre-production. Security Copilot becomes relevant only after Defender/Sentinel are activated.

**Recommendation:** Defer. Revisit when security monitoring stack is deployed.

---

## 4. Licensing Cost Model (Estimate)

Based on Microsoft's current pricing and IPAI's likely scale:

| Offering | Model | Estimated Cost (10-user team) | When Relevant |
|---|---|---|---|
| Foundry Agent Service | Token consumption only | $50-200/mo (depends on usage) | Now |
| Azure OpenAI | Token consumption | $100-500/mo | Now |
| Entra ID | Included with M365 (P1/P2 for conditional access) | $0-90/mo | P0 |
| M365 Copilot | $30/user/mo | $300/mo (10 users) | P3 |
| Copilot Studio (included) | Included with M365 Copilot for internal | $0 | P3 |
| Copilot Studio (standalone) | $0.01/credit or $200/25K credits | $200-600/mo | If external agents needed |
| Security Copilot | $4/SCU/hr provisioned | ~$2,880/mo (1 SCU) | Deferred |
| Power BI Pro | $10/user/mo | $100/mo | P2 |
| GitHub Copilot Business | $19/user/mo | $190/mo | Now |

**Total incremental for P3 (M365 Copilot + Copilot Studio):** ~$300-600/mo for 10 users.

---

## 5. Architecture Decision: Where Each Agent Type Should Live

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Classification                       │
├─────────────────┬───────────────────┬───────────────────────┤
│   Complexity    │   Build Platform  │   Delivery Surface    │
├─────────────────┼───────────────────┼───────────────────────┤
│ Simple FAQ/KB   │ Copilot Studio    │ Teams, SharePoint     │
│ Dept workflow   │ Copilot Studio    │ Teams, M365 Copilot   │
│ Pulser family   │ Foundry Agent Svc │ Web widget, Odoo,     │
│ (complex orch)  │ + Agent Framework │ Teams (via M365 SDK)  │
│ Finance agents  │ Foundry Agent Svc │ Odoo, M365 Copilot    │
│ Multi-agent     │ Foundry Agent Svc │ API, Odoo, Teams      │
│ Security ops    │ Security Copilot  │ Defender portal       │
└─────────────────┴───────────────────┴───────────────────────┘
```

---

## 6. Doctrine Updates Required

If this analysis is accepted, the following doctrine artifacts need updates:

| Artifact | Change |
|---|---|
| `ssot/architecture/services.yaml` | Add: M365 Copilot (planned), Copilot Studio (evaluation), Agent 365 (watchlist) |
| `docs/architecture/ACTIVE_PLATFORM_BOUNDARIES.md` | Add enterprise delivery surfaces section |
| `docs/architecture/INSIGHTPULSEAI_TARGET_STATE_ARCHITECTURE.md` | Add M365 delivery channel to user journeys |
| Memory: `target_architecture_v2.md` | Already mentions M365 as delivery surface — confirm scope |
| Memory: `project_azure_integration_doctrine.md` | Add Copilot Studio and Agent 365 to doctrine |

---

## 7. Recommended Sequencing

```
P0 (Now)          P1 (ERP)           P2 (Analytics)      P3 (Enterprise Delivery)
─────────────     ─────────────      ─────────────       ─────────────────────
Entra bootstrap   Odoo stabilize     Power BI deploy     M365 Copilot licenses
Foundry agents    HA database        Fabric complete     Agents SDK wrapper
MCP tool registry Backup/restore     Databricks apps     Copilot Studio eval
                  App Insights                           Teams channel for Pulser
                                                         Agent 365 readiness
```

---

## 8. Foundry Lifecycle Contract

Microsoft frames Foundry as a unified end-to-end platform, not a single product. The canonical development lifecycle has four stages that map directly to InsightPulse AI's agent development workflow:

| Stage | Foundry Capability | IPAI Implementation |
| ----- | ------------------ | ------------------- |
| **Selection** | Model catalog, multi-provider (OpenAI, Anthropic, Fireworks) | `data-intel-ph-resource` model deployments |
| **Optimization** | Fine-tuning, prompt engineering, RAG grounding | AI Search (`srch-ipai-dev`) + Odoo context builder |
| **Observability** | Evaluation, tracing, App Insights integration | `ipai.copilot.telemetry` → App Insights |
| **Security** | Red-teaming, content safety, Entra governance | Entra ID (planned), action queue human-in-loop |

**Key distinction:** The Microsoft sample repo (`microsoft/microsoft-foundry-e2e-js`) is a learning/buildathon reference, not a deployment template. The InsightPulse AI canonical implementation remains Odoo + Azure-native infra + Foundry-backed agents. The lifecycle model above is the adoptable artifact; the repo structure is not.

**Portal + SDK duality:** Foundry exposes both a portal surface (`ai.azure.com`) and a code-first SDK. IPAI uses the SDK path exclusively (`foundry_service.py`, `tool_executor.py`). Portal is for exploration and evaluation, not runtime authority — consistent with existing policy `portal_ui_is_not_runtime_authority: true`.

---

## 9. Source Attribution

This analysis is based on:
- Microsoft Copilot & Agent Offerings Landscape research (Mar 2026) — provided as conversation input
- Enterprise benchmark audit: `docs/audits/ODOO_AZURE_ENTERPRISE_BENCHMARK.md` (2026-03-24)
- SSOT: `ssot/architecture/services.yaml` v1.0.0 (2026-03-25)
- Service matrix: `infra/ssot/azure/service-matrix.yaml` v1.2 (2026-03-21)
- Platform boundaries: `docs/architecture/ACTIVE_PLATFORM_BOUNDARIES.md` (2026-03-25)
- Project memory: `target_architecture_v2.md`, `project_azure_integration_doctrine.md`

---

*Generated 2026-03-25. Requires commercial validation of pricing and licensing prerequisites.*
