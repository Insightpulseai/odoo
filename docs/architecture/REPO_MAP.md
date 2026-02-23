# REPO_MAP.md — GraphRAG Agent Navigation Map
#
# Generated: 2026-02-23 | Git SHA: 980c9998a
# For AI agents (Claude Code, Codex, Cursor) navigating this monorepo.
# Complement to AGENTS.md (SSOT-generated agent instructions).
# Update: python scripts/build_kb_graph.py (graph layer), then update this file.

---

## 1. Identity & Coordinates

| Key             | Value                                          |
|-----------------|------------------------------------------------|
| Repo            | `Insightpulseai/odoo` (github.com)             |
| Workspace ID    | `ipai`                                         |
| Branch (main)   | `main`                                         |
| Odoo version    | CE 19.0                                        |
| Supabase        | `spdtwktxdalcfigzeqrz` (us-east-1)             |
| Production IP   | `178.128.112.214` (DO Singapore)               |
| Domain          | `insightpulseai.com` (.net deprecated)         |
| Python          | 3.12+ (pyenv: odoo-19-dev)                     |
| Node            | ≥18.0, pnpm 9+, Turborepo                     |
| EE parity target| ≥80% via CE + OCA + ipai_*                    |

---

## 2. Directory Tree (canonical paths only)

```
/
├── addons/
│   ├── odoo/          [no_touch]      Odoo CE core addons
│   ├── oca/           [overlay_only]  OCA community (≈100+ submodules, git-aggregated)
│   └── ipai/          [editable]      Custom ipai_* modules (55 modules, 250+ .py files)
│
├── apps/
│   ├── ops-console/                   OpsConsole (Next.js 15, App Router)
│   ├── odoo-mobile-ios/               iOS app (Fastlane + XCode)
│   └── mcp-jobs/                      MCP job runner service
│
├── web/
│   ├── ai-control-plane/              Claude + AI agent control plane (Next.js)
│   ├── odoo-frontend-shell/           Odoo frontend shell (Next.js)
│   └── odooops-dashboard/             OpsConsole BI dashboard
│
├── agents/
│   ├── mcp/servers/lib-mcp-server/   MCP server (11 tools)
│   ├── registry/odoo_skills.yaml     Agent skill registry
│   └── skills/                        Skill instruction folders
│
├── automations/
│   └── n8n/workflows/                n8n workflow JSONs (canonical SSOT)
│
├── scripts/
│   ├── build_kb_graph.py             GraphRAG node/edge indexer ← NEW
│   ├── ingest_knowledge_graph.py     Legacy KG ingest
│   ├── generate_repo_index.py        Repo index generator
│   ├── automations/                  sweep_repo.py, deploy_n8n_all.py
│   ├── agents/                       sync_agent_instructions.py, drift checker
│   ├── ci/                           Gate scripts (addons path, supabase contract)
│   ├── dns/                          DNS artifact generator
│   └── kb/                           KB indexing helpers
│
├── infra/
│   ├── cloudflare/                   DNS records (generated)
│   ├── dns/subdomain-registry.yaml   DNS SSOT ← edit this, never generated
│   └── observability/                Monitoring dashboards
│
├── supabase/
│   ├── migrations/                   ≈70+ migration files
│   └── functions/                    42 Edge Functions
│
├── spec/                             62+ spec bundles (Spec-kit format)
├── docs/
│   ├── ai/SSOT.md                    AI agent SSOT (canonical)
│   └── architecture/
│       ├── schema.prisma             DB ORM (public, ops, auth, cron schemas)
│       ├── REPO_MAP.md               This file
│       └── INDEX.json                Machine-readable Layer 1 index ← NEW
│
├── runtime/docker/
│   ├── Dockerfile.ce19               Odoo CE 19 image
│   └── docker-compose*.yml           Compose stacks
│
├── .devcontainer/                    Codespaces / local DevContainer
├── .github/workflows/               265 CI/CD workflows
├── CLAUDE.md                         Claude Code entry point → docs/ai/SSOT.md
└── AGENTS.md                         Auto-generated from docs/ai/SSOT.md (do not edit)
```

---

## 3. Addons Policy Zones

| Zone | Path | `addon_kind` | `edit_policy` | Rule |
|------|------|-------------|---------------|------|
| Core | `addons/odoo/` | `core` | `no_touch` | Read-only reference |
| OCA | `addons/oca/` | `oca` | `overlay_only` | `_inherit` only, never patch |
| Custom | `addons/ipai/` | `ipai` | `editable` | All custom work here |
| Generated | (runtime) | `generated` | `editable` | Safe to regenerate |

