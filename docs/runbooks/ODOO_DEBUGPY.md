# Odoo debugpy Runbook

> Deterministic step-debugging for Odoo CE 19 across three modes.
> Toggle: `IPAI_DEBUGPY=1` env var.  Port: `5678`.

---

## How it works

`scripts/odoo_debugpy_entrypoint.py` is a thin wrapper that reads `IPAI_DEBUGPY`.
When set to a truthy value (`1`, `true`, `yes`), it calls `debugpy.listen()` before
`os.execvp`-ing into Odoo.  When `IPAI_DEBUGPY=0` (the default), the wrapper is a
zero-overhead pass-through.

```
IPAI_DEBUGPY=0  →  entrypoint → os.execvp("odoo", args)  (no output, no overhead)
IPAI_DEBUGPY=1  →  entrypoint → debugpy.listen(:5678) → os.execvp("odoo", args)
```

**Startup log line** — when enabled, the wrapper prints a greppable JSON summary
before starting debugpy:
```
{"ipai_debugpy": true, "port": 5678, "wait": false}
```
Grep this in CI/logs: `docker logs odoo-core | grep ipai_debugpy`

**Exit codes:**

| Code | Meaning |
|------|---------|
| 0 | Odoo exited cleanly (`os.execvp` replaces the wrapper process) |
| 2 | `IPAI_DEBUGPY=1` but `debugpy` not installed — rebuild with dev image |

`IPAI_DEBUGPY_WAIT=1` blocks Odoo startup until VS Code attaches (useful for
debugging early initialisation — models, registry loading, etc.).

**`workers` must be 0** — debugpy cannot follow forked worker processes.
`config/dev/odoo.conf` already sets `workers = 0`.

---

## Mode 1 — Launch local (inside DevContainer)

VS Code starts the Odoo process directly via the debugpy launch adapter.
No `IPAI_DEBUGPY` toggle needed — debugpy is the runner.

**Steps:**

1. Open the repo in VS Code and **Reopen in Container**.
2. Select **Run and Debug** → `Odoo (Launch local)`.
3. VS Code starts `/usr/bin/odoo` under debugpy; breakpoints work immediately.

**Config used:** `.vscode/launch.json` → `"Odoo (Launch local)"`

```json
"program": "/usr/bin/odoo",
"args": ["--config=${workspaceFolder}/config/dev/odoo.conf", "--workers=0", ...]
```

---

## Mode 2 — Attach (DevContainer, running via compose)

Odoo runs inside the devcontainer as a compose service. VS Code attaches.

**Steps:**

1. Set `IPAI_DEBUGPY=1` in your host shell (or add to `.env`):
   ```bash
   export IPAI_DEBUGPY=1
   ```
2. Open the repo in VS Code and **Reopen in Container**.
   The compose overlay (`.devcontainer/docker-compose.devcontainer.yml`) starts
   Odoo via the entrypoint wrapper with `IPAI_DEBUGPY=1` and exposes port `5678`.
3. Wait for Odoo log line: `[debugpy] listening on 0.0.0.0:5678`
4. Select **Run and Debug** → `Odoo (Attach — DevContainer / debugpy :5678)`.
5. Set breakpoints — they bind immediately.

**To block startup until you attach** (debug early init):
```bash
export IPAI_DEBUGPY=1 IPAI_DEBUGPY_WAIT=1
```

**Config used:** `.vscode/launch.json` → `"Odoo (Attach — DevContainer / debugpy :5678)"`

```json
"pathMappings": [
  { "localRoot": "${workspaceFolder}", "remoteRoot": "/workspaces/odoo" }
]
```

---

## Mode 3 — Attach (plain Docker Compose, no DevContainer)

Odoo runs as a plain `docker compose` stack. Expose port 5678 and attach.

**Steps:**

1. Expose port 5678 in `docker-compose.yml` odoo service:
   ```yaml
   ports:
     - "${ODOO_PORT:-8069}:8069"
     - "${ODOO_LONGPOLL_PORT:-8072}:8072"
     - "5678:5678"   # add this line
   ```
2. Start compose with the toggle:
   ```bash
   IPAI_DEBUGPY=1 docker compose up -d
   ```
3. Wait for: `[debugpy] listening on 0.0.0.0:5678`
4. Select **Run and Debug** → `Odoo (Attach — Docker CE19 image / debugpy :5678)`.

**Config used:** `.vscode/launch.json` → `"Odoo (Attach — Docker CE19 image / debugpy :5678)"`

```json
"pathMappings": [
  { "localRoot": "${workspaceFolder}/addons/ipai", "remoteRoot": "/mnt/extra-addons/ipai" },
  { "localRoot": "${workspaceFolder}/addons/oca",  "remoteRoot": "/mnt/oca" }
]
```

---

## Port conflict: n8n in docker-compose.dev.yml

`docker-compose.dev.yml` originally mapped n8n to host port `5678`.
It has been remapped to `5679:5678` so the dev overlay does not conflict with debugpy.

| Service | Container port | Host port |
|---------|---------------|-----------|
| Odoo debugpy | 5678 | 5678 |
| n8n (dev.yml) | 5678 | 5679 |

The DevContainer does **not** load `docker-compose.dev.yml` (only `docker-compose.yml` +
`.devcontainer/docker-compose.devcontainer.yml`), so there is no conflict in Mode 2.

---

## Failure symptoms

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Breakpoints show "unverified" | `justMyCode: true` | Set `"justMyCode": false` in launch.json |
| Breakpoints never hit | Wrong `pathMappings` | Verify container mount paths vs. `remoteRoot` values |
| `Connection refused` on attach | debugpy not listening | Check `IPAI_DEBUGPY=1` is set; check `docker logs odoo-core` for `[debugpy]` line |
| Odoo hangs on startup | `IPAI_DEBUGPY_WAIT=1` but no client attached | Attach VS Code immediately, or set `IPAI_DEBUGPY_WAIT=0` |
| Port 5678 already in use | n8n dev.yml not updated | Confirm `docker-compose.dev.yml` maps n8n to `5679:5678` |
| Entrypoint exits with code 2 | `IPAI_DEBUGPY=1` but debugpy not installed (prod/stage image) | Run `docker compose build --no-cache odoo` to rebuild dev image; check for `DEBUGPY_MISSING` in stderr |
| `ModuleNotFoundError: debugpy` | Import error variant of the above | Same fix: rebuild dev image |
| Workers > 0 warning | Requests split across processes | `workers = 0` in `config/dev/odoo.conf`; `--workers=0` in compose command |

---

## Related files

| File | Role |
|------|------|
| `scripts/odoo_debugpy_entrypoint.py` | Wrapper: conditional debugpy.listen → execvp |
| `docker/dev/Dockerfile` | Bakes `debugpy` into the dev image |
| `config/dev/odoo.conf` | Sets `workers = 0` |
| `.devcontainer/docker-compose.devcontainer.yml` | IPAI_DEBUGPY env + port 5678 + wrapper command |
| `.devcontainer/devcontainer.json` | Forwards port 5678 to host |
| `docker-compose.yml` | IPAI_DEBUGPY env passthrough (odoo service) |
| `docker-compose.dev.yml` | n8n remapped to 5679 to free 5678 |
| `.vscode/launch.json` | Three VS Code debug configurations |
