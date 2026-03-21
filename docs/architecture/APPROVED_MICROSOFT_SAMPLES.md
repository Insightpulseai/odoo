# Approved Microsoft Sample References

> Curated list of Microsoft/Azure sample code approved as reference implementations.
> Samples not listed here are not canonical unless explicitly approved.

---

## SAP Integration Samples

| Sample | Status | Use As |
|--------|--------|--------|
| **SAP Cloud SDK on Azure Functions Quickstart** | Approved | Thin adapter reference for event/webhook-style SAP integration via OData |
| **SAP Cloud SDK on Azure App Service Quickstart (TypeScript)** | Approved | Longer-lived SAP adapter service reference |
| **SAP CAP on Azure App Service Quickstart** | Reference only | App-pattern reference; Cosmos DB for PostgreSQL does **not** match platform doctrine |
| SAP NetWeaver 2-tier / 3-tier templates | Excluded | SAP landscape hosting — not in scope |
| SAP LaMa templates | Excluded | SAP landscape hosting — not in scope |
| SAP HANA Azure NetApp Files templates | Excluded | SAP landscape hosting — not in scope |
| S/4HANA fully activated appliance | Excluded | SAP landscape hosting — not in scope |
| SAP file server / ILM store templates | Excluded | SAP landscape hosting — not in scope |

### Governing Rule

> SAP is an integrated external enterprise surface. Use Azure Functions or App Service with SAP Cloud SDK for adapter services. Do not adopt SAP infrastructure hosting templates as canonical platform architecture unless SAP runtime hosting is explicitly in scope.

---

## Classification Key

| Status | Meaning |
|--------|---------|
| **Approved** | May be used as a baseline or reference implementation |
| **Reference only** | Study the pattern, but do not adopt the infrastructure/DB choices |
| **Excluded** | Not aligned to target state; do not use unless scope explicitly changes |

---

*Last updated: 2026-03-21*
