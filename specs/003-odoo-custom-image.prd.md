---
id: 003
title: Odoo CE Custom Image – Production Artifact Spec
owner: jgtolentino
status: approved
version: 1.0.0
repo: odoo-ce
tags:
  - odoo
  - docker
  - digitalocean
  - doks
  - cd-pipeline
created_at: 2025-11-24
updated_at: 2025-11-24
---

# 003 – Odoo CE Custom Image – Production Artifact Spec

## 1. Overview & Purpose

This specification defines the **canonical custom Docker image** for Odoo CE 18, built from the upstream `odoo:18.0` base and extended with InsightPulse-specific configuration and addons. The custom image implements the "Smart Customization" pattern where all custom modules and dependencies are baked into the image for immutable, consistent deployments.

The image is the **single source of truth** for all runtime behavior in:
- **DigitalOcean VPS** (`docker-compose.prod.yml`)
- **DigitalOcean Kubernetes (DOKS)** (`odoo` Deployment)

**Canonical Image Reference:**
```text
ghcr.io/jgtolentino/odoo-ce:v0.9.0
```

A `:latest` alias MAY exist but MUST NOT be relied upon as a stable version identifier.

## 2. Goals & Non-Goals

### 2.1 Goals

1. **Immutable Deployment Artifact**
   - CE/OCA-only addons baked in (`./addons`, `./oca` via mounted volumes)
   - Production config baked in (`./deploy/odoo.conf`)
   - Custom modules (`ipai_*`) included at build time
   - System dependencies pre-installed
   - Consistent CI/production environment

2. **Security-First Design**
   - Non-root user execution (`USER odoo`)
   - Minimal attack surface
   - Secure base image (official `odoo:18.0`)
   - No secrets embedded in image

3. **Multi-Environment Support**
   - Standardize deployment across:
     - Docker Compose (`docker-compose.prod.yml`) on DO VPS
     - DOKS Deployments using the same image tag
   - Consistent behavior across all environments

4. **Zero-Downtime Automation**
   - GitHub Actions automated build and push
   - Automated testing and validation
   - Trivial image swapping via single tag update

### 2.2 Non-Goals

- Not defining all CI/CD workflows in detail (only image requirements)
- Not describing Kubernetes manifests in full (covered by DOKS infra spec)
- Not handling Odoo database migrations beyond standard `-u` module update flow
- Support for Odoo Enterprise features
- IAP or odoo.com integrations
- Manual deployment processes
- Environment-specific customizations at image level

## 3. Architecture Overview

### 3.1 Image Structure

```
Custom Odoo CE Image (ghcr.io/jgtolentino/odoo-ce:v0.9.0)
├── Base: odoo:18.0 (official)
├── System Dependencies
│   ├── build-essential
│   ├── libpq-dev
│   ├── git
│   └── libssl-dev
├── Custom Modules
│   ├── /mnt/extra-addons (ipai_* modules, baked)
│   └── /mnt/oca-addons (OCA modules, optional volume)
├── Python Dependencies
│   └── requirements.txt (if present)
├── Configuration
│   └── /etc/odoo/odoo.conf (default, overridable)
├── Environment Variables
│   ├── HOST=db
│   ├── PORT=5432
│   ├── USER=odoo
│   ├── PASSWORD=odoo
│   └── DB=odoo
└── Security
    └── USER odoo (non-root)
```

### 3.2 Deployment Paths

**Path 1: GitHub Actions CI/CD**
- Build: `Dockerfile` → `ghcr.io/jgtolentino/odoo-ce:v0.9.0`
- Push: GitHub Container Registry
- Deploy: VPS (Docker Compose) or DOKS (Kubernetes)

**Path 2: Docker Compose (VPS)**
- Image: `ghcr.io/jgtolentino/odoo-ce:v0.9.0`
- Configuration: `docker-compose.prod.yml`
- Secrets: `.env.production` + environment variables

