# Architecture: Hybrid MCP Governance (Microsoft-Native)

## 1. Vision
The Agent Factory V2 is transformed into a **Microsoft-Native** autonomous platform through the multi-cell integration of the Microsoft MCP suite.

## 2. Functional MCP Cells

### 🟦 Ingestion & Automation (The "Sensors")
- **Markitdown MCP**: Normalizes diverse vendor inputs (PDF, Excel, Audio) into Markdown for the AI extraction pipeline.
- **Playwright MCP**: Conducts synthetic UI testing of Odoo gates and scrapes legacy bank portals for reconciliation data.

### 🟩 Intelligence & Knowledge (The "Brain")
- **Azure AI Foundry MCP**: Self-governed model evaluation, deployment, and benchmark runs.
- **Microsoft Learn MCP**: Real-time RAG against official Microsoft documentation for Odoo-Azure operational support.
- **NuGet MCP**: Autonomous dependency management for Odoo custom addons.

### 🟥 Governance & Security (The "Guardians")
- **Microsoft Entra MCP**: Natural language querying of organizational identity to verify approval hierarchies.
- **Microsoft Sentinel MCP**: Proactive security data exploration for the Factory's audit lake.
- **Azure DevOps MCP**: Multi-channel engineering lifecycle management.

### 🟨 Analytics & Real-Time (The "Visibility")
- **Fabric Real-Time Intelligence**: KQL-driven querying of event streams for millisecond-latency performance monitoring.
- **Clarity MCP**: User behavior analytics for the Odoo Copilot OWL widget.

## 3. Integrated Workflow Scenario: "The Sentinel Guard"
1. **Trigger**: An unauthorized configuration change is detected in Azure AKS.
2. **Analysis**: **Microsoft Sentinel MCP** identifies the source principal.
3. **Verification**: **Microsoft Entra MCP** checks if the principal is a member of the 'Emergency DevOps' group.
4. **Action**: If unauthorized, the Agent uses **AKS MCP** to roll back the configuration and opens a priority incident in **Azure DevOps**.

## 4. Roadmap (Phase 31+)
- [ ] **Markitdown Normalizer**: Implement at the n8n ingestion boundary for all finance agents.
- [ ] **Sentinel Auditor**: Automated security scans of the Agent Evidence Pack vault.
- [ ] **Microsoft Learn RAG**: Enable the Odoo Copilot to consult `MicrosoftDocs` for complex Azure setup assistance.
