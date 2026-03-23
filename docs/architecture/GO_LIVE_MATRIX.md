# Go-Live Matrix

> Per-surface readiness matrix. Cross-references the Go-Live Checklist with each assistant surface.
> SSOT: `ssot/governance/copilot_release_stages.yaml`

---

## Surface Readiness

| Gate | Odoo Copilot | Diva Copilot | Studio Copilot | Genie | Doc Intelligence |
|------|:---:|:---:|:---:|:---:|:---:|
| Identity (Entra) | Partial | Partial | Not started | Not started | Not started |
| Secrets (Key Vault) | Done | Done | Not started | Not started | Partial |
| Model contract | Done (gpt-4.1) | Done (gpt-4.1) | Not started | Not started | Partial (docai) |
| KB / retrieval | Done (26 chunks) | Partial (mode KBs) | Not started | Not started | Partial (OCR) |
| Eval pack | Not started | Not started | Not started | Not started | Not started |
| Audit trail | Done | Done | Not started | Not started | Not started |
| Rate limiting | Done | Done | Not started | Not started | Not started |
| Company scoping | Done | Done | N/A (workspace) | N/A (data gov) | Done |
| Write gate (fail-closed) | Done | Done | N/A | N/A (read-only) | N/A |
| Streaming | Done | Done | Not started | Not started | N/A |
| SLO baseline | Not started | Not started | Not started | Not started | Not started |
| Privacy docs | Not started | Not started | Not started | Not started | Not started |
| Partner Center | Not started | Not started | Not started | Not started | Not started |

---

## Go-Live Sequence

### Wave 1 — Internal Beta (Current)

- Odoo Copilot: advisory read-only, trusted internal users
- Diva Copilot: mode routing, trusted internal users

### Wave 2 — Grounded Retrieval GA

Prerequisites: eval pack pass, docs corpus expansion, SLO baseline

- Odoo Copilot: grounded retrieval, expanded KB
- Diva Copilot: all modes with quality-gated routing

### Wave 3 — Action Execution

Prerequisites: write gate validation, maker-checker for sensitive actions

- Odoo Copilot: controlled write actions (fail-closed -> policy-gated)
- Document Intelligence: extraction -> Odoo record creation

### Wave 4 — Analytics and Creative

Prerequisites: semantic layer, provider broker, workspace isolation

- Genie: governed analytics Q&A
- Studio Copilot: creative finishing pipeline

### Wave 5 — Marketplace

Prerequisites: Teams app package, Partner Center submission, privacy docs

- All surfaces: marketplace listing eligibility

---

## Blocking Dependencies

| Blocker | Surfaces Affected | Resolution |
|---------|-------------------|------------|
| Eval pack not created | All | Create per-surface eval packs with pass/fail thresholds |
| SLO baseline missing | All | Establish 7-day baseline in staging |
| Entra identity not wired | All | Complete Entra app registration + OIDC |
| Full docs corpus (26 -> 7000+) | Odoo Copilot, Diva | Full Odoo 19 documentation crawl + index |
| Semantic layer not wired | Genie | Databricks SQL + Power BI semantic model |
| Provider broker not implemented | Studio | fal/Gemini/Imagen integration |
| Workspace isolation not implemented | Studio | `workspace_id` scoping |

---

## SSOT References

- Go-live checklist: `docs/architecture/GO_LIVE_CHECKLIST.md`
- Release stages: `ssot/governance/copilot_release_stages.yaml`
- Per-surface status: `ssot/agents/diva_copilot.yaml#release`
- AgentOps doctrine: `docs/architecture/AGENTOPS_DOCTRINE.md`

---

*Last updated: 2026-03-24*
