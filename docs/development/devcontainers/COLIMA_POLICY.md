# Colima Docker Context Policy — DevContainers

## Rule: DevContainers always use the `colima` (default) context

| Profile | Context name | Socket | Use for |
|---------|-------------|--------|---------|
| `colima` (default) | `colima` | `~/.colima/default/docker.sock` | DevContainers, staging, tunnel |
| `colima --profile odoo` | `colima-odoo` | `~/.colima/odoo/docker.sock` | Supabase Docker isolation only |

**`devcontainer.json` must always have `"dockerContext": "colima"`.**
Never use `colima-odoo` in `devcontainer.json` — that profile is not running during normal dev sessions.

## Switch scripts

```bash
# For DevContainers (default — always start here)
source scripts/docker/use_colima_default.sh

# For Supabase isolation (only when explicitly needed)
source scripts/docker/use_colima_odoo.sh
```

`use_colima_odoo.sh` contains an explicit warning: **"Never use this for Dev Containers."**

## When to start the odoo profile

Only when running Supabase-specific Docker workloads in isolation (not the normal dev workflow).
The odoo profile is NOT required for:
- VS Code DevContainers
- Odoo app containers
- PostgreSQL, Redis, n8n

## Verify before DevContainer rebuild

```bash
unset DOCKER_HOST DOCKER_CONTEXT
docker context use colima
docker info >/dev/null && echo "OK: colima default reachable"
cat .devcontainer/devcontainer.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('dockerContext','MISSING'))"
# Expected: colima
```

## Background: why two Colima profiles?

The `colima --profile odoo` profile provides a separate Docker daemon (separate network namespace) for running Supabase's local Docker stack without polluting the default dev Docker environment. It must be started explicitly with `colima start --profile odoo` and stopped when not needed.

SSOT: `scripts/docker/use_colima_odoo.sh`, `scripts/docker/use_colima_default.sh`
