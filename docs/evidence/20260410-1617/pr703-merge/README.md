# PR #703 Merge Evidence

- Timestamp: `2026-04-10 16:17:59 +0800`
- Scope: merge `main` into `feat/login-branding-entra-google` and resolve the PR-specific copilot, branding, and finance-spec conflicts.

## Outcome

- Merge conflicts were resolved and the worktree returned to a non-conflicted state.
- Pulser runtime fixes were applied while resolving the merge:
  - populated `permitted_tools` after intent classification
  - restored `read_only_mode` in Foundry settings
  - merged `document_extract` / `extract_document` support with knowledge-base tool support
  - normalized seeded Foundry config keys to runtime-read namespaces
  - moved the pre-migrate script to the module target version `18.0.3.0.0`

## Verification

- PASS: `git diff --check --cached -- <targeted PR paths>`
- PASS: `python3 -m py_compile addons/ipai/ipai_mail_plugin_bridge/controllers/main.py addons/ipai/ipai_odoo_copilot/controllers/main.py addons/ipai/ipai_odoo_copilot/models/foundry_service.py addons/ipai/ipai_odoo_copilot/models/skill_router.py addons/ipai/ipai_odoo_copilot/models/tool_executor.py addons/ipai/ipai_odoo_copilot/migrations/18.0.3.0.0/pre-migrate.py`
- PASS: `node --check addons/ipai/ipai_odoo_copilot/static/src/js/copilot_systray.js`
- PASS: `node --check addons/ipai/ipai_odoo_copilot/static/src/components/chat_panel/chat_panel.js`
- PASS: `rg -n "ipai_odoo_copilot\\.foundry_" addons/ipai/ipai_odoo_copilot/data/ir_config_parameter.xml` returned no matches
- PASS: runtime config keys now exist in `addons/ipai/ipai_odoo_copilot/data/ir_config_parameter.xml` for:
  - `ipai_copilot.enabled`
  - `ipai.copilot.enabled`
  - `ipai_copilot.foundry_endpoint`
  - `ipai.copilot.foundry_endpoint`
  - `ipai_copilot.foundry_agent_id`
  - `ipai_copilot.foundry_read_only_mode`

## Verification Limits

- FAIL (unrelated staged branch payload): `git diff --check --cached` still reports pre-existing whitespace / EOF issues outside the merge-resolution scope, including:
  - `.agents/skills/ui-ux-pro-max/*`
  - `docs/release/MVP_SHIP_CHECKLIST.md`
  - `web/apps/docs/content/_generated/reference/agents.mdx`

