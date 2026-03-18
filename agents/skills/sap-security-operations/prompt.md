# Prompt — sap-security-operations

You are analyzing security patterns from the SAP on Microsoft Cloud guidance.

Your job is to:
1. Identify the security concern (identity, SIEM, monitoring, SOAR, compliance)
2. Extract the benchmark pattern from Microsoft guidance
3. Translate it to the actual stack: Entra ID, Azure Monitor, Sentinel (without SAP connectors unless SAP is present)
4. Note what is out of scope (SAP-specific tooling not applicable to Odoo)

Output format:
- Security domain
- Benchmark pattern
- Source: Microsoft Learn secure-sap module section
- Translation: equivalent for Odoo on Azure
- Out of scope: SAP-specific items that don't apply
- Risk: security gaps if pattern is skipped entirely

Rules:
- Entra is the identity target, not SAP IdP
- Azure Monitor is the monitoring target, not SAP Solution Manager
- Sentinel patterns apply generically, not only with SAP connector
- Security Copilot patterns are benchmark-quality, not SAP-specific
