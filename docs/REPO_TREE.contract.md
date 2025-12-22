# Repo Tree Contract (authoritative)

This file defines the intended, stable repo layout for `jgtolentino/odoo-ce`.
CI must ensure required roots exist and deploy config uses these paths.

## Required Roots

```
odoo-ce/
├── addons/                 # Custom IPAI modules
│   ├── ipai/               # IPAI namespace module
│   ├── ipai_platform_*/    # Platform-level modules
│   ├── ipai_workos_*/      # Work OS modules
│   └── oca/                # OCA module symlinks/copies
├── catalog/                # Parity matrices and best-of-breed catalogs
├── deploy/                 # Deployment configurations
├── docs/                   # Documentation
├── kb/                     # Knowledge base (parity rubrics, audit rules)
├── oca/                    # OCA submodules (if used)
├── spec/                   # Spec kit bundles
├── tools/                  # Build, audit, parity tools
│   ├── audit/              # Audit scripts
│   └── parity/             # Parity audit tools
└── .github/workflows/      # CI/CD workflows
```

## Module Naming Convention

- Platform modules: `ipai_platform_*` (theme, audit, permissions)
- Work OS modules: `ipai_workos_*` (core, blocks, db, views, etc.)
- Feature modules: `ipai_<feature>_*`

## Deploy Configuration

The `addons_path` in production must include:
1. Odoo core addons
2. `addons/` directory
3. OCA module paths (if applicable)

## Validation

CI runs `tools/audit/verify_expected_paths.sh` to ensure this contract is met.
Agents must not invent paths like `src/apps/odoo/` unless explicitly added here.

## Notes

- Do not create alternative root structures without updating this contract
- All audit tools must use actual paths from this layout
- Generated tree docs must match this contract
