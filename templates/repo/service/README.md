# Service Repo Template

Scaffold for a deployable service repository.

## Expected Structure

```text
<service-name>/
├── .github/
│   └── workflows/
├── apps/           # Deployable applications
├── packages/       # Shared internal packages
├── services/       # Service implementations
├── docs/           # Architecture and runbooks
├── spec/           # Spec bundles (prd, plan, tasks)
├── ssot/           # Intended-state contracts
├── tests/          # Integration and contract tests
├── Dockerfile
├── CLAUDE.md
└── README.md
```

## Conventions

- Each service has its own Dockerfile and health check endpoint.
- Secrets via Azure Key Vault, never hardcoded.
- CI via GitHub Actions (reusable workflow from `.github/workflows/reusable-ci.yml`).
- Deploy via Azure Container Apps or Azure DevOps pipeline.
