# v0.9.0 - Infrastructure Unification Release

**Release Date**: 2025-11-25  
**Status**: Pre-production (Infrastructure Ready)  
**Previous Release**: None (First tagged release)

## 🎯 What's Included

This release marks the completion of deployment infrastructure unification for InsightPulse Odoo CE. All runtime paths now reference a single custom image and share consistent naming schemes.

## ✨ Key Features

### 🏗️ Custom Image Architecture
- **Base**: Official `odoo:18.0` image
- **Baked Addons**: `./addons` → `/mnt/extra-addons/`
- **Configuration**: `./deploy/odoo.conf` → `/etc/odoo/odoo.conf`
- **Security**: Non-root execution (`USER odoo`)
- **Canonical Image**: `ghcr.io/jgtolentino/odoo-ce:latest`

### 🔧 Deployment Paths
- **VPS (Docker Compose)**: Production-ready compose file
- **DOKS (Kubernetes)**: Complete K8S manifests in `deploy/k8s/`
- **Unified Secrets**: Canonical naming across all environments

### 📚 Documentation
- `specs/003-odoo-custom-image.prd.md` - Custom image specification
- `docs/SECRETS_NAMING_AND_STORAGE.md` - Unified secrets naming
- `docs/DEPLOYMENT_NAMING_MATRIX.md` - Resource naming matrix
- `scripts/full_deploy_sanity.sh` - Deployment validation script

## 🚀 How to Deploy

### Build + Push Canonical Image
```bash
export IMAGE=ghcr.io/jgtolentino/odoo-ce:latest
echo "$GHCR_PAT" | docker login ghcr.io -u jgtolentino --password-stdin
docker build -t "$IMAGE" .
docker push "$IMAGE"
```

### VPS Deployment (Docker Compose)
```bash
ssh ubuntu@159.223.75.148
cd ~/odoo-prod
git pull origin main

docker compose -f docker-compose.prod.yml pull odoo
docker compose -f docker-compose.prod.yml up -d

# Apply module migrations
export ODOO_MODULES="ipai_ppm_advanced,ipai_internal_shop,ipai_finance_ppm,auth_oidc"
export DB_NAME="odoo"
docker compose -f docker-compose.prod.yml exec odoo odoo-bin -c /etc/odoo.conf \
  -d "$DB_NAME" -u "$ODOO_MODULES" --stop-after-init
```

### DOKS Deployment (Kubernetes)
```bash
kubectl apply -f deploy/k8s/
kubectl rollout status deployment/odoo-deployment -n odoo-prod
```

## ✅ Validation

### Pre-Deployment Check
```bash
scripts/full_deploy_sanity.sh
```

### Success Criteria
- [ ] `docker build` and `docker push` succeed
- [ ] VPS deployment via Docker Compose works
- [ ] DOKS deployment via Kubernetes works
- [ ] `/web` endpoint returns HTTP 200/302
- [ ] Custom modules load without errors

## 🔄 Migration Notes

### From Previous State
- **No breaking changes** - this is the first tagged release
- **New**: Canonical image reference `ghcr.io/jgtolentino/odoo-ce:latest`
- **New**: Unified secrets naming (`ODOO_DB_PASSWORD`, etc.)
- **New**: Complete K8S manifests for DOKS deployment

### Secret Migration
- Legacy `POSTGRES_PASSWORD` → Canonical `ODOO_DB_PASSWORD`
- Database user `ipai` → Canonical `odoo`
- Database name `ipai` → Canonical `odoo`

## 📈 Next Steps

### v1.0.0 - Production Ready
- [ ] Build and push v0.9.0 Docker image
- [ ] Deploy to VPS and validate
- [ ] Deploy to DOKS and validate
- [ ] Smoke test all custom modules
- [ ] Cut v1.0.0 production release

## 🐛 Known Issues

- None identified - this is a foundational infrastructure release

## 📋 Files Changed

### New Files
- `specs/003-odoo-custom-image.prd.md`
- `docs/SECRETS_NAMING_AND_STORAGE.md`
- `docs/DEPLOYMENT_NAMING_MATRIX.md`
- `scripts/full_deploy_sanity.sh`
- `deploy/k8s/` (all K8S manifests)

### Updated Files
- `docker-compose.prod.yml` (canonical image reference)
- `docs/DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md` (canonical naming)

## 🔗 Related Documentation

- [Custom Image Specification](./specs/003-odoo-custom-image.prd.md)
- [Secrets Naming Guide](./docs/SECRETS_NAMING_AND_STORAGE.md)
- [Deployment Naming Matrix](./docs/DEPLOYMENT_NAMING_MATRIX.md)
- [DOKS Success Criteria](./docs/DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md)

---

**This release establishes the foundation for reliable, repeatable deployments across VPS and DOKS environments. The infrastructure is now unified and ready for production deployment testing.**