**Path 3: Kubernetes (DOKS)**
- Image: `ghcr.io/jgtolentino/odoo-ce:v0.9.0`
- Configuration: `deploy/k8s/` manifests
- Secrets: Kubernetes Secrets

## 4. Requirements

### 4.1 Functional Requirements

**Base Image**
- MUST use `odoo:18.0` as base
- MUST run Odoo under the non-root `odoo` user

**Custom Addons**
- MUST bake local addons into the image:
  - `./addons` → `/mnt/extra-addons/`
- Optional: OCA addons kept as separate volumes, not baked (to keep image lean)
- MUST preserve compatibility with:
  - `ipai_ppm_advanced`
  - `ipai_internal_shop`
  - `ipai_finance_ppm`
  - `auth_oidc`
  - Any other CE/OCA-only modules defined in the project

**Python Dependencies**
- MUST install dependencies from `requirements.txt` if present in `/mnt/extra-addons/`
- MUST use `--no-cache-dir` to minimize image size

**Configuration**
- MUST copy a production config into the image:
  - `./deploy/odoo.conf` → `/etc/odoo/odoo.conf`
- Config MUST be overridable via:
  - Bind mounts in `docker-compose.prod.yml`
  - Environment variables (e.g., `HOST`, `USER`, `PASSWORD`, `DB`)

**Runtime Environment**
- MUST expose runtime defaults via ENV:
  - `HOST` (default `db`)
  - `PORT` (default `5432`)
  - `USER` (default `odoo`)
  - `PASSWORD` (default `odoo`)
  - `DB` (default `odoo`)
- MUST not hard-code real secrets into the image

**Deployment Compatibility**
- VPS path: `docker-compose.prod.yml` MUST reference versioned image tag
- DOKS path: Kubernetes Deployment spec MUST use same versioned image tag

### 4.2 Non-Functional Requirements

**Security**
- MUST run as `USER odoo`, not root
- MUST NOT bake secrets, tokens, or PATs into the image
- MUST follow canonical secret naming from `SECRETS_NAMING_AND_STORAGE.md`
- MUST use read-only filesystem where possible

**Performance**
- Image build MUST complete successfully on standard DO droplet or CI runner
- MUST use multi-stage builds or optimization where applicable

**Portability**
- Built image MUST run identically in:
  - Local Docker environment
  - DO VPS via Compose
  - DOKS via Kubernetes Deployment

**Size Optimization**
- MUST use `--no-install-recommends` for apt packages
- MUST clean up apt cache after installations
- MUST use `--no-cache-dir` for pip installations

## 5. Technical Specifications

### 5.1 Dockerfile Definition

File: `./Dockerfile`

```dockerfile
# Custom Odoo CE image for InsightPulse
# Base: Official Odoo 18.0 CE
FROM odoo:18.0

# Install required system dependencies for custom modules
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        git \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy custom CE/OCA addons baked into the image
# Owner set to odoo for runtime safety
COPY --chown=odoo:odoo ./addons /mnt/extra-addons/

# Install Python dependencies if a requirements file exists
RUN if [ -f /mnt/extra-addons/requirements.txt ]; then \
      pip install --no-cache-dir -r /mnt/extra-addons/requirements.txt; \
    fi

# Provide default configuration inside the image
# Override with bind mount in compose for environment-specific configs
COPY --chown=odoo:odoo ./deploy/odoo.conf /etc/odoo/odoo.conf

# Default environment placeholders (override at runtime via compose/ENV)
ENV HOST=db \
    PORT=5432 \
    USER=odoo \
    PASSWORD=odoo \
    DB=odoo

# Run as non-root for security
USER odoo

# Health check (optional but recommended)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8069/web/health || exit 1
```

**Key Properties:**
- Delta architecture: upstream `odoo:18.0` + InsightPulse deltas only
- No Enterprise modules baked in
- Configurable via `ENV` and bind mounts
- Follows security best practices

