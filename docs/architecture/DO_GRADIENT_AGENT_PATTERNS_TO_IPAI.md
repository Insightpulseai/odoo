# DO Gradient Agent Patterns → IPAI Canonical Mapping (TBWA\SMP)

This document extracts **automation-first** patterns from DigitalOcean Gradient™ AI Platform "Create Agents" + "ADK build/test/deploy" docs and maps them to the **TBWA\SMP Odoo CE + Superset + Supabase** stack.

Sources:
- DO "How to Create Agents…" (API/CLI fields, endpoints, provisioning flow)
- DO "Agent Instructions Best Practices" (what "instructions" really are)
- DO "Build, Test, and Deploy Agents using ADK" (local dev loop + prerequisites)

---

## 0) What we're learning (the transferable primitives)

DigitalOcean's Gradient Agent Platform implicitly standardizes a deployable agent as:

**Workspace/Project → Agent → (optional) Knowledge Base → Endpoint + API Key(s)**

Key transferable learnings:
1) **API-first provisioning**: Agents are created deterministically via API/CLI with: name, model, instructions, project/workspace, region, optional KB(s).
2) **Instructions are first-class config** (system prompt + routing glue): define identity/objectives/restrictions and the "prompt engineering" wiring between resources.
3) **Local dev loop**: ADK provides a reproducible local run/test pattern and expects env-driven config.

---

## 1) Canonical typology (IPAI mirror)

### 1.1 DigitalOcean terms → IPAI terms

| DigitalOcean Gradient term | Meaning | IPAI canonical equivalent |
|---|---|---|
| Project / Workspace | container of agents + billing + access boundary | `workspace` (env/tenant boundary) |
| Agent | instruction + model + attached KBs | `agent` (single responsibility) |
| Knowledge Base | RAG corpus store | `kb` (Supabase pgvector or DO KB) |
| Region | runtime location | `region` (SGP1 / nearest) |
| Endpoint + API key | callable runtime surface | `endpoint` + `access_key` |

---

## 2) IPAI agent registry model (repo-controlled, no UI dependency)

### 2.1 Registry file layout (suggested)

```text
agents/
  odoo_ops/
    instruction.md
    routes.yaml
    tools.yaml
  superset_analyst/
    instruction.md
    routes.yaml
    tools.yaml
  mailgun_delivery/
    instruction.md
    routes.yaml
    tools.yaml
contracts/
  agents/
    agent-registry.schema.json
```

### 2.2 Minimal YAML registry contract (example)

```yaml
version: 1
workspace: tbwa-smp-prod
region: sgp1
agents:
  - slug: odoo-ops
    name: "Odoo Ops Agent"
    model:
      provider: bring-your-own
      id: "<model_uuid>"
    instruction_file: "agents/odoo_ops/instruction.md"
    knowledge_bases:
      - slug: odoo-runbooks
        source: supabase_vector
        ref: "ops.kb_odoo_runbooks"
    endpoints:
      - visibility: private
        auth: bearer
        secret_ref: "DO_AGENT_API_KEY_ODOO_OPS"
    tags: ["odoo", "ops", "tbwa-smp"]
```

This mirrors DO's creation fields (`name`, `model_uuid`, `instruction`, `project_id`, `region`, optional `knowledge_base_uuid`, and tags/description).

---

## 3) Automation-first provisioning (DO pattern you can copy)

### 3.1 "List options → Create agent" flow

DO's docs recommend listing available options via API/CLI for:

* models (API endpoint + CLI commands)
* regions (API endpoint + CLI commands)
* knowledge bases (API endpoint + CLI commands)

**IPAI mirror rule**:

* never hardcode IDs in docs without a "list step"
* your deploy scripts should resolve IDs dynamically, then create/update agents.

### 3.2 API create agent (canonical payload shape)

DigitalOcean's "create agent" API uses a POST request with fields including:
`name`, `model_uuid`, `instruction`, `description`, `project_id`, `tags`, `region`, `knowledge_base_uuid`.

**IPAI mirror**: your `agent-registry.yaml` should contain those fields (or equivalents) and a deploy script should translate YAML → API payload.

---

## 4) Secrets & key management (canonical, runtime-only)

### 4.1 What DO implies

* Agents are created via API/CLI requiring a DO token.
* ADK expects environment variables via `.env` for deployment/runtime config.

**Required environment variables**:
- `GRADIENT_MODEL_ACCESS_KEY`: Authentication for model access
- `DIGITALOCEAN_API_TOKEN`: Personal access token with all CRUD scopes for `genai` and read scope for `project`

### 4.2 TBWA\SMP canonical secret placement

**GitHub Actions secrets** (build/deploy):

* `DO_API_TOKEN` (provision agent resources / registry operations)
* `SUPABASE_SERVICE_ROLE_KEY` (server-side only; Edge Functions)
* `MAILGUN_API_KEY` (server-side only)
* `ODOO_MASTER_PASSWORD` (only where needed)

**Droplet runtime** (if running any agent gateway/service):

* `/opt/<service>/.env` (chmod 600)

