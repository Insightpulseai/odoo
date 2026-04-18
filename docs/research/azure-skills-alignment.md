# Research Report: Azure Skills & Copilot SDK Alignment
# Target: Pulser for Odoo (Q3 2026 GTM)
# Date: 2026-04-18

## 1. Executive Summary
Following the deep research into `https://github.com/microsoft/azure-skills.git` and the Microsoft Learn documentation for custom skills, we have identified the canonical architecture for building "Microsoft-Native" agentic capabilities. Pulser for Odoo will adopt the **Azure Agent Plugin** pattern to ensure seamless integration with GitHub Copilot, Microsoft Copilot, and Azure AI Foundry.

## 2. The "Gold Standard" Skill Architecture
The official `azure-skills` repository utilizes a modular, folder-based structure that we must adopt for all `ipai_*` agentic skills:

- **Structure**: Each capability is a directory containing a `SKILL.md` file (Instructions) and a `references/` directory (Implementation details/SDK guides).
- **Metadata**: Every `SKILL.md` must contain YAML frontmatter with a unique `name` and a high-fidelity `description` (this is the trigger mechanism for AI discovery).
- **Workspace Standard**: For AI Foundry integrations, we will implement the `.foundry/` workspace convention, specifically the `agent-metadata.yaml` contract for project endpoints and model routing.

### 3.1 Microsoft Learn MCP Tools
The official **Microsoft Learn MCP Server** (`https://learn.microsoft.com/api/mcp`) is the canonical source for documentation research.
- **`microsoft_docs_search`**: Target technical concepts, limits, and tutorials.
- **`microsoft_docs_fetch`**: Retrieve high-fidelity article content for "Copilot-native" knowledge ingestion.
- **`microsoft_code_sample_search`**: Search for GitHub-hosted Azure samples (e.g., Odoo + ACA Bicep templates).

### 3.2 Azure AI Foundry VS Code Integration
The **Microsoft Foundry for Visual Studio Code** extension is the mandatory local developer surface.
- **Capability**: Allows direct management of Foundry Projects, ACR image pushes, and Agent playgrounds from the IDE.
- **Workflow**: `Foundry Resource` (Cloud) → `Foundry Project` (Management Plane) → `VS Code Extension` (Local Dev).
The `microsoft-foundry` skill in the official repo identifies several mission-critical patterns for Pulser:

- **Agent Types**: Distinction between `Prompt` (LLM-backed) and `Hosted` (Container-based/Odoo-integrated) agents.
- **Observability**: Integration with `trace` and `observe` sub-skills to harvest production traces into evaluation datasets.
- **SDK Compliance**: 
    - **Document Intelligence**: Finalized the Python SDK `1.0.x` contract—must use positional/keyword `body=` for `begin_analyze_document` (fixing previous `analyze_request` version drift).
    - **Identity**: Mandatory use of `DefaultAzureCredential` for all service-to-service flows (Entra ID).

## 4. GTM Alignment Checklist
To align with the **AI Business Solutions** solution area, Pulser's Marketplace offer must:
1. Provide a self-contained Skill Pack (compatible with the Azure Agent Plugin).
2. Use the `.foundry` workspace standard for tenant-specific configuration.
3. Support the "Transactable SaaS" landing page requirements via Entra ID SSO.

- [x] Migrate `addons/ipai/ipai_pulser_assistant` instructions to the `SKILL.md` + `references/` pattern. (COMPLETED: `agents/skills/` migration)
- [x] Implement `.foundry/agent-metadata.yaml` scaffolding in the Odoo deployment template. (COMPLETED: Synchronized with SEA resources)
- [x] Finalize the `ipai-marketplace-fulfillment-bot` using the `entra-app-registration` skill patterns. (COMPLETED: Registered in Entra SSOT)

## 6. Conclusion: Ignition Complete (2026-04-18)
The **GTM Ignition** phase is officially concluded. The Pulser for Odoo platform has been successfully audited and synchronized with the verified "System of Record" in the Microsoft Azure portal. All specialized agents are grounded in canonical Microsoft technical topics and are ready for Marketplace deployment.

---
*Created by Antigravity (InsightPulse AI Engineering Assistant)*
