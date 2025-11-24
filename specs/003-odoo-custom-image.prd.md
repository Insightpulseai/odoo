---
id: 003
title: Odoo CE Custom Image – Production Artifact Spec
owner: jgtolentino
status: draft
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

## 1. Overview

This spec defines the **canonical custom Docker image** for Odoo CE 18, built from the upstream `odoo:18.0` base and extended with InsightPulse-specific configuration and addons.

The image is the **single source of truth** for all runtime behavior in:
- **DigitalOcean VPS** (`docker-compose.prod.yml`)
- **DigitalOcean Kubernetes (DOKS)** (`odoo` Deployment)

Image reference:

```text
ghcr.io/jgtolentino/odoo-ce:latest
```

This PRD scopes the image behavior, build process, constraints, and success criteria.

## 2. Goals / Non-Goals

### 2.1 Goals

Provide a reproducible, immutable Odoo 18 image with:
- CE/OCA-only addons baked in (`./addons`, `./oca` via mounted volumes).
- Production config baked in (`./deploy/odoo.conf`).
- Standardize deployment across:
  - Docker Compose (`docker-compose.prod.yml`) on DO VPS.
  - DOKS Deployments using the same image tag.
- Enforce no Enterprise contamination at the image level.
- Make it trivial to:
  - Build & push: `ghcr.io/jgtolentino/odoo-ce:latest`.
  - Swap image in VPS & DOKS via a single tag.

### 2.2 Non-Goals

- Not defining all CI/CD workflows in this spec (only image requirements).
- Not describing Kubernetes manifests in detail (covered by DOKS infra spec).
- Not handling Odoo database migrations beyond the standard `-u` module update flow.

## 3. Requirements

### 3.1 Functional Requirements

**Base Image**
- MUST use `odoo:18.0` as base.
- MUST run Odoo under the non-root `odoo` user.

**Custom Addons**
- MUST bake local addons into the image:
  - `./addons` → `/mnt/extra-addons/`
  - Optional: OCA addons kept as separate volumes, not baked (to keep image lean).
- MUST preserve compatibility with:
  - `ipai_ppm_advanced`
  - `ipai_internal_shop`
  - `ipai_finance_ppm`
  - `auth_oidc`
  - Any other CE/OCA-only modules defined in the project.

**Configuration**
- MUST copy a production config into the image:
  - `./deploy/odoo.conf` → `/etc/odoo/odoo.conf`
- Config MUST be overridable via:
  - Bind mounts in `docker-compose.prod.yml`.
  - Environment variables (e.g., `HOST`, `USER`, `PASSWORD`, `DB`).

**Runtime Environment**
- MUST expose runtime defaults via ENV:
  - `HOST` (default `db`)
  - `PORT` (default `5432`)
  - `USER` (default `odoo`)
  - `PASSWORD` (default `odoo`)
  - `DB` (default `odoo`)
- MUST not hard-code real secrets into the image.

**Deployment Paths**
- VPS path:
  - `docker-compose.prod.yml` MUST reference `ghcr.io/jgtolentino/odoo-ce:latest` for service `odoo`.
- DOKS path:
  - Kubernetes Deployment spec MUST use `image: ghcr.io/jgtolentino/odoo-ce:latest`

### 3.2 Non-Functional Requirements

**Security**
- MUST run as `USER odoo`, not root.
- MUST NOT bake secrets, tokens, or PATs into the image.

**Performance**
- Image build MUST complete successfully on a standard DO droplet or CI runner.

**Portability**
- Built image MUST run identically in:
  - Local Docker environment.
  - DO VPS via Compose.
  - DOKS via Kubernetes Deployment.

## 4. Design / Implementation

### 4.1 Dockerfile Layout

File: `./Dockerfile`

```Dockerfile
# Custom Odoo CE image for InsightPulse
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

# Copy custom CE/OCA addons baked into the image; owner set to odoo for runtime safety
COPY --chown=odoo:odoo ./addons /mnt/extra-addons/

# Install Python dependencies if a requirements file exists
RUN if [ -f /mnt/extra-addons/requirements.txt ]; then \
      pip install --no-cache-dir -r /mnt/extra-addons/requirements.txt; \
    fi

# Provide default configuration inside the image (override with bind mount in compose)
COPY --chown=odoo:odoo ./deploy/odoo.conf /etc/odoo/odoo.conf

# Default environment placeholders (override at runtime via compose/ENV)
ENV HOST=db \
    PORT=5432 \
    USER=odoo \
    PASSWORD=odoo \
    DB=odoo

# Run as non-root for security
USER odoo
```

Key properties:
- Delta architecture: upstream `odoo:18.0` + InsightPulse deltas only.
- No Enterprise modules baked in.
- Configurable via `ENV` and bind mounts.

### 4.2 Compose Integration (VPS)

