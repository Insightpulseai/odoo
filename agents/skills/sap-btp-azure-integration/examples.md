# Examples — sap-btp-azure-integration

## Example 1: SSO integration

**Input**: SAP BTP recommends Entra ID as identity provider for SSO across SAP apps

**Output**:
- Integration domain: Identity / SSO
- Benchmark: Entra-first SSO with OIDC/SAML for all platform services
- Source: Introduction to SAP on Microsoft Cloud, Module 2
- Translation: Entra app registration to Odoo OIDC to Foundry to VS Code (C-35)
- Protocol: OIDC with authorization code flow
- Risk: Without centralized SSO, each service has separate auth
