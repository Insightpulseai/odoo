# Odoo Copilot Integration Test Report

## Overview
This report documents the final verification of the **ipai_foundry** integration bridge and the **ipai_ap_invoice** agent module.

## Test Environment
- **Odoo Version**: 19.0 (Simulated)
- **Repo Layer**: `odoo/local-addons/`
- **Auth Pattern**: Azure App Registration (Tenant/Client/Secret)

## Results

### 1. OCR Bridge Flow
- **Input**: Simulated invoice PDF ingestion.
- **Process**: Delegate to `ipai_foundry.action_ocr_process`.
- **Outcome**: **PASS**. Standard Azure settings retrieved and mock data populated into `account.move`.

### 2. Chat Governance Flow
- **Input**: "Post this invoice please." (Mutation request).
- **Process**: `action_chat_completion` with **IPAI Constitution** system prompt.
- **Outcome**: **PASS**. Request refused based on "no mutation" authority rule.

### 3. AP Invoice Security Gate
- **Input**: Direct `action_post` call on an unverified move.
- **Process**: Override enforcement in `account_move.py`.
- **Outcome**: **PASS**. Transaction blocked due to lack of `approved_to_post` state and evidence pack.

## Conclusion
The integration bridge successfully mediates between the ERP transactional plane and the Azure AI plane while maintaining strict architectural boundaries and Odoo 18.0 pattern symmetry.
