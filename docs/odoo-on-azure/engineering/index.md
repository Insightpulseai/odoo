# Engineering

> **Benchmark**: AI-led SDLC with Azure and GitHub
> **Canonical source**: `agents/docs/engineering/` and `.github/docs/engineering/`

## Purpose

Cross-repo entry point for the engineering lifecycle documentation family. Full content lives in the subsystem directories that own the executable truth.

## Doc Ownership

| Topic | Canonical Location | Owner |
|---|---|---|
| AI-led engineering model (full) | [agents/docs/engineering/index.md](../../../agents/docs/engineering/index.md) | `agents` |
| AI-led SDLC | `agents/docs/engineering/ai-led-sdlc.md` | `agents` |
| Coding agent and quality agent | `agents/docs/engineering/coding-agent-and-quality-agent.md` | `agents` |
| SRE feedback loop | `agents/docs/engineering/sre-agent-and-operational-feedback.md` | `agents` |
| Spec-driven development | `.github/docs/engineering/spec-driven-development.md` | `.github` |
| Repo governance and policies | `.github/docs/engineering/repo-governance-and-policies.md` | `.github` |
| CI/CD and preview environments | `.github/docs/engineering/ci-cd-and-preview-environments.md` | `.github` |

## Benchmark Position

| Microsoft Reference | IPAI Equivalent | Status |
|---|---|---|
| Spec-driven development | `spec/` bundles (76) | Operational |
| Coding agents | GitHub Copilot + Claude Code + custom agents | Operational |
| Quality agents | `.github/agents/` + skills | Scaffold |
| CI/CD | GitHub Actions (CI) + Azure DevOps (deploy) | Operational |
| Preview environments | ACA revision-based previews | Partial |
| SRE feedback loops | Alert → n8n → backlog | Scaffold |

## Key Rule

Agent-generated code goes through the same CI gates as human-authored code. No `--no-verify`, no skipped hooks.

## Azure Boards and GitHub Traceability Model

### Canonical flow

```
Spec Bundle (spec/<target>/prd.md)
  └→ Azure Boards Epic ([TARGET] ...)
       └→ Feature ([FEATURE] ...)
            └→ User Story (WRITE: / EVIDENCE: / INDEX: ...)
                 └→ Task
                      └→ GitHub Branch → PR → Merge Commit
                           └→ Resolve AB#<id> / Validate AB#<id>
```

### Required conventions

| Convention | Rule |
|---|---|
| PR keyword | Every closing PR must include `Resolve AB#<id>` or `Validate AB#<id>` |
| Evidence PRs | Use `Validate AB#<id>` to signal proof, not just code |
| Bug fixes | Use `Fixes AB#<id>` |
| Bare references | `AB#<id>` links without state change — use for cross-references |
| Build status | YAML pipeline status must be linked on the work item |

### Traceability validation

- Boards → PR: every Closed Story has a linked PR
- PR → Build: every merged PR has a build result
- Build → Evidence: every `EVIDENCE:` Story has an artifact in `docs/evidence/`
- Evidence → Boards: every evidence artifact references its AB# work item

See `docs/planning/DOC_PROGRAM_WORK_ITEM_TEMPLATES.md` for full templates and keyword rules.

## Related Documents

- `docs/architecture/ODOO_ON_AZURE_REFERENCE_ARCHITECTURE.md` — Layer 7
- `docs/odoo-on-azure/reference/doc-authority.md` — ownership model
- `ssot/governance/platform-authority-split.yaml` — CI/CD authority
- `docs/planning/DOC_PROGRAM_WORK_ITEM_TEMPLATES.md` — work-item templates
- `docs/planning/DOC_PROGRAM_SPRINT_MODEL.md` — sprint operating model

---

*Created: 2026-04-05 | Version: 1.1*
