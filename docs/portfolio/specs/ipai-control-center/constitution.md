# Constitution — IPAI Control Center (Spec Kit)

## 1) Purpose
IPAI Control Center is the unified operational cockpit inside Odoo CE 18 for:
- Portfolio/Program/Project Management (PPM)
- Advisor-style recommendations (cost/security/reliability/ops/performance)
- Workbooks registry for analytics (Superset/BI dashboards)
- Connectors/ingestion for signals (n8n/webhooks/Supabase/Mattermost)

## 2) Non-Negotiables
1. **Odoo CE 18 first**: Use native models and views wherever possible; OCA modules fill gaps; IPAI custom only where required.
2. **Idempotent ingestion**: Any inbound signal ingestion must be deterministic and safe to retry (dedupe keys, upserts, audit logs).
3. **Unique XML IDs**: All inherited QWeb/Views must use unique `id=` values. Never reuse core xmlids.
4. **No restart loops in compose**: `--stop-after-init` must not run on services with restart policies; init is a one-shot job.
5. **Separation of concerns**:
   - `ipai_workspace_core` = shared base primitives
   - `ipai_ppm` = PPM domain
   - `ipai_advisor` = recommendations + scoring
   - `ipai_workbooks` = analytics registry
   - `ipai_connectors` = integrations + ingestion
6. **Single source of truth**:
   - Odoo = workflow UI + operational records
   - Supabase = analytics-grade log + time-series snapshots (ops_advisor schema)
7. **RLS is mandatory** on Supabase tables (least privilege by role).
8. **Pulser SDK required**: the repo must include a Pulser SDK install step and a minimal config stub for agent-triggered automation.

## Non-Negotiable Principles (Legacy - Preserved for Reference)

### 1. Single Source of Truth
- **Operational state**, recommendations, scores, activity logs, and PPM snapshots are stored in **Supabase PostgreSQL**
- **Odoo** is the **action + workflow** surface for assignment, status tracking, and governance
- **Superset** is the **analysis** surface for deep-dive analytics and trend visualization
- No data duplication between systems except for legitimate caching/performance needs

### 2. Thin Odoo, Heavy Analytics Outside
- Odoo modules store **only** what Odoo needs for governance workflows and user assignment
- **No "BI inside Odoo"** beyond overview tiles, summary charts, and drill-through links
- All complex analytics, time-series analysis, and reporting live in Superset workbooks
- Odoo acts as the operational workflow hub, not the analytical data warehouse

### 3. Idempotent Automation
- All ingest/evaluation jobs **must be idempotent** and safe to rerun without side effects
- Recommendation creation uses **deterministic keys** (source + category + resource + title hash) to prevent duplicates
- Scoring algorithms produce **consistent results** when run multiple times with same inputs
- Failed automation jobs can be **safely retried** without data corruption

### 4. Explainable Recommendations
Every recommendation **must include**:
- **Evidence**: Concrete data/metrics supporting the recommendation
- **Impact**: Quantified business impact (cost savings, risk reduction, performance gain)
- **Remediation**: Clear playbook with step-by-step fix instructions
- **Owner**: Assigned person/team responsible for resolution
- **Confidence**: Algorithm confidence score (0.0-1.0)

### 5. GitOps First
- Infrastructure + deployments are **GitOps-managed** (ArgoCD/Flux patterns)
- Runtime configuration changes **must be reflected back to Git**
- All Odoo modules, n8n workflows, and Supabase migrations are version-controlled
- Changes follow pull request workflow with code review and CI validation

### 6. Composable Architecture
- Each capability (Advisor, PPM, Workbooks, Notifications) can **run independently**
- Modules have **clear boundaries** and well-defined integration contracts
- Failure in one subsystem **does not cascade** to others
- New capabilities can be added **without modifying** existing modules

### 7. Minimal Manual Operations
- Scheduled jobs, exports, notifications, and score refresh are **fully automated**
- Manual intervention required **only for exceptions** and human judgment calls
- Self-healing automation detects and recovers from transient failures
- Observability built in from day one (logging, metrics, traces)

## Constraints

### Technology Stack
- **Odoo**: Odoo 18.0 CE + OCA 18.0 ecosystem modules only
- **Database**: Supabase PostgreSQL (project: `spdtwktxdalcfigzeqrz`)
- **Automation**: n8n workflows (webhooks + cron + error handling)
- **Notifications**: Mattermost (treated as Slack substitute)
- **Analytics**: Apache Superset dashboards
- **Infrastructure**: DigitalOcean App Platform + Spaces (no Azure, no AWS)

### Observability & Data Sources
- Data sources may vary (Prometheus/Loki/OpenTelemetry optional)
- System **must degrade gracefully** when observability sources unavailable
- Minimum viable sources: GitHub webhooks, Odoo database, manual input
- Additional sources can be added incrementally without breaking existing flows

### Integration Patterns
- Mattermost used exclusively for notifications (no complex bot interactions in v1)
- n8n is the **workflow bus** for all event-driven automation
- Superset dashboards linked from Odoo, not embedded (iframe optional for v2)
- All external APIs use **retry logic** with exponential backoff

## Out of Scope (v1)

Explicitly **NOT included** in v1 to maintain focus:

1. **Full Azure-equivalent identity stack**: Entra CA/SCIM/PIM beyond practical RBAC claims
2. **API Management monetization**: Quota enforcement, developer portal, API marketplace
3. **Real-time stream processing**: Event Hubs/Synapse-class streaming at Azure scale
4. **Interactive Mattermost actions**: Complex slash commands, modal dialogs, interactive buttons
5. **Multi-tenant SaaS**: Per-customer isolation, billing, white-labeling
6. **Mobile apps**: Native iOS/Android applications (responsive web only)
7. **Advanced ML/AI**: Predictive analytics, anomaly detection beyond simple thresholds

