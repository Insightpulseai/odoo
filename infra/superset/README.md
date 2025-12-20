# Superset Integration

Apache Superset BI dashboard integration via **artifact contract pattern**.

## Why NOT a Submodule

Superset is **not** a git submodule. Instead, we use a pinned container image reference:

| Approach | Pros | Cons | When to Use |
|----------|------|------|-------------|
| **Artifact Contract** (this) | Clean CI, easy rollback, clear ownership | No single-PR atomic changes | 90% of cases |
| Git Subtree | Atomic changes, works offline | Heavy repo, merge complexity | Rarely |
| Git Submodule | Pin exact commits | CI friction, checkout issues, footguns | Never |

## Files

| File | Purpose |
|------|---------|
| `manifest.json` | Pinned image reference (tag, digest, metadata) |
| `do-app-spec.yaml` | DigitalOcean App Platform deployment spec |
| `README.md` | This documentation |

## Workflows

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| `.github/workflows/superset-bump.yml` | Update image tag | Manual or repository_dispatch |

## Usage

### Check Current Version

```bash
cat infra/superset/manifest.json | jq '.artifact'
```

### Bump to New Version

**Manual (via GitHub UI):**
1. Go to Actions → "Superset Bump"
2. Enter tag (e.g., `v1.2.0`)
3. Run workflow
4. Review and merge the PR

**Via CLI:**
```bash
gh workflow run superset-bump.yml -f tag=v1.2.0
```

**From Superset Repo (webhook):**
```bash
# In superset repo CI, after push:
gh api repos/jgtolentino/odoo-ce/dispatches \
  -f event_type=superset-release \
  -f client_payload='{"tag":"v1.2.0","digest":"sha256:abc123..."}'
```

### Deploy

```bash
# Create app
doctl apps create --spec infra/superset/do-app-spec.yaml

# Update existing app
doctl apps update <app-id> --spec infra/superset/do-app-spec.yaml
```

## Artifact Contract

The contract between `odoo-ce` and `superset` repos:

```
┌──────────────────┐          ┌──────────────────┐
│   superset repo  │          │    odoo-ce repo  │
│                  │          │                  │
│  Build → Push    │  image   │   manifest.json  │
│  to GHCR         │ ───────▶ │   (pinned tag)   │
│                  │          │                  │
│  CI: build,      │  webhook │   do-app-spec    │
│  scan, push      │ ───────▶ │   (deploy spec)  │
└──────────────────┘          └──────────────────┘
```

1. **superset repo** builds and pushes `ghcr.io/jgtolentino/ipai-superset:<tag>`
2. **superset repo** (optionally) sends `repository_dispatch` to odoo-ce
3. **odoo-ce** `superset-bump` workflow updates `manifest.json` and `do-app-spec.yaml`
4. **PR** is opened for review
5. **After merge**, DO App auto-deploys new image

## Environment Variables

Required secrets in DigitalOcean App Platform:

| Variable | Description |
|----------|-------------|
| `SUPERSET_SECRET_KEY` | Flask secret key (generate with `openssl rand -base64 42`) |
| `DATABASE_URL` | Postgres connection string |
| `REDIS_URL` | Redis connection string |

## Health Check

```bash
curl https://superset.insightpulseai.net/health
```

Expected response:
```json
{"status": "OK"}
```
