# CP-1: Identity & MFA Assessment Evidence

## Date: 2026-03-19
## Source: Entra admin center screenshots

## Tenant Overview

| Field | Value |
|-------|-------|
| Tenant ID | 402de71a-87ec-4302-a609-fb76098d1da7 |
| Primary domain | insightpulseai.com |
| Plan | Entra Free |
| Identity Secure Score | 23.33% |
| Users | 4 |
| Groups | 12 |
| Apps | 4 |
| Devices | 0 |

## Users

| Display Name | Type | Identity Source | Role |
|-------------|------|-----------------|------|
| Emergency Admin | Member | Cloud | Break-glass |
| Jake Tolentino | Member | MicrosoftAccount | Global Administrator |
| JAKE TOLENTINO | Guest | ExternalAzureAD | External (Deakin) |
| Platform Admin | Member | Cloud | Admin |

## Authentication Methods Enabled

| Method | Enabled | Target |
|--------|---------|--------|
| Microsoft Authenticator | Yes | All users |
| Software OATH tokens | Yes | All users |
| Temporary Access Pass | Yes | All users |
| Email OTP | Yes | All users |
| Passkey (FIDO2) | No | — |
| SMS | No | — |

## Authentication Strengths

3 built-in strengths defined. **None configured in Conditional Access policies.**

## Assessment

**Status: PARTIAL**

### In place
- Authentication methods enabled at tenant level
- Microsoft Authenticator available for all users
- Emergency Admin account exists
- 2 high-privileged role assignments visible

### Not in place
- No Conditional Access policies enforce MFA
- Per-user MFA enrollment status not verified from screenshots
- Identity Secure Score is 23.33% (target: >50%)
- No evidence of actual authenticator registration per user

## Actions needed to close CP-1

1. Verify per-user MFA registration (check Per-user MFA page)
2. Create Conditional Access policy requiring MFA for admins
3. Capture enrollment evidence screenshot
4. Address Identity Secure Score recommendations
5. Confirm Emergency Admin has MFA registered independently

## Risk note

Without Conditional Access enforcement, MFA is optional even though methods are enabled. This means admin accounts could authenticate with password-only. For go-live, at minimum the Global Administrator and Platform Admin accounts must have verified MFA enrollment.
