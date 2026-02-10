# Phase 6: Agent Library Wireup - Evidence

**Date**: 2026-02-10 11:47
**Scope**: Canonical agent library seed + SDK constants + Odoo wrapper

## Files Created

### 1. Supabase Migration
- `supabase/migrations/20260210_03_agent_library_seed.sql` (222 lines)
- 10 agent definitions with prompts, schemas, model routing
- 3 production flows: cms_homepage, support_response, odoo_workflow

### 2. TypeScript SDK
- `packages/ipai-ai-sdk/src/agentLibrary.ts`
- Typed constants for `AgentFlowName` and `AgentName`
- Updated `packages/ipai-ai-sdk/src/index.ts` to export

### 3. Python SDK
- `packages/ipai-ai-sdk-python/ipai_ai_sdk/agent_library.py`
- Python `Literal` types for flow and agent names
- Updated `packages/ipai-ai-sdk-python/ipai_ai_sdk/__init__.py` to export

### 4. Odoo Wrapper
- `addons/ipai/ipai_ai_platform/models/agent_library.py`
- Convenience methods: `run_cms_homepage_pipeline()`, `run_support_pipeline()`, `run_odoo_workflow_pipeline()`
- Updated `addons/ipai/ipai_ai_platform/models/__init__.py` to import

## Agents Defined

1. **intent_router** - Classify request intent and route to next agent
2. **cms_brief_to_sections** - Convert homepage brief to section plan
3. **cms_section_generator** - Generate individual CMS sections
4. **cms_seo_pack** - Generate SEO meta and OG tags
5. **publish_check** - Validate content for completeness and policy
6. **support_triage** - Classify support issues by category/severity
7. **support_draft** - Draft support response with fix steps
8. **policy_safety_check** - Check for security/policy violations
9. **odoo_action_plan** - Convert Odoo workflow request to plan
10. **odoo_action_payload** - Generate safe Odoo action payload

## Flows Defined

1. **cms_homepage_pipeline**: brief → sections → seo → check → gate
2. **support_response_pipeline**: triage → draft → safety → gate
3. **odoo_workflow_pipeline**: plan → payload → safety → gate

## Verification

### Python SDK
```bash
python3 -m compileall ipai_ai_sdk/
# ✅ Compiles without errors
```

### TypeScript SDK
```bash
pnpm build
# ⚠️ Pre-existing type errors in client.ts (not related to agent library)
# ✅ Agent library types compile successfully
# ✅ JS/MJS bundles generated
```

## Next Steps

To deploy:
1. Apply migration: `supabase db push`
2. Update Odoo module: `odoo -u ipai_ai_platform --stop-after-init`
3. Test flows via SDK or Odoo shell

## Notes

- Agent prompts use `{{text}}` and `{{context}}` placeholders for template rendering
- All agents default to 'default' model (can be overridden via model routing)
- Human gates required at end of each flow (no auto-publish)
- TypeScript SDK has pre-existing type errors unrelated to this work
