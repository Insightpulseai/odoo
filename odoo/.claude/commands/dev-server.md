# Command: Start Dev Server

[ROLE] Coding agent in Claude Code Web. You have a cloud shell, file access to the repo root, and browser-based port preview.

[GOAL] Start and maintain the application dev server(s) defined in devserver.config.json / Makefile, then report back the active URLs/ports.

[CONSTRAINTS]
- Do not ask the user questions.
- Use only shell, scripts, and repo config; no manual UI steps.
- Assume devserver.config.json and Makefile exist at repo root.
- Prefer `make dev` unless config explicitly requires both frontend + backend.

[EXECUTION PLAN]
1. Inspect devserver.config.json to discover services, default service, ports, and health paths.
2. Inspect the Makefile to confirm dev targets (dev, dev-minimal, dev-full, dev-frontend, dev-backend).
3. Install dependencies if missing (npm/pip/etc.); cache node_modules/venv when possible.
4. Start the default dev service in a long-lived terminal pane.
5. Wait until the configured port responds on the configured healthPath.
6. Return a summary of:
   - which services are running,
   - which ports they listen on,
   - how to open them in the Claude Code Web browser preview.

---

## Step 1: Analyze Configuration

```bash
# Read devserver config
cat devserver.config.json | head -50

# Check available Makefile targets
grep -E "^(dev|dev-):" Makefile || true
```

## Step 2: Check Environment

```bash
# Check Docker availability
docker --version || echo "Docker not available"
docker compose version || echo "Docker Compose not available"

# Check Node.js
node --version || echo "Node.js not available"
pnpm --version || npm --version || echo "No JS package manager"

# Check Python
python3 --version || python --version || echo "Python not available"
```

## Step 3: Start Services

### Option A: Full Docker Stack (Recommended)
```bash
# Start minimal stack (Postgres + Odoo Core)
make dev-minimal
```

### Option B: Frontend Only (Control Room)
```bash
make dev-frontend
```

### Option C: Backend Only (Control Room API)
```bash
make dev-backend
```

### Option D: Full Stack
```bash
make dev-full
```

## Step 4: Health Checks

```bash
# Check service status
make dev-status

# Run health checks
make dev-health
```

## Step 5: Individual Service Health

```bash
# Odoo Core (primary)
curl -sf http://localhost:8069/web/health && echo "✅ Odoo Core healthy"

# Control Room Frontend
curl -sf http://localhost:3000/ >/dev/null && echo "✅ Control Room healthy"

# n8n
curl -sf http://localhost:5678/healthz && echo "✅ n8n healthy"
```

---

## Output Format

After starting services, report:

```
## Dev Server Status

| Service | Port | Status | Preview URL |
|---------|------|--------|-------------|
| Odoo Core | 8069 | ✅ Running | http://localhost:8069 |
| PostgreSQL | 5432 | ✅ Running | - |
| n8n | 5678 | ⚪ Not started | http://localhost:5678 |
| Control Room | 3000 | ⚪ Not started | http://localhost:3000 |

**Default Service:** Odoo Core
**Health Check:** Passed

To open preview in Claude Code Web, use port 8069.
```

---

## Profiles (from devserver.config.json)

- **minimal**: postgres, odoo-core
- **development**: postgres, odoo-core, n8n, control-room
- **full**: all services

---

## Stop Services

```bash
make dev-stop
```
