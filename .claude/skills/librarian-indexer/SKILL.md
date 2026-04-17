---
name: librarian-indexer
description: Meta-skill that indexes, audits, and auto-generates Claude skills for the IPAI platform. Covers skill cataloguing, drift detection, auto-generation workflows, Azure Pipelines CI gates, and IPAI-specific trigger routing. Use when creating/updating skills, auditing the skill library for stale references, or wiring new agents into the skill registry.
---

# Librarian Indexer — IPAI Edition v3.0

## What this skill does

Maintains the `/mnt/skills/user/` catalogue as a living, auditable asset:
- Generates new skill stubs from a validated template
- Detects drift: deprecated references, wrong Odoo version, wrong CI system
- Routes skill load triggers to the correct skill bundles
- Writes or updates `skills-registry.json` entries
- Produces Azure Pipelines lint gates for skill hygiene

**CI/CD doctrine**: Azure Pipelines is the sole CI/CD authority. GitHub Actions is FORBIDDEN — remove any reference on sight.

---

## §1 — IPAI skill inventory (canonical)

### `/mnt/skills/user/` — current catalogue

| Skill folder | Domain | Load trigger |
|---|---|---|
| `ipai-platform` | Master bundle — Azure resources, agent routing, WAF | "IPAI", "InsightPulseAI", "Pulser", any Azure resource name |
| `ipai-odoo-platform` | Odoo 18 CE dev, OCA-first, BIR compliance, ACA deploy | "Odoo", "OCA", "ipai_*", "BIR", "`<list>`", "view_mode" |
| `ipai-resource-map` | Azure resource constants — MIs, RGs, sub IDs | Any IPAI Azure resource lookup |
| `ipai-agent-platform` | MAF patterns, Foundry Agent Service, judge infra | "agent", "MAF", "Foundry agent", "judge" |
| `odoo18-ce-development` | Odoo 18 CE Smart Delta, OCA conventions, ACA deploy | "Odoo 18", "delta module", "Smart Delta" |
| `prisma2020-flow-diagram` | PRISMA 2020 R + Python flow diagrams | "PRISMA", "systematic review", "flow diagram" |
| `doing-meta-analysis-r` | Harrer et al. R meta-analysis methodology | "meta-analysis", "forest plot", "heterogeneity", "I²" |
| `meta-analysis-pipeline` | Python PRISMA + forest/funnel without R | "Python meta-analysis", "pub bias", "PRISMA Python" |
| `consulting-writeup-pwc` | PwC-style reports, SCQA, answer-first | "consulting", "PwC", "board-ready", "executive summary" |
| `editorial-pipeline-tools` | Schema-first linting, YAML-to-deck CI | "editorial CI", "linter", "SCQA validate" |
| `editorial-print-production` | Print-ready PDF, InDesign handoff, CMYK | "print", "InDesign", "CMYK", "bleed" |
| `design-system-engineer` | Fluent 2, Material 3, Fiori token translation | "design system", "Fluent", "token", "component" |
| `figma-design-to-code` | Figma MCP → React/Tailwind/Odoo code | "Figma", "design-to-code", "Code Connect" |
| `fluent-perf-testing` | Playwright + Lighthouse CI for Fluent 2 UI | "performance test", "Lighthouse", "Fluent perf" |
| `mcp-complete-guide` | Production MCP server, 11-phase guide | "MCP server", "tool schema", "semantic layer" |
| `drawio-diagrams-enhanced` | draw.io XML + PMBOK shapes | "draw.io", "BPMN", "swimlane", "WBS" |
| `pmbok-project-management` | PMBOK 7, risk, schedule, cost control | "PMBOK", "project management", "risk register" |
| `librarian-indexer` | This skill — catalogue management | "skill index", "catalogue", "skill audit", "librarian" |

### `/mnt/skills/public/` — platform skills (read-only)

`docx`, `pdf`, `pdf-reading`, `pptx`, `xlsx`, `frontend-design`, `file-reading`, `product-self-knowledge`

### `/mnt/skills/examples/` — example skills (read-only)

`web-artifacts-builder`, `skill-creator`, `mcp-builder`, `brand-guidelines`, `theme-factory`

---

## §2 — Skill metadata schema

Every skill MUST have a valid YAML frontmatter block:

```yaml
---
name: <kebab-case-name>
description: >
  One-sentence trigger description (what Claude should load this skill for).
  Include: domain keywords, primary use cases, what it replaces/pairs with.
  ≤ 200 characters for accurate trigger matching.
---
```

### Extended registry entry (skills-registry.json)

