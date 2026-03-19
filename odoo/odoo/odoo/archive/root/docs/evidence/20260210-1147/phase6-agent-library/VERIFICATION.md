# Phase 6 Agent Library Wireup - VERIFICATION

## ✅ DEPLOYED

**Commit**: c80e5562
**Branch**: main
**Status**: Pushed to origin

## Files Created (8 total)

### 1. Supabase Migration
- supabase/migrations/20260210_03_agent_library_seed.sql (222 lines)
  ✅ 10 agent definitions
  ✅ 3 production flows
  ✅ Conflict-safe inserts (ON CONFLICT DO NOTHING)

### 2. TypeScript SDK
- packages/ipai-ai-sdk/src/agentLibrary.ts
  ✅ AgentFlowName type (3 flows)
  ✅ AgentName type (10 agents)
  ✅ Exported from index.ts

### 3. Python SDK
- packages/ipai-ai-sdk-python/ipai_ai_sdk/agent_library.py
  ✅ AgentFlowName Literal type
  ✅ AgentName Literal type
  ✅ Exported from __init__.py

### 4. Odoo Integration
- addons/ipai/ipai_ai_platform/models/agent_library.py
  ✅ ipai.ai.agent_library model
  ✅ 3 convenience methods
  ✅ Imported in models/__init__.py
  ✅ Black/isort formatted

### 5. Evidence
- docs/evidence/20260210-1147/phase6-agent-library/EVIDENCE.md

## 10 Canonical Agents

1. intent_router - Route requests to appropriate flow
2. cms_brief_to_sections - Homepage brief → section plan
3. cms_section_generator - Generate CMS sections
4. cms_seo_pack - SEO meta/OG tag generation
5. publish_check - Content validation
6. support_triage - Support issue classification
7. support_draft - Support response drafting
8. policy_safety_check - Security validation
9. odoo_action_plan - Odoo workflow planning
10. odoo_action_payload - Safe action generation

## 3 Production Flows

1. cms_homepage_pipeline: brief → sections → seo → check → gate
2. support_response_pipeline: triage → draft → safety → gate
3. odoo_workflow_pipeline: plan → payload → safety → gate

## Next Steps (Deploy)

### Apply Migration
```bash
supabase db push
```

### Update Odoo Module
```bash
odoo -u ipai_ai_platform --stop-after-init
```

### Test Flow (Example)
```python
# Via Odoo shell
odoo shell <<'EOF'
org_id = "<ORG_UUID>"
lib = env["ipai.ai.agent_library"]
run = lib.run_cms_homepage_pipeline(org_id, {
    "goal": "Homepage",
    "audience": "Enterprise",
    "product": "InsightPulseAI",
    "ctas": [{"label": "Request a demo", "href": "/contact"}]
})
print(run)
EOF
```

## Pre-Commit Hooks
✅ black (Python formatting)
✅ isort (Import sorting)
✅ flake8 (Linting)
✅ No Enterprise dependencies
✅ All hooks passed

## Quality Standards
- ✅ Evidence documented
- ✅ All code formatted
- ✅ Type safety (TypeScript + Python)
- ✅ Odoo integration clean
- ✅ Migration conflict-safe
- ✅ Human gates enforced
