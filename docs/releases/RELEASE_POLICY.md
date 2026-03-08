# Release Policy

## Immutable Release Policy

GitHub releases in this repository are **immutable**.
Only release title and notes may be edited after creation.
The tag target (commit SHA) and assets cannot be changed.

## Release Classes

| Pattern | Purpose | Example |
|---------|---------|---------|
| `vYYYY.MM.DD-<sha7>` | Build artifact release | `v2026.03.02-2ee9837` |
| `prod-YYYYMMDD-HHMM` | Production deployment marker | `prod-20260302-0241` |

### Build Releases (`v*`)

- Created by CI on every deployable build
- Tag encodes the date and short SHA
- Multiple `v*` tags may exist for the same day

### Production Releases (`prod-*`)

- Created when a build is actually deployed to production
- Tag encodes deployment timestamp (UTC)
- The tagged commit is the exact code running in production
- Only one `prod-*` tag should be "Latest" at any time

## Allowed Actions

| Action | Allowed | Notes |
|--------|---------|-------|
| Edit release title/body | Yes | Clarify notes, add audit links |
| Create new release from new tag | Yes | Standard deployment flow |
| Create new `prod-*` release | Yes | When a different commit is deployed |
| Retarget existing release to different commit | **No** | Immutable — create a new release instead |
| Delete a release | **No** | Historical record must be preserved |
| Treat note edit as evidence of new deployment | **No** | Notes != deployment |

## Deployment Truth

Production truth is determined by three layers:

1. **Deployed commit SHA** — the `prod-*` tag target
2. **Merged PRs reachable from that SHA** — code inclusion
3. **Runtime activation evidence** — modules installed, migrations applied, config present

A feature is only "deployed and active" when all three layers confirm it.

## Release Audit

Use `scripts/release/audit_prod_release.sh` to audit any production release:

```bash
./scripts/release/audit_prod_release.sh prod-20260302-0241 prod-20260302-0211
```

Or trigger the `release-audit.yml` workflow manually in GitHub Actions.
