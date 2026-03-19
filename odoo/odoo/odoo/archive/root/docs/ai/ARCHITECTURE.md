# Architecture Overview
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

```
┌─────────────────────────────────────────────────────────────────────┐
│                   InsightPulse AI Stack (Self-Hosted)                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Slack (SaaS) ◄──► n8n ◄──► Odoo CE 19 ◄──► PostgreSQL 16          │
│       │             │          (8069)                                │
│       │             │                                                │
│       │             └──────────► Supabase (external integrations)    │
│       │                                                              │
│       └───────────────────────► AI Agents (Pulser, Claude, Codex)   │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│  Superset (BI)  │  Keycloak (SSO)  │  DigitalOcean (Hosting)        │
└─────────────────────────────────────────────────────────────────────┘
```

## Authority Model: System of Record vs Single Source of Truth

### Canonical Statement

**Odoo is the System of Record for transactional and regulated business data. Supabase is the Single Source of Truth for the platform control plane, integrations, evidence/audit, analytics serving layer, and AI indexes. Odoo data is mirrored one-way into Supabase for read, product, and intelligence use cases; Supabase replicas are non-authoritative for transactions.**

### Authority by Domain

#### Odoo = System of Record (SoR)

**Authoritative for:**

- Accounting entries, invoices, payments
- HR records (employees, contracts, timesheets)
- Inventory & stock moves
- CRM leads/opportunities
- Purchases, sales orders
- Any legal/financial/regulated business objects

**Writes:** All transactional business data writes happen in Odoo.

#### Supabase = Single Source of Truth (SSOT)

**Authoritative for:**

- **Control plane metadata** (`ops.*`): projects, environments, runs, evidence, artifacts
- **Integration state**: webhooks, sync cursors, idempotency keys
- **AI/RAG indexes**: embeddings, retrieval logs, vector search
- **Analytics serving layer**: gold/platinum tables, materialized views, caches
- **Product UI state**: saved queries, dashboards, user preferences (if not in Odoo)

**Writes:** Platform, integration, analytics, and AI infrastructure data writes happen in Supabase.

### Mirroring Policy

#### One-Way Mirror: Odoo → Supabase

- **Pattern:** Append-only events + derived views in Supabase
- **Purpose:** Read-optimized copies for analytics, AI, and product surfaces
- **Constraint:** Supabase replicas MUST NOT be used to decide transactional truth

#### Governance Guardrails

1. **Read-only by policy:** Supabase tables that mirror Odoo are **read-only** (enforced via RLS)
2. **No dual-write:** No Supabase edits that override Odoo transactional truth
3. **Explicit write-back:** Any write-back to Odoo happens via **controlled APIs/jobs**, never by sync
4. **Deterministic keys:** All mirrored entities use stable identifiers (`external_id`, UUID, natural keys)

### Examples

| Entity               | Authoritative System | Replica/Consumer        | Flow                              |
|----------------------|----------------------|-------------------------|-----------------------------------|
| Invoice record       | Odoo (SoR)           | Supabase read replica   | Odoo → Supabase (one-way)         |
| OdooOps run metadata | Supabase (SSOT)      | None                    | Supabase only                     |
| Employee master      | Odoo (SoR)           | Supabase analytics view | Odoo → Supabase (materialized)    |
| RAG embeddings       | Supabase (SSOT)      | None                    | Supabase only                     |
| Payment transaction  | Odoo (SoR)           | Superset dashboard      | Odoo → Supabase → Superset        |

## Cost-Minimized Self-Hosted Philosophy

**We BUILD everything ourselves to minimize costs:**
- NO Azure, AWS, GCP managed services
- NO expensive SaaS subscriptions
- NO per-seat enterprise licensing

**Self-hosted stack:**
- **Hosting**: DigitalOcean droplets (~$50-100/mo vs $1000s cloud)
- **Database**: PostgreSQL 16 (self-managed, not RDS)
- **DNS**: Cloudflare (delegated from Spacesquare registrar)
- **Mail**: Zoho Mail (replaces deprecated Mailgun)
- **BI**: Apache Superset (free, self-hosted)
- **SSO**: Keycloak (free, self-hosted)
- **Automation**: n8n (self-hosted, not cloud)
- **Chat**: Slack (SaaS - replaces deprecated Mattermost)

## Docker Architecture

**Development Stack** (sandbox/dev):
- **Odoo CE 19**: Single container with EE parity (port 8069)
- **PostgreSQL 16**: Database backend (port 5433 external, 5432 internal)
- **Optional Tools**: pgAdmin (5050), Mailpit (8025) via `--profile tools`

**Production Stack** may include additional specialized containers per deployment environment.
