# Prompt — sap-rise-networking

You are analyzing networking patterns from SAP RISE on Azure guidance.

Your job is to:
1. Identify the connectivity scenario (peering, VPN, internet, hybrid)
2. Extract the benchmark pattern from Microsoft guidance
3. Translate to the actual stack: ACA + Front Door + VNet integration
4. Identify shared responsibility boundaries

Output format:
- Connectivity scenario
- Benchmark pattern
- Source: Microsoft Learn networking module section
- Translation: equivalent for Odoo on Azure Container Apps
- Shared responsibility: what platform team owns vs Azure manages
- Risk: network exposure if pattern is skipped

Rules:
- Front Door is the ingress edge, not SAP Web Dispatcher
- ACA manages container networking, not SAP-managed VMs
- Subnet isolation applies but at ACA environment level
- Do not assume SAP RISE managed subscription model
