# Secrets Naming and Storage - Canonical Reference

## Overview
This document defines the canonical naming scheme for all secrets and environment variables used across the InsightPulse Odoo CE deployment stack. All deployment configurations must reference these canonical names.

## Canonical Secret Names

### GHCR / Registry
| Secret Name | Purpose | Used In | Stored In |
|-------------|---------|---------|-----------|
| `GHCR_PAT` | GitHub Personal Access Token for GHCR read/write | GitHub Actions, Docker login | GitHub Actions Secrets |

### DigitalOcean
| Secret Name | Purpose | Used In | Stored In |
|-------------|---------|---------|-----------|
| `DO_API_TOKEN` | DigitalOcean API access | DOKS deployment, doctl | GitHub Actions Secrets, doctl config |
| `DO_SPACES_KEY` | DigitalOcean Spaces access key | File storage (if needed) | GitHub Actions Secrets |
| `DO_SPACES_SECRET` | DigitalOcean Spaces secret key | File storage (if needed) | GitHub Actions Secrets |

### Database (PostgreSQL)
| Secret Name | Purpose | Used In | Stored In |
|-------------|---------|---------|-----------|
| `ODOO_DB_NAME` | Database name | Odoo config, Postgres | `.env.production`, K8S secrets |
| `ODOO_DB_USER` | Database username | Odoo config, Postgres | `.env.production`, K8S secrets |
| `ODOO_DB_PASSWORD` | Database password | Odoo config, Postgres | `.env.production`, K8S secrets |

### Odoo Application
| Secret Name | Purpose | Used In | Stored In |
|-------------|---------|---------|-----------|
| `ODOO_ADMIN_LOGIN` | Odoo admin username | Odoo authentication | `.env.production`, K8S secrets |
| `ODOO_ADMIN_PASSWORD` | Odoo admin password | Odoo authentication | `.env.production`, K8S secrets |
| `ODOO_MASTER_PASSWORD` | Odoo database master password | Database operations | `.env.production`, K8S secrets |

### Keycloak (SSO - Future)
| Secret Name | Purpose | Used In | Stored In |
|-------------|---------|---------|-----------|
| `KEYCLOAK_ADMIN_USER` | Keycloak admin username | Keycloak admin console | `.env.production`, K8S secrets |
| `KEYCLOAK_ADMIN_PASSWORD` | Keycloak admin password | Keycloak admin console | `.env.production`, K8S secrets |

### CI / GitHub Actions
| Secret Name | Purpose | Used In | Stored In |
|-------------|---------|---------|-----------|
| `GHCR_PAT` | GitHub Container Registry access | Image build/push | GitHub Actions Secrets |
| `DO_API_TOKEN` | DigitalOcean API access | DOKS deployment | GitHub Actions Secrets |

## Storage Locations

### GitHub Actions Secrets
- Access via: GitHub Repository Settings → Secrets and variables → Actions
- Used for: CI/CD workflows, automated deployments
- Secrets stored here: `GHCR_PAT`, `DO_API_TOKEN`, `DO_SPACES_KEY`, `DO_SPACES_SECRET`

### Environment Files (`.env.production`)
- Location: `/opt/odoo-ce/.env.production` (on VPS)
- Used for: Docker Compose deployments
- Secrets stored here: `ODOO_DB_NAME`, `ODOO_DB_USER`, `ODOO_DB_PASSWORD`, `ODOO_ADMIN_LOGIN`, `ODOO_ADMIN_PASSWORD`, `ODOO_MASTER_PASSWORD`

### Kubernetes Secrets
- Location: DOKS cluster namespace
- Used for: Kubernetes deployments
- Secrets stored here: All application secrets (`ODOO_DB_*`, `ODOO_ADMIN_*`, `KEYCLOAK_*`)

### DigitalOcean doctl Configuration
- Location: Local/CI doctl configuration
- Used for: DOKS cluster management
- Secrets stored here: `DO_API_TOKEN`

## Migration from Legacy Names

### Current → Canonical
- `POSTGRES_PASSWORD` → `ODOO_DB_PASSWORD`
- Database user `ipai` → `odoo` (canonical user)
- Database name `ipai` → `odoo` (canonical database)

## Security Best Practices

1. **Never commit secret values** to version control
2. **Use different values** for each environment (dev/staging/prod)
3. **Rotate secrets regularly** according to security policy
4. **Use strong, randomly generated passwords** for all secrets
5. **Limit access** to secret storage locations

## Example Usage

### Docker Compose (.env.production)
```bash
ODOO_DB_NAME=odoo
ODOO_DB_USER=odoo
ODOO_DB_PASSWORD=your_secure_password_here
ODOO_ADMIN_LOGIN=admin
ODOO_ADMIN_PASSWORD=your_admin_password_here
ODOO_MASTER_PASSWORD=your_master_password_here
```

### Kubernetes Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: odoo-secrets
type: Opaque
data:
  ODOO_DB_PASSWORD: <base64-encoded-password>
  ODOO_ADMIN_PASSWORD: <base64-encoded-password>
```

### GitHub Actions
```yaml
- name: Login to GHCR
  run: echo "${{ secrets.GHCR_PAT }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
```

## Compliance

All deployment configurations must reference these canonical secret names. Any deviation requires documentation and approval from the infrastructure team.
