# Examples — sap-security-operations

## Example 1: Identity integration

**Input**: SAP guidance recommends Entra ID as identity provider for SAP applications

**Output**:
- Security domain: Identity
- Benchmark: Entra-first IdP with SSO for ERP workloads
- Source: Secure SAP on Microsoft Cloud, Module 6
- Translation: Entra app registration for Odoo, Foundry, VS Code (C-35)
- Out of scope: SAP-specific SAML/principal propagation to BTP
- Risk: If skipped, identity remains fragmented across Keycloak/local auth

## Example 2: Sentinel monitoring

**Input**: SAP guidance recommends Sentinel for SAP workload monitoring and threat detection

**Output**:
- Security domain: SIEM
- Benchmark: Centralized SIEM with workload-specific detection rules
- Source: Secure SAP on Microsoft Cloud, Module 6
- Translation: Sentinel for Azure workload monitoring (ACA, PG, Front Door logs)
- Out of scope: SAP-specific Sentinel connector (requires SAP system)
- Risk: Without SIEM, security events across Azure resources are unmonitored