### 5.2 Image Naming Convention

| Component | Value | Purpose |
|-----------|-------|---------|
| Registry | GitHub Container Registry (GHCR) | Secure, integrated with GitHub |
| Repository | `ghcr.io/jgtolentino/odoo-ce` | Canonical location |
| Tag (Production) | `v0.9.0`, `v1.0.0`, etc. | Semantic versioning |
| Tag (CI) | `sha-{commit}` | CI builds tracking |
| Tag (Alias) | `latest` | NOT for production use |

**Canonical Reference:** `ghcr.io/jgtolentino/odoo-ce:v0.9.0`

### 5.3 Compose Integration (VPS)

File: `./docker-compose.prod.yml` (relevant sections)

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: odoo
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_MAX_CONNECTIONS: 100
    volumes:
      - odoo-db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 10s
      timeout: 5s
      retries: 5

  odoo:
    image: ghcr.io/jgtolentino/odoo-ce:v0.9.0
    container_name: odoo-ce
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      HOST: db
      USER: odoo
      PASSWORD: ${DB_PASSWORD}
      ODOO_RC: /etc/odoo/odoo.conf
    volumes:
      - ./deploy/odoo.conf:/etc/odoo/odoo.conf:ro
      - ./addons:/mnt/extra-addons
      - ./oca:/mnt/oca-addons
      - odoo-filestore:/var/lib/odoo
    ports:
      - "127.0.0.1:8069:8069"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8069/web/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

volumes:
  odoo-db-data:
  odoo-filestore:
```

### 5.4 Environment Variables

| Variable | Purpose | Required | Default | Example |
|----------|---------|----------|---------|---------|
| `HOST` | Database host | Yes | `db` | `postgres-service` (K8S) |
| `PORT` | Database port | Yes | `5432` | `5432` |
| `USER` | Database user | Yes | `odoo` | `odoo` |
| `PASSWORD` | Database password | Yes | - | From secrets |
| `DB` | Database name | Yes | `odoo` | `odoo` |
| `ODOO_RC` | Config file path | Yes | `/etc/odoo/odoo.conf` | Same |

### 5.5 Volume Mounts

| Path | Purpose | Type | Notes |
|------|---------|------|-------|
| `/mnt/extra-addons` | Custom ipai_* modules | Read-only | Baked or mounted |
| `/mnt/oca-addons` | OCA modules | Read-only | Mounted volume |
| `/etc/odoo/odoo.conf` | Configuration | Read-only | Override default |
| `/var/lib/odoo` | Filestore | Read-write | Persistent data |

### 5.6 Registry & Build Process

**Manual Build + Push:**

```bash
export IMAGE=ghcr.io/jgtolentino/odoo-ce:v0.9.0

# Login to GHCR
echo "$GHCR_PAT" | docker login ghcr.io -u jgtolentino --password-stdin

# Build image
docker build -t "$IMAGE" .

# Push to registry
docker push "$IMAGE"
```

**CI/CD Pipeline (GitHub Actions):**

```yaml
name: Build and Push Odoo CE Image

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/jgtolentino/odoo-ce
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix={{branch}}-
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

## 6. Configuration Management

### 6.1 Odoo Configuration

**File:** `deploy/odoo.conf`

```ini
[options]
addons_path = /mnt/extra-addons,/mnt/oca-addons
data_dir = /var/lib/odoo
admin_passwd = ${ADMIN_PASSWORD}
db_host = ${HOST}
db_port = ${PORT}
db_user = ${USER}
db_password = ${PASSWORD}
db_name = ${DB}
http_port = 8069
list_db = False
proxy_mode = True
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200
log_level = info
```

**Environment-Specific Overrides:**
- Mounted as read-only volume in Docker Compose
- Environment variables take precedence over config file values
- Use `.env.production` for sensitive values

### 6.2 Database Configuration

**Canonical Values:**
- Database name: `odoo`
- Database user: `odoo`
- Connection via environment variables
- Password sourced from secrets management

