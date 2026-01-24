# Dump Review → Stack Upgrades Prompt

Use this template when reviewing pasted dumps (notes, screenshots, links, chat logs) to extract actionable stack improvements.

---

## How to Use

1. Paste the dump content in sections
2. For EACH section, apply the template below
3. Output concrete artifacts (SQL, YAML, scripts, docs)

---

## Template (apply to each section)

### A) What this section is (1–2 lines)
- Identify the domain (e.g., CI/CD, observability, agent runtime, docs surface, testing, k8s, etc.)
- Identify whether it's **actionable** for our stack.

### B) Fit to current stack (bullet map)
Map to:
- **Odoo CE + OCA** on DigitalOcean (ERP layer)
- **Supabase** (system-of-record observability plane)
- **Vercel** (frontend + optional Observability Plus retention)
- **n8n** (automation fabric, thin orchestrator)
- **GitHub** (Spec Kit + CI gates)
- **External docs** (Figma/Microsoft/GitHub/SAP knowledge surfaces)

### C) Improvements (prioritized, no fluff)
Give:
- **P0**: immediate wins (≤3) — can implement now
- **P1**: next iteration (≤3) — implement this week
- **P2**: later (≤3) — backlog

Each improvement must include:
- **What** to change
- **Where** (file paths / component / service)
- **How to validate** (commands + expected evidence artifact)

### D) Risks / failure modes (≤5 bullets)

### E) Output artifacts to add to repo
One or more of:
- Migration SQL (`db/migrations/*.sql`)
- Workflow YAML (`.github/workflows/*.yml`)
- Audit scripts (`scripts/audit/*`)
- Architecture docs (`docs/architecture/*`)
- Evidence generator (`docs/evidence/*`)
- n8n workflow JSON (`n8n/workflows/*.json`)

---

## Example Application

**Section**: "Vercel llms-full.txt documentation format"

### A) What this is
- Documentation packaging format for LLM consumption
- Actionable: YES — we can adopt this pattern for our docs

### B) Fit to current stack
- **GitHub**: Store llms-full.txt in repo root
- **Vercel**: Serve at `/llms-full.txt` route
- **n8n**: Use in workflow context injection
- **External docs**: Fetch and index external llms packs

### C) Improvements
- **P0**: Create `docs/llms-full.txt` generator script
- **P0**: Add to CI to regenerate on doc changes
- **P1**: Fetch external llms packs (Vercel, n8n, OCA)
- **P2**: Auto-inject into Claude Code context

### D) Risks
- External fetches may 403 (record failures, don't fail silently)
- Large llms-full.txt may exceed context limits
- Version drift between llms.txt and actual docs

### E) Artifacts
- `scripts/docs/build_llms_full.sh`
- `scripts/docs/fetch_external_llms_packs.sh`
- `.github/workflows/docs-llms-update.yml`

---

## Agent Prompt (copy-paste ready)

```text
[ROLE] Senior platform engineer + automation architect. Review a pasted multi-topic "dump" (notes, screenshots, links, chat logs). Produce actionable improvements to my production stack.

[GOAL] For each section of the dump, identify what it suggests for improving: (1) Odoo+OCA, (2) Supabase, (3) Vercel, (4) DigitalOcean/Docker, (5) n8n workflows, (6) agentic AI runtime patterns.

[CONSTRAINTS]
- No UI instructions. Output CLI/scripts/config only.
- Prefer idempotent automation.
- Assume n8n is self-hosted in Docker on DigitalOcean.
- Assume Supabase is the backend and Vercel hosts the frontend.
- Provide concrete artifacts: compose snippets, env templates, workflow JSON, SQL, GitHub Actions YAML.

[OUTPUT FORMAT]
For each section:
1) What it is (1 sentence)
2) Risk/limitation if used naïvely (bullets)
3) Best-practice integration into my stack (bullets)
4) Concrete artifacts (code blocks):
   - n8n workflow snippet or node plan
   - Supabase SQL / Edge Function stub (if relevant)
   - Docker compose / env changes (if relevant)
   - CI checks / GitHub Actions (if relevant)
5) Verification commands (curl/sql/kubectl where applicable)
```

---

## Quick Reference: Stack Components

| Component | Role | Key Files |
|-----------|------|-----------|
| Odoo CE + OCA | ERP runtime | `addons/ipai/**`, `docker-compose.yml` |
| Supabase | Observability SSOT | `db/migrations/*.sql` |
| Vercel | Frontend + deploys | `apps/web/**`, deploy hooks |
| n8n | Automation fabric | `n8n/workflows/**/*.json` |
| GitHub | CI + Spec Kit | `.github/workflows/**`, `spec/**` |
| DigitalOcean | Infrastructure | `infra/do-oca-stack/**` |
