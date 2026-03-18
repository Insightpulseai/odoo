# Edge Functions CI Deploy Pattern

## Purpose
GitHub Actions workflow for automated Edge Function deployment to Supabase with SSOT/SOR boundary validation.

## Folder Layout
```
.github/workflows/
├── deploy-supabase.yml      # Main deployment workflow
└── validate-ssot-sor.yml    # Boundary validation workflow

supabase/functions/
├── <function-name>/
│   └── index.ts
└── .env.example             # Template for all functions
```

## Required Environment Variables
**GitHub Actions Secrets:**
- `SUPABASE_ACCESS_TOKEN`: Supabase management API token (for `supabase deploy`)
- `SUPABASE_PROJECT_ID`: Supabase project ID
- `SUPABASE_DB_PASSWORD`: Database password (for migration validation)

**Function Runtime Secrets (injected via Supabase CLI):**
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

## Minimal Code Skeleton

**.github/workflows/deploy-supabase.yml:**
```yaml
name: Deploy Supabase Functions

on:
  push:
    branches: [main]
    paths:
      - 'supabase/functions/**'
  workflow_dispatch:

jobs:
  validate-boundaries:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check for shadow ledger patterns
        run: |
          # Scan for forbidden table names in migrations/functions
          if grep -r "CREATE TABLE.*\(invoice\|journal\|payment\|stock_move\)" supabase/; then
            echo "Error: Detected potential shadow ledger table creation"
            exit 1
          fi

      - name: Validate ownership declarations
        run: |
          # Check that all new integrations declare owner_system
          python scripts/ci/validate_ownership_declarations.py

  deploy:
    runs-on: ubuntu-latest
    needs: validate-boundaries

    steps:
      - uses: actions/checkout@v4

      - uses: supabase/setup-cli@v1
        with:
          version: latest

      - name: Deploy Edge Functions
        run: |
          supabase functions deploy --project-ref ${{ secrets.SUPABASE_PROJECT_ID }}
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}

      - name: Set function secrets
        run: |
          supabase secrets set \
            --project-ref ${{ secrets.SUPABASE_PROJECT_ID }} \
            SUPABASE_URL=${{ secrets.SUPABASE_URL }} \
            SUPABASE_SERVICE_ROLE_KEY=${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
```

## Failure Modes
- **Deployment timeout**: Supabase CLI may timeout on large functions; split into smaller functions
- **Secret sync failure**: Secrets may not propagate immediately; add retry logic
- **SSOT/SOR boundary violation**: CI check fails if shadow ledger detected; requires manual fix
- **Migration conflicts**: Database migrations may conflict with existing schema; use `--dry-run` first

## SSOT/SOR Boundary Notes
- **Pre-deployment validation**: CI MUST scan for shadow ledger patterns before allowing deployment
- **Ownership declarations**: New integrations must declare `owner_system: odoo|supabase` in spec
- **Audit trail requirement**: All deployed functions must emit `ops.runs/run_events/artifacts`
- **Secret management**: Secrets injected via GitHub Actions, never committed to git
- **Rollback strategy**: Keep previous function version available; use `supabase functions deploy --legacy-bundle` for rollback
