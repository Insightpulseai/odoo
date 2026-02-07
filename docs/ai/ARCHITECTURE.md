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