**OCA override pattern**:
```python
# addons/ipai/ipai_<oca_module>_override/models/my_override.py
class MyOverride(models.Model):
    _inherit = '<oca.model.name>'
    # add fields / override methods here
```

---

## 4. ipai Modules by Domain (55 total)

### AI & Intelligence
`ipai_ai_agent_builder` · `ipai_ai_agents_ui` · `ipai_ai_automations` ·
`ipai_ai_copilot` · `ipai_ai_fields` · `ipai_ai_livechat` · `ipai_ai_platform` ·
`ipai_ai_rag` · `ipai_ai_tools` · `ipai_foundation` · `ipai_platform_api` ·
`ipai_platform_theme` · `ipai_rest_controllers`

### Finance & Compliance (PH BIR)
`ipai_finance_ppm` · `ipai_finance_close_seed` · `ipai_finance_tax_return` ·
`ipai_finance_workflow` · `ipai_bir_notifications` · `ipai_bir_plane_sync` ·
`ipai_equity` · `ipai_esg` · `ipai_esg_social` · `ipai_hr_expense_liquidation` ·
`ipai_hr_payroll_ph`

### Operations & Infrastructure
`ipai_auth_oidc` · `ipai_documents_ai` · `ipai_enterprise_bridge` ·
`ipai_expense_ocr` · `ipai_helpdesk` · `ipai_helpdesk_refund` ·
`ipai_mail_bridge_zoho` · `ipai_odooops_shell` · `ipai_ops_connector` ·
`ipai_planning_attendance` · `ipai_project_templates` · `ipai_sign` ·
`ipai_system_config` · `ipai_zoho_mail`

### UI / Theme / Design
`ipai_chatgpt_sdk_theme` · `ipai_copilot_ui` · `ipai_design_system` ·
`ipai_design_system_apps_sdk` · `ipai_theme_copilot` · `ipai_theme_fluent2` ·
`ipai_theme_tbwa` · `ipai_ui_brand_tokens` · `ipai_web_fluent2` ·
`ipai_web_icons_fluent` · `ipai_web_mail_compat` · `ipai_web_theme_tbwa` ·
`ipai_website_coming_soon`

### Verticals & Connectors
`ipai_vertical_media` · `ipai_vertical_retail` · `ipai_whatsapp_connector`

---

## 5. GraphRAG KB Layer (Supabase public schema)

Applied migration: `20260223000008_kb_graph_layer.sql`

### Tables
| Table | Rows (2026-02-23) | Purpose |
|-------|-------------------|---------|
| `kb_chunks` | 0 (ready) | Text chunks for semantic search |
| `kb_embeddings` | 0 (ready) | pgvector(1536) embeddings |
| `kb_nodes` | 386 | Graph nodes (module/file/model) |
| `kb_edges` | 337 | Typed directed edges |

### Node type counts
| Type | Count |
|------|-------|
| `File` | 250 |
| `Model` | 81 |
| `OdooModule` | 55 |

### Edge type counts
| Type | Count |
|------|-------|
| `DEFINED_IN` | 329 |
| `DEPENDS_ON` | 8 |

### Supported node types
`File` · `OdooModule` · `Model` · `View` · `Asset` · `AssetBundle` · `Controller` · `Doc`

### Supported edge types
`CALLS` · `DEPENDS_ON` · `INHERITS_FROM` · `ASSET_IN_BUNDLE` · `REMOVES` · `OVERLAYS` · `DEFINED_IN` · `IMPORTS`

### Example traversal queries
```sql
-- All files in a module
SELECT n.name, n.path
FROM kb_nodes n
JOIN kb_edges e ON e.dst_id = n.id
WHERE e.type = 'DEFINED_IN'
  AND e.src_id = (SELECT id FROM kb_nodes WHERE type='OdooModule' AND name='ipai_finance_ppm');

-- Module dependency chain
SELECT dst.name
FROM kb_edges e
JOIN kb_nodes dst ON e.dst_id = dst.id
WHERE e.type = 'DEPENDS_ON'
  AND e.src_id = (SELECT id FROM kb_nodes WHERE type='OdooModule' AND name='ipai_ai_rag');

-- Policy-gated agent query: find editable nodes only
SELECT type, name, path FROM kb_nodes
WHERE addon_kind = 'ipai' AND edit_policy = 'editable'
ORDER BY type, name;
```