```jsonc
{
  "name": "ipai-bir-tax-compliance",
  "path": "/mnt/skills/user/ipai-bir-tax-compliance/SKILL.md",
  "domain": "finance",
  "plane": "CoreOps",
  "ado_area": "InsightPulseAI\\CoreOps",
  "odoo_version": "18.0",
  "depends_on": ["ipai-odoo-platform", "ipai-resource-map"],
  "agents": ["tax_guru"],
  "deprecated_refs": [],
  "last_audited": "2026-04-15",
  "status": "active"
}
```

---

## §3 — Drift detection rules

Run this audit before publishing any skill update. Flag as errors:

| Pattern | Rule | Action |
|---|---|---|
| `GitHub Actions` / `.github/workflows` | FORBIDDEN — Azure Pipelines only | Remove entirely |
| `Supabase` / `supabase` | DEPRECATED | Remove; replace with `pg-ipai-odoo platform schema` |
| `Vercel` / `vercel` | DEPRECATED | Remove; replace with ACA |
| `n8n` / `n8n.io` | DEPRECATED | Remove; replace with Service Bus |
| `DigitalOcean` / `DO droplet` | DEPRECATED | Remove |
| `Cloudflare` / `cloudflare` | DEPRECATED | Remove |
| `nginx` | DEPRECATED | Remove |
| `Odoo 19` / `odoo19` / `19.0.*` in version | Wrong version | Replace with Odoo 18 CE / `18.0.*` |
| `<tree>` in Odoo view XML | Deprecated tag | Replace with `<list>` |
| `view_mode="tree` | Deprecated value | Replace with `view_mode="list,form"` |
| `DockerHub` / `docker.io` | Not IPAI registry | Replace with `acripaidev.azurecr.io` |
| `secrets.GITHUB_TOKEN` | GitHub Actions secret | Remove (Azure Pipelines uses service connection) |
| `Supabase project: spdtwktxdalcfigzeqrz` | Stale credential hint | Remove |
| `pgvector` without `pg-ipai-odoo` context | Missing resource context | Add `pg-ipai-odoo.postgres.database.azure.com` |

### Drift scan (bash)

```bash
# Run from repo root — exits non-zero if violations found
grep -rn \
  "GitHub Actions\|\.github/workflows\|supabase\|Supabase\|Vercel\|vercel\|n8n\|DigitalOcean\|cloudflare\|Cloudflare\|DockerHub\|dockerhub\|Odoo 19\|odoo19\|<tree>\|view_mode=\"tree\|nginx" \
  /mnt/skills/user/ \
  --include="*.md" \
  | grep -v "DEPRECATED\|deprecated\|removed\|do not use" \
  | tee /tmp/skill-drift.txt

VIOLATIONS=$(wc -l < /tmp/skill-drift.txt)
echo "Drift violations: $VIOLATIONS"
[ "$VIOLATIONS" -eq 0 ] && echo "PASS" || exit 1
```

---

## §4 — Skill generation template

Use this template when creating a new `ipai_*` skill from scratch:

