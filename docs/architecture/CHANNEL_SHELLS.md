# Channel Shell Architecture — Pulser for Odoo

This document formalizes the "One Core, Three Shells" model, defining how Pulser for Odoo is delivered across enterprise and engineering surfaces.

---

## 1. The "One Core, Three Shells" Model (BOM 5)

Pulser is architected as a centralized Core authority delivered through specialized Channel Shells.

### Pulser Core (The Hub)
- **Authority**: Odoo CE 18 (System of Action and Record).
- **Reasoning**: Azure AI Foundry (Grounding and Logic).
- **Identity**: Microsoft Entra ID (Source of Identity).

### The Three Shells (The Spokes)
1. **Web Shell (B2B Dashboard)**: The native Pulser web experience (React/Next.js) for high-density finance tasks.
2. **Enterprise Shell (M365/Teams)**: Power by **Microsoft Agents SDK**. Targeted at casual/finance-proximate users within the productivity suite.
3. **Engineering Shell (DevOps/Ops)**: Powered by **GitHub Copilot SDK**. Targeted at internal SREs, developers, and platform operators.

## 2. Shell Integration Matrix

| Shell | Optimized SDK | Host Surfaces | Primary Interaction |
|-------|---------------|---------------|---------------------|
| **Enterprise** | Microsoft Agents | Teams, Outlook, Copilot | Activity / Graph / Adaptive Cards |
| **Engineering**| GitHub Copilot | VSC, CLI, GitHub.com | JSON-RPC / CLI / Markdown |
| **Web** | Native / IPAI | Browser | High-fidelity UI / Dashboards |

## 3. Authentication and Handoff

Security is maintained through a unified identity bridge.

- **Identity Bridge**: Microsoft Entra ID (OIDC).
- **Token Handoff**: Shells must obtain an OIDC token from the Customer Entra Tenant.
- **Core Access**: The token is passed to the Pulser Core via the **Agent Runtime** for authorization against Odoo records.
- **Stateless Shells**: Shells are prohibited from persisting business state. All transactional outcomes must be written back to the Pulser Core (Odoo).

## 4. Communication Protocols

- **Enterprise Shell**: Uses the **Bot Framework Activity** protocol for message routing and state management.
- **Engineering Shell**: Uses the **GitHub Copilot JSON-RPC** protocol for IDE-local and repo-aware command execution.
- **Core API**: All shells communicate with the Core via protected **Agent-as-an-API (A2A)** endpoints.

---

*Last updated: 2026-04-11*
