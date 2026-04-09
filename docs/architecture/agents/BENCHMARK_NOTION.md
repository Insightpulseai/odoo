# Benchmark: Agent Factory vs. Notion 3.0 Agents

## Executive Summary

**Notion 3.0** introduces a powerful, general-purpose "Agent" system designed to automate knowledge work across a broad workspace. The **Agent Factory (Odoo/BIR focused)** is a specialized, hardened alternative designed for **high-stakes, transactional ERP environments**.

| Dimension | Notion 3.0 Agents | Agent Factory (Tax Pulse) |
| :--- | :--- | :--- |
| **Logic/Context** | General knowledge & productivity | **Vertical ERP (Odoo) & Tax (BIR)** |
| **Customization** | No-code personality & memory pages | **Contract-first SSOT & Persona Prompts** |
| **Safety Model** | Granular Row-Level Permissions | **3-Agent Isolation + Fail-Closed Gates** |
| **Integrations** | Native MCP support (Slack, Jira, etc.) | **Odoo MCP + Azure AI Foundry IQ** |
| **Execution** | Autopilot (Schedules/Triggers) | **Approval-Gated Transactional Logic** |
| **Verification** | User-defined "Memory" checks | **Expert-in-the-loop & Eval-Gate (≥0.8)** |

---

## 1. Domain: Breadth vs. Depth

**Notion 3.0** is "horizontally" agentic. It can summarize a document, find an answer in Slack, or update a generic task database. It excels at "busywork" across diverse tools.

**Agent Factory** is "vertically" specialized. It doesn't just "update a database"; it **computes withholding tax** based on PH Revenue Regulations, **validates journal entries**, and **generates eFPS-compliant XML**. It is built for environments where a mistake isn't just a typo—it's a regulatory penalty.

---

## 2. Safety & Governance

Notion 3.0 relies on **granular row-level permissions** to keep agents in check. This is effective for document access but insufficient for financial transactions.

**Agent Factory Hardening**:
*   **3-Agent Split**: Isolation between user-facing **Advisory** (read-only) and internal-only **Actions** (write-capable).
*   **Fail-Closed Release Gates**: A release candidate is blocked if it regresses in groundedness or fails a safety evaluation.
*   **Bounded Writes**: Writes are not just "allowed"; they are restricted to a **model/field allowlist** and guided by Odoo's native state machine.

---

## 3. Automation vs. Orchestration

Notion's **Autopilot** is designed for background task execution (e.g., "every Friday morning"). 

The Agent Factory's **Supervisor/Router** is designed for **deterministic workflow orchestration**. It doesn't just run on a schedule; it manages **Exactly-Once** delivery of instructions and provides a "human-expert" checkpoint before any high-risk tax filing or payment instruction is finalized.

---

## 4. Connectivity: MCP & Odoo-Native

Both systems embrace the **Model Context Protocol (MCP)** for tool connectivity.
*   **Notion 3.0** uses MCP to bridge knowledge silos (GitHub, Slack, Jira).
*   **Agent Factory** uses MCP to create a high-fidelity bridge between the AI reasoning layer and the **Odoo 18.0 ORM**, ensuring that tools have deep, type-safe access to the ERP's business logic.

---

## Conclusion

Notion 3.0 Agents are the benchmark for **team productivity and knowledge synthesis**. The Agent Factory is the benchmark for **Enterprise Control and Regulatory Compliance**.

For companies running **Odoo in the Philippines**, the Agent Factory (with Tax Pulse) provides the "Tax Guru" expertise and "Fail-Closed" safety that a general-purpose productivity agent cannot replicate.