```markdown
---
name: <skill-name>
description: >
  <Trigger description — what Claude loads this for. Include domain keywords.>
---

# <Skill title> — IPAI Edition

## Purpose
<One paragraph. What problem does this solve? Which agents/modules does it serve?>

## Scope
- Odoo version: 18.0 CE
- OCA-first: yes — list OCA modules this depends on
- ipai_* delta: yes/no — only when CE+OCA cannot cover
- Azure resources: list canonical names (ipai-copilot-resource, pg-ipai-odoo, etc.)
- Agents: list provisioned agents this skill serves

## Prerequisites
- [ ] `ipai-odoo-platform` loaded (for Odoo 18 CE conventions)
- [ ] `ipai-resource-map` loaded (for Azure resource names)

## Core patterns

### [Pattern name]
<Code, config, or structured guidance. Production-grade only.>

## Odoo conventions (enforced)
- Views: `<list>` always — never `<tree>`
- `view_mode="list,form"` — never `"tree,form"`
- Module version: `18.0.x.x.x`
- Depends: OCA modules first, `ipai_*` delta last

## Azure conventions (enforced)
- CI/CD: Azure Pipelines only (`azure-pipelines/`)
- GitHub Actions: FORBIDDEN
- Secrets: `kv-ipai-dev-sea` — never in code
- Registry: `acripaidev.azurecr.io` — never DockerHub
- Identity: `DefaultAzureCredential` → `ManagedIdentityCredential` in prod

## Artifact paths
| Output | Target path |
|---|---|
| Odoo module | `odoo/addons/ipai/<module_name>/` |
| Azure IaC | `infra/azure/<resource-type>/*.bicep` |
| Pipeline | `azure-pipelines/*.yml` |
| Agent skill | `agents/skills/<domain>/SKILL.md` |
| Platform contract | `platform/contracts/*.yaml` |
| Runbook | `docs/runbooks/*.md` |

## Related skills
- Pairs with: `ipai-odoo-platform`, `ipai-resource-map`
- ADO area path: `InsightPulseAI\<CoreOps|AdsIntel|Research|DataIntel|Platform|ReleaseOps>`
```

---

## §5 — Skill trigger routing (IPAI-specific)

Load triggers for Claude — map user intent to correct skill bundles:

```yaml
triggers:
  # Core operations
  odoo_general:
    keywords: ["Odoo", "OCA", "module", "ipai_*", "addons", "manifest"]
    load: [ipai-odoo-platform, ipai-resource-map]

  bir_tax:
    keywords: ["BIR", "2307", "2550M", "1601-C", "SAWT", "ATC code", "eBIRForms"]
    load: [ipai-odoo-platform, ipai-resource-map]
    agent: tax_guru

  bank_recon:
    keywords: ["reconciliation", "account_reconcile", "bank statement", "period close"]
    load: [ipai-odoo-platform, ipai-resource-map]
    agent: bank_recon

  finance_close:
    keywords: ["month-end", "mis_builder", "D+5", "period lock", "Finance Close"]
    load: [ipai-odoo-platform, ipai-resource-map]
    agent: finance_close

  # Agent platform
  agent_build:
    keywords: ["MAF", "agent framework", "Foundry agent", "skill file", "judge"]
    load: [ipai-agent-platform, ipai-resource-map]

  mcp_server:
    keywords: ["MCP server", "tool schema", "ipai-odoo-mcp", "FastMCP", "StreamableHTTP"]
    load: [mcp-complete-guide, ipai-agent-platform]

  # Azure / infra
  azure_infra:
    keywords: ["Bicep", "ACA", "pg-ipai-odoo", "kv-ipai-dev-sea", "rg-ipai"]
    load: [ipai-resource-map, ipai-platform]

  ci_cd:
    keywords: ["azure-pipelines", "pipeline", "build agent", "ipai-build-agent"]
    load: [ipai-resource-map]
    note: "Azure Pipelines only — never GitHub Actions"

  # Research / PrismaLab
  systematic_review:
    keywords: ["PRISMA", "systematic review", "meta-analysis", "forest plot", "RoB"]
    load: [prisma2020-flow-diagram, doing-meta-analysis-r, meta-analysis-pipeline]

  # Creative / media
  w9_studio:
    keywords: ["W9 Studio", "TVC", "content job", "booking", "Sora 2", "finishing"]
    load: [ipai-resource-map]

  # Skill management
  skill_audit:
    keywords: ["skill", "catalogue", "index", "drift", "librarian"]
    load: [librarian-indexer]
```

---

## §6 — Azure Pipelines gate for skill hygiene

Add to `azure-pipelines/skill-audit.yml`:

```yaml
# azure-pipelines/skill-audit.yml
trigger:
  paths:
    include: [agents/skills/**/*.md, docs/**/*.md]

pool:
  name: ipai-build-agent

jobs:
  - job: SkillDriftCheck
    displayName: Skill drift audit
    steps:
      - script: |
          VIOLATIONS=$(grep -rn \
            "GitHub Actions\|\.github/workflows\|supabase\|Supabase\|Vercel\|n8n\|DigitalOcean\|Cloudflare\|DockerHub\|Odoo 19\|<tree>\|view_mode=\"tree" \
            agents/skills/ docs/ \
            --include="*.md" \
            | grep -v "DEPRECATED\|deprecated\|removed" \
            | wc -l)

          echo "Drift violations: $VIOLATIONS"
          [ "$VIOLATIONS" -eq 0 ] && echo "##vso[task.setvariable variable=driftClean]true" || \
          { echo "##vso[task.logissue type=error]Skill drift detected: $VIOLATIONS violations"; exit 1; }
        displayName: Drift scan

      - script: |
          # Validate all SKILL.md files have valid frontmatter
          python - << 'EOF'
          import os, yaml, sys
          failures = []
          for root, dirs, files in os.walk('agents/skills'):
              for f in files:
                  if f == 'SKILL.md':
                      path = os.path.join(root, f)
                      with open(path) as fh:
                          content = fh.read()
                      if not content.startswith('---'):
                          failures.append(f"{path}: missing frontmatter")
                          continue
                      parts = content.split('---', 2)
                      if len(parts) < 3:
                          failures.append(f"{path}: malformed frontmatter")
                          continue
                      try:
                          meta = yaml.safe_load(parts[1])
                          if 'name' not in meta:
                              failures.append(f"{path}: missing 'name' field")
                          if 'description' not in meta:
                              failures.append(f"{path}: missing 'description' field")
                      except Exception as e:
                          failures.append(f"{path}: YAML parse error: {e}")
          if failures:
              for f in failures: print(f"ERROR: {f}")
              sys.exit(1)
          print(f"OK: all SKILL.md files valid")
          EOF
        displayName: Frontmatter validation
