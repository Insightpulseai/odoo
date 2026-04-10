# Plan: Pulser for Odoo

> **Human-facing title**: `Pulser for Odoo`
> **Subtitle**: `Pulser Assistant for Odoo`
> **Canonical Slug**: `pulser-odoo`
> **Implementation Strategy**: Thin-bridge Odoo adapter with tri-modal agent routing.

---

## 1. Runtime Split & Architecture

The Pulser for Odoo system is split across two primary responsibility zones, following Microsoft's current architecture framing for Foundry Agents:

### 1.1 Use Foundry for:
- **Model Hosting & Agent Service**: Lifecycle and reasoning substrate.
- **Evaluations & Monitoring**: Quality and safety gates for the agent estate.
- **Guardrails**: Enterprise-ready content safety and groundedness checks.
- **Identity Boundary**: Microsoft Entra ID managed identity boundary.

### 1.2 Use Odoo / App Runtime for:
- **ERP Integration**: Context packaging (active record, user ACLs).
- **Business Workflow Logic**: Final seat of technical and accounting authority.
- **Tool Adapters**: Bounded Odoo JSON-RPC or OpenAPI connectors.
- **Chat/Session UX**: The conversational shell (OWL component).
- **Domain Orchestration**: Selecting and routing to the correct agent for the task.

### 1.3 Best-Fit Reference Strategy
To ensure a production-ready rollout, the implementation adopts these benchmarks:
1. **`foundry-agent-webapp`**: Primary reference for the app/runtime pattern and Entra ID auth.
2. **`foundry-samples`**: Primary reference for Bicep/infra and service wiring examples.
3. **`Foundry-Local-Lab`**: Reference for local RAG and multi-agent experimentation.

---

## 2. Deployment Modes

### 2.1 Pilot Mode (MVP Default)
- **Runtime**: Lightweight agent shell on Azure Container Apps.
- **Networking**: Public endpoints with WAF protection.
- **Grounding**: File-based grounding (PDF/JSON) and live Odoo RPC.
- **Monitoring**: Application Insights baseline.

### 2.2 Governed Mode (Promotion Lane)
- **Runtime**: Managed Foundry Agent Service.
- **Networking**: Private endpoints and VNet isolation.
- **Grounding**: Azure AI Search with governed lakehouse grounding (Databricks).
- **Compliance**: Expanded tracing, evaluation, and safety gates.

---

## 3. Implementation Phases

### Phase 1: Bridge Foundations
1. Define tri-modal intent schema (Informational / Navigational / Transactional).
2. Establish the `ipai_odoo_copilot` module scaffold with security groups.
3. Build the context packager and HTTP provider for Foundry.
4. Implement the audit trail within Odoo.

### Phase 2: Finance-First Grounding
1. Implement Q&A context for Accounting (move, partner, bank).
2. Build Reconciliation and Collections assistance flows.
3. Wire domain agents (Expense, Project) with bounded tool access.
4. Implement the approval-gated action mediation pipeline.

### Phase 3: Knowledge & Compliance
1. Deploy RAG-only grounding for policies and SOPs.
2. Update global references to "Pulser for Odoo".
3. Apply Foundry description patches.
4. Finalize the release contract and ship-readiness checklist.

---

## 4. Technical Constraints

1. **ORM only**: No direct SQL writes; all actions go through the Odoo ORM.
2. **Security-First**: Context packaging must respect Odoo's native record rules and field-level permissions.
3. **No LLM in Odoo**: Keep the Odoo process thin; inference logic resides in Azure.
4. **Audit Completeness**: 100% request/response coverage is non-negotiable.

---

*Last updated: 2026-04-10*
