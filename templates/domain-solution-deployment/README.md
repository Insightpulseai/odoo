# Domain Solution Deployment Spec Template

Governs deployment of named domain solutions as first-class workload items.
Benchmarked against Microsoft Business Process Solutions deployment pattern.

## Pattern

Every domain solution must declare:

1. **Deployment boundary** — workspace/project where the solution lives
2. **Required roles** — admin/owner prerequisites for enablement
3. **Target region** — data residency and capacity placement
4. **Orchestration connection** — control-plane/metadata store (before source onboarding)
5. **Source onboarding sequence** — ordered connector setup (after orchestration is live)
6. **Post-deploy verification** — health, freshness, reconciliation checks

## Usage

Copy `deployment-spec.md` into the domain solution's spec directory:

```
spec/<domain-solution>/
├── constitution.md
├── prd.md
├── plan.md
├── tasks.md
└── deployment-spec.md    ← this template
```

Fill in all sections. A domain solution is not deployable until all sections are complete.