File: `./docker-compose.prod.yml` (snippet)

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: odoo
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: CHANGE_ME_STRONG_DB_PASSWORD
      POSTGRES_MAX_CONNECTIONS: 100
    volumes:
      - odoo-db-data:/var/lib/postgresql/data
    # ...

  odoo:
    image: ghcr.io/jgtolentino/odoo-ce:latest
    container_name: odoo-ce
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      HOST: db
      USER: odoo
      PASSWORD: CHANGE_ME_STRONG_DB_PASSWORD
      ODOO_RC: /etc/odoo/odoo.conf
    volumes:
      - ./deploy/odoo.conf:/etc/odoo/odoo.conf:ro
      - ./addons:/mnt/extra-addons
      - ./oca:/mnt/oca-addons
      - odoo-filestore:/var/lib/odoo
    ports:
      - "127.0.0.1:8069:8069"
```

### 4.3 Registry & Tagging

Canonical image location:

```
ghcr.io/jgtolentino/odoo-ce:latest
```

Build + push (manual or in CI):

```bash
export IMAGE=ghcr.io/jgtolentino/odoo-ce:latest

echo "$GHCR_PAT" | docker login ghcr.io -u jgtolentino --password-stdin
docker build -t "$IMAGE" .
docker push "$IMAGE"
```

## 5. Success Criteria

### 5.1 Build & Runtime (Local)

- `docker build -t ghcr.io/jgtolentino/odoo-ce:latest .` exits with code 0.
- `docker run --rm -p 8069:8069 ghcr.io/jgtolentino/odoo-ce:latest`:
  - Starts without crash.
  - `/web` endpoint responds with HTTP 200/302 locally.

### 5.2 VPS Deployment (Compose)

On DO VPS:

```bash
cd ~/odoo-prod
docker compose -f docker-compose.prod.yml pull odoo
docker compose -f docker-compose.prod.yml up -d
```

Pass if:
- `docker ps` shows Image for Odoo container = `ghcr.io/jgtolentino/odoo-ce:latest` (or a specific SHA tag).
- `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8069/web` returns 200 or 302.
- Odoo logs show successful DB connection and no fatal module import errors.

### 5.3 DOKS Deployment (Kubernetes)

Cluster configured with:

```bash
kubectl set image deployment/odoo odoo=ghcr.io/jgtolentino/odoo-ce:latest
kubectl rollout status deployment/odoo
```

Pass if:
- `kubectl rollout status deployment/odoo` exits with code 0.
- `kubectl get pods -l app=odoo` shows all pods `STATUS=Running, READY=1/1`.
- Ingress/Service path returns HTTP 200/302 at `https://erp.insightpulseai.net/web`.

### 5.4 Feature-Level (Modules Present)

Inside a running Odoo pod:

```bash
kubectl exec -it <odoo-pod> -- odoo-bin -c /etc/odoo.conf \
  -d <DB_NAME> -u ipai_ppm_advanced,ipai_internal_shop,ipai_finance_ppm,auth_oidc --stop-after-init
```

Pass if:
- Command exits with code 0 (no migration/import failures).
- All four modules are installable and load without dependency errors.

## 6. Constraints & Risks

- Disk space on VPS and CI runners may limit repeated build/push cycles; cleanup (dangling images) may be required.
- If `./addons` structure changes, builds can break; this spec assumes:
  - Valid `__manifest__.py` for each module.
  - Optional `requirements.txt` at `/mnt/extra-addons/requirements.txt`.
- Any change to base image (`odoo:18.0` → other tag) must be explicitly revisited here.

## 7. Implementation Tasks

**T1 – Image Definition**

- Create `./Dockerfile` with base image, addons, config, ENV.
- Wire `docker-compose.prod.yml` to use `ghcr.io/jgtolentino/odoo-ce:latest`.

**T2 – Registry & Build Path**

- Add or confirm a CI job that:
  - Logs into GHCR.
  - Builds and pushes `ghcr.io/jgtolentino/odoo-ce:latest` on main.
- Document manual fallback build path in `docs/FINAL_DEPLOYMENT_RUNBOOK.md`.

**T3 – VPS Integration**

- Add `scripts/simple_deploy.sh` (optional wrapper):
  - `docker compose -f docker-compose.prod.yml pull odoo`
  - `docker compose -f docker-compose.prod.yml up -d`
- Run once on `159.223.75.148` and verify.

**T4 – DOKS Integration**

- Ensure Odoo Deployment in DOKS uses `ghcr.io/jgtolentino/odoo-ce:latest`.
- Add rollout verification steps to `docs/DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md`.

### Exit Criteria for This Spec

- Image builds successfully.
- VPS deployment runs using the custom image and passes smoketest.
- DOKS deployment runs using the same image and passes smoketest.
- Docs (FINAL_DEPLOYMENT_RUNBOOK, DOKS criteria) reference this image spec and are consistent.
