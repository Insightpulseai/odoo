# Agentic SDLC Constitution — InsightPulseAI

> Governance constraints for all agents operating in the SDLC loop.
> This file is the constitution referenced by Spec Kit, coding agents, and SRE agents.
> It defines what agents CAN and CANNOT do within the InsightPulseAI platform.

---

## 1. Data Authority Model

### SSOT / SOR Separation

```
Agent Framework (orchestration — stateless executor)
        ↓ emits run events / artifacts
Supabase ops.* (SSOT — single source of truth)
        ↓ posts accounting artifacts
Odoo (SOR — system of record / ledger)
```

| Layer | Role | Tables / Resources |
|-------|------|--------------------|
| **Supabase** (SSOT) | Control plane, orchestration state, telemetry | `ops.specs`, `ops.spec_tasks`, `ops.incidents`, `ops.runs`, `ops.run_events`, `ops.platform_events` |
| **Odoo** (SOR) | Business transactions, accounting, ERP data | `account.move`, `sale.order`, `project.task`, `hr.expense` |
| **GitHub** (Code SSOT) | Source code, issues, PRs, CI/CD state | Repos, issues, PRs, actions |
| **Azure** (Infra SSOT) | Infrastructure state, secrets, identity | ACA revisions, Key Vault, Entra ID |

**Rule**: Agents read from SSOT, write business transactions to SOR. Agent state lives in SSOT (Supabase), never in the agent process.

---

## 2. Tech Stack Constraints

### Allowed

| Category | Allowed |
|----------|---------|
| **Language** | Python 3.12+ (Odoo), TypeScript (Edge Functions, web) |
| **ERP** | Odoo CE 18.0 only |
| **Extensions** | OCA modules (Stable+ maturity), `ipai_*` bridge modules |
| **Database** | PostgreSQL 16 (Azure Flexible Server for Odoo, Supabase for ops) |
| **Compute** | Azure Container Apps (Southeast Asia) |
| **Edge** | Azure Front Door (TLS termination, WAF) |
| **AI** | Claude (primary), Azure OpenAI (fallback) |
| **Automation** | n8n (integration/webhook routing), Agent Framework (multi-step reasoning) |
| **Auth** | Keycloak (transitional) → Microsoft Entra ID (target) |
| **Mail** | Zoho SMTP (`smtp.zoho.com:587`) |
| **Secrets** | Azure Key Vault (`kv-ipai-dev`) |
| **Observability** | Azure Monitor, Sentry, OTLP |

### Banned (Never Use)

| Category | Banned | Reason |
|----------|--------|--------|
| **ERP** | Odoo Enterprise modules | CE-only policy |
| **ERP** | odoo.com IAP calls | CE-only, no vendor lock-in |
| **Hosting** | DigitalOcean | Deprecated 2026-03-15 |
| **Hosting** | Vercel | Deprecated 2026-03-11 |
| **Mail** | Mailgun | Deprecated, replaced by Zoho |
| **Chat** | Mattermost | Deprecated 2026-01-28 |
| **Domain** | `insightpulseai.net` | Deprecated 2026-02 |
| **DB** | Supabase for Odoo data | Odoo uses its own PostgreSQL |
| **Auth** | Session cookies for agent calls | API key or OAuth2 bearer only |
| **Code** | `cr.commit()` in Odoo | ORM handles transactions |
| **Code** | f-string in `_()` translations | Use lazy interpolation |
| **Code** | Global JS patches in Odoo | Use native Odoo 18 patterns |

---

## 3. Agent Behavior Rules

### Scope

1. **One task = one PR** — agents never combine unrelated changes
2. **Max 10 files per PR** — if more are needed, decompose the task
3. **No cross-boundary changes** — a single PR must not cross SSOT domain boundaries
4. **Read before write** — agents must read existing code before modifying
5. **Verify before commit** — every change must pass: lint + test + build

### State Management

6. **Externalize all state** — agent state goes to `ops.runs` / `ops.run_events`, never in-process
7. **Idempotent operations** — agents must handle re-execution without side effects
8. **Checkpoint progress** — long-running tasks checkpoint to Supabase every 60 seconds
9. **Timeout enforcement** — max 10 minutes per task, escalate to human on timeout

### Safety

10. **No destructive operations without human approval** — `DROP TABLE`, `rm -rf`, force push, etc.
11. **Sandbox untrusted code** — agent-generated code runs in isolated ACA sessions
12. **No secret access** — agents never read/write secrets directly; use Key Vault references
13. **Deterministic CI/CD** — agents invoke pipelines, pipelines never invoke agents
14. **Human-in-the-loop at PR review** — auto-merge only for severity:low with passing tests

### Quality

15. **Tests required** — every code change includes or updates tests
16. **Evidence required** — save test output to `docs/evidence/<stamp>/<scope>/`
17. **Commit convention** — `feat|fix|refactor|docs|test|chore(scope): description`
18. **OCA first** — prefer OCA modules over custom `ipai_*` for any standard functionality

