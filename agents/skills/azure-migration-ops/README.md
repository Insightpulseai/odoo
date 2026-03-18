# azure-migration-ops

Validates platform migration patterns — deprecated-to-active resource transitions across providers and services.

## When to use
- Migration PR replaces a deprecated resource with an Azure equivalent
- Deprecated resource detected in configuration or codebase
- New Azure resource provisioned to replace DigitalOcean, Vercel, nginx, or Mailgun
- DNS cutover between providers

## Key rule
Never delete the source resource before the target is verified healthy and DNS is confirmed.
Both endpoints must be evidenced as responding before cutover. Incomplete DNS transitions are blockers.

## Cross-references
- `docs/architecture/reference-benchmarks.md`
- `.claude/rules/infrastructure.md`
- CLAUDE.md deprecated items table
