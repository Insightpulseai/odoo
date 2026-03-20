# CP-1: Identity & MFA Assessment

## Date: 2026-03-20

## Tenant

- Tenant: `insightpulseai.com` (`ceoinsightpulseai.onmicrosoft.com`)
- License: Microsoft Entra ID Free
- Users: 4

## Admin Identities

| Identity | Type | MFA Status |
| --- | --- | --- |
| `admin@insightpulseai.com` (Platform Admin) | Member / Internal | Enrolled |
| `emergency-admin@insightpulseai.com` | Member / Internal | In progress |
| `ceo_insightpulseai.com#EXT#` (Jake) | Member / External | Pending decision: convert to internal or keep as non-canonical |
| `s224670304_deakin.edu.au#EXT#` | Guest | N/A for go-live |

## Authentication Methods Policy

- Microsoft Authenticator: enabled for all users
- Temporary Access Pass: enabled for all users
- Software OATH: enabled for all users
- Email OTP: enabled for all users
- Registration campaign: to be enabled

## CP-1 Verdict

- CP-1a (policy/config): **PASS** — methods enabled, correct policy surface
- CP-1b (enrollment): **PARTIAL** — admin enrolled, emergency-admin in progress
- CP-1c (identity cleanup): **OPEN** — Jake external identity decision pending

## Next Actions

- Complete emergency-admin MFA enrollment (interactive)
- Enable registration campaign via Entra portal (Graph API needs Policy.ReadWrite.AuthenticationMethod)
- Decide: convert Jake external → internal or keep non-canonical
- Move automation to workload identities (mandatory MFA Phase 2)