---

## 4. Module Philosophy

```
Config → OCA → Delta (ipai_*)
```

1. **Config**: Can Odoo's built-in configuration solve it? Use that.
2. **OCA**: Does an OCA module (Stable+ maturity, 18.0 branch, CI green) exist? Use that.
3. **Delta**: Only create `ipai_*` when (1) and (2) cannot solve the problem.

### OCA Adoption Gates

Before an agent installs any OCA module:
- 18.0 branch exists and CI green on OCA repo
- `development_status` >= `Stable` in `__manifest__.py`
- Test install in disposable DB (`test_<module>`)
- No conflicts with existing `ipai_*` modules
- Documented in `config/addons.manifest.yaml`

---

## 5. Odoo Coding Standards

### Model Class Attribute Order

```
_name → _description → _inherit → _inherits → _rec_name → _order
→ default methods → field declarations → SQL constraints
→ compute/inverse/search → selection methods → constrains/onchange
→ CRUD methods → action methods → business methods
```

### Naming

- Many2one: `*_id`, One2many/Many2many: `*_ids`
- Compute: `_compute_<field>`, Action: `action_<verb>`
- Boolean: `is_*` or `has_*`
- Module: `ipai_<domain>_<feature>`

### XML IDs

- View: `<model>_view_<type>`, Action: `<model>_action`
- Security group: `group_<name>`, ACL: `access_<model>_<group>`

---

## 6. Database Rules

| Database | Purpose | Who Uses |
|----------|---------|----------|
| `odoo_dev` | Development | Agents + developers |
| `odoo_dev_demo` | Demo/showroom | On-demand only |
| `odoo_staging` | Staging rehearsal | CI + staging ACA |
| `odoo` | Production | Prod ACA only |
| `test_<module>` | Disposable test | Agents during testing |

**Rule**: Agents NEVER touch `odoo` (prod) or `odoo_staging` directly. Use `odoo_dev` for development, `test_<module>` for testing.

---

## 7. Supabase Schema Additions

### ops.specs (Spec SSOT)

Tracks structured specifications created by spec agents.

```sql
CREATE TABLE IF NOT EXISTS ops.specs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    title TEXT NOT NULL,
    intent TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'active', 'completed', 'cancelled')),
    spec_bundle JSONB NOT NULL DEFAULT '{}',
    constitution_hash TEXT,
    github_repo TEXT,
    created_by UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### ops.spec_tasks (Task Decomposition)

Individual tasks decomposed from a spec, each maps to one GitHub issue and one PR.

```sql
CREATE TABLE IF NOT EXISTS ops.spec_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    spec_id UUID REFERENCES ops.specs(id) ON DELETE CASCADE,
    task_index INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'in_progress', 'completed', 'blocked', 'cancelled')),
    github_issue_number INTEGER,
    github_pr_number INTEGER,
    assignee TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);
```

### ops.incidents (SRE Incident Tracking)

Tracks incidents detected by SRE agents, linked to specs and PRs for closed-loop resolution.

```sql
CREATE TABLE IF NOT EXISTS ops.incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT NOT NULL DEFAULT 'low'
        CHECK (severity IN ('critical', 'high', 'medium', 'low')),
    status TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'investigating', 'mitigating', 'resolved', 'closed')),
    source TEXT NOT NULL DEFAULT 'manual'
        CHECK (source IN ('manual', 'sre_agent', 'monitor_alert', 'user_report')),
    telemetry_context JSONB DEFAULT '{}',
    github_issue_number INTEGER,
    spec_id UUID,
    resolution_pr_number INTEGER,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 8. Cross-Repo Responsibility

| SDLC Phase | Repo | What Lives There |
|------------|------|------------------|
| Spec | `agents` | Skills, constitution, workflows |
| Code | `odoo` | Odoo modules, OCA, addons |
| Quality | `.github` | Reusable CI workflows, policies |
| Deploy | `infra` | Bicep, Terraform, ACA config |
| Observe | `ops-platform` | Edge Functions, vault, control plane |
| Automate | `automations` | n8n workflows, runbooks, cron |
| Analytics | `lakehouse` | Databricks, medallion pipelines |

---

## 9. Closed-Loop Execution Contract

```
Intent (natural language)
  → /speckit.specify → ops.specs (SSOT)
  → /speckit.tasks → ops.spec_tasks → GitHub issues
  → coding-agent-from-issue.yaml → PR
  → quality-gate.yml (CI)
  → deploy-azure.yml → ACA revision
  → SRE agent observes (Azure Monitor)
  → sre-to-issue-to-agent.yaml → ops.incidents
  → GitHub issue → coding agent
  → Loop closes
```

Every transition emits an event to `ops.run_events`. Every artifact is traceable from intent to deployment.

---

*Last updated: 2026-03-15*
