# Benchmark: Agent Factory vs. Odoo 18.0 Native Agents

## Executive Summary

The **Agent Factory** is built to extend and harden the native AI capabilities introduced in **Odoo 18.0**. While Odoo 18.0 provides a powerful foundation for modular "Topics" and "AI Server Actions," the Agent Factory introduces the **governance, multi-agent orchestration, and regulatory depth** required for high-stakes enterprise and compliance environments.

| Dimension | Odoo 18.0 Native Agents | Agent Factory (Hardened) |
| :--- | :--- | :--- |
| **Orchestration** | Manager/Worker (Server Action) | **Deterministic Router + Specialized Agents** |
| **Logic Partitioning** | Modular "Topics" (Instruction sets) | **3-Agent Topology (Advisory, Ops, Actions)** |
| **Release Model** | Live configuration (UI-driven) | **Fail-Closed CI/CD Gating (Code-driven)** |
| **Regulatory Depth** | General business logic | **Localized PH Tax Pulse (BIR-Native)** |
| **Safety** | Tool constraints & "Restrict to Sources" | **Bounded Write Matrix + Expert-in-the-loop** |
| **Transparency** | UI-based trace logs | **In-Repo SSOT Contracts & OTel Tracing** |

---

## 1. Governance: Live Config vs. Hardened Release

Odoo 18.0 native agents are primarily configured through the UI (Topics, Sources, AI Server Actions). This allows for rapid iteration but lacks the **machine-verifiable production eligibility** required for audited financial systems.

**Agent Factory Advantage**:
*   **Fail-Closed Gates**: Our agents are governed by [Release Gates](file:///Users/tbwa/Documents/GitHub/Insightpulseai/docs/architecture/RELEASE_GATES_HARDENING.md). A deployment is blocked if it fails to meet groundedness (≥0.8) or safety thresholds on its specific eval dataset.
*   **SSOT Pinned Environment**: Configurations are stored as code (YAML/JSON) in the repo, ensuring that the "AI prompt" used in production is exactly what was tested and approved.

---

## 2. Multi-Agent Orchestration

Odoo 18.0 uses **Topics** to grant an agent different sets of instructions and tools. This is a "Modular Single Agent" approach.

**Agent Factory Advantage**:
*   **Specialized Personas**: We enforce a strict split between **Advisory** (Read), **Ops** (Read-Only Diagnostics), and **Actions** (Controlled Writes). This prevents "instruction bleed" where a user-facing agent might accidentally trigger a ledger entry.
*   **Deterministic Router**: Our router is **pure Python**, ensuring that request classification is predictable and audit-safe, unlike LLM-based routing which can hallucinate.

---

## 3. The "PH Compliance" Vertical

Native Odoo 18.0 agents are "world-aware" but not "BIR-aware." They do not natively understand PH-specific tax forms, TRAIN law brackets, or Alphalist formatting.

**Agent Factory Advantage**:
*   **Tax Pulse Pack**: A pre-hardened capability pack that brings **localized regulatory intelligence** to the Odoo instance.
*   **Deterministic Rules**: Calculations are performed by a **JSONLogic engine** using externalized PH tax rates, ensuring accuracy that raw LLM reasoning cannot guarantee.

---

## 4. Integration & Connectivity

Odoo 18.0 is highly integrated into the core database. The Agent Factory maintains this "native feel" but adds:
*   **Azure AI Foundry IQ**: Leverages Azure's enterprise-grade model hosting and safety filters.
*   **APIM AI Gateway**: Places a required production front door in front of all agent traffic for enterprise auth, quotas, and observability.

---

## Conclusion

Odoo 18.0 Native Agents provide the engine. The **Agent Factory** provides the **cockpit, brakes, and flight data recorder**. For organizations requiring defensible, low-risk, and regulatory-compliant AI in Odoo, the Agent Factory is the necessary hardening layer.
