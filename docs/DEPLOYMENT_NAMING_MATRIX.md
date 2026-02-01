# Deployment Naming Matrix - Canonical Reference

## Overview
This document defines the canonical naming scheme for all resources across the InsightPulse Odoo CE deployment stack. All deployment configurations must use these canonical names.

## Resource Naming Matrix

| Logical Component | Docker / Compose Name | Kubernetes Name(s) | DNS Record(s) | Image/Tag |
|-------------------|----------------------|-------------------|---------------|-----------|
| **Odoo Application** | `ipai-ce` | `odoo-deployment`, `odoo-service`, `odoo-ingress` | `erp.insightpulseai.com` | `ghcr.io/jgtolentino/odoo-ce:latest` |
| **PostgreSQL Database** | `ipai-db` | `postgres-statefulset`, `postgres-service` | - | `postgres:16` |
| **Keycloak (SSO)** | `keycloak` | `keycloak-deployment`, `keycloak-service`, `keycloak-ingress` | `auth.insightpulseai.com` | `quay.io/keycloak/keycloak:latest` |
| **Network** | `odoo-ce_ipai_backend` | `odoo-prod` (namespace) | - | - |

## Detailed Resource Specifications

### Docker Compose Resources

#### Services
- **Odoo**: `ipai-ce`
  - Container name: `ipai-ce`
  - Image: `ghcr.io/jgtolentino/odoo-ce:latest`
  - Port: `8069`

- **PostgreSQL**: `ipai-db`
  - Container name: `ipai-db`
  - Image: `postgres:16`
  - Port: `5432`

- **Keycloak**: `keycloak` (future)
  - Container name: `keycloak`
  - Image: `quay.io/keycloak/keycloak:latest`
  - Port: `8080`

#### Networks
- **Backend Network**: `odoo-ce_ipai_backend`
  - Driver: `bridge`
  - Scope: `local`

#### Volumes
- **Database Data**: `ipai-db-data`
- **Filestore**: `ipai-filestore`

### Kubernetes Resources

#### Namespace
- **Production**: `odoo-prod`

#### Odoo Resources
- **Deployment**: `odoo-deployment`
- **Service**: `odoo-service`
  - Type: `ClusterIP`
  - Port: `8069`
- **Ingress**: `odoo-ingress`
  - Host: `erp.insightpulseai.com`
  - TLS: Enabled

#### PostgreSQL Resources
- **StatefulSet**: `postgres-statefulset`
- **Service**: `postgres-service`
  - Type: `ClusterIP`
  - Port: `5432`

#### Keycloak Resources (Future)
- **Deployment**: `keycloak-deployment`
- **Service**: `keycloak-service`
  - Type: `ClusterIP`
  - Port: `8080`
- **Ingress**: `keycloak-ingress`
  - Host: `auth.insightpulseai.com`
  - TLS: Enabled

### DNS Records

#### Primary Domain
- **Base**: `insightpulseai.com`

#### Subdomains
- **ERP Application**: `erp.insightpulseai.com` → Odoo CE
- **Authentication**: `auth.insightpulseai.com` → Keycloak SSO
- **Documentation**: `docs.insightpulseai.com` → Documentation site
- **API**: `api.insightpulseai.com` → API gateway (future)

### File Paths and Locations

#### Docker Compose Files
- **Production**: `docker-compose.prod.yml`
- **Development**: `docker-compose.yml`

#### Odoo Configuration
- **Main Config**: `deploy/odoo.conf`
- **Nginx Config**: `deploy/nginx/erp.insightpulseai.com.conf`

#### Kubernetes Manifests
- **Namespace**: `deploy/k8s/namespace.yaml`
- **Odoo**: `deploy/k8s/odoo-deployment.yaml`, `deploy/k8s/odoo-service.yaml`, `deploy/k8s/odoo-ingress.yaml`
- **PostgreSQL**: `deploy/k8s/postgres-statefulset.yaml`, `deploy/k8s/postgres-service.yaml`
- **Keycloak**: `deploy/k8s/keycloak-deployment.yaml`, `deploy/k8s/keycloak-service.yaml`, `deploy/k8s/keycloak-ingress.yaml`

### Environment Variables

#### Database Configuration
- **Database Name**: `odoo` (canonical)
- **Database User**: `odoo` (canonical)
- **Database Password**: `ODOO_DB_PASSWORD` (secret)

#### Odoo Configuration
- **Admin User**: `admin` (canonical)
- **Admin Password**: `ODOO_ADMIN_PASSWORD` (secret)
- **Master Password**: `ODOO_MASTER_PASSWORD` (secret)

## Deployment Commands

### Docker Compose
```bash
# Production deployment
cd /opt/odoo-ce
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps
```

### Kubernetes (DOKS)
```bash
# Apply all manifests
kubectl apply -f deploy/k8s/

# Check deployment status
kubectl get pods -n odoo-prod
kubectl get services -n odoo-prod
kubectl get ingress -n odoo-prod
```

## Migration from Legacy Names

### Current → Canonical
- Database user `ipai` → `odoo`
- Database name `ipai` → `odoo`
- Container names remain `ipai-*` for backward compatibility
- Network name remains `odoo-ce_ipai_backend` for compatibility

## Compliance

All deployment configurations must use these canonical resource names. Any deviation requires documentation and approval from the infrastructure team.

## Cross-References

- **Secrets**: See [SECRETS_NAMING_AND_STORAGE.md](./SECRETS_NAMING_AND_STORAGE.md)
- **DOKS Deployment**: See [DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md](./DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md)
- **Final Deployment**: See [FINAL_DEPLOYMENT_GUIDE.md](./FINAL_DEPLOYMENT_GUIDE.md)
