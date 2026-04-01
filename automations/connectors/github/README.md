# GitHub Connector

Wrapper for GitHub API interactions used by automation jobs.

## Scope

- Repository management (branches, PRs, issues)
- Actions workflow dispatch
- Release and tag operations
- Webhook event parsing

## Auth

Uses `GITHUB_TOKEN` (Actions-provided) or a GitHub App installation token.
Never hardcode PATs. Secrets resolved from Azure Key Vault.

<!-- TODO: Implement base connector class with retry and rate-limit handling -->
