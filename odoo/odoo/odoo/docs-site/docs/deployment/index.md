# Deployment

InsightPulse AI runs on **Azure Container Apps** as the canonical compute runtime. All public traffic routes through **Azure Front Door** for TLS termination, WAF, and edge caching.

The deployment stack covers:

- **Azure Container Apps** for all microservices (Odoo, Keycloak, MCP, OCR, Superset, Plane)
- **Docker Compose** for local development with PostgreSQL 16
- **Devcontainer** for reproducible Odoo development environments
- **CI/CD** with 355+ GitHub Actions workflows gating every merge
- **DNS & routing** via Cloudflare delegated to Azure Front Door

## Pages in this section

| Page | Description |
|------|-------------|
| [Azure Container Apps](azure-container-apps.md) | Production compute runtime and Front Door configuration |
| [Docker](docker.md) | Local development stack and compose commands |
| [CI/CD](ci-cd.md) | GitHub Actions pipelines and quality gates |
| [Devcontainer](devcontainer.md) | VS Code devcontainer path contract and rules |
| [DNS & routing](dns-routing.md) | Cloudflare DNS, subdomain registry, mail configuration |
