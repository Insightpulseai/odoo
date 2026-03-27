# Agent Platform Architecture

This document defines the canonical contract for Agentic AI systems within the InsightPulseAI ecosystem, synthesizing the **Google Component Model** and **Azure Orchestration Patterns**.

## 1. Governance Principles
1. **Deterministic Over Agentic**: Do not use agentic workflows for simple, deterministic tasks (e.g., direct classification).
2. **Stateless Scalability**: All agent applications MUST be stateless. Session and operation state MUST be externalized to Odoo (SOR) or Supabase (Control Plane).
3. **Decoupled Tools**: All reusable capabilities must be exposed via **Model Context Protocol (MCP)**.
4. **Explicit Orchestration**: The choice of orchestration pattern MUST be documented in the agent's spec bundle.

## 2. The Multi-Layer Component Contract (Google Cloud)
- **Frontend**: Odoo Copilot (OWL), Telegram Bot, or Slack Bridge.
- **Agent Development Framework**: Python (LangChain/Semantic Kernel) or n8n.
- **Tools**: MCP-hosted functions (Retrieval, Execution, API).
- **Memory**: Database-backed history and cross-session state.
- **Runtime**: Azure Container Apps (ACA) / n8n.
- **Execution Patterns**: Explicit mapping to the Azure pattern matrix.

## 3. Orchestration Pattern Matrix (Azure)

### A. Sequential (Deterministic Flows)
- **Use Case**: AP Invoice Processing, Bank Reconciliation.
- **Logic**: A -> B -> C with clear linear dependencies.
- **Requirement**: Strong schema validation between steps.

### B. Maker-Checker (Quality Gates)
- **Use Case**: Spec Reviews, Policy Violations, Production Releases.
- **Logic**: Specialist Agent -> Critic Agent -> Result.
- **Requirement**: Explicit pass/fail criteria and iteration caps.

### C. Concurrent (Parallel Analysis)
- **Use Case**: Multi-perspective risk scoring, ensemble reasoning.
- **Logic**: Agents run in parallel; outputs are aggregated.
- **Constraint**: No shared state dependencies during execution.

### D. Handoff (Dynamic Routing)
- **Use Case**: General Copilot triage, Escalation handling.
- **Logic**: Primary Dispatcher -> Specialist Agent.
- **Constraint**: Use only when the specific specialist is not knowable at launch.

### E. Magentic (Autonomous Planning)
- **Use Case**: Autonomous investigation and remediation.
- **Logic**: Manager Agent -> Task Ledger -> Sub-Agents.
- **Governance**: Requires strict human-in-the-loop (HITL) gates.

---
**Authority**: Agent Factory V2 Policy
**Standard Compliance**: Google Cloud Architecture + Azure AI Design Guidelines
