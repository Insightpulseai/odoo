# PRD: OdooOps Console Auth (Supabase)

## Goal
Ship a Next.js console (ops.insightpulseai.com) with Supabase Auth + RLS enforcing org isolation.

## Core Features
- Email/password + magic link (optional) + MFA-ready
- Org membership + roles (admin/operator/viewer)
- Session via @supabase/ssr (App Router)
- Audit logs for sign-in/out and privileged actions
- API routes protected by Supabase service role server-side only

## Non-Goals
- Replacing Odoo login at erp.insightpulseai.com
- Implementing Odoo SSO (future phase)
