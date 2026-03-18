# Odoo Code Metrics Ops Skill

## Purpose

Measure Odoo codebase metrics via CLI. Covers odoo-bin cloc, lines of code counting, module size analysis, and code health indicators.

## Owner

odoo-cli-operator

## Preconditions

- Odoo CE 19.0 installed
- Target database with modules installed (for database-aware cloc)
- Addons path configured

## Covered Operations

### Code Line Count (cloc)

- `odoo-bin cloc --database <db> --addons-path <paths>` — count lines for installed modules
- `odoo-bin cloc --path <addons-dir>` — count lines for all modules in a directory
- `odoo-bin cloc --database <db> --addons-path <paths> -c <module>` — count for specific module

### Output Interpretation

cloc reports:
- Python lines (models, controllers, wizards, tests)
- XML lines (views, data, security, reports)
- JavaScript lines (widgets, actions, services)
- CSS/SCSS lines (stylesheets)
- Total customization effort per module

### Module Size Analysis

- Small module: < 500 lines total
- Medium module: 500-2000 lines
- Large module: 2000-5000 lines
- Very large module: > 5000 lines (review for splitting)

### Health Indicators

- Test-to-code ratio (tests/total Python)
- XML-to-Python ratio (views vs logic)
- Module dependency count (from __manifest__.py)

## Disallowed Operations

- Code execution (cloc is read-only)
- Database modification
- This skill is purely analytical — no mutations

## Verification

- cloc output shows per-module breakdown
- Line counts match expected module sizes
- No errors in addons-path resolution
