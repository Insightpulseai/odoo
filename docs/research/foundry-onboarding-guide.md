# Developer Guide: Azure AI Foundry Onboarding

> Canonical workflow for Pulser for Odoo developers transitioning to the "Foundry-Native" management plane.

---

## 1. Prerequisites
- **Azure CLI**: `az login` to your InsightPulseAI subscription.
- **Azure Developer CLI**: `azd auth login`.
- **VS Code Extension**: Install [Microsoft Foundry for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.microsoft-foundry).
- **Entra ID**: Ensure your account has the `Contributor` and `Cognitive Services Contributor` roles on the AI Foundry Resource Group.

## 2. Local Environment Setup (macOS)
On Apple Silicon Macs, the Azure CLI tools are typically installed in `/opt/homebrew/bin/`, which may not be in your default shell `PATH`.

### 2.1 Fix Path (Persistent)
Add the following to your `~/.zshrc` or `~/.bash_profile`:
```bash
export PATH="/opt/homebrew/bin:$PATH"
```

### 2.2 Verify Tools
```bash
az version
azd version
```

> [!NOTE]
> If `azd version` panics with "Operation not permitted" regarding `/Users/tbwa/.azd`, ensure you have proper filesystem permissions or try running the command from a native terminal with Full Disk Access.

### 2.3 Python SDK
The project uses `requirements-ai.txt` for Foundry-native development.
```bash
source .venv/bin/activate
pip install -r requirements-ai.txt
```

## 3. Workspace Setup (.foundry)
Every `ipai_` agent or Odoo wrapper project must initialize a `.foundry` directory at the root:

```bash
mkdir .foundry
touch .foundry/agent-metadata.yaml
```

### 3.1 agent-metadata.yaml Example
```yaml
agentName: "pulser-assistant-ph"
defaultEnvironment: "dev"
environments:
  dev:
    projectEndpoint: "https://ipai-foundry-ph.eastus2.inference.ai.azure.com"
    azureContainerRegistry: "acripaiprod.azurecr.io"
    testCases:
      - id: "ap-invoice-extraction"
        evaluator: "rag_faithfulness"
        threshold: 0.85
```

## 4. Core Workflows

### 4.1 Model Deployment
Use the VS Code extension to browse the **Model Catalog**. 
- Select a model (e.g., `gpt-4o`).
- Right-click → **Deploy to Project**.
- Copy the deployment name into your Odoo `ir.config_parameter`.

### 4.2 Agent Testing (Playground)
Use the **Foundry Agent Playground** within VS Code to test your system prompts and tool bindings (`ipai_` MCP tools) before committing code to the Odoo module.

### 4.3 Trace Observation
1. Enable **Application Insights** in your Foundry Project.
2. Review operational traces for failed Odoo document extractions.
3. Harvest "Gold" traces into the `datasets/` folder for future evaluation runs.

---
*Created per GTM-spec Section 6 alignment (2026-04-18)*
