# Repo Boundaries

> Defines the ownership boundary between the umbrella monorepo and nested git repositories.

## Rule

The umbrella repo (`Insightpulseai`) tracks only umbrella-native assets. Nested git repositories are managed as **separate git boundaries** and must never have their contents staged in the umbrella index.

## Nested Repos (Must Not Track)

| Path | Ownership | Purpose |
|------|-----------|---------|
| `odoo/` | Separate git repo | ERP runtime (Odoo 19 CE + OCA + IPAI bridge) |
| `data-intelligence/` | Separate git repo | Databricks analytics engineering |
| `documentaion/` | Separate git repo | Legacy docs (review for archival) |
| `web-site/` | Separate git repo | Legacy web site (review for archival) |
| `archive/dot-github-repo/` | Separate git repo | Archived org governance |
| `archive/work/` | Separate git repo | Archived work |
| `archive/root/addons/oca/` | Embedded OCA repos | Archived OCA submodules |

All of the above are excluded via `.gitignore` at the umbrella root.

## Umbrella-Native Paths

These paths are owned and tracked by the umbrella repo:

| Path | Domain |
|------|--------|
| `addons/` | Odoo modules (ipai_*, shared across repos) |
| `agents/` | Agent personas, skills, evals |
| `agent-platform/` | Agent runtime engine |
| `automations/` | n8n workflows, scheduled jobs |
| `docs/` | Cross-repo architecture and governance |
| `design/` | Design tokens and brand assets |
| `infra/` | IaC, DNS, Azure config |
| `packages/` | Shared Node packages |
| `platform/` | Platform control plane |
| `scripts/` | Automation scripts |
| `spec/` | Spec bundles |
| `ssot/` | Intended-state truth |
| `web/` | Web surfaces (ops console, landing pages) |
| `.github/` | CI/CD workflows |

## Enforcement

- `.gitignore`: Prevents accidental staging of nested repo contents
- `ssot/repo/ownership-boundaries.yaml`: Machine-readable boundary rules
- Agent behavior: Never stage files from nested repos in the umbrella commit set

## Managing Nested Repos

Each nested repo is managed independently:

```bash
# Umbrella work
cd /Users/tbwa/Documents/GitHub/Insightpulseai
git add agents/ docs/ ...  # only umbrella-native paths

# Odoo work (separate repo)
cd odoo/
git add addons/ipai/...    # managed in its own git history
```

Do not mix umbrella and nested repo changes in a single commit.

---

*Last updated: 2026-03-24*
