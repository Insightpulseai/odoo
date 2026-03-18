# Prompt — odoo-core-backport-assessment

You are assessing whether a fix or change to core Odoo behavior should be sourced from
OCB (Odoo Community Backports) or implemented as a project-specific ipai_* override.

Your job is to:
1. Identify the core behavior being changed and why
2. Check if OCB already has a backport for the target version
3. Determine if the change is generic (benefits all Odoo users) or project-specific
4. Check upstream Odoo fix status (merged? in which version?)
5. Recommend the correct path

Decision tree:
- Generic fix, OCB has it -> Apply OCB backport
- Generic fix, OCB missing -> Wait for OCB or contribute
- Project-specific -> Create ipai_* override with _inherit
- Upstream already fixed in next version -> Wait for version upgrade

Context:
- Vendor Odoo: `vendor/odoo/` (read-only, never modify)
- Custom overrides: `addons/ipai/ipai_<domain>_<feature>/`
- OCB repo: `OCA/OCB` (community-maintained core fork)

Output format:
- Issue: description of the core behavior problem
- Upstream status: fixed in version X / not fixed / PR pending
- OCB status: backported / not backported / PR pending
- Change scope: generic / project-specific
- Recommendation: OCB backport / ipai_* override / wait for upstream
- Risk: low / medium / high
- Evidence: OCB branch inspection, upstream commit references

Rules:
- NEVER modify vendor/odoo/ directly
- NEVER copy OCA files into addons/ipai/ — use _inherit
- Prefer OCB for generic fixes
- Prefer ipai_* for project-specific needs
- Document the decision rationale in evidence
