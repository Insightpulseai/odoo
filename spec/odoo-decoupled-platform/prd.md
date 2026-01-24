# PRD: Odoo Decoupled Platform

> Product Requirements Document for the decoupled Odoo + Supabase architecture.

## Overview

This platform implements a **Shelf/Plane/Atomic-CRM style architecture** where:
- Odoo serves as a **domain service** (ERP, accounting, inventory)
- Supabase provides **auth, database, and edge functions**
- Modern web/mobile apps consume **stable API contracts**

## Goals

### Primary Goals
1. **Decouple app velocity from Odoo complexity** - Ship app features without touching Odoo
2. **Enterprise-grade auth without Odoo** - Supabase Auth + RLS for app security
3. **Multi-tenant isolation by default** - Org-based RLS policies
4. **Odoo as ERP backbone** - Keep accounting, inventory, workflows in Odoo
5. **Real-time sync** - Events/webhooks for Odoo↔App data consistency

### Non-Goals
- Replacing Odoo's core ERP functionality
- Building custom accounting/inventory in Supabase
- Direct browser access to Odoo APIs

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  Web App (Next.js) │ Mobile App (React Native) │ CLI Tools      │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Supabase Platform                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Supabase     │  │ PostgREST    │  │ Edge Functions       │   │
│  │ Auth         │  │ API          │  │ (Odoo Bridge)        │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│                           │                    │                 │
│                    ┌──────┴──────┐             │                 │
│                    ▼             ▼             ▼                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              PostgreSQL (RLS-protected)                   │   │
│  │  app.* schema (App-owned)  │  odoo.* schema (sync tables) │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ (Edge Functions / Workers)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Odoo Domain Service                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Accounting   │  │ Inventory    │  │ Custom Addons        │   │
│  │ (BIR/Tax)    │  │ (Stock)      │  │ (ipai_*)             │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## User Stories

### App User
- As an app user, I authenticate via Supabase Auth (email/password, OAuth, SSO)
- As an app user, I only see data for orgs I belong to (RLS-enforced)
- As an app user, I never interact with Odoo directly

### App Developer
- As a developer, I build features using Supabase client libraries
- As a developer, I define RLS policies for authorization
- As a developer, I consume Odoo data via synced tables, not API calls

### Odoo Admin
- As an Odoo admin, I manage ERP operations (invoices, inventory, workflows)
- As an Odoo admin, I expose data via webhooks/events to Supabase sync
- As an Odoo admin, I don't manage app user authentication

### Platform Operator
- As an operator, I deploy schema changes via migrations
- As an operator, I monitor sync health via ops.* schema
- As an operator, I enforce parity controls via CI gates

## Functional Requirements

### FR-1: Authentication
- [ ] Supabase Auth as sole identity provider for app users
- [ ] Support email/password, OAuth (Google, GitHub), and SAML SSO
- [ ] Session management via Supabase (not Odoo)
- [ ] Service account authentication for Odoo integration

### FR-2: Authorization
- [ ] RLS policies on all app.* and odoo.* schema tables
- [ ] Org-based multi-tenancy (org_id in all relevant tables)
- [ ] Role-based access (org_owner, org_admin, member)
- [ ] Policy-based permissions (no app code authorization)

### FR-3: Data Sync
- [ ] Edge function for Odoo→Supabase sync
- [ ] Webhook receiver for Odoo events
- [ ] Sync cursor tracking in odoo.sync_cursors
- [ ] Conflict resolution strategy (last-write-wins or merge)

### FR-4: Schema Management
- [ ] All schema in supabase/migrations/
- [ ] Entity ownership documented in spec/schema/entities.yaml
- [ ] CI validation of migration files
- [ ] Generated types from schema (TypeScript, OpenAPI)

### FR-5: Observability
- [ ] Run tracking in ops.runs
- [ ] Event logging in ops.run_events
- [ ] Artifact storage in ops.artifacts
- [ ] Sync health metrics exposed

## Non-Functional Requirements

### NFR-1: Security
- Service role keys never in client code
- All API-exposed tables have RLS
- Secrets stored in environment, not repo

### NFR-2: Performance
- Sync latency < 30 seconds for critical entities
- API response time < 200ms (p95)
- Edge function cold start < 500ms

### NFR-3: Reliability
- Sync retries with exponential backoff
- Dead-letter queue for failed syncs
- Graceful degradation if Odoo unavailable

### NFR-4: Maintainability
- Spec-driven documentation
- Generated API types
- CI gates for all contracts
