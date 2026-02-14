# AI Module Deprecation Manifest

**Version:** 1.0.0
**Status:** Authoritative
**Last Updated:** 2026-01-13

---

## Purpose

This document lists all IPAI AI modules and their deprecation status under the minimal AI layer policy.

---

## Policy Summary

Per the minimal stack policy:

- **KEEP**: Only 4 survivor modules (2 business + 1 theme + 1 bridge)
- **DEPRECATE**: All other AI modules
- **REPLACE**: Use CE/OCA equivalents where available

---

## Survivor Modules (KEEP)

| Module | Version | Purpose | Status |
|--------|---------|---------|--------|
| `ipai_bir_compliance` | 18.0.1.0.0 | BIR 2307 & Alphalist | KEEP |
| `ipai_finance_ppm` | 18.0.1.1.0 | Finance PPM (Notion parity) | KEEP |
| `ipai_theme_copilot` | 18.0.1.0.0 | Fluent-style TBWA theme | KEEP (new) |
| `ipai_ask_ai_bridge` | 18.0.1.0.0 | External Copilot launcher | KEEP (new) |

**Total: 4 modules** (2 business + 1 theme + 1 bridge)

---

## AI Modules to Deprecate

### Tier 1: Immediate Deprecation (No Dependencies)

These modules have no critical dependents and can be removed immediately:

| Module | Reason | Replacement |
|--------|--------|-------------|
| `ipai_aiux_chat` | Unfinished scaffold | External Copilot UI |
| `ipai_document_ai` | Optional OCR | External OCR service |
| `ipai_marketing_ai` | Domain-specific | N/A (not in scope) |
| `ipai_studio_ai` | NL customization | N/A (not in scope) |
| `ipai_advisor` | Recommendations | N/A (not in scope) |
| `ipai_ai_connectors` | Webhook integrations | External integrations |
| `ipai_ai_sources_odoo` | KB export | External ETL |
| `ipai_ai_provider_kapa` | Kapa RAG | Pulser gateway |

### Tier 2: Consolidation Required

These modules have overlapping functionality - choose ONE or deprecate all:

| Module | Overlaps With | Decision |
|--------|---------------|----------|
| `ipai_copilot_ui` | `ipai_copilot_hub`, `ipai_ai_agents_ui` | DEPRECATE (use external UI) |
| `ipai_copilot_hub` | `ipai_copilot_ui` | DEPRECATE (use external UI) |
| `ipai_ai_copilot` | `ipai_ai_agents`, `ipai_ai_agents_ui` | DEPRECATE (use bridge) |
| `ipai_ai_agents` | `ipai_ai_copilot` | DEPRECATE (use bridge) |
| `ipai_ai_agents_ui` | `ipai_ai_copilot` | DEPRECATE (use external UI) |

### Tier 3: Core Infrastructure (Review Required)

These modules provide foundational capabilities - evaluate carefully:

| Module | Purpose | Recommendation |
|--------|---------|----------------|
| `ipai_ai_core` | AI threads/messages | DEPRECATE - move to external service |
| `ipai_agent_core` | Skill/tool registry | DEPRECATE - move to external service |
| `ipai_ai_provider_pulser` | AI gateway | DEPRECATE - use external Pulser directly |
| `ipai_ai_prompts` | Prompt templates | DEPRECATE - move to Spec Kit |
| `ipai_ai_audit` | Governance/audit | DEPRECATE - use external logging |

### Tier 4: Finance-Specific (Conditional)

| Module | Depends On | Recommendation |
|--------|------------|----------------|
| `ipai_ask_ai` | `ipai_finance_ppm` | DEPRECATE - use external RAG |
| `ipai_ask_ai_chatter` | `ipai_ask_ai` | DEPRECATE - use external RAG |

---

## Deprecation Process

### Step 1: Mark as Deprecated

Add to each module's `__manifest__.py`:

```python
{
    "installable": False,  # Prevent new installs
    "deprecated": True,
    "deprecated_by": "ipai_ask_ai_bridge",
    "deprecation_reason": "Replaced by external AI service per ASK_AI_CONTRACT.md",
}
```

### Step 2: Add Migration Notice

Create `migrations/18.0.1.0.0/pre-migrate.py`:

```python
import logging
_logger = logging.getLogger(__name__)

def migrate(cr, version):
    _logger.warning(
        "Module ipai_xxx is deprecated. "
        "AI functionality moved to external service. "
        "See docs/architecture/ASK_AI_CONTRACT.md"
    )
```

### Step 3: Update Dependencies

Any module depending on deprecated AI modules should:
1. Remove the dependency
2. Use `ipai_ask_ai_bridge` for launcher functionality
3. Call external service directly for AI features

### Step 4: Archive (Future)

After verification period, modules will be:
1. Moved to `addons/_deprecated/`
2. Eventually removed from repository

---

## Timeline

| Phase | Action | Modules |
|-------|--------|---------|
| Phase 1 | Mark deprecated | Tier 1 (8 modules) |
| Phase 2 | Consolidate | Tier 2 (5 modules) |
| Phase 3 | Migrate core | Tier 3 (5 modules) |
| Phase 4 | Finance review | Tier 4 (2 modules) |

---

## Full Module List (21 AI Modules)

| # | Module | Status | Action |
|---|--------|--------|--------|
| 1 | `ipai_agent_core` | Active | DEPRECATE |
| 2 | `ipai_ai_agents` | Active | DEPRECATE |
| 3 | `ipai_ai_agents_ui` | Active | DEPRECATE |
| 4 | `ipai_ai_audit` | Active | DEPRECATE |
| 5 | `ipai_ai_connectors` | Active | DEPRECATE |
| 6 | `ipai_ai_copilot` | Active | DEPRECATE |
| 7 | `ipai_ai_core` | Active | DEPRECATE |
| 8 | `ipai_ai_prompts` | Active | DEPRECATE |
| 9 | `ipai_ai_provider_kapa` | Active | DEPRECATE |
| 10 | `ipai_ai_provider_pulser` | Active | DEPRECATE |
| 11 | `ipai_ai_sources_odoo` | Active | DEPRECATE |
| 12 | `ipai_aiux_chat` | Scaffold | DEPRECATE |
| 13 | `ipai_advisor` | Active | DEPRECATE |
| 14 | `ipai_ask_ai` | Active | DEPRECATE |
| 15 | `ipai_ask_ai_chatter` | Active | DEPRECATE |
| 16 | `ipai_copilot_hub` | Active | DEPRECATE |
| 17 | `ipai_copilot_ui` | Active | DEPRECATE |
| 18 | `ipai_document_ai` | Active | DEPRECATE |
| 19 | `ipai_marketing_ai` | Active | DEPRECATE |
| 20 | `ipai_studio_ai` | Active | DEPRECATE |
| 21 | `ipai_theme_copilot` | **NEW** | **KEEP** |
| 22 | `ipai_ask_ai_bridge` | **NEW** | **KEEP** |

---

## Verification

After deprecation, verify:

```bash
# Check no AI modules are installed (except bridge)
./scripts/ci/check_deprecated_modules.sh

# Verify external service connectivity
curl -s https://copilot.example.com/health

# Verify bridge module works
docker compose exec odoo-core odoo -d odoo_core -u ipai_ask_ai_bridge --stop-after-init
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-13 | Initial deprecation manifest |
