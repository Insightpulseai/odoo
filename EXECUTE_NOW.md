# EXECUTE NOW - DEPLOY v0.9.0 TO FIX 502 ERROR

## 🚨 EXECUTE THESE EXACT COMMANDS ON YOUR VPS

**Use DigitalOcean Console (https://cloud.digitalocean.com) → Droplet 159.223.75.148 → Access Console**

```bash
# 1. Navigate to production directory
cd ~/odoo-prod

# 2. Pull latest code and configuration
git pull origin main

# 3. Deploy v0.9.0 with optimized Dockerfile
docker compose -f docker-compose.prod.yml pull odoo
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d

# 4. Verify deployment
docker compose -f docker-compose.prod.yml ps
curl -s -o /dev/null -w "%{http_code}\n" https://erp.insightpulseai.net
```

## ✅ EXPECTED OUTPUT

**After command #4:**
- ✅ `docker compose -f docker-compose.prod.yml ps` shows:
  ```
  NAME                COMMAND                  SERVICE             STATUS              PORTS
  ipai-db             "docker-entrypoint.s…"   db                  running             5432/tcp
  ipai-ce             "/entrypoint.sh odoo"    odoo                running             0.0.0.0:8069->8069/tcp
  ```
- ✅ `curl` returns **200** or **302** (not 502)

## 🎯 WHAT GETS DEPLOYED

- **v0.9.0 Infrastructure Unification**
- **Production-optimized Docker image** with custom modules baked in
- **Fixed deployment manifests**
- **Semantic versioning** implemented

## 🔧 IF DEPLOYMENT FAILS

**Run these troubleshooting commands:**

```bash
# Check what's wrong
docker compose -f docker-compose.prod.yml logs odoo --tail=50
docker compose -f docker-compose.prod.yml logs db --tail=20

# Check services
docker compose -f docker-compose.prod.yml ps

# Restart if needed
docker compose -f docker-compose.prod.yml restart odoo
sudo systemctl restart nginx

# Check Nginx
sudo nginx -t
sudo systemctl status nginx
```

## 📊 CURRENT STATUS

- ⚠️ **v0.9.0 git tag** exists locally (remote push pending network access)
- ⚠️ **Docker image** verification requires Docker daemon (Colima) running to pull `ghcr.io/jgtolentino/odoo-ce:v0.9.0`
- ⚠️ **Sanity script** updated for `v0.9.0` but requires Docker daemon for optional build
- ⚠️ **Git state**: commit and push outstanding changes before deployment

## 🔍 Deployment Status – v0.9.0 (Honest State)

**What is true right now**

- ✅ `scripts/full_deploy_sanity.sh` **passes** end-to-end  
  - Uses `ghcr.io/jgtolentino/odoo-ce:${VERSION:-v0.9.0}`  
  - Skips the optional Docker build when no daemon is running
- ✅ `Dockerfile` is aligned with the spec  
  - Base image: `odoo:18.0`  
  - Addons baked in at `/mnt/extra-addons`  
  - Non-root `USER odoo`  
  - Explicit `ENV ODOO_RC=/etc/odoo/odoo.conf` to match runtime expectations
- ✅ All manifests now reference **v0.9.0**  
  - `docker-compose.prod.yml` → `ghcr.io/jgtolentino/odoo-ce:v0.9.0`  
  - `deploy/k8s/odoo-deployment.yaml` → `ghcr.io/jgtolentino/odoo-ce:v0.9.0`
- ✅ `docs/FINAL_DEPLOYMENT_GUIDE.md` documents a **manual v0.9.0** deployment flow  
  - No GitHub Actions assumed  
  - DigitalOcean console + SSH path is the canonical route

**What is explicitly _not_ verified**

- ⚠️ `v0.9.0` git tag push to GitHub is **not verified** from this environment  
  - `git tag v0.9.0` exists locally  
  - `git push origin v0.9.0` still needs a real networked run
- ⚠️ `ghcr.io/jgtolentino/odoo-ce:v0.9.0` existence in GHCR is **not re-verified** here  
  - Docker/Colima is not running in this environment  
  - `docker pull ghcr.io/jgtolentino/odoo-ce:v0.9.0` must be run on a host with a working daemon
- ⚠️ `main` is **ahead of origin**  
  - Untracked files: `.github/copilot-instructions.md`, `EXECUTE_NOW.md`  
  - Recent changes to `Dockerfile`, `scripts/full_deploy_sanity.sh`, and `docs/FINAL_DEPLOYMENT_GUIDE.md` are local-only until committed & pushed

**Next actions to make “production-ready” true**

1. **On your dev machine (with Docker running)**  
   ```bash
   # Verify image in GHCR
   docker pull ghcr.io/jgtolentino/odoo-ce:v0.9.0
   ```

2. **Commit & push repo + tag**

   ```bash
   git add Dockerfile scripts/full_deploy_sanity.sh docs/FINAL_DEPLOYMENT_GUIDE.md EXECUTE_NOW.md .github/copilot-instructions.md
   git commit -m "chore: align v0.9.0 sanity, docs, and image spec"
   git push origin main
   git push origin v0.9.0
   ```

3. **On the VPS (DigitalOcean console or SSH)**

   ```bash
   cd ~/odoo-prod
   git pull origin main
   docker compose -f docker-compose.prod.yml pull odoo
   docker compose -f docker-compose.prod.yml down
   docker compose -f docker-compose.prod.yml up -d

   docker compose -f docker-compose.prod.yml ps
   curl -s -o /dev/null -w "%{http_code}\\n" https://erp.insightpulseai.net/web
   ```

Only after **all three** are done is it honest to say:
`production_deployment_ready = true` for `v0.9.0`.

---

**EXECUTE THE 4 COMMANDS ABOVE IN DIGITALOCEAN CONSOLE TO DEPLOY v0.9.0 AND FIX THE 502 ERROR**
