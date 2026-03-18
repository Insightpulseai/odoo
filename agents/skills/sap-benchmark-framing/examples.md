# Examples — sap-benchmark-framing

## Example 1: Environment separation

**Input**: SAP on Azure guidance recommends hub/non-prod/prod/DR environment separation

**Output**:
- Pattern: Environment separation with landing zones
- Classification: BENCHMARK
- Source: SAP on Azure workload documentation, planning guide
- Translation: Odoo uses 4 canonical databases (odoo_dev, odoo_dev_demo, odoo_staging, odoo) across local and Azure Container Apps environments
- Risk: If treated as integration, would require SAP-style landing zone tooling instead of ACA-native environment model

## Example 2: AvaTax marketplace

**Input**: AvaTax is available on Azure Marketplace

**Output**:
- Pattern: Tax calculation engine
- Classification: BENCHMARK (no plan available for PH market)
- Source: Azure Marketplace listing, reference-benchmarks.md
- Translation: Odoo fiscal positions + ipai_bir_tax_compliance module
- Risk: If treated as integration, would block on marketplace procurement path that doesn't exist for PH