```

---

## §7 — Auto-generation workflows

### Workflow A: New `ipai_*` Odoo delta module skill

```
Input: "Create skill for ipai_ar_collections"

Steps:
1. Load ipai-odoo-platform (OCA-first hierarchy, Odoo 18 CE conventions)
2. Load ipai-resource-map (Azure resource names)
3. Identify OCA base modules: account_credit_control, credit_control_*
4. Map to provisioned agent: pulser (id-ipai-agent-pulser-dev)
5. Apply §4 template:
   - name: ipai-ar-collections
   - plane: CoreOps
   - depends_on: [ipai-odoo-platform, ipai-resource-map]
   - agents: [pulser]
6. Add OCA module install snippet (CE conventions, no GitHub Actions)
7. Add Azure Pipelines deploy step (azure-pipelines/odoo-deploy.yml)
8. Validate drift (§3) — zero violations
9. Write agents/skills/ar_collections/SKILL.md
10. Update agents/registry/skills-index.json entry
```

### Workflow B: New agent skill from MAF pattern

```
Input: "Create skill for the bank_recon agent"

Steps:
1. Load ipai-agent-platform (MAF patterns, Foundry wiring)
2. Load ipai-resource-map (id-ipai-agent-bank-recon-dev, cosmos-ipai-dev)
3. Document sub-agent pipeline (Ledger Collector → Discrepancy Detector → Correction Suggestion)
4. Map tools: ipai-odoo-mcp tools used, srch-ipai-dev indexes
5. Document Service Bus trigger: sb-ipai-dev-sea topic
6. Apply §4 template with agent-specific sections
7. Validate: no GitHub Actions, no Supabase, Odoo 18 CE only
8. Write agents/skills/finance_recon/SKILL.md
```

### Workflow C: Skill audit + remediation

```
Input: "Audit all skills for drift"

Steps:
1. Run §3 drift scan across /mnt/skills/user/
2. Categorise findings: deprecated refs / wrong version / wrong CI
3. For each violation:
   a. Identify the deprecated term
   b. Apply correct IPAI equivalent (§3 action column)
   c. Verify fix doesn't introduce new violations
4. Re-run scan → zero violations
5. Update last_audited timestamp in skills-registry.json
6. Commit: "chore(skills): drift remediation YYYY-MM-DD"
```

---

## §8 — Canonical repo paths for skill artefacts

```
agents/
  skills/
    <domain>/
      SKILL.md                 # Claude-readable skill
  registry/
    skills-index.json          # Lightweight index (name, path, trigger keywords)
  system/
    *.system.md                # Agent system prompts

platform/
  contracts/
    *.schema.json              # JSON Schema for skill payloads

docs/
  runbooks/
    skill-audit.md             # This workflow as a runbook

azure-pipelines/
  skill-audit.yml              # §6 pipeline gate
```

---

## §9 — Known violations in current library (as of 2026-04-15)

Run remediation immediately:

| Skill | File | Violation | Fix |
|---|---|---|---|
| librarian-indexer | SKILL.md:15 | "GitHub Actions" | Remove section |
| librarian-indexer | SKILL.md:69 | "push_to_dockerhub" | Replace with `acripaidev.azurecr.io` |
| librarian-indexer | SKILL.md:143-263 | Full GitHub Actions templates | Replace with Azure Pipelines equivalents |
| librarian-indexer | SKILL.md:630 | "Supabase, Superset, Notion" | Remove — deprecated |
| librarian-indexer | SKILL.md:719-734 | `odoo19-oca-devops`, `supabase-rpc-manager` | Replace with `ipai-odoo-platform`, `ipai-resource-map` |
| librarian-indexer | SKILL.md:924-951 | GitHub Actions examples + Supabase project ID | Remove entirely |
| librarian-indexer | SKILL.md:964 | `odoo19-oca-devops/` in directory tree | Replace with `ipai-odoo-platform` |
| librarian-indexer | SKILL.md:966 | `supabase-rpc-manager/` in directory tree | Remove |
| librarian-indexer | SKILL.md:1039 | `odoo19-oca-devops + oca-bot-integration` trigger | Replace with `ipai-odoo-platform, ipai-resource-map` |
| librarian-indexer | SKILL.md:1044 | "Supabase" trigger → `supabase-rpc-manager` | Remove |

Total violations: 18. All in the skill that manages all other skills — fix first.
