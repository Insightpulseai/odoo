# Pulser Chat Shell Addon

## Scope

Scaffolded a thin Odoo 18 addon at `addons/ipai/ipai_pulser_chat/` for the Pulser chat shell.

The addon owns only:

- Owl systray launcher
- chat drawer UI
- authenticated user/company/record context handoff
- narrow HTTP proxy to an external Pulser backend
- minimal Odoo settings

The addon does not own:

- model routing
- tool or MCP policy
- memory or eval orchestration
- Foundry or agent runtime orchestration

## Authority

- Product authority: `spec/pulser-odoo/prd.md`
- Release-scope authority: `ssot/release/go-live-scope-matrix.yaml`
- Architectural invariant: `spec/pulser-odoo/constitution.md`

## Verification

- `PASS` Python syntax: `py-compile.txt`
- `PASS` JavaScript syntax: `node-check-systray.txt`, `node-check-panel.txt`
- `PASS` XML well-formedness: `xml-parse.txt`
- `PASS` Repo health on staged changes: `repo-health.txt`
- `PASS` Spec validation: `spec-validate.txt`
- `PASS` Local CI gate on staged changes: `ci-local.txt`
- `NOT EXECUTED` Odoo install/runtime smoke test against a running local instance

## Notes

The chat drawer close behavior was normalized so the systray component owns open/close state directly. This avoids unverified child callback binding patterns in Owl templates.