**Supabase** (Edge Functions):

* `supabase secrets set ...` for server-side usage

Rule: **instructions + registry are versioned in git; secrets are never in git**.

---

## 5) Instructions as first-class artifacts (how to write + enforce)

DO explicitly frames "instructions" as combining system prompts (identity/objectives/restrictions) plus prompt engineering glue (agent/resource/backend relationships).

### 5.1 Canonical instruction structure

Each `instruction.md` must include:

**1. Identity** (unique name, role, scope):
```markdown
## Identity
You are the **Odoo Ops Agent** for TBWA\SMP production infrastructure.
```

**2. Objectives** (primary goal, key responsibilities, priorities):
```markdown
## Objectives
- Monitor Odoo CE 18.0 health and performance
- Execute routine maintenance tasks (module updates, database backups)
- Escalate critical issues to DevOps team
```

**3. Expertise** (supported features, technical domains, data sources):
```markdown
## Expertise
- Odoo CE 18.0 architecture and OCA module ecosystem
- PostgreSQL 16 query optimization
- Docker Compose orchestration patterns
- Access to: Odoo logs, Supabase analytics, Mailgun delivery metrics
```

**4. Restrictions** (topics to discuss and avoid):
```markdown
## Restrictions
**Allowed**: Odoo CE operations, OCA modules, production troubleshooting
**Forbidden**: Enterprise module discussions, unauthorized database schema changes
```

**5. Limitations** (knowledge gaps, escalation paths):
```markdown
## Limitations
- Cannot modify production schema without approval
- Limited to read-only Supabase access
- Escalate finance/payroll queries to Finance SSC team
```

### 5.2 IPAI enforceable rule

* each agent must have `instruction.md`
* CI fails if missing
* instructions must include all 5 sections above
* Tool routing policy must be explicit (what tools it can call)

---

## 6) Local sandbox dev loop (ADK → IPAI mirror)

DO's ADK doc positions a local build/test loop and expects env-driven config.

**Prerequisites**:
- Python 3.13 (other versions cause deployment failures)
- `requirements.txt` listing all dependencies (must include `gradient-adk`)
- `.env` file with required environment variables
- Model access key and personal access token configured

### 6.1 Canonical "agent entrypoint" contract (suggested)

**DO ADK pattern**:
```python
@entrypoint
def entry(payload, context):
    query = payload["prompt"]
    inputs = {"messages": [HumanMessage(content=query)]}
    result = workflow.invoke(inputs)
    return result
```

**IPAI mirror pattern**:
```python
@entrypoint
def handle(payload, context):
    """
    Payload contract:
    {
      "meta": {"workspace": "tbwa-smp-dev", "trace_id": "..."},
      "task": {"type": "odoo.module.audit", "args": {"db": "odoo"}},
      "context": {"links": [], "artifacts": []}
    }
    """
    task_type = payload["task"]["type"]
    args = payload["task"]["args"]
    trace_id = payload["meta"]["trace_id"]

    # Route to appropriate tool/workflow
    result = route_task(task_type, args, trace_id)
    return {"status": "success", "result": result, "trace_id": trace_id}
```

### 6.2 Local dev loop commands

**Start local server**:
```bash
cd agents/odoo_ops
gradient agent run --verbose  # Starts on localhost:8080
```

**Test agent locally**:
```bash
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{
    "meta": {"workspace": "tbwa-smp-dev", "trace_id": "local-test-001"},
    "task": {"type": "odoo.module.list", "args": {"db": "odoo"}},
    "context": {}
  }'
```

**Deploy to production**:
```bash
gradient agent deploy  # 1-5 minutes, returns endpoint URL
```

**Verify production deployment**:
```bash
curl -X POST \
  -H "Authorization: Bearer $DIGITALOCEAN_TOKEN" \
  -H "Content-Type: application/json" \
  "https://agents.do-ai.run/v1/{workspace-id}/{deployment-name}/run" \
  -d '{"task": {"type": "odoo.health.check"}}'
```

---

## 7) Verification checklist (must be green)

### 7.1 Registry integrity

* `agents/<slug>/instruction.md` exists
* YAML validates against `contracts/agents/agent-registry.schema.json`
* No secrets committed (secret scanners / denylist)

### 7.2 Provisioning

* List models/regions/KBs step works (no hardcoded stale UUIDs)
* Create agent payload matches canonical field shape

### 7.3 Runtime

* Endpoint responds 200 for `/health`
* Calls log `trace_id` and tool routing decision
* KB grounding enabled when configured (or explicitly disabled)

**Health check template**:
```bash
curl -sf http://localhost:8080/health || exit 1
curl -sf https://agents.do-ai.run/v1/{workspace}/{agent}/health \
  -H "Authorization: Bearer $DO_TOKEN" || exit 1
```

---

## 8) IPAI agent examples (canonical templates)

### 8.1 Odoo Ops Agent

**Purpose**: Production Odoo CE 18.0 operations, monitoring, maintenance

**Tools**:
- `odoo.module.list` - List installed modules
- `odoo.module.audit` - Validate module dependencies
- `odoo.health.check` - System health metrics
- `supabase.query` - Analytics queries (read-only)

