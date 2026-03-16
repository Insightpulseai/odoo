# Copilot Runtime Selection Contract (C-30)

Version: 1.0.0 | Status: Active | Created: 2026-03-13

## Purpose

Declares which copilot module is the canonical runtime for the InsightPulse AI
Odoo platform, and formally deprecates the legacy Gemini/Supabase bridge path.

---

## Canonical Runtime

| Attribute | Value |
|-----------|-------|
| **Module** | `addons/ipai/ipai_odoo_copilot` |
| **Spec bundle** | `spec/ipai-odoo-copilot-azure/` |
| **SSOT manifests** | `ssot/ai/` |
| **AI Runtime** | Azure AI Foundry (project `data-intel-ph`) |
| **Model** | `gpt-4.1` via Azure AI Agent Service |
| **Knowledge** | Azure AI Search (`srch-ipai-dev`) |
| **Auth** | Managed identity (IMDS) → env key (`AZURE_FOUNDRY_API_KEY`) fallback |
| **Odoo role** | Thin config/control surface — settings UI, health probe, agent verification |
| **Foundry role** | Execution runtime — chat, tools, knowledge grounding |
| **Secrets posture** | Never in Odoo DB; env vars / Azure Key Vault only |

---

## Deprecated Runtime

| Attribute | Value |
|-----------|-------|
| **Module** | `addons/ipai/ipai_ai_copilot` |
| **Contract** | C-17 (`AI_COPILOT_CONTRACT.md`) — status changed to **Deprecated** |
| **AI Runtime** | Gemini via Vercel bridge → Supabase pgvector RAG |
| **Status** | **DEPRECATED** as of 2026-03-13 |
| **Reason** | Platform is migrating to Azure-native architecture; Gemini bridge depends on deprecated Vercel deployment and `ipai_ai_widget` (also deprecated) |

### Deprecation constraints

- `ipai_ai_copilot` remains `installable: True` because `ipai_workspace_core` depends on it
- No new features, tools, or integrations should target `ipai_ai_copilot`
- Migration path: `ipai_workspace_core` must remove its `ipai_ai_copilot` dependency before the legacy module can be set to `installable: False`
- C-17 contract is frozen — no updates to the Gemini bridge endpoint contract
- C-25 (Governed Tool Specs) transitions to `ipai_odoo_copilot` tool dispatch when Phase 3 tools are implemented

---

## Architecture

```
ipai_odoo_copilot (canonical)
  Odoo ──config/health──► Azure AI Foundry (data-intel-ph)
                              ├── gpt-4.1 agent
                              ├── Azure AI Search (srch-ipai-dev)
                              └── Tool execution (Phase 3, future)

ipai_ai_copilot (deprecated)
  Odoo ──bridge HTTP──► Vercel (deprecated) ──► Gemini API
                              └── Supabase pgvector RAG
```

---

## Validation

| Check | Method |
|-------|--------|
| SSOT AI manifests valid | `python3 scripts/ci/validate_ssot_ai.py` → exit 0 |
| Module compiles | `python3 -m py_compile addons/ipai/ipai_odoo_copilot/models/*.py` |
| Spec bundle complete | 4 files in `spec/ipai-odoo-copilot-azure/` |
| No secrets in module | grep for hardcoded keys → 0 matches |
| Config resolution | `ir.config_parameter` keys only store non-secret Azure coordinates |

---

## Change Log

| Date | Version | Change |
|------|---------|--------|
| 2026-03-13 | 1.0.0 | Initial contract: `ipai_odoo_copilot` canonical, `ipai_ai_copilot` deprecated |
