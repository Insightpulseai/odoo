# Semantic Versioning Strategy - InsightPulse Odoo CE

## Overview

This document defines the semantic versioning strategy for the InsightPulse Odoo CE repository, establishing a reliable release process with versioned Docker images and proper Git tagging.

## Release Strategy

### Versioning Scheme

| Version | Status | Purpose |
|---------|--------|---------|
| `v0.9.0` | Pre-production | Infrastructure unification release |
| `v1.0.0` | Production | First production-ready release |
| `v1.1.0`, `v1.2.0`, ... | Production | Feature releases |
| `v1.0.0-rc1`, `v1.0.0-rc2` | Release Candidate | Pre-production testing |

### Current Release

**v0.9.0 - Infrastructure Unification**
- **Status**: Pre-production (Infrastructure Ready)
- **Purpose**: Mark completion of deployment infrastructure unification
- **Docker Image**: `ghcr.io/jgtolentino/odoo-ce:v0.9.0`

## Docker Image Tagging

### Tag Strategy

| Tag | Purpose | Usage |
|-----|---------|-------|
| `v0.9.0` | Versioned release | Production deployments |
| `latest` | Latest stable | Development, CI/CD |
| `prod` | Production alias | Optional production marker |

### Image Building

```bash
# Build and push versioned images
./scripts/build_and_push_version.sh v0.9.0

# Manual alternative
export VERSION=v0.9.0
export IMAGE_BASE=ghcr.io/jgtolentino/odoo-ce

docker build -t "$IMAGE_BASE:$VERSION" -t "$IMAGE_BASE:latest" .
docker push "$IMAGE_BASE:$VERSION"
docker push "$IMAGE_BASE:latest"
```

## Deployment Manifests

### Versioned Deployments

Both deployment methods now use versioned tags:

**Docker Compose (VPS)**
```yaml
# docker-compose.prod.yml
image: ghcr.io/jgtolentino/odoo-ce:v0.9.0
```

**Kubernetes (DOKS)**
```yaml
# deploy/k8s/odoo-deployment.yaml
image: ghcr.io/jgtolentino/odoo-ce:v0.9.0
```

### Benefits

- **Rollback Safety**: Pin to specific versions for stability
- **Reproducibility**: Exact same image across environments
- **Audit Trail**: Clear version history for deployments

## Release Process

### 1. Pre-Release Validation

```bash
# Run sanity checks
scripts/full_deploy_sanity.sh

# Build and test locally
docker build -t odoo-ce-test:latest .
```

### 2. Create Git Tag

```bash
git tag -a v0.9.0 -m "v0.9.0 – unified custom image + DOKS/VPS manifests"
git push origin v0.9.0
```

### 3. Build and Push Images

```bash
./scripts/build_and_push_version.sh v0.9.0
```

### 4. Update Deployment Manifests

Update all deployment manifests to reference the new version:
- `docker-compose.prod.yml`
- `deploy/k8s/odoo-deployment.yaml`

### 5. Create GitHub Release

1. Go to GitHub Releases
2. Create release from tag `v0.9.0`
3. Use `RELEASE_v0.9.0.md` as release notes template

## Validation Scripts

### Full Deploy Sanity

```bash
scripts/full_deploy_sanity.sh
```

**Validates:**
- Canonical image references
- Documentation completeness
- Dockerfile alignment
- Local build capability

### Build and Push

```bash
scripts/build_and_push_version.sh [version]
```

**Features:**
- Version format validation
- GHCR login check
- Multi-tag building and pushing
- Next steps guidance

## Migration to v1.0.0

### Prerequisites

- [ ] Build and push v0.9.0 Docker image
- [ ] Deploy to VPS and validate
- [ ] Deploy to DOKS and validate
- [ ] Smoke test all custom modules
- [ ] Verify `/web` endpoint returns 200/302

### v1.0.0 Release Criteria

- [ ] All v0.9.0 prerequisites completed
- [ ] Production deployment successful
- [ ] Custom modules functioning correctly
- [ ] No critical issues identified
- [ ] Documentation updated for production

## Rollback Strategy

### Docker Compose (VPS)

```bash
# Revert to previous version
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### Kubernetes (DOKS)

```bash
# Rollback to specific version
kubectl set image deployment/odoo-deployment odoo=ghcr.io/jgtolentino/odoo-ce:v0.9.0
kubectl rollout status deployment/odoo-deployment -n odoo-prod
```

## Related Documentation

- [Custom Image Specification](../specs/003-odoo-custom-image.prd.md)
- [Secrets Naming and Storage](./SECRETS_NAMING_AND_STORAGE.md)
- [Deployment Naming Matrix](./DEPLOYMENT_NAMING_MATRIX.md)
- [DOKS Deployment Success Criteria](./DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md)

## Release History

| Version | Date | Status | Purpose |
|---------|------|--------|---------|
| v0.9.0 | 2025-11-25 | Pre-production | Infrastructure unification |

---

**This strategy ensures reliable, versioned deployments with clear rollback capabilities and production-ready release processes.**
