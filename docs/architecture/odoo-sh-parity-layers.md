# Odoo.sh Parity — Architecture Layer Diagram

**Quick Reference**: Visual breakdown of 3-layer architecture achieving 95% Odoo.sh parity

---

## Layer Architecture

```mermaid
graph TB
    subgraph "Layer 1: Infrastructure (23 features)"
        A1[GitHub Actions]
        A2[GHCR Registry]
        A3[Codespaces]
        A4[DigitalOcean Droplets]
        A5[DO PostgreSQL]
        A6[Cloudflare DNS/WAF]
    end

    subgraph "Layer 2: Control Plane (22 features)"
        B1[Supabase ops.* Schema]
        B2[Edge Functions Runner]
        B3[RLS Policies]
        B4[Backup/Restore System]
        B5[Audit Trails]
        B6[RBAC Engine]
    end

    subgraph "Layer 3: Modules (15 features)"
        C1[OCA Modules: 35]
        C2[IPAI Modules: 43]
        C3[n8n Workflows]
        C4[MCP Servers: 11]
        C5[Superset Dashboards]
    end

    A1 --> B2
    A2 --> B2
    A4 --> B1
    B2 --> A4
    B1 --> C2
    C3 --> B5
    C4 --> C2
```

---

## Feature Distribution

| Layer | Features | Coverage | Key Components |
|-------|----------|----------|----------------|
| **Infrastructure** | 23 | 100% | Git, CI/CD, Compute, DNS, CDN |
| **Control Plane** | 22 | 95% | Orchestration, RBAC, Audit, Backups |
| **Modules** | 15 | 87% | Business logic, UI, Integrations |
| **Total** | 60 | 95% | 57/60 features covered |

---

## Data Flow: Git Push → Production

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Git as GitHub
    participant CI as GitHub Actions
    participant CP as Control Plane
    participant EF as Edge Function
    participant RT as Runtime (DO)

    Dev->>Git: git push origin feature/new-feature
    Git->>CI: Trigger build-and-deploy.yml
    CI->>CI: Build GHCR image
    CI->>CP: ops.queue_run(project, env, sha)

    loop Every 10s
        EF->>CP: ops.claim_next_run(worker_id)
        CP-->>EF: Run details
    end

    EF->>RT: Pull GHCR image
    EF->>RT: Deploy to feature-new-feature.erp.insightpulseai.com
    RT->>RT: Run smoke tests
    RT->>CP: ops.append_event(run_id, "deploy_success")
    CP->>Git: Post deployment comment on PR
```

---

## Critical Path: Staging-from-Prod Clone

```mermaid
graph LR
    A[Staging Build Triggered] --> B[Clone Prod DB]
    B --> C[Mask PII]
    C --> D[Deploy to Staging]
    D --> E[Run Smoke Tests]
    E --> F{Tests Pass?}
    F -->|Yes| G[Mark Success]
    F -->|No| H[Rollback]
    H --> I[Alert Team]
```

**Key Principle**: Fresh prod-clone DB per staging build (no DB reuse)

---

## Backup & Restore Flow

```mermaid
graph TB
    subgraph "Backup Schedule"
        A1[Cron: Daily 2am UTC]
        A1 --> B1[ops.create_backup]
        B1 --> C1[pg_dump]
        B1 --> C2[tar filestore]
        B1 --> C3[snapshot logs]
        C1 --> D[ops.backups table]
        C2 --> D
        C3 --> D
    end

    subgraph "Retention Policy"
        D --> E{Age Check}
        E -->|< 7 days| F[Keep: Daily]
        E -->|7-28 days| G[Keep: Weekly]
        E -->|28-90 days| H[Keep: Monthly]
        E -->|> 90 days| I[Delete]
    end

    subgraph "Restore Flow"
        J[User: ops restore] --> K{Env?}
        K -->|Staging| L[Self-serve]
        K -->|Prod| M[Approval Gate]
        M --> N[ops.approvals]
        N --> O[ops.restore_backup]
        L --> O
        O --> P[pg_restore]
        O --> Q[untar filestore]
    end
```

**Retention**: 7 daily / 4 weekly / 3 monthly (Odoo.sh parity)

---

## Security Layers

```mermaid
graph TB
    subgraph "Authentication"
        A1[Google Workspace SSO]
        A1 --> A2[Supabase Auth]
        A2 --> A3[Odoo Session]
    end

    subgraph "Authorization"
        B1[ops.project_members]
        B1 --> B2[ops.roles]
        B2 --> B3[RLS Policies]
        B3 --> B4[Environment Access]
    end

    subgraph "Network Security"
        C1[Cloudflare WAF]
        C1 --> C2[IP Whitelist]
        C2 --> C3[DDoS Protection]
        C3 --> C4[Nginx Reverse Proxy]
    end

    subgraph "Audit Trail"
        D1[ops.run_events]
        D1 --> D2[ops.audit_trail]
        D2 --> D3[Immutable Logs]
    end

    A3 --> B4
    B4 --> C4
    C4 --> D1
```

---

## Monitoring Architecture

```mermaid
graph TB
    subgraph "Data Collection"
        A1[Odoo Logs] --> B1[ops.run_events]
        A2[Docker Logs] --> B1
        A3[PostgreSQL Metrics] --> B2[DO Monitoring]
        A4[Nginx Access Logs] --> B1
    end

    subgraph "Aggregation"
        B1 --> C1[Event Aggregator Edge Function]
        B2 --> C2[Prometheus Exporter]
        C1 --> D1[Supabase Realtime]
        C2 --> D2[Grafana]
    end

    subgraph "Visualization"
        D1 --> E1[Superset Dashboards]
        D2 --> E1
        E1 --> F1[Performance Metrics]
        E1 --> F2[Error Rates]
        E1 --> F3[Usage Analytics]
    end

    subgraph "Alerting"
        E1 --> G1[n8n Workflows]
        G1 --> H1[Slack Notifications]
        G1 --> H2[Email Alerts]
    end
```

---

## Week 1 Focus: Control Plane Schema

```mermaid
graph LR
    A[ops.projects] --> B[ops.environments]
    B --> C[ops.runs]
    C --> D[ops.run_events]
    C --> E[ops.artifacts]

    F[ops.backups] --> G[ops.restores]

    H[ops.project_members] --> I[ops.roles]
    I --> J[RLS Policies]

    C --> K[ops.approvals]

    L[ops.policies] --> B
    L --> C
```

**Week 1 Deliverables**:
1. Create 9 tables in `ops.*` schema
2. Implement RLS policies for all tables
3. Add 6 core RPCs (queue_run, claim_next_run, etc.)
4. CI validation for schema completeness

---

## Reference

- **Full Documentation**: `docs/architecture/odoo-sh-parity.md`
- **Verification**: `./scripts/verify-parity-coverage.sh`
- **Spec Bundle**: `spec/odoo-sh-clone/`
- **DNS SSOT**: `infra/dns/subdomain-registry.yaml`
