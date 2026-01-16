# Runbook: Docker Desktop Cleanup & SSOT Alignment

**Owner:** Basher-Docker (Docker Steward Agent)
**Host:** MacBook-Pro
**Purpose:** Keep local Docker Desktop aligned to the Odoo dev sandbox SSOT.

---

## 1. Context

- Canonical Odoo dev sandbox:
  - `~/Documents/GitHub/odoo-ce/sandbox/dev`
  - `docker-compose.yml` in that directory is the source of truth.
- Local Docker is for:
  - Odoo 18 CE app + Postgres
  - Optional Mailpit + pgAdmin when `tools` profile is used.
- Everything else (extensions, old experiments, MCP helpers) is a **candidate for cleanup**.

SSOT is defined in:

```text
infra/docker/DOCKER_DESKTOP_SSOT.yaml
```

---

## 2. Objectives

1. Audit current Docker state (containers, images, volumes).
2. Compare against SSOT and classify resources:
   - `expected`
   - `candidate_cleanup`
   - `unsafe_to_touch`
3. Propose a safe cleanup plan.
4. Apply cleanup (when explicitly requested).
5. Verify Odoo dev sandbox is healthy.

---

## 3. Quick Start (Agent Command)

From the Odoo sandbox:

```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
./scripts/docker-desktop-audit.sh
```

This script:

- Lists containers, images, volumes.
- Highlights anything **not** matching the SSOT allow-lists.
- Writes a JSONL audit log under `logs/docker_audit_log.jsonl`.

Use this as the baseline for the Basher-Docker agent.

---

## 4. Manual Cleanup Commands (to be run by Agent)

> ⚠️ These are examples. The agent should tailor them to the actual audit output.

### 4.1 Stop and Remove Extension Containers

```bash
# Stop obvious extension/MCP containers
docker ps --format '{{.ID}} {{.Image}}' \
  | egrep 'docker-extension|mcp/|artifision/|mochoa/|pgmystery/' \
  | awk '{print $1}' \
  | xargs -r docker stop

# Remove them
docker ps -a --format '{{.ID}} {{.Image}}' \
  | egrep 'docker-extension|mcp/|artifision/|mochoa/|pgmystery/' \
  | awk '{print $1}' \
  | xargs -r docker rm
```

### 4.2 Remove Extension / Old Images

```bash
docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' \
  | egrep 'docker-extension|mcp/|artifision/|mochoa/|pgmystery/' \
  | awk '{print $2}' \
  | xargs -r docker rmi
```

### 4.3 Remove Dangling Images & Volumes

```bash
# Dangling images
docker image prune -f

# Unused volumes (be careful; SSOT volumes are preserved by name)
docker volume ls --format '{{.Name}}' \
  | egrep -v '^(odoo-dev-db-data|odoo-dev-filestore)$' \
  | xargs -r docker volume rm
```

---

## 5. Re-start & Verify Odoo Dev Sandbox

From the sandbox directory:

```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev

# Bring up core services
docker compose up -d

# Or include tools profile
docker compose --profile tools up -d

# Check status
docker compose ps
```

Expected:

- Containers: `odoo-dev`, `odoo-dev-db` (plus `mailpit`, `pgadmin` when tools are enabled).
- Volumes: `odoo-dev-db-data`, `odoo-dev-filestore`.
- Browser: `http://localhost:8069` loads Odoo, DB selector shows only `odoo_dev`.

---

## 6. Audit Log (For Future RL / Analytics)

Each audit run should append a line to:

```text
logs/docker_audit_log.jsonl
```

Fields:

- `timestamp`
- `host`
- `containers_expected`
- `containers_extra`
- `images_expected`
- `images_extra`
- `volumes_expected`
- `volumes_extra`

This log will later feed a small policy learner / heuristic tuner.

---

## 7. Acceptance Criteria

This runbook is **complete** when:

1. Docker Desktop shows only:
   - Odoo dev containers (and optional tools when requested).
2. No Docker extension / MCP helper containers or images remain.
3. Only SSOT volumes exist for Odoo.
4. `docker-desktop-audit.sh` runs cleanly and:
   - Classifies all resources correctly.
   - Writes an audit line.
5. Odoo dev sandbox is reachable at `http://localhost:8069` and uses `odoo_dev` only.
6. `infra/docker/DOCKER_DESKTOP_SSOT.yaml` is committed and versioned.

---

## 8. Agent Prompt Stub

When using Claude Code / Codex, start with:

> Audit my Docker Desktop against infra/docker/DOCKER_DESKTOP_SSOT.yaml using scripts/docker-desktop-audit.sh. Show me a drift report and then propose safe cleanup commands for extension/MCP images only. Do not execute cleanup until I say APPLY CLEANUP.
