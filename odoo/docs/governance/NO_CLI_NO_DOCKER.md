# NO_CLI_NO_DOCKER Policy

**Status**: Active
**Created**: 2026-02-12
**Portfolio Initiative**: PORT-2026-011
**Evidence**: EVID-20260212-006

---

## Policy Statement

**Direct CLI/Docker commands are forbidden in development workflows.**

All infrastructure operations must use:
1. **Declarative configuration** (docker-compose.yml, Dockerfile, k8s manifests)
2. **Sanctioned automation** (scripts/docker/, Ansible playbooks, GitOps)
3. **Managed services** (Supabase CLI, GitHub Actions, DO App Platform)

---

## Rationale

### Why This Policy Exists

**Problem**: Direct CLI/Docker commands create:
- **Undocumented state changes**: `docker run` commands executed in terminal sessions leave no audit trail
- **Non-reproducible environments**: Manual commands can't be replicated across team members
- **Drift and inconsistency**: Different developers run different commands, creating environment divergence
- **Security vulnerabilities**: Direct SSH/psql access bypasses security controls and audit logging

**Solution**: Enforce infrastructure-as-code and automation-first workflows:
- **Declarative config**: `docker-compose.yml` documents exact container configuration
- **Sanctioned automation**: `scripts/docker/` provides versioned, tested, auditable automation
- **GitOps**: ArgoCD/Flux ensures cluster state matches git repository
- **Managed services**: Supabase CLI, GitHub Actions provide audited, reproducible deployments

---

## Forbidden Patterns

### 1. Direct Docker Commands

**Forbidden**:
```bash
# ❌ Direct docker run
docker run -d -p 5432:5432 postgres:16

# ❌ Direct docker exec
docker exec -it odoo-web-1 bash

# ❌ Direct docker build
docker build -t myapp:latest .

# ❌ Direct docker push
docker push myregistry.com/myapp:latest
```

**Allowed**:
```bash
# ✅ Use docker-compose (declarative)
docker-compose up -d

# ✅ Use sanctioned automation
bash scripts/docker/odoo-restart.sh

# ✅ Use CI/CD pipeline
gh workflow run deploy-production.yml
```

---

### 2. Direct Kubernetes Commands

**Forbidden**:
```bash
# ❌ Direct kubectl apply
kubectl apply -f deployment.yml

# ❌ Direct kubectl exec
kubectl exec -it pod-name -- bash

# ❌ Direct kubectl port-forward
kubectl port-forward svc/postgres 5432:5432
```

**Allowed**:
```bash
# ✅ Use GitOps (ArgoCD/Flux)
git commit -m "feat: update deployment" k8s/deployment.yml
git push origin main
# ArgoCD auto-syncs from git

# ✅ Use sanctioned automation
bash scripts/k8s/deploy-staging.sh

# ✅ Use managed services
# DigitalOcean App Platform, Vercel, Supabase Edge Functions
```

---

### 3. Direct SSH Commands

**Forbidden**:
```bash
# ❌ Direct SSH to production
ssh root@178.128.112.214

# ❌ Direct SSH with manual commands
ssh user@server "systemctl restart nginx"

# ❌ Direct file transfer
scp local-file.txt user@server:/path/to/destination
```

**Allowed**:
```bash
# ✅ Use Ansible playbooks (declarative)
ansible-playbook playbooks/restart-nginx.yml

# ✅ Use sanctioned automation
bash scripts/ssh/deploy-odoo.sh

# ✅ Use managed services
# GitHub Actions, Supabase CLI, DO App Platform
```

---

### 4. Direct Database Commands

**Forbidden**:
```bash
# ❌ Direct remote psql
psql -h production.database.com -U admin -d mydb

# ❌ Direct pg_dump without automation
pg_dump -h remote-db -U admin mydb > backup.sql

# ❌ Direct SQL execution
psql -h remote-db -c "DELETE FROM sensitive_table;"
```

**Allowed**:
```bash
# ✅ Use Supabase CLI (managed migrations)
supabase db push

# ✅ Use sanctioned automation
bash scripts/db/backup-production.sh

# ✅ Use migrations (versioned, auditable)
pnpm --filter @repo/migrations run migrate:up

# ✅ Use Supabase client (RLS-protected)
# Edge Functions with Supabase client
```

---

## Approved Patterns

### Declarative Configuration

**docker-compose.yml** (container orchestration):
```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
```

**Dockerfile** (image definition):
```dockerfile
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

**k8s/deployment.yml** (Kubernetes manifests):
```yaml
apiVersion: web/v1
kind: Deployment
metadata:
  name: odoo-web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: odoo
  template:
    metadata:
      labels:
        app: odoo
    spec:
      containers:
        - name: web
          image: myregistry.com/odoo:19.0
          ports:
            - containerPort: 8069
```

---

### Sanctioned Automation

**scripts/docker/** (approved automation directory):
```bash
# scripts/docker/odoo-restart.sh
#!/bin/bash
set -euo pipefail

