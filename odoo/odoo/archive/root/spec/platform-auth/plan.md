# Plan — Platform Auth Architecture

> Implementation plan for unified auth across the InsightPulse AI platform.

---

## Phase 1: Foundation (Current State — Live)

Already implemented:
- [x] Supabase Auth as IdP (JWT, sessions, MFA, RLS)
- [x] Keycloak deployed at auth.insightpulseai.com
- [x] `ipai_auth_oidc` module in Odoo (OIDC + TOTP MFA)
- [x] MCP gateway multi-path Bearer validation (ADR-007)
- [x] GitHub App `pulser-hub` for installation token auth
- [x] n8n credential store for service auth

## Phase 2: Enable SSO Across Apps

1. Enable `ipai_auth_oidc` in Odoo production (currently disabled)
2. Configure Supabase Auth direct integration for web apps (ops-console, workspace)
3. Configure n8n UI SSO via Keycloak OIDC (admin/operator access only)
4. Implement authorization code + PKCE for mobile app

## Phase 3: Harden Service Auth

1. Audit all n8n workflows for credential usage — replace any inline secrets with credential store refs
2. Create dedicated integration user in Odoo for n8n (replace any shared human credentials)
3. Create dedicated service principals for Databricks integrations
4. Implement webhook signature validation for all inbound n8n triggers
5. Rotate all service credentials and document rotation schedule

## Phase 4: Audit & Compliance

1. Enable auth event forwarding from all systems to `ops.platform_events`
2. Implement proactive token refresh in auth_session FSM (address identified gap)
3. Set up quarterly access review process (C-10 policy)
4. Create n8n credential store monthly review checklist
5. Document auth incident response procedures

## Phase 5: Advanced Federation

1. GitHub SAML SSO via Keycloak (requires Enterprise tier)
2. Plane/Shelf/CRM SSO integration (when supported by those platforms)
3. Cross-app session sharing via Supabase Auth
