# Prompt — odoo-openupgrade-assessment

You are assessing upgrade readiness for an Odoo instance using OpenUpgrade as the benchmark.

Your job is to:
1. Inventory all installed modules and their current versions
2. Check OpenUpgrade migration script coverage for each module
3. Identify modules without migration scripts (coverage gaps)
4. Classify each module: covered, partial, missing
5. Assess custom ipai_* modules for manual migration needs
6. Generate a structured upgrade readiness report

Context:
- Source: `OCA/OpenUpgrade` repository for the target version branch
- Module inventory: `config/addons.manifest.yaml` and database installed modules
- Custom modules: `addons/ipai/` directory
- OCA modules: `addons/oca/` directory

Output format:
- Current version: source
- Target version: destination
- Total modules: count
- Covered by OpenUpgrade: count (list)
- Partial coverage: count (list with gaps noted)
- No coverage: count (list)
- Custom modules requiring manual migration: count (list)
- Risk classification: low/medium/high/critical
- Recommended next step: rehearsal or gap remediation
- Evidence: OpenUpgrade branch inspection results

Rules:
- Never assume OpenUpgrade covers all modules
- Always check per-module, not just per-repo
- Flag any module without a migration script as a gap
- Custom ipai_* modules always require manual assessment
- Require upgrade rehearsal before production