---

## 6. Key Entrypoints

| What | Path |
|------|------|
| Odoo server config | `config/dev/odoo.conf` |
| Main Dockerfile | `runtime/docker/docker/Dockerfile.ce19` |
| DevContainer | `.devcontainer/devcontainer.json` |
| OpsConsole app | `apps/ops-console/app/page.tsx` |
| AI control plane | `web/ai-control-plane/` |
| MCP server tools | `agents/mcp/servers/lib-mcp-server/src/tools.py` |
| Supabase schema | `docs/architecture/schema.prisma` |
| n8n workflows | `automations/n8n/workflows/` |
| KB graph indexer | `scripts/build_kb_graph.py` |
| DNS SSOT | `infra/dns/subdomain-registry.yaml` |
| Agent SSOT | `docs/ai/SSOT.md` |

---

## 7. CI Gates (key workflows)

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `cd-production.yml` | push/main | Production deploy gate |
| `build-odoo-ce19-*.yml` | push | CE 19 Docker image |
| `supabase-db-push.yml` | push | Migration push |
| `supabase-sql-rls-checks.yml` | push | RLS audit |
| `odoo-addons-path-guard.yml` | push | Addons path enforcement |
| `agent-instructions-drift.yml` | push/main | SSOT drift check |
| `agentic-codebase-crawler.yml` | schedule | KB crawler |
| `automation-sweep.yml` | schedule | n8n workflow audit |
| `ops-console-check.yml` | push | OpsConsole bundle gate |

---

## 8. Golden Paths

### Add Odoo module
```bash
# 1. Scaffold spec
bash scripts/speckit-scaffold.sh ipai_<domain>_<feature>

# 2. Create module
mkdir -p addons/ipai/ipai_<domain>_<feature>/{models,views,security,data}
# Write __manifest__.py, __init__.py, models/__init__.py

# 3. Commit + install
git add addons/ipai/ipai_<domain>_<feature>/
# CI installs on push

# 4. Update KB graph
python scripts/build_kb_graph.py
```

### Apply Supabase migration
```bash
# Preferred (Supabase CLI)
supabase db push --linked

# Fallback (when migration history out of sync)
PGPASSWORD=$POSTGRES_PASSWORD psql \
  "postgresql://postgres.spdtwktxdalcfigzeqrz:${POSTGRES_PASSWORD}@aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require" \
  -f supabase/migrations/<filename>.sql
# Then register:
psql ... -c "INSERT INTO supabase_migrations.schema_migrations(version,name,statements)
             VALUES ('<version>','<name>',ARRAY['-- applied via psql'])
             ON CONFLICT DO NOTHING;"
```

### Override OCA module
```bash
mkdir -p addons/ipai/ipai_<oca_module>_override/models
# __manifest__.py: depends = ['<oca_module>']
# models/override.py: _inherit = '<model.name>'
```

### Update DNS
```bash
# 1. Edit SSOT
nano infra/dns/subdomain-registry.yaml

# 2. Generate artifacts
bash scripts/dns/generate-dns-artifacts.sh

# 3. Commit all
git add infra/dns/ infra/cloudflare/ docs/architecture/runtime_identifiers.json
git commit -m "chore(deploy): add <subdomain> DNS record"
# CI applies via Terraform on merge
```

---

## 9. Invariants (never violate)

1. CE only — no Enterprise modules, no odoo.com IAP calls
2. OCA `overlay_only` — `_inherit` in ipai_* override, never direct edits in addons/oca/
3. Database isolation — Odoo uses local PostgreSQL; Supabase is external integration bus only
4. Secrets in env only — `.env*` local, GitHub Actions secrets in CI, never in source
5. DNS via SSOT — `subdomain-registry.yaml` → generate → commit → CI applies (never direct Cloudflare)
6. Deprecated: `.net` domain, Mattermost, Mailgun, Affine, Appfine — never reintroduce
7. Mail via `ipai_mail_bridge_zoho` — never raw SMTP calls from Odoo models
8. Migration sync — if `supabase db push` fails, use direct psql + manual history insert
9. KB graph — re-run `python scripts/build_kb_graph.py` after module changes
10. Agent output format — follow CLAUDE.md structured output contract for all agent runs

---

*REPO_MAP.md — machine-readable agent navigation layer.*
*Update: run `python scripts/build_kb_graph.py` then refresh section 5 stats.*