## 7. Security Requirements

### 7.1 Base Image Security
- Use official `odoo:18.0` image only
- Regular security updates via base image updates
- No additional package installation unless necessary
- Keep apt cache clean

### 7.2 Runtime Security
- Execute as non-root user (`USER odoo`)
- No privileged capabilities
- Read-only filesystem where possible
- Health checks enabled

### 7.3 Secret Management
- **Never embed secrets in image**
- Use environment variables or Kubernetes secrets
- Follow canonical naming from `SECRETS_NAMING_AND_STORAGE.md`
- Rotate secrets regularly

## 8. Success Criteria & Testing

### 8.1 Build & Runtime (Local)

**Test 1: Image Build**
```bash
docker build -t ghcr.io/jgtolentino/odoo-ce:v0.9.0 .
```
✅ Pass if: Exit code 0, no build errors

**Test 2: Local Run**
```bash
docker run --rm -p 8069:8069 \
  -e HOST=localhost \
  -e PASSWORD=test \
  ghcr.io/jgtolentino/odoo-ce:v0.9.0
```
✅ Pass if: 
- Container starts without crash
- `/web` endpoint responds with HTTP 200/302
- No fatal errors in logs

### 8.2 VPS Deployment (Compose)

**Test 3: VPS Deployment**
```bash
cd ~/odoo-prod
docker compose -f docker-compose.prod.yml pull odoo
docker compose -f docker-compose.prod.yml up -d
```

✅ Pass if:
- `docker ps` shows correct image tag
- `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8069/web` returns 200 or 302
- Odoo logs show successful DB connection
- No fatal module import errors
- Health check passes

### 8.3 DOKS Deployment (Kubernetes)

**Test 4: K8S Deployment**
```bash
kubectl set image deployment/odoo odoo=ghcr.io/jgtolentino/odoo-ce:v0.9.0
kubectl rollout status deployment/odoo
```

✅ Pass if:
- `kubectl rollout status deployment/odoo` exits with code 0
- `kubectl get pods -l app=odoo` shows all pods `STATUS=Running, READY=1/1`
- Ingress/Service path returns HTTP 200/302 at `https://erp.insightpulseai.net/web`
- Pod health checks pass

### 8.4 Feature-Level (Modules Present)

**Test 5: Module Availability**
```bash
kubectl exec -it <odoo-pod> -- odoo-bin -c /etc/odoo/odoo.conf \
  -d odoo \
  -u ipai_ppm_advanced,ipai_internal_shop,ipai_finance_ppm,auth_oidc \
  --stop-after-init
```

✅ Pass if:
- Command exits with code 0
- All four modules install/update without errors
- No dependency resolution failures
- Database schema updates complete

### 8.5 Acceptance Criteria

**Image Quality:**
- [ ] Image builds successfully in CI
- [ ] Custom modules accessible at runtime
- [ ] Configuration file properly mounted
- [ ] Non-root user execution verified
- [ ] Health checks respond correctly

**Deployment Success:**
- [ ] VPS deployment via Docker Compose works
- [ ] DOKS deployment via Kubernetes works
- [ ] Database connectivity established
- [ ] Custom modules load without errors
- [ ] All services healthy after deployment

**Security Compliance:**
- [ ] No secrets embedded in image
- [ ] Non-root user execution verified
- [ ] Base image security scans pass
- [ ] Environment variables properly used
- [ ] Read-only mounts enforced where applicable

## 9. Constraints & Risks

### 9.1 Technical Constraints

**Disk Space**
- CI runners may have limited disk space
- Implement image cleanup strategy
- Monitor dangling images

**Build Dependencies**
- Assumes valid `__manifest__.py` for each module
- Assumes optional `requirements.txt` at `/mnt/extra-addons/requirements.txt`
- Base image changes require spec revision

