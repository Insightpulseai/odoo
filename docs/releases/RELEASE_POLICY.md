# Release Policy

## Immutable release policy

GitHub releases in this repository are immutable.
Only release title and notes may be edited after creation.
The tag target (commit SHA) and attached assets cannot be changed.

## Release classes

| Pattern | Meaning | Example |
|---------|---------|---------|
| `vYYYY.MM.DD-<sha>` | Build artifact release | `v2026.03.02-bc852ae` |
| `prod-YYYYMMDD-HHMM` | Production deployment marker | `prod-20260302-0241` |

## Allowed actions

- Edit title/body of an existing release (notes correction)
- Create a new release from a new tag (new deployment)
- Create a new prod release when a different commit is deployed

## Disallowed actions

- Retarget an immutable release to a different commit
- Treat a release note edit as evidence of a new deployment
- Delete a prod release to hide deployment history

## Deployment truth

Production truth is determined by:

1. **Deployed commit SHA** — the exact commit the prod tag points to
2. **Merged PRs reachable from that SHA** — code inclusion proof
3. **Runtime activation evidence** — module installs, migrations, config, env vars

## "Should this have been deployed?" decision tree

```
Feature merged before prod SHA?
  ├── No  → Feature is NOT in this release (expected)
  └── Yes → Is it reachable from prod SHA?
              ├── No  → Feature is NOT in this release (branch topology)
              └── Yes → Code is deployed. Is it active?
                          ├── Requires migration/module/config → Check runtime
                          └── No activation needed → Active
```

## Audit process

Use `scripts/release/audit_prod_release.sh` to generate a release audit report.
Use `.github/workflows/release-audit.yml` to run audits via CI.
Template: `docs/releases/PROD_RELEASE_AUDIT.md`
