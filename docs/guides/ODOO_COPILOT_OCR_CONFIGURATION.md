# IPAI Odoo Copilot & Document Intelligence Configuration

## Overview
To connect the Odoo runtime to the Azure AI plane (Foundry and Document Intelligence), the **`ipai_foundry`** module must be configured.

## 1. Setup Azure Resources
- **Azure Foundry**: Deploy a model (e.g., GPT-4o) and capture the **Target URI** and **API Key**.
- **Azure Document Intelligence**: Create a resource and capture the **Endpoint** and **API Key**.

## 2. Odoo Configuration
Navigate to **IPAI > Configuration > Settings** and input the captured credentials:
| Field | Value |
| :--- | :--- |
| **Foundry Endpoint** | `https://your-foundry-resource.azure.com/...` |
| **Foundry API Key** | `********************************` |
| **Doc Intel Endpoint** | `https://your-ocr-resource.cognitiveservices.azure.com/` |
| **Doc Intel Key** | `********************************` |

## 3. Core Odoo Actions
The following actions enable the "Foundry + OCR" workflow:

### A. Document Ingestion (OCR)
- **Action**: `action_ipai_ingest_ocr` (defined in `ipai_ap_invoice`)
- **Process**: 
  1. Sends binary attachment to Azure Document Intelligence.
  2. Receives structured JSON.
  3. Maps fields to `account.move` (Vendor, Date, Lines).

### B. Copilot Reasoning (Foundry)
- **Model**: `ipai.foundry.connector`
- **Method**: `call_foundry_completion(prompt)`
- **Process**:
  1. Wraps the prompt in the **IPAI Constitution** system message.
  2. Enforces citation requirements.
  3. Returns governed insights/plans.

### C. Release Gate Validation
- **Method**: `action_ipai_rehearse_staging`
- **Process**: Performs the machine-readable audit before any production state transition.

## 4. Troubleshooting
Check **Settings > Technical > Parameters > System Parameters** for keys prefixed with `ipai.`.