**Module Structure**
- Changes to `./addons` structure can break builds
- Module dependencies must be explicitly declared
- OCA modules must be compatible with Odoo CE 18.0

### 9.2 Operational Risks

**Image Size Growth**
- Monitor image size trends
- Implement pruning strategy for old images
- Consider multi-stage builds for optimization

**Registry Quotas**
- GHCR has storage limits
- Implement retention policy for old tags
- Archive historical versions if needed

**Version Conflicts**
- Ensure semantic versioning consistency
- Test compatibility before production deployment
- Maintain version compatibility matrix

## 10. Implementation Tasks

### 10.1 Phase 1: Image Definition (T1)

**Deliverables:**
- [ ] Create `./Dockerfile` with all requirements
- [ ] Wire `docker-compose.prod.yml` to use versioned image
- [ ] Add health check configuration
- [ ] Document all environment variables

**Acceptance:**
- Image builds locally without errors
- All custom modules present in built image
- Configuration file properly included

### 10.2 Phase 2: Registry & Build Path (T2)

**Deliverables:**
- [ ] Add/confirm GitHub Actions workflow
- [ ] Configure GHCR authentication
- [ ] Implement semantic versioning tags
- [ ] Document manual fallback build path in `docs/FINAL_DEPLOYMENT_RUNBOOK.md`

**Acceptance:**
- CI pipeline builds and pushes image on main branch
- Semantic version tags created on release
- Manual build process documented and tested

### 10.3 Phase 3: VPS Integration (T3)

**Deliverables:**
- [ ] Add `scripts/simple_deploy.sh` wrapper script
- [ ] Update Docker Compose configuration
- [ ] Configure environment variables
- [ ] Test deployment on `159.223.75.148`

**Acceptance:**
- Deployment script executes without errors
- Services start correctly
- Health checks pass
- Odoo web interface accessible

### 10.4 Phase 4: DOKS Integration (T4)

**Deliverables:**
- [ ] Update Kubernetes Deployment manifest
- [ ] Add rollout verification steps
- [ ] Update `docs/DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md`
- [ ] Test full deployment cycle

**Acceptance:**
- K8S deployment uses correct image version
- Rollout completes successfully
- All pods healthy
- Ingress routes traffic correctly

### 10.5 Exit Criteria for This Spec

- [x] Image builds successfully
- [x] VPS deployment runs using custom image
- [x] VPS deployment passes all smoke tests
- [x] DOKS deployment runs using same image
- [x] DOKS deployment passes all smoke tests
- [x] Documentation updated and consistent

## 11. Cross-References

### 11.1 Related Documentation
- [SECRETS_NAMING_AND_STORAGE.md](../docs/SECRETS_NAMING_AND_STORAGE.md) - Secret management patterns
- [DEPLOYMENT_NAMING_MATRIX.md](../docs/DEPLOYMENT_NAMING_MATRIX.md) - Naming conventions
- [DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md](../docs/DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md) - K8S deployment criteria
- [FINAL_DEPLOYMENT_GUIDE.md](../docs/FINAL_DEPLOYMENT_GUIDE.md) - Comprehensive deployment guide
- [FINAL_DEPLOYMENT_RUNBOOK.md](../docs/FINAL_DEPLOYMENT_RUNBOOK.md) - Operational runbook

### 11.2 Implementation Files
- `Dockerfile` - Image definition
- `docker-compose.prod.yml` - VPS deployment configuration
- `deploy/k8s/` - Kubernetes manifests
- `.github/workflows/` - CI/CD pipelines
- `scripts/simple_deploy.sh` - Deployment automation

## 12. Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| v1.0.0 | 2025-11-24 | Initial specification (merged from codex and main branches) | jgtolentino |

---

**Document Status:** ✅ Approved for Production Use

**Next Review:** 2025-12-24 (Monthly cadence)

This specification ensures that the custom Odoo CE image serves as a reliable, secure, and consistent deployment artifact across all InsightPulse ERP environments.