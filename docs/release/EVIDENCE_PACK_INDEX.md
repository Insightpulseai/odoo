# Evidence Pack Index

Use one folder per live verification run.

## Naming convention

`docs/evidence/<YYYYMMDD-HHMMZ>-<environment>-deployment-readiness/`

Example:

`docs/evidence/20260408-1530Z-staging-deployment-readiness/`

## Expected contents

- `README.md` — completed evidence pack template
- `logs/`
- `screenshots/`
- `responses/`
- `links.txt`

## Minimum required artifacts

- agent-platform live smoke log
- infra live smoke log
- negative invoice JSON result
- ACA / Front Door verification output
- managed identity / RBAC verification output
- PostgreSQL smoke output
- final go/no-go note
