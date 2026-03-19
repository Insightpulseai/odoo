# Tasks — Platform Auth Architecture

> Actionable task breakdown for unified auth implementation.

---

## Phase 1: Foundation (Complete)

- [x] Deploy Supabase Auth as platform IdP
- [x] Deploy Keycloak at auth.insightpulseai.com
- [x] Create `ipai_auth_oidc` Odoo module
- [x] Implement MCP gateway multi-path Bearer (ADR-007)
- [x] Configure GitHub App `pulser-hub` for installation tokens
- [x] Set up n8n credential store

## Phase 2: Enable SSO

- [ ] Enable `ipai_auth_oidc` in Odoo production
- [ ] Integrate Supabase Auth in ops-console
- [ ] Integrate Supabase Auth in workspace app
- [ ] Configure n8n OIDC via Keycloak (admin access)
- [ ] Implement authorization code + PKCE in mobile app
- [ ] Test cross-app SSO flow end-to-end

## Phase 3: Harden Service Auth

- [ ] Audit all n8n workflows for inline secrets
- [ ] Create dedicated Odoo integration user for n8n
- [ ] Create Databricks service principal
- [ ] Implement webhook signature validation (inbound n8n triggers)
- [ ] Rotate all service credentials
- [ ] Document credential rotation schedule

## Phase 4: Audit & Compliance

- [ ] Forward auth events to ops.platform_events
- [ ] Implement proactive token refresh (auth_session FSM gap)
- [ ] Set up quarterly access review process
- [ ] Create n8n credential store review checklist
- [ ] Document auth incident response procedures

## Phase 5: Advanced Federation

- [ ] GitHub SAML SSO via Keycloak
- [ ] Plane SSO integration
- [ ] Shelf SSO integration
- [ ] CRM SSO integration
- [ ] Cross-app session sharing
