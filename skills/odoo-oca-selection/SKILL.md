# OCA selection and custom-module decision skill

Use this skill when:
- Choosing between OCA and custom code
- Evaluating EE parity gaps
- Deciding whether a new addon is allowed
- Reviewing module proposals for policy compliance

## Decision Order

```
1. CE core       — can Odoo's built-in config solve it?
2. OCA           — does a vetted community module exist?
3. Config/data   — can data/security/views solve it without code?
4. External bridge — does it belong outside Odoo? (AI, OCR, runtime)
5. Thin custom addon — only if steps 1-4 don't solve it
```

## OCA Quality Gates

Before recommending any OCA module:
- 18.0 branch exists and CI green on OCA repo
- `development_status` >= `Stable` in `__manifest__.py`
- Test install in disposable DB (`test_<module>`) — classify per testing.md
- No conflicts with existing `ipai_*` modules
- No Enterprise dependencies or odoo.com IAP calls

Reference: `ssot/odoo/oca-18-availability-matrix.yaml` (76 must-have modules, 90% direct 18.0 coverage).

## Custom Module Boundary

When a custom `ipai_*` addon IS justified:
- Thin bridge to external service (API call, webhook, status sync)
- Action launch point for external capability
- Auth/session mapping (Odoo user ↔ external identity)
- Minimal UI hook (systray, button, widget) for external feature

When a custom addon is NOT justified:
- Fat reimplementation of Enterprise features
- Embedding SDK/runtime/orchestration logic inside Odoo
- Duplicating what an OCA module already provides
- Adding platform infrastructure (MCP, RAG, LLM) to addons/

Reference: `ssot/odoo/custom_module_policy.yaml`

## Default Conclusion

- OCA first
- Thin `ipai_*` bridge/meta modules only
- No broad EE-parity custom modules unless explicitly approved in the EE gap matrix

## Refuse or Escalate If

- The proposal creates a >500 line custom addon for something OCA covers
- The proposal adds platform/AI/runtime logic to addons/
- The OCA module has `development_status: Beta` for a production path
