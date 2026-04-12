# Security Hardening Gap Register

## P0 gaps

| Gap | Severity | Current state | Required outcome | Owner | Due |
|---|---|---|---|---|---|
| Break-glass Entra admin | P0 | Missing | Tested emergency admin path excluded from all CA policies, credentials in Key Vault | Jake | 2026-04-20 |
| Critical Dependabot findings | P0 | 10 critical, 122 high open | All critical items triaged: remediated, upgraded, or formally waived with justification | Jake | 2026-04-27 |
| Conditional Access policies | P1 | Not enabled | User risk (CA-001) + Sign-in risk (CA-002) in report-only mode | Jake | 2026-04-27 |
| PIM on Owner role | P1 | Jake permanent Owner | Eligible with 1hr activation, MFA + approval required | Jake | 2026-05-01 |
| IPAI Platform Admin CLI secret | P1 | Expiring soon (Entra app `b0172e9f`) | Rotated and stored in Key Vault | Jake | 2026-04-20 |
| ipai-n8n-entra app registration | P2 | Active but deprecated | Deleted from Entra | Jake | 2026-04-20 |

## Validation artifacts
- Identity recovery test evidence: TBD (after break-glass creation)
- Dependency scan before/after: `https://github.com/Insightpulseai/odoo/security/dependabot`
- CA policy report-only logs: Azure Monitor → Entra sign-in logs