echo "Restarting Odoo containers..."
docker-compose restart odoo-web odoo-db
docker-compose ps
echo "Restart complete."
```

**Key Requirements**:
1. **Error handling**: `set -euo pipefail` for fail-fast behavior
2. **Logging**: Echo progress and outcomes
3. **Idempotency**: Can run multiple times safely
4. **Documentation**: Header comments explain purpose

---

### GitOps Workflows

**ArgoCD/Flux** (Kubernetes sync):
```yaml
# argocd-app.yml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: odoo-production
spec:
  source:
    repoURL: https://github.com/Insightpulseai/odoo
    path: k8s/production
    targetRevision: main
  destination:
    server: https://kubernetes.default.svc
    namespace: odoo
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

**Benefits**:
- Git as single source of truth
- Automated sync on git push
- Audit trail via git history
- Declarative desired state

---

## CI Gate Enforcement

**Automated Scanning** (`.github/workflows/no-cli-no-docker-gate.yml`):

This policy is enforced via automated CI gate that scans for forbidden patterns:

- **Trigger**: Pull requests, pushes to main
- **Scanner**: `scripts/gates/scan-forbidden-commands.sh`
- **Output**: SARIF format for GitHub Code Scanning integration
- **Failure**: PR blocked until violations resolved

**Forbidden Patterns Detected**:
- `docker (run|exec|build|push)`
- `kubectl` (except in sanctioned automation)
- `ssh` (except localhost)
- `psql -h` (except localhost)

**Allowlist** (excluded from scan):
- `scripts/docker/` - Sanctioned automation
- `docker-compose.yml`, `Dockerfile` - Declarative config
- `docs/`, `*.md` - Documentation
- `.github/workflows/` - CI/CD pipelines

**How to Fix Violations**:

1. **Move to sanctioned automation**:
   ```bash
   # Create automation script
   cat > scripts/docker/my-operation.sh <<'EOF'
   #!/bin/bash
   set -euo pipefail
   echo "Running my operation..."
   docker-compose restart myservice
   EOF
   chmod +x scripts/docker/my-operation.sh

   # Reference in code/docs
   echo "Run: bash scripts/docker/my-operation.sh"
   ```

2. **Use declarative config**:
   ```yaml
   # docker-compose.yml
   services:
     myservice:
       image: myimage:latest
       command: ["my-command"]
   ```

3. **Request exception** (rare):
   - Add to allowlist in `scripts/gates/scan-forbidden-commands.sh`
   - Document rationale in PR description
   - Requires maintainer approval

**Evidence**:
- Gate logs: `docs/evidence/20260212-2000/no-cli-docker-gate/`
- SARIF output: GitHub Security tab
- Workflow runs: GitHub Actions history

---

## Exceptions

**Legitimate Use Cases** (require documentation):

1. **Local debugging** (never in CI/production):
   ```bash
   # Developer laptop ONLY
   docker exec -it odoo-web-1 bash
   # Investigate production issue locally
   ```

2. **One-time migrations** (documented in evidence):
   ```bash
   # Migration script: scripts/migrations/2026-02-12-data-fix.sh
   # Evidence: docs/evidence/20260212-2000/data-migration/
   ssh root@server "cd /app && ./migrate.sh"
   ```

3. **Emergency hotfixes** (with post-mortem):
   ```bash
   # Emergency fix (must create automation after)
   docker exec odoo-web-1 python -c "fix_critical_bug()"
   # Post-mortem: Create scripts/hotfix/fix-critical-bug.sh
   ```

**Exception Process**:
1. Document exception reason in PR
2. Create evidence in `docs/evidence/`
3. Add to allowlist in `scripts/gates/scan-forbidden-commands.sh`
4. Require maintainer approval
5. Create follow-up task to automate

---

## Migration Guide

**For Existing Direct CLI/Docker Usage**:

**Step 1: Audit Current Usage**
```bash
# Find all direct docker commands
git grep -E "docker (run|exec|build|push)" scripts/

# Find all direct ssh commands
git grep -E "ssh .+@" scripts/
```

**Step 2: Create Sanctioned Automation**
```bash
# Example: Replace direct docker exec
# Before:
docker exec -it odoo-web-1 python manage.py migrate

# After (scripts/docker/odoo-migrate.sh):
#!/bin/bash
set -euo pipefail
echo "Running Odoo migrations..."
docker-compose exec odoo-web python manage.py migrate
echo "Migrations complete."
```

**Step 3: Update Documentation**
```markdown
# Before:
Run: `docker exec -it odoo-web-1 python manage.py migrate`

# After:
Run: `bash scripts/docker/odoo-migrate.sh`
```

**Step 4: Verify CI Gate**
```bash
# Test gate locally
bash scripts/gates/scan-forbidden-commands.sh

# Commit changes
git add scripts/docker/odoo-migrate.sh
git commit -m "chore(docker): migrate to sanctioned automation"
git push origin feature-branch
```

---

## References

**Related Policies**:
- `docs/portfolio/PORT-2026-011.md` - Integration Hardening & Compliance
- `docs/evidence/EVID-20260212-006/` - Policy enforcement evidence

**Related Infrastructure**:
- `.github/workflows/no-cli-no-docker-gate.yml` - CI gate enforcement
- `scripts/gates/scan-forbidden-commands.sh` - Violation scanner
- `scripts/docker/` - Sanctioned automation directory

**External Resources**:
- [12-Factor App: Config](https://12factor.net/config)
- [Infrastructure as Code: GitOps](https://www.gitops.tech/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

*Policy created: 2026-02-12*
*Status: Active - CI gate enforced*
*Portfolio Initiative: PORT-2026-011*
