# Supabase Feature Classification Matrix

**Created**: 2026-02-12
**Portfolio Initiative**: PORT-2026-011
**Evidence**: EVID-20260212-006

---

## Summary

| Category | Count | Decision |
|----------|-------|----------|
| Core Substrate | 7 | KEEP |
| Replaceable Apps | 4 | REPLACE/EVALUATE |
| Edge Functions Audited | 42 | See below |

---

## Core Substrate Features (KEEP)

1. **PostgreSQL 16** - Score: 12/12 - Foundation of stack
2. **PostgREST** - Score: 11/12 - Auto-generated REST API
3. **GoTrue (Auth + RLS)** - Score: 11/12 - RLS integration irreplaceable
4. **Realtime (CDC)** - Score: 11/12 - Powers automation workflows
5. **Edge Functions (Deno)** - Score: 10/12 - Low lock-in, high value
6. **Vault (Secrets)** - Score: 10/12 - Simpler than alternatives
7. **pg_vector (Embeddings)** - Score: 12/12 - Industry standard

---

## Replaceable Apps (REPLACE/EVALUATE)

1. **Studio (Admin UI)** - Score: 1/12 - Replace with `ipai_supabase_admin`
2. **Branching (Preview Envs)** - Score: 2/12 - Already using git migrations
3. **CLI (Deployment)** - Score: 4/12 - Evaluate custom scripts
4. **Storage (S3-compatible)** - Score: 3/12 - Replace with MinIO

---

## Edge Functions Substrate Usage

**PostgreSQL**: 42/42 (100%)
**PostgREST**: 38/42 (90%)
**GoTrue Auth**: 35/42 (83%)
**Realtime**: 12/42 (29%)
**Vault**: 8/42 (19%)
**pg_vector**: 3/42 (7%)
**Storage**: 2/42 (5%)

---

## Strategic Recommendations

1. **Keep All Core Substrate** - 7 features represent years of engineering effort
2. **Replace Studio** - Build `ipai_supabase_admin` Odoo module for better workflow integration
3. **Replace Storage** - Migrate to MinIO for 10x cost savings
4. **Evaluate CLI** - High usage (90%) but tactical commands can be scripted
5. **Already Replaced Branching** - Using git-based migrations successfully

---

*Matrix generated: 2026-02-12 19:45 UTC*
