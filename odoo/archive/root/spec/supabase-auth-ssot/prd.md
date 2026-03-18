# PRD — Supabase Auth SSOT

**Version**: 1.0.0
**Status**: Active
**Authority doc**: `docs/architecture/SSOT_BOUNDARIES.md §1`

## Problem

The platform currently has identity fragmented across:
- Odoo internal user management (primary auth for ERP users)
- Supabase Auth (used by apps, Edge Functions, n8n)
- No defined boundary — any service can become an ad-hoc IdP

This creates: duplicate user records, inconsistent session enforcement, no MFA story, no audit trail for auth events, and no safe path to SSO.

## Goal

Make Supabase Auth the single identity authority. Odoo becomes a consumer of that identity, not a competitor to it.

## Functional Requirements

### FR-1: Identity SSOT (P0)
- Supabase Auth is authoritative for all `@insightpulseai.com` users
- Supabase `auth.users.id` (UUID) is the canonical user identifier across all services

### FR-2: Odoo Minimal Projection (P0)
- `res.users` gains field `x_supabase_user_id` (UUID, unique)
- Projection created/updated by `provision-odoo-user` Edge Function
- Prohibited fields: password hash, social provider data, session tokens

### FR-3: Auth Hooks → Odoo Provisioning (P1)
- Supabase Auth hook on `signup` triggers `provision-odoo-user`
- Edge Function creates `res.users` record if missing, updates email/company if changed
- All invocations logged to `ops.platform_events`

### FR-4: RBAC + RLS Baseline (P1)
- Platform roles defined in Supabase (`platform_roles` table)
- RLS policies on all `integrations.*` and `bridge.*` tables
- Odoo access groups derived from Supabase role, not managed independently

### FR-5: MFA Enforcement (P1)
- TOTP MFA required for all `@insightpulseai.com` internal users
- Enforced via Supabase Auth settings (not Odoo)

### FR-6: Third-Party JWT Trust (P2)
- Supabase JWKS endpoint declared in `config/auth/jwt_trust.yaml`
- Odoo and n8n configured to validate Supabase JWTs
- No service parses unsigned or unvalidated JWTs

### FR-7: SSO with SAML (P2 — requires Supabase Pro)
- Enterprise SSO for `@insightpulseai.com` via SAML IdP
- Spec amendment required before enabling

### FR-8: OAuth 2.1 Server (P3)
- Supabase becomes the OAuth2 IdP for external integrations
- Replaces ad-hoc API key patterns in n8n and Edge Functions

## Out of Scope
- Odoo portal user auth (portal disabled)
- Zoho Mail OAuth2 (covered by `spec/zoho-mail-bridge/`)
- Social login for end customers (not a B2C product)