## Success Definition

The IPAI Control Center is considered **successful** when:

### User Acceptance Criteria
- ✅ **One dashboard** shows category health scores (0-100) and top 5 recommendations per category
- ✅ **Odoo users** can assign, track status, set due dates, and close recommendations
- ✅ **n8n workflows** post actionable updates to Mattermost automatically
- ✅ **Workbooks** provide drill-down analytics with filters and exportable reports
- ✅ **Portfolio owners** see program/project health rollups and risk registers in one place

### Technical Acceptance Criteria
- ✅ Recommendation ingestion API achieves **<2s p95 latency**
- ✅ Score recomputation completes in **<30s for 1000 recommendations**
- ✅ No duplicate recommendations created (idempotency guaranteed)
- ✅ RLS policies enforce category + owner-based access control
- ✅ **95%+ uptime** for advisor overview dashboard
- ✅ All automation jobs have **error handling + retry logic**

### Business Value Metrics
- **% critical recommendations resolved** in 7/14/30 days (target: 80%/90%/95%)
- **Score improvement** over 30 days per category (target: +10 points)
- **Deployment failures** correlated to reliability recommendations (target: 90% match)
- **Portfolio health** distribution (target: 70% green, 20% yellow, 10% red)
- **Time to detect issues** (target: <1 hour from event to recommendation)

## Governance Model

### Roles & Responsibilities
- **Platform Owner**: Approves architecture changes, sets category weights, owns roadmap
- **Ops Lead**: Manages reliability/performance recommendations, owns playbook quality
- **Security Owner**: Manages security recommendations, approves risk acceptance
- **Finance Owner**: Manages cost recommendations, tracks savings impact
- **PMO Lead**: Manages PPM hierarchy, risk register, resource allocation

### Change Management
- Configuration changes (category weights, severity thresholds) follow **pull request workflow**
- Recommendation schema changes require **migration + backward compatibility**
- Playbook updates versioned with **approval workflow** (peer review required)
- API contract changes follow **semantic versioning** (major.minor.patch)

### Data Retention
- **Recommendations**: Retained for 2 years, then archived
- **Scores**: Daily snapshots retained for 1 year, then aggregated to monthly
- **Activity logs**: Retained for 90 days, then purged
- **Exports**: On-demand generation, not permanently stored

## Compliance & Security

### Access Control
- **Category-based RLS**: Users see only recommendations for categories they own
- **Owner-based RLS**: Users see recommendations assigned to them or their team
- **Admin override**: Platform admins can view all recommendations
- **Audit trail**: All status changes, assignments, and closures logged

### Data Privacy
- **No PII in recommendations**: Use resource IDs, not personal names
- **Anonymized metrics**: Aggregate data for trends, not individual attribution
- **GDPR-compliant exports**: CSV/PDF exports exclude sensitive fields
- **Right to deletion**: Manual purge process for deleted resources

### Security Posture
- **Secrets management**: All API keys in environment variables, never in code
- **TLS everywhere**: HTTPS for all external endpoints
- **Least privilege**: Service accounts with minimal required permissions
- **Dependency scanning**: Automated vulnerability checks in CI

## Evolution Roadmap

### v1.0 — Foundation (MVP)
- Advisor overview + recommendation lifecycle
- Basic PPM (portfolio/program/risk)
- n8n automation + Mattermost notifications
- Workbooks registry + CSV export

### v1.1 — Enhanced Intelligence
- Resource allocation tracking + overload detection
- Deeper observability inputs (Prometheus/Loki)
- Advanced filtering + bulk actions
- PDF export with executive summary

### v1.2 — Policy & Compliance
- GitOps integration (ArgoCD/Flux)
- Policy compliance reporting (Kyverno/OPA)
- Drift detection + remediation
- Recommendation SLA tracking

### v2.0 — Predictive & Proactive
- ML-based anomaly detection
- Predictive scoring (forecast next 30 days)
- Automated remediation (self-healing)
- Embedded Superset dashboards in Odoo

## 3) Success Criteria (Definition of Done)
- Advisor dashboard works end-to-end: ingest → dedupe → recommendation list → status transitions → score refresh.
- PPM has portfolios/programs/risks/resource allocations with rollups visible in Odoo UI.
- Workbooks registry shows linked dashboards and supports tagging/ownership.
- CI passes: repo-structure, guardrails, parity tests.
- Production-grade docs: PRD + plan + tasks + constitution are present and coherent.

## 4) Quality Bar (NFRs)
- **Performance**: list views load <2s for 10k records; scoring recompute for 1k recs <60s (async option).
- **Observability**: audit log for lifecycle changes; ingestion logs; score snapshots.
- **Security**: Odoo ACLs + record rules; Supabase RLS + service-role only in CI/Edge.
- **Compatibility**: Odoo 18 CE; OCA 18.0 branches only; no enterprise-only dependencies.

## 5) Change Control
- Any schema changes require:
  - migration script
  - updated data dictionary
  - updated PRD section (Data Requirements)
- Any UI changes require:
  - screenshot in PR
  - view XML review for xmlid uniqueness and inheritance correctness

---

## Legacy Documentation (Preserved for Reference)

### Appendix: Pulser SDK Integration

The IPAI Control Center **must include** instructions to install and wire the Pulser SDK for:
- **Agent registration**: "Advisor Evaluator" as a named agent/tool
- **Governance automation**: Policy compliance checks, approval workflows
- **Observable workflows**: All n8n workflows registered as Pulser-managed agents

Pulser SDK enables:
- Unified agent registry across Odoo, n8n, and edge functions
- Centralized observability for all automation workflows
- Automated governance and compliance reporting
