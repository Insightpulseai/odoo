# ipai_llm_supabase_bridge — Implementation Plan

**Version**: 1.0.0 | **Status**: Active | **Last updated**: 2026-02-28

---

## Phase 1 — Vendor + Port Apexive Core Modules to 19.0

**Goal**: Running `llm`, `llm_tool`, `llm_assistant`, `llm_thread`, `llm_openai`,
`llm_mcp_server` in Odoo 19 devcontainer.

**Estimated effort**: Low (automated migration checklist, minimal OWL risk)

### 1.1 — Fork and initialize submodule

```bash
cd /workspaces/odoo
git submodule add -b 18.0 https://github.com/apexive/odoo-llm vendor/apexive-llm
cd vendor/apexive-llm && git checkout -b 19.0-ipai
```

### 1.2 — Apply 19.0 migration checklist to all Phase 1 modules

Per module (`llm`, `llm_thread`, `llm_tool`, `llm_assistant`, `llm_openai`, `llm_mcp_server`):

```bash
# Find all <tree> views and replace with <list>
find <module>/ -name "*.xml" -exec sed -i 's/<tree/<list/g; s/<\/tree>/<\/list>/g' {} +

# Find view_mode="tree,...
grep -rn 'view_mode="tree' <module>/

# Check for deprecated API usage
grep -rn '\.\_cr\b\|\.\_uid\b\|\.\_context\b\|read_group(' <module>/ --include="*.py"

# Check route type
grep -rn "type='json'" <module>/ --include="*.py"
```

Manual fixes after sed:
- `view_mode="tree,form"` → `"list,form"` in `ir.actions.act_window`
- `_cr` → `env.cr`, `_uid` → `env.uid`, `_context` → `env.context`
- `read_group()` → `_read_group()` (internal) or `formatted_read_group()` (reports)
- `@route(type='json')` → `@route(type='jsonrpc')`
- `__manifest__.py` version string: `18.0.x.y.z` → `19.0.x.y.z`

### 1.3 — Add vendor to addons_path

`config/dev/odoo.conf`:
```ini
addons_path = /workspaces/odoo/addons/odoo,
              /workspaces/odoo/addons/oca,
              /workspaces/odoo/vendor/apexive-llm,
              /workspaces/odoo/addons/ipai
```

### 1.4 — Install and smoke-test

```bash
docker compose exec -T odoo odoo -d odoo_dev \
  -i llm,llm_tool,llm_assistant,llm_thread,llm_openai,llm_mcp_server --stop-after-init

# MCP endpoint check
curl http://localhost:8069/llm/mcp -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

**Verification**: All 6 modules installed, MCP endpoint returns tool list.

---

## Phase 2 — Port `llm_anthropic` (16.0 → 19.0 + Claude 4.x)

**Goal**: Working Claude provider with tool use and Claude 4.5 models.

### 2.1 — Cherry-pick from 16.0

```bash
cd vendor/apexive-llm
git remote add apexive-16 https://github.com/apexive/odoo-llm  # if not already
git fetch apexive-16 16.0
git checkout -b port/llm_anthropic 19.0-ipai
git cherry-pick apexive-16/16.0 -- llm_anthropic/
```

### 2.2 — Bring provider interface up to 18.0/19.0 spec

The 16.0 `llm.provider` interface evolved significantly. Key diffs (inspect `llm/models/llm_provider.py`):
- Replace direct `anthropic.Anthropic()` client usage with the `_provider_type` field
  and `_get_client()` pattern used in other 18.0 providers
- Implement `_generate(messages, tools=None)` signature
- Add `_model_list()` to return Claude 4.5 family models

### 2.3 — Extend with Claude 4.x model list and tool use

```python
CLAUDE_MODELS = [
    ("claude-opus-4-6", "Claude Opus 4.6"),
    ("claude-sonnet-4-6", "Claude Sonnet 4.6"),
    ("claude-haiku-4-5-20251001", "Claude Haiku 4.5"),
]

# Tool use: map llm_tool declarations → anthropic SDK tool format
# tools = [{"name": t.name, "description": t.description,
#            "input_schema": json.loads(t.parameter_schema)} for t in tools_arg]
```

### 2.4 — Add anthropic to external_dependencies

```python
"external_dependencies": {"python": ["anthropic>=0.40.0"]},
```

### 2.5 — Test

```bash
docker compose exec -T odoo odoo -d odoo_dev \
  -i llm_anthropic --stop-after-init

docker compose exec -T odoo odoo -d odoo_dev \
  --test-tags /llm_anthropic --stop-after-init
