# Spec-kit methodology

Every significant feature requires a spec bundle before implementation begins. Spec bundles define the rules, requirements, plan, and tasks for a feature in a structured, machine-readable format.

## Spec bundle structure

Each spec bundle lives in `spec/<feature>/` and contains four files:

```
spec/<feature>/
├── constitution.md    # Immutable rules (never modified after approval)
├── prd.md             # Product requirements document
├── plan.md            # Implementation plan
└── tasks.md           # Task checklist with status tracking
```

### Constitution

The constitution defines immutable rules for the feature. Once approved, these rules cannot be changed — only extended.

Example rules from `spec/finance-unified/constitution.md`:

- All monetary values use `Decimal` with 4-digit precision
- Tax computations follow BIR regulations exactly
- No hardcoded tax rates — all rates come from configuration tables

### PRD (product requirements document)

The PRD defines what the feature must do:

- User stories
- Acceptance criteria
- Non-functional requirements
- Dependencies and constraints

### Plan

The implementation plan defines how to build the feature:

- Module structure
- Data models
- API contracts
- Migration strategy

### Tasks

The task checklist tracks implementation progress:

```markdown
- [x] Create base module structure
- [x] Define data models
- [ ] Implement computation engine
- [ ] Write unit tests
- [ ] Integration test with existing modules
```

## Example spec bundles

| Bundle | Scope |
|--------|-------|
| `finance-unified` | Unified finance module with BIR compliance |
| `sap-joule-concur-odoo-azure` | SAP integration architecture |
| `adls-etl-reverse-etl` | Azure Data Lake ETL pipelines |

## Validation

Run `spec_validate.sh` to check spec bundle completeness:

```bash
./scripts/spec_validate.sh
```

This script verifies:

- All four files exist in each spec bundle
- Constitution is not empty
- PRD contains acceptance criteria
- Tasks use valid checkbox syntax

!!! failure "Missing spec = blocked"
    Significant changes without a spec bundle are rejected during verification. Create the spec bundle first.

## When a spec bundle is required

| Change type | Spec required? |
|-------------|---------------|
| New `ipai_*` module | Yes |
| Major feature addition | Yes |
| Architecture change | Yes |
| Bug fix | No |
| Config change | No |
| Documentation update | No |
