# Repo Tree Contract (Authoritative)

This file defines the **canonical, stable repo layout** for `jgtolentino/odoo-ce`.
CI must ensure required roots exist and deploy config uses these paths.

> **Important**: This is the **flat structure** currently in use. Do NOT invent paths
> (forbidden example paths: `src/apps/odoo/` or `src/addons/`) unless this contract is explicitly updated.

## Required Root Directories

```
odoo-ce/
├── addons/                     # ALL custom IPAI modules (flat, not under src/)
│   ├── ipai/                   # IPAI namespace module
│   ├── ipai_bir_tax_compliance/
│   ├── ipai_close_orchestration/
│   ├── ipai_month_end/
│   ├── ipai_platform_audit/    # Platform: activity logging
│   ├── ipai_platform_permissions/  # Platform: scope/role management
│   ├── ipai_ppm_a1/
│   ├── ipai_tbwa_finance/
│   ├── ipai_workos_affine/     # Work OS: umbrella module
│   ├── ipai_workos_blocks/     # Work OS: block editor
│   ├── ipai_workos_canvas/     # Work OS: edgeless canvas
│   ├── ipai_workos_collab/     # Work OS: comments/mentions
│   ├── ipai_workos_core/       # Work OS: workspace/space/page
│   ├── ipai_workos_db/         # Work OS: databases/properties
│   ├── ipai_workos_search/     # Work OS: global search
│   ├── ipai_workos_templates/  # Work OS: templates
│   ├── ipai_workos_views/      # Work OS: table/kanban/calendar
│   └── oca/                    # OCA modules (subdir or symlinks)
├── catalog/                    # Parity matrices and best-of-breed catalogs
│   ├── best_of_breed.yaml
│   └── equivalence_matrix_*.csv
├── deploy/                     # Deployment configurations
│   ├── docker-compose.yml
│   └── odoo.conf
├── docs/                       # Documentation
│   ├── REPO_TREE.contract.md   # This file (authoritative)
│   ├── REPO_TREE.generated.md  # Auto-generated tree
│   └── REPO_SNAPSHOT.json      # Auto-generated snapshot
├── kb/                         # Knowledge base
│   ├── audit/                  # Audit rules
│   └── parity/                 # Parity rubrics/baselines
├── spec/                       # Spec kit bundles
│   └── workos-notion-clone/    # Notion clone spec
├── tools/                      # Build, audit, parity tools
│   ├── audit/                  # Audit scripts
│   │   ├── gen_repo_tree.sh
│   │   ├── gen_snapshot_json.sh
│   │   ├── run_audit_bundle.sh
│   │   ├── snapshot.sh
│   │   └── verify_expected_paths.sh
│   └── parity/                 # Parity audit tools
│       └── parity_audit.py
└── .github/workflows/          # CI/CD workflows
```

## Module Naming Conventions

| Pattern | Purpose | Examples |
|---------|---------|----------|
| `ipai_platform_*` | Platform-level shared modules | `ipai_platform_audit`, `ipai_platform_permissions` |
| `ipai_workos_*` | Work OS (Notion clone) modules | `ipai_workos_core`, `ipai_workos_blocks` |
| `ipai_<feature>_*` | Feature-specific modules | `ipai_bir_tax_compliance`, `ipai_month_end` |

## Deploy Configuration (addons_path)

The `addons_path` in `deploy/odoo.conf` must include:

```ini
addons_path = /opt/odoo/addons,/opt/odoo-ce/addons,/opt/odoo-ce/addons/oca
```

**Note**: Odoo core addons come from the Odoo installation or a submodule.
Custom modules live in `addons/` at the repo root.

## Validation (CI-enforced)

CI runs these checks on every PR:

1. `tools/audit/verify_expected_paths.sh` - Ensures required directories exist
2. `tools/audit/run_audit_bundle.sh` - Generates audit artifacts
3. `tools/parity/parity_audit.py` - Runs parity checks

## What NOT to Do

- **DO NOT** create forbidden restructure paths like `src/apps/odoo_core/` or `src/addons/`
- **DO NOT** invent alternative module locations
- **DO NOT** bypass this contract without updating this file first
- **DO NOT** trust agent audits that reference non-existent paths

## How to Regenerate Documentation

```bash
# Generate all audit artifacts
bash tools/audit/run_audit_bundle.sh

# Or individually:
bash tools/audit/gen_repo_tree.sh .
bash tools/audit/gen_snapshot_json.sh docs/REPO_SNAPSHOT.json
```

---

## Optional Future Refactor: `src/` Structure (NOT ACTIVE)

> **Status**: NOT ACTIVE. This section documents a potential future refactor only.
> Do not implement without explicit team decision and contract update.

If the team decides to adopt a `src/` structure in the future, the changes would be:

### Proposed Future Layout

```
odoo-ce/
├── src/
│   ├── apps/odoo_core/         # Odoo core as submodule (mock path)
│   │   ├── addons/             # Built-in Odoo modules
│   │   └── odoo/               # Odoo framework
│   ├── addons/                 # Custom IPAI modules (moved from addons/)
│   │   ├── ipai_*/
│   │   └── ipai_workos_*/
│   └── oca/                    # OCA modules (moved from addons/oca/)
├── deploy/
├── docs/
└── ...
```

### Optional Future Refactor (Currently FORBIDDEN - Examples Only)

**NOTE**: These paths are NOT ALLOWED currently. This section documents a hypothetical future restructure.

1. Move `addons/` contents to `src/addons/` (FORBIDDEN currently)
2. Add Odoo core as submodule at `src/apps/odoo_core/` (FORBIDDEN currently)
3. Move OCA modules to `src/oca/` (FORBIDDEN currently)
4. Update `deploy/odoo.conf` (HYPOTHETICAL EXAMPLE):
   ```ini
   # FORBIDDEN EXAMPLE - do not use these paths
   addons_path = /opt/odoo-ce/src/apps/odoo_core/addons,/opt/odoo-ce/src/addons,/opt/odoo-ce/src/oca
   ```
5. Update all CI workflows
6. Update this contract document

### Why NOT Active Now

- Current flat structure is working
- Modules already deployed and tested
- No immediate benefit to reorganization
- Risk of breaking existing deployments

---

*Last updated: 2024-12-22*
*Commit: See git log for current HEAD*
