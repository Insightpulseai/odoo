# W9 Boundary Model Evidence

- Scope: codify W9 Studio as a Google Workspace OU/persona boundary, an Odoo company boundary when business-entity separation is required, and not a separate Entra tenant by default
- Local stamp: `20260423-0131` (Asia/Manila)
- Source baseline:
  - `docs/architecture/w9-google-workspace-integration.md`
  - `platform/ssot/identity/directory-authority-matrix.yaml`
  - `docs/tenants/TENANCY_MODEL.md`

## Files added

- `platform/contracts/business/company-boundaries.yaml`
- `platform/contracts/identity/test-matrix.yaml`
- `docs/architecture/W9_BOUNDARY_MODEL.md`

## Verification

- `PASS` Both new YAML contracts parsed successfully
- `PASS` Company-boundary contract states that a Google Workspace OU is not an Odoo company and not an Entra tenant
- `PASS` W9 Google Workspace users `business@`, `finance@`, and `accounts@w9studio.net` are captured as the W9 persona cohort
- `PASS` W9 is mapped to Odoo company target `2`, matching the existing tenancy model decision record
- `PASS` Test matrix explicitly keeps normal Git/CI branching and requires Odoo company context for W9 business-entity testing

## Notes

- This pass codifies the boundary model only. It does not create or validate any live Odoo company, Entra tenant, or Google Workspace policy object.
