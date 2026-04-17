---
name: odoo-docs-enhance
description: Fetch and annotate Odoo 18 developer documentation with IPAI-specific context — OCA-first alternatives, Azure ACA deployment notes, IPAI module conventions, and Odoo 18 CE breaking changes. Use before ingesting docs into the product-help RAG index. Triggers on "odoo docs", "annotate howto", or "enhance documentation".
disable-model-invocation: false
user-invocable: true
allowed-tools: Bash(curl *) Read Write
---

# Odoo docs enhancer

You are annotating official Odoo 18 developer documentation for IPAI's codebase context.
The output is an enhanced `.md` file ready for ingestion into the `product-help-index` RAG index.

## IPAI overlays to apply to every Odoo doc

### 1. Odoo version pin
Add at the top of every enhanced doc:
```
> IPAI context: Odoo **18 CE** (not EE, not 19). ACA deployment.
> View XML: use `<list>` tag, never `<tree>`. Use `view_mode="list,form"`.
```

### 2. OCA-first annotation
For every topic that has an OCA module equivalent, add:
```
> OCA-first: Before implementing custom code, check [oca/<repo>] for a maintained module.
> IPAI rule: configure → OCA → minimal custom `ipai_*` bridge module.
```

### 3. Azure ACA deployment notes
For topics involving server config, workers, or infrastructure:
```
> Azure ACA: IPAI runs ipai-odoo-dev-web / cron / worker on Container Apps (rg-ipai-dev-odoo-runtime).
> PG Flex host: pg-ipai-odoo.postgres.database.azure.com (rg-ipai-dev-odoo-data, SEA).
> Secrets: Azure Key Vault via DefaultAzureCredential — never in environment variables or git.
```

### 4. Breaking changes — Odoo 18 CE
Add a warning block for any API that changed between 16/17 and 18:
```
> Odoo 18 CE breaking change: [specific change]
> Migration: [what to do instead]
```

Known Odoo 18 CE breaking changes to annotate:
- `_cr`, `_context`, `_uid` deprecated on models — use `self.env.cr`, `self.env.context`, `self.env.uid`
- `osv.osv` removed — use `models.Model`
- `<tree>` view tag deprecated — use `<list>`
- `type="tree"` in `ir.actions.act_window` deprecated — use `type="list"`
- `fields.Datetime.now()` returns aware datetime — ensure comparisons use aware datetimes
- HTTP controllers: `@http.route` signature changed for JSON endpoints

### 5. IPAI module naming
For any howto covering module creation:
```
> IPAI convention: custom modules use `ipai_` prefix. OCA modules use their upstream name unchanged.
> Module placement: odoo/custom/ipai_<name>/ for IPAI bridges, odoo/OCA/<repo>/ for OCA.
> Never modify OCA module source — create a thin `ipai_*` bridge that inherits.
```

### 6. Security / RLS alignment
For any howto covering access rights or security:
```
> IPAI security: all custom models must have ir.model.access.csv entries.
> Finance models: restrict to canonical pulser_* role groups (see pulser-finance-rbac skill).
> No ir.rule bypass for app clients — service role exceptions only.
```

## Operations

### Enhance a single howto page (`/pulser-odoo:odoo-docs-enhance $0`)
Argument: URL or local file path

1. Fetch the page content (use `curl -s $0` or read from file)
2. Strip HTML nav / sidebar — extract only the main content body
3. Convert to clean markdown
4. Apply IPAI overlays (sections 1–6 above) at relevant locations
5. Add a metadata header:
   ```
   ---
   source: $0
   version: odoo-18-ce
   enhanced: $(date -u +%Y-%m-%dT%H:%M:%SZ)
   index_target: product-help-index
   ipai_reviewed: false
   ---
   ```
6. Save to `docs/odoo-18-enhanced/<slug>.md`
7. Flag any sections that need manual IPAI review with `> ⚠️ REVIEW NEEDED:`

### Enhance all howtos (`/pulser-odoo:odoo-docs-enhance all`)
Run against the full howtos index:
- `web_services` — XML-RPC / JSON-RPC API
- `javascript_view` — Custom view types
- `website_themes` — Website Builder themes
- `define_module_data` — Demo and seed data
- `company` — Multi-company
- `translations` — i18n

Produce one enhanced file per page, then generate an index at
`docs/odoo-18-enhanced/INDEX.md` listing all pages, their status, and RAG ingestion readiness.

### Check ingestion readiness (`/pulser-odoo:odoo-docs-enhance check $0`)
For file `$0`, verify:
- [ ] Metadata header present
- [ ] IPAI version pin present
- [ ] No raw HTML remaining
- [ ] All `⚠️ REVIEW NEEDED` items have been addressed or marked as accepted
- [ ] File is under 100KB (Azure AI Search chunk limit)
Output: READY / NEEDS REVIEW with specific items
