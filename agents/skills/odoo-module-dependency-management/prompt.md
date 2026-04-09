# Prompt — odoo-module-dependency-management

You are validating the Odoo module dependency graph for the InsightPulse AI platform.

Your job is to:
1. Parse the target module's `__manifest__.py` for its `depends` list
2. Resolve the full transitive dependency chain
3. Verify all dependencies are available in the configured addons paths
4. Check for circular dependencies
5. Validate OCA module compatibility with Odoo 18 (check 19.0 branch exists)
6. Verify no Enterprise module dependencies (hard blocker)
7. Check alignment with `config/addons.manifest.yaml`
8. Produce a dependency graph report

Platform context:
- Custom addons: `addons/ipai/` (69 ipai_* modules)
- OCA addons: `addons/oca/` (hydrated via gitaggregate at runtime)
- Upstream addons: `vendor/odoo/addons/` (CE core)
- Manifest SSOT: `config/addons.manifest.yaml`
- Module philosophy: Config -> OCA -> Delta (ipai_*)

Dependency rules:
- ipai_* modules may depend on: base Odoo CE, OCA stable modules, other ipai_* modules
- ipai_* modules must NOT depend on: Enterprise modules, odoo.com IAP, beta OCA modules
- OCA modules must be from 19.0 branch with `development_status >= Stable`

Output format:
- Module: name and version
- Direct dependencies: list from __manifest__.py
- Transitive chain: full resolved graph
- Missing: any unresolvable dependencies
- Circular: detected cycles (if any)
- Enterprise violations: any EE dependencies found
- Manifest alignment: present in addons.manifest.yaml (pass/fail)
- Evidence: __manifest__.py contents and resolution trace

Rules:
- Never introduce Enterprise module dependencies
- Never modify OCA source — create ipai_* override
- Config -> OCA -> Delta philosophy
- Bind to local addons paths, not Odoo.sh app store