**Knowledge base**:
- Supabase vector store: `ops.kb_odoo_runbooks`
- Sources: Odoo CE docs, OCA guidelines, internal runbooks

**Restrictions**:
- Read-only database access
- No schema modifications without approval
- Escalate finance queries to Finance SSC

### 8.2 Superset Analyst Agent

**Purpose**: BI dashboard creation, SQL query optimization, data visualization

**Tools**:
- `superset.dashboard.create` - Create dashboards
- `superset.chart.create` - Create visualizations
- `superset.sql.execute` - Run SQL queries
- `supabase.query` - Direct Scout data access

**Knowledge base**:
- Supabase vector store: `analytics.kb_superset_patterns`
- Sources: Superset docs, SQL optimization guides, Scout schema docs

**Restrictions**:
- Analytics databases only (no Odoo production database)
- Query timeout: 30 seconds max
- Result size limit: 10,000 rows

### 8.3 Mailgun Delivery Agent

**Purpose**: Email deliverability monitoring, bounce handling, compliance

**Tools**:
- `mailgun.events.query` - Query delivery events
- `mailgun.suppressions.list` - List bounces/complaints
- `mailgun.stats.get` - Delivery statistics
- `supabase.log` - Store delivery metrics

**Knowledge base**:
- Supabase vector store: `mailgun.kb_delivery_best_practices`
- Sources: Mailgun docs, email authentication guides, compliance rules

**Restrictions**:
- Read-only Mailgun API access
- No customer email content access
- Escalate compliance issues to legal team

---

## 9) Appendix: DO doc facts we are explicitly mirroring

* Creating an agent via API/CLI requires providing a name, foundation model identifier, instructions, project identifier, and region; DO recommends adding a knowledge base for grounding.
* API create agent request example includes fields: `name`, `model_uuid`, `instruction`, `description`, `project_id`, `tags`, `region`, `knowledge_base_uuid`.
* Agent instruction best practices: system prompts define identity/objectives/restrictions/limitations; "prompt engineering" manages relationships between agents/resources/backend processes.
* Instructions should "balance between keeping them concise to reduce token usage and costs and still detailed enough to guide consistent and accurate behavior."
* ADK workflow is env-driven and expects language/runtime prerequisites (Python 3.13) and dependencies in repo structure.
* ADK local dev loop: `gradient agent run` starts server on `localhost:8080` with `/run` endpoint, use `--verbose` for debugging.
* Entrypoint function must use `@entrypoint` decorator and accept `(payload, context)` parameters.
* Required environment variables: `GRADIENT_MODEL_ACCESS_KEY` and `DIGITALOCEAN_API_TOKEN`.
* Deployment via `gradient agent deploy` returns endpoint: `https://agents.do-ai.run/v1/{workspace-id}/{deployment-name}/run`

---

## 10) CI/CD integration (canonical workflow)

### 10.1 GitHub Actions workflow (agent registry validation)

```yaml
name: agent-registry-validation

on:
  push:
    paths:
      - 'agents/**'
      - 'contracts/agents/**'
  pull_request:
    paths:
      - 'agents/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate registry structure
        run: |
          set -euo pipefail

          # Check all agents have instruction.md
          for agent_dir in agents/*/; do
            agent_slug=$(basename "$agent_dir")
            if [ ! -f "$agent_dir/instruction.md" ]; then
              echo "❌ Missing instruction.md for $agent_slug"
              exit 1
            fi
          done

          # Validate YAML against schema
          pip install jsonschema pyyaml
          python scripts/validate_agent_registry.py

          echo "✅ Agent registry validation passed"

      - name: Check for secrets
        run: |
          # Fail if secrets detected in instructions
          if grep -r "GRADIENT_MODEL_ACCESS_KEY\|DIGITALOCEAN_API_TOKEN" agents/; then
            echo "❌ Secrets found in agent files"
            exit 1
          fi
          echo "✅ No secrets detected"
```

### 10.2 Deployment workflow (production agent provisioning)

```yaml
name: deploy-agents-production

on:
  push:
    branches: [main]
    paths:
      - 'agents/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python 3.13
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install ADK
        run: pip install gradient-adk

      - name: Deploy agents
        env:
          GRADIENT_MODEL_ACCESS_KEY: ${{ secrets.GRADIENT_MODEL_ACCESS_KEY }}
          DIGITALOCEAN_API_TOKEN: ${{ secrets.DO_API_TOKEN }}
        run: |
          for agent_dir in agents/*/; do
            agent_slug=$(basename "$agent_dir")
            echo "Deploying $agent_slug..."
            cd "$agent_dir"
            gradient agent deploy
            cd ../..
          done

      - name: Verify deployments
        run: |
          python scripts/verify_agent_deployments.py
```

---

**Last Updated**: 2026-01-14
**Stack**: Odoo CE 18.0 + Superset + Supabase + DigitalOcean
**DO Gradient AI Platform Docs Version**: Latest (as of 2026-01-14)
