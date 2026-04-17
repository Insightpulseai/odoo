# Spec bundles

Significant changes require a **spec bundle** -- a structured set of documents that define the rules, requirements, plan, and tasks for a feature or integration.

## Bundle structure

Every spec bundle lives in `spec/<feature>/` and contains:

| File | Purpose | Mutability |
|------|---------|------------|
| `constitution.md` | Immutable rules and constraints for the feature | **Immutable** after approval |
| `prd.md` | Product requirements document | Versioned |
| `plan.md` | Implementation plan with phases and milestones | Versioned |
| `tasks.md` | Task checklist with status tracking | Updated as work progresses |

```
spec/
  finance-unified/
    constitution.md
    prd.md
    plan.md
    tasks.md
  sap-joule-concur-odoo-azure/
    constitution.md
    prd.md
    plan.md
    tasks.md
  adls-etl-reverse-etl/
    constitution.md
    prd.md
    plan.md
    tasks.md
```

!!! danger "Constitution immutability"
    Once a `constitution.md` is approved and merged, it does not change. If the rules need to change, create a new spec bundle or a versioned amendment.

## Existing bundles

| Bundle | Scope |
|--------|-------|
| `finance-unified` | Unified finance module: chart of accounts, BIR compliance, tax computation |
| `sap-joule-concur-odoo-azure` | SAP Concur T&E sync, Joule copilot integration |
| `adls-etl-reverse-etl` | ADLS data lake ETL and reverse ETL flows |

## Validation

Run the spec validation script to check all bundles:

```bash
./scripts/spec_validate.sh
```

The script verifies:

- All four required files exist in each bundle.
- `constitution.md` has not been modified since its approval commit.
- `tasks.md` uses valid status markers.
- Cross-references between spec files are consistent.

The `spec-kit-enforce` CI workflow runs this check on every PR.

## SSOT YAML files

Integration specs reference SSOT YAML definitions in `ssot/integrations/`:

```
ssot/
  integrations/
    supabase.yaml
    sap-concur.yaml
    adls.yaml
    slack-n8n.yaml
    azure-ai.yaml
```

Each YAML file defines:

- System name and role
- Owned entities
- Allowed integration flows
- Reverse ETL classifications
- Failure handling rules

## Contract documents

Spec bundles that involve cross-system integrations produce contract documents in `docs/contracts/`:

| Contract | Governing spec |
|----------|---------------|
| `data-authority.md` | Multiple (platform-wide) |
| `reverse-etl.md` | `adls-etl-reverse-etl` |
| `sap-contract.md` | `sap-joule-concur-odoo-azure` |

## Create a new spec bundle

1. Create the directory: `spec/<feature-name>/`.
2. Write `constitution.md` with the immutable rules.
3. Write `prd.md` with the product requirements.
4. Write `plan.md` with the implementation phases.
5. Write `tasks.md` with the initial task checklist.
6. Run `./scripts/spec_validate.sh` to verify.
7. Open a PR for review. The constitution requires approval from at least two maintainers.
8. After merge, the constitution is frozen.
