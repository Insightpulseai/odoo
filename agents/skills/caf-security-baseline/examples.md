# Examples — caf-security-baseline

## Example 1: Initial security posture assessment

**Input**: Assess security posture for `rg-ipai-dev` environment.

**Output**:
- Secure score: 62/100
- Zero trust maturity:
  - Identity: Basic (Keycloak SSO, no Conditional Access, no PIM)
  - Network: Basic (Front Door TLS, no Private Link, no NSG granularity)
  - Data: Advanced (PostgreSQL encryption at rest, Key Vault for secrets)
  - Applications: Basic (GHAS enabled, no runtime WAF rules)
  - Infrastructure: Basic (Defender free tier, no CIS benchmark compliance)
- Critical findings:
  - No MFA on admin accounts (Keycloak limitation — resolved by Entra migration)
  - 2 Container Apps using admin credentials for ACR pull (should use managed identity)
- High findings:
  - No Private Link for PostgreSQL (public endpoint exposed)
  - No Conditional Access policies
  - Defender for Cloud on free tier (limited threat detection)
- Roadmap:
  1. (Week 1) Fix ACR pull to use managed identity — Critical
  2. (Week 2) Enable Defender for Containers and Databases — High
  3. (Week 3) Add Private Link for PostgreSQL — High
  4. (Month 2) Complete Entra ID migration for MFA + Conditional Access — Critical

## Example 2: Pre-production security gate

**Input**: Security review before promoting staging to production.

**Output**:
- Secure score: 78/100 (improved from 62)
- Gate status: CONDITIONAL PASS
- Passed:
  - Managed identity on all ACA apps — PASS
  - Key Vault for all secrets — PASS
  - TLS on all public endpoints — PASS
  - GHAS scanning active — PASS
  - Encryption at rest on all databases — PASS
- Conditional:
  - Defender for Cloud on Standard tier — WARN (free tier, recommend upgrade)
  - Incident response procedure — WARN (documented but not tested)
- Blocked:
  - None — no Critical findings blocking production
- Recommendation: Proceed to production with accepted risks documented

## Example 3: Keycloak-to-Entra security impact assessment

**Input**: Assess security impact of migrating from Keycloak to Entra ID.

**Output**:
- Security improvements:
  - Conditional Access policies (geo-fencing, device compliance, risk-based auth)
  - PIM for just-in-time privileged access
  - Native MFA with Authenticator app and FIDO2 keys
  - Risk-based sign-in detection (Identity Protection)
  - Unified audit log in Azure Monitor
- Security risks during transition:
  - Dual IdP period: both Keycloak and Entra active (increased attack surface)
  - Token validation must handle both issuers during transition
  - Service accounts need migration without downtime
  - Break-glass admin access must work on both IdPs
- Mitigations:
  - Per-app cutover (not big-bang) to minimize dual-IdP window
  - Monitoring on both IdPs during transition
  - Break-glass account on Entra with emergency access policy
  - Keycloak decommission only after 2-week validation period
