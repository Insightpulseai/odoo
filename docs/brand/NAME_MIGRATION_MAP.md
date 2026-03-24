# Pulser Brand Migration Map

**Authority**: `docs/brand/PULSER_NAMING_DOCTRINE.md`
**SSOT**: `ssot/brand/assistant-brand.yaml`
**Effective**: 2026-03-25

---

## Legacy → Canonical Name Mapping

| Legacy Term | Canonical Term | Surface | Status | Sunset Target |
|-------------|---------------|---------|--------|---------------|
| Odoo Copilot | **Pulser** | ERP assistant | Deprecated | Phase 1 (2026-03-25) |
| Ask Odoo Copilot | **Ask Pulser** | Landing page widget | Deprecated | Phase 1 (2026-03-25) |
| DIVA Copilot | **Pulser Diva** | Orchestration shell | Deprecated | Phase 1 (2026-03-25) |
| W9 Studio Copilot | **Pulser Studio** | Creative ops | Deprecated | Phase 1 (2026-03-25) |
| W9 Studio | **Pulser Studio** | Creative ops (product) | Deprecated | Phase 1 (2026-03-25) |
| Studio Copilot | **Pulser Studio** | Creative ops | Deprecated | Phase 1 (2026-03-25) |
| Pulsar | **Pulser** | Spelling variant | Deprecated | Phase 1 (2026-03-25) |
| Document Intelligence | **Pulser Docs** | Document review | Active alias | Phase 2 |

## Transition Aliases (Allowed During Migration)

| Canonical | Allowed Alias | Context | Sunset |
|-----------|--------------|---------|--------|
| Pulser | Pulser for Odoo | When platform clarity needed | Permanent (descriptive) |
| Pulser | InsightPulseAI Pulser | Pitch decks, formal docs | Permanent |
| Pulser Diva | Diva by Pulser | Marketing collateral | Phase 2 review |
| Pulser Studio | Pulser for W9 Studio | Compatibility/context pages | Phase 2 review |
| Ask Pulser | Ask Pulser for Odoo | Integration-specific pages | Permanent (descriptive) |

## Phase 1 Scope (Complete)

- [x] Landing page widget: "Ask Odoo Copilot" → "Ask Pulser"
- [x] Landing page UI labels: "Odoo Copilot" → "Pulser"
- [x] Server gateway mock responses: Pulser branding
- [x] SSOT brand registry: `ssot/brand/assistant-brand.yaml`
- [x] SSOT assistant surfaces: `ssot/agents/assistant_surfaces.yaml` v2
- [x] Architecture docs: `ASSISTANT_SURFACES.md`, `MARKETING_ASSISTANT_DOCTRINE.md`
- [x] Naming doctrine: `docs/brand/PULSER_NAMING_DOCTRINE.md`
- [x] Migration map: this file

## Phase 2 Scope (Pending)

- [ ] Remaining `docs/architecture/*.md` files (~20 files)
- [ ] Spec bundles (`spec/*/prd.md`, `constitution.md`)
- [ ] Governance YAML (`ssot/governance/*.yaml`)
- [ ] Agent platform references (`agent-platform/`)
- [ ] Web apps (control-room, saas-landing, diva-goals)
- [ ] Eval/benchmark names
- [ ] Odoo module `__manifest__.py` description + systray XML label
- [ ] n8n workflow display names
- [ ] Databricks notebook references

## Phase 3 Scope (Deferred)

- [ ] Odoo module technical name (`ipai_odoo_copilot` → only at major version bump)
- [ ] Azure resource names (`ipai-copilot-gateway` → infrastructure, low priority)
- [ ] Repository slugs (if/when separate repos created)
- [ ] npm/pip package names

---

*Last updated: 2026-03-25*