```

---

## Phase 3 — Scaffold `ipai_llm_supabase_bridge` Module

**Goal**: Bridge emits events for all Apexive lifecycle points; DLQ + cron working.

### 3.1 — Module file layout

```
addons/ipai/ipai_llm_supabase_bridge/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── ipai_bridge_config.py    # TransientModel, webhook config, test connection
│   ├── ipai_bridge_event.py     # Outbox + DLQ model, _emit(), _try_send(), crons
│   ├── llm_tool.py              # _inherit llm.tool → hook _execute()
│   └── llm_thread.py            # _inherit llm.thread → hook create(), _generate()
├── security/
│   ├── ir.model.access.csv
│   └── ipai_llm_supabase_bridge_groups.xml
├── views/
│   ├── ipai_bridge_event_views.xml
│   └── ipai_bridge_config_views.xml
├── data/
│   └── ipai_llm_supabase_bridge_data.xml    # Cron: retry(5min) + flush(1min)
└── tests/
    └── test_bridge_event.py
```

### 3.2 — Hook patterns

`llm_tool.py`:
```python
class LlmTool(models.Model):
    _inherit = "llm.tool"

    def _execute(self, *args, **kwargs):
        # Emit tool.call BEFORE (capture args)
        result = super()._execute(*args, **kwargs)
        # Emit tool.result AFTER (capture result)
        return result
```

`llm_thread.py`:
```python
class LlmThread(models.Model):
    _inherit = "llm.thread"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # Emit thread.create for each new thread
        return records

    def _generate(self, *args, **kwargs):
        # Emit generation.start
        result = super()._generate(*args, **kwargs)
        # Emit generation.complete
        return result
```

### 3.3 — Install and basic test

```bash
docker compose exec -T odoo odoo -d odoo_dev \
  -i ipai_llm_supabase_bridge --stop-after-init

# Run unit tests
docker compose exec -T odoo odoo -d odoo_dev \
  --test-tags /ipai_llm_supabase_bridge --stop-after-init
```

---

## Phase 4 — Supabase Schema + Edge Function

**Goal**: Migration applied, Edge Function deployed, E2E event ingestion working.

### 4.1 — Apply Supabase migration

```bash
# Via CLI
supabase db push --project-ref spdtwktxdalcfigzeqrz

# Or paste into Supabase Dashboard SQL Editor
# supabase/migrations/20260228_001_ops_llm_observability.sql
```

### 4.2 — Deploy Edge Function

```bash
supabase functions deploy llm-webhook-ingest \
  --project-ref spdtwktxdalcfigzeqrz

supabase secrets set LLM_BRIDGE_WEBHOOK_SECRET=<generate-random-32-chars> \
  --project-ref spdtwktxdalcfigzeqrz
```

### 4.3 — Configure Odoo bridge

Odoo Settings → Technical → IPAI Supabase Bridge → Configuration:
- Webhook URL: `https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/llm-webhook-ingest`
- HMAC Secret: (same value set in Supabase Vault)
- Enabled: ✓

Use "Test Connection" button → verify ping event in `ops.run_events`.

### 4.4 — E2E integration test

```bash
# 1. Run a full chat exchange via MCP or Odoo assistant UI
# 2. Verify events in Supabase
psql "$SUPABASE_DB_URL" -c "
SELECT event_type, status, timestamp
FROM ops.run_events
ORDER BY timestamp DESC LIMIT 10;"

# Expected: thread.create, generation.start, generation.complete
```

---

## Phase 5 — SSOT Registration

```bash
# Update bridges catalog
vim ssot/bridges/catalog.yaml  # Add ipai_llm_supabase_bridge entry

# Update secrets registry
vim ssot/secrets/registry.yaml  # Add anthropic_api_key, llm_bridge_webhook_secret

# Update AI SSOT
vim ssot/ai/odoo_ai.yaml  # Note anthropic as available provider

# Create contract doc
touch docs/contracts/LLM_SUPABASE_BRIDGE_CONTRACT.md

# Verify CI gate
python scripts/ci/check_parity_and_bridges_ssot.py
```

---

## Dependency Graph

```
Phase 1 (vendor port) ──────────┐
                                 ▼
Phase 2 (llm_anthropic) ────► Phase 3 (bridge module)
                                 │
Phase 4 (Supabase) ─────────────┘
                                 ▼
Phase 5 (SSOT) ───────────── (any order, last)
```

Phases 1 and 4 can proceed in parallel.
Phase 3 requires Phase 1 (depends on `llm`, `llm_tool`, `llm_thread`).
Phase 2 requires Phase 1 (extends `llm` provider interface).
Phase 5 can be done incrementally alongside other phases.
