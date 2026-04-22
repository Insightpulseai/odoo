# W9 Boundary Model

## Doctrine

> Google Workspace OU = persona and policy grouping.
> Odoo company = business entity boundary.
> Separate tenant = organization identity boundary.

W9 Studio in Google Workspace is currently a **Google Workspace organizational unit**
with active users:

- `business@w9studio.net`
- `finance@w9studio.net`
- `accounts@w9studio.net`

That makes W9 valid as a **persona set**, **policy-scoped user group**, and
**customer-like test cohort**. It does not make W9 a separate Entra tenant or
an Odoo company by itself.

## Canonical Mapping

| Surface | W9 means |
|---|---|
| Google Workspace | Organizational unit and user personas |
| Odoo | Separate company if W9 is a distinct business/legal/accounting entity |
| Microsoft / Entra | Separate tenant only when external-org isolation is required |
| Git / CI | No special branch or environment model |

## Current Boundary Decision

- Keep W9 as a Google Workspace OU for persona and policy testing.
- Model W9 as a separate Odoo company when business, accounting, or visibility boundaries are required.
- Do not create a separate Entra tenant for W9 unless cross-tenant or customer-install behavior must be validated.

## Contract Anchors

- [company-boundaries.yaml](/Users/tbwa/Documents/GitHub/Insightpulseai/platform/contracts/business/company-boundaries.yaml)
- [test-matrix.yaml](/Users/tbwa/Documents/GitHub/Insightpulseai/platform/contracts/identity/test-matrix.yaml)
- [TENANCY_MODEL.md](/Users/tbwa/Documents/GitHub/Insightpulseai/docs/tenants/TENANCY_MODEL.md)
- [w9-google-workspace-integration.md](/Users/tbwa/Documents/GitHub/Insightpulseai/docs/architecture/w9-google-workspace-integration.md)
- [directory-authority-matrix.yaml](/Users/tbwa/Documents/GitHub/Insightpulseai/platform/ssot/identity/directory-authority-matrix.yaml)
