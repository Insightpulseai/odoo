# Plane API Routing Fix

> **Status**: Blocker for Phase 4
> **Date**: 2026-03-13
> **Ref**: `spec/plane-unified-docs/plan.md` Phase 3 / Phase 4

## Problem

The Plane instance at `plane.insightpulseai.com` serves the React SPA frontend for all paths, including `/api/v1/*`. The API backend is unreachable — all requests return `text/html` (the SPA catch-all).

**Evidence**:
```
$ curl -sI -H "X-API-Key: $PLANE_API_KEY" https://plane.insightpulseai.com/api/v1/workspaces/
content-type: text/html
```

## Root Cause

Plane self-hosted requires multiple services behind a proxy:

| Service | Role | Default Port |
|---------|------|-------------|
| `web` | React SPA frontend | 3000 |
| `api` | Django REST backend | 8000 |
| `worker` | Celery background jobs | — |
| `beat-worker` | Celery scheduled tasks | — |
| `proxy` | Caddy reverse proxy | 80/443 |
| `live` | WebSocket (real-time) | — |

The proxy (Caddy) routes:
- `/api/*` → `api:8000`
- `/` (everything else) → `web:3000`

Current Azure Container App `ipai-plane-dev` appears to only serve the `web` frontend, with no routing to the `api` backend.

## Fix Options

### Option A: Multi-container Plane deployment (recommended)

Deploy all Plane services as separate Azure Container Apps or as a single multi-container app:

1. `ipai-plane-web` — Plane web frontend (port 3000)
2. `ipai-plane-api` — Plane API backend (port 8000)
3. `ipai-plane-worker` — Celery worker
4. `ipai-plane-beat` — Celery beat scheduler
5. Use Azure Front Door path-based routing:
   - `/api/*` → `ipai-plane-api:8000`
   - `/*` → `ipai-plane-web:3000`

### Option B: Single container with Caddy proxy

Deploy the official Plane Docker Compose stack (includes its own Caddy proxy) as a single container group. Expose Caddy's port 80 and let Azure Front Door handle TLS termination.

### Option C: Azure Container Apps with sidecar

Use the Azure Container Apps sidecar pattern to run `web`, `api`, and `proxy` in the same container app with internal networking.

## Verification

After fix, this must return JSON (not HTML):

```bash
curl -s -H "X-API-Key: $PLANE_API_KEY" \
  -H "Accept: application/json" \
  "https://plane.insightpulseai.com/api/v1/workspaces/" | python3 -m json.tool
```

## Next Step

Once the API is routed:

```bash
./scripts/plane/scaffold_workspace.sh
```

This creates all Phase 4 artifacts (10 projects, 15 wiki pages, 5 templates).

## References

- [Plane Architecture](https://developers.plane.so/self-hosting/plane-architecture)
- [Docker Compose Setup](https://developers.plane.so/self-hosting/methods/docker-compose)
- Spec: `spec/plane-unified-docs/plan.md` Phase 3
