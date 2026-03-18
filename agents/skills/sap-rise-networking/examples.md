# Examples — sap-rise-networking

## Example 1: VNet peering

**Input**: SAP RISE guidance recommends VNet peering between customer and SAP-managed subscriptions

**Output**:
- Connectivity scenario: VNet peering
- Benchmark: Peering between workload VNet and shared-services VNet
- Source: Explore Azure networking for SAP RISE, Module 5
- Translation: ACA environment VNet integration with hub VNet for shared PG, Key Vault
- Shared responsibility: Azure manages ACA networking; platform team manages VNet rules
- Risk: Without VNet integration, ACA uses default managed networking (less control)
