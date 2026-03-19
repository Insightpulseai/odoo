# Supabase SSOT Doctrine – Product Requirements Document

## Overview

This document defines the architectural doctrine for data ownership, orchestration, and secret management across the InsightPulseAI platform.

## Problem Statement

Without clear boundaries between systems, agents and developers risk:
- Writing business data to the wrong system
- Duplicating secrets across multiple stores
- Creating conflicting sources of truth
- Running automation from inappropriate contexts
- AI agents accessing unauthorized data

## Solution

Establish a strict doctrine defining:
1. **Supabase as Single Source of Truth (SSOT)** for platform, analytics, AI, and orchestration
2. **Odoo as System of Record (SoR)** for business transactions and compliance
3. Clear data ownership boundaries with no overlap
4. Centralized secret management in Supabase Vault
5. Explicit conflict resolution rules

## Functional Requirements

### FR-1: Data Ownership Enforcement

| Requirement | Description |
|-------------|-------------|
| FR-1.1 | All business transactions MUST be written to Odoo |
| FR-1.2 | All analytical data MUST be written to Supabase |
| FR-1.3 | Data replication from Odoo→Supabase is read-only |
| FR-1.4 | Shadow tables in Supabase are clearly marked as replicas |

### FR-2: Secret Management

| Requirement | Description |
|-------------|-------------|
| FR-2.1 | Supabase Vault is the canonical secret store |
| FR-2.2 | No secrets in Odoo models or database |
| FR-2.3 | No secrets committed to Git |
| FR-2.4 | Edge Function secrets only for runtime values |

### FR-3: Orchestration

| Requirement | Description |
|-------------|-------------|
| FR-3.1 | pg_cron schedules live in Supabase |
| FR-3.2 | Edge Functions handle async operations |
| FR-3.3 | n8n handles cross-system workflows |
| FR-3.4 | Odoo never runs scheduled jobs |

### FR-4: AI Agent Access

| Requirement | Description |
|-------------|-------------|
| FR-4.1 | Agents default to Supabase for reads |
| FR-4.2 | Odoo access requires explicit permission |
| FR-4.3 | Agent memory stored in Supabase |
| FR-4.4 | AI outputs stored in designated schemas |

## Non-Functional Requirements

### NFR-1: Auditability
- All Odoo writes must be traceable
- Supabase maintains audit logs for all changes

### NFR-2: Security
- Row-level security (RLS) on all Supabase tables
- Secrets encrypted at rest in Vault

### NFR-3: Consistency
- Single source of truth per data domain
- No conflicting data across systems

## Success Criteria

1. Zero business transactions written directly to Supabase
2. Zero secrets stored in Odoo or Git
3. All scheduled jobs run from Supabase/n8n
4. AI agents operate within defined boundaries
5. Clear audit trail for all data modifications

## Dependencies

- Supabase Pro plan (Vault, pg_cron, Edge Functions)
- Odoo CE 19 with ipai_* modules
- n8n self-hosted instance
- GitHub Actions for CI/CD
