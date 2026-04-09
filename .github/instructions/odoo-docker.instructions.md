---
applyTo: "docker/**/*,docker-compose*.yml,.dockerignore"
---

You are editing Odoo 18 CE Docker and container configuration.

## Image family

- **Prod** (`docker/Dockerfile.prod`): Bakes addons into image, no volume mounts
- **Dev** (`docker/Dockerfile.dev`): Mount-friendly, adds debugpy/ipython/watchdog
- Both use `odoo:18.0` official base image
- Same `docker/entrypoint.sh` for both

## Role-based startup

The entrypoint reads `ODOO_ROLE` env var:

| Role | Flags | Serves HTTP? | Cron? |
|------|-------|:------------:|:-----:|
| `web` | `--max-cron-threads=0` | Yes (8069+8072) | No |
| `cron` | `--no-http --workers=0 --max-cron-threads=2` | No | Yes |
| `worker` | `--no-http --workers=0 --max-cron-threads=0` | No | No |

Worker role runs OCA `queue_job` jobrunner (polls DB for enqueued jobs).

## Addon layout in image

```
/usr/lib/python3/dist-packages/odoo/addons   CE core (Debian pkg)
/opt/odoo/src/oca/<repo>/                     OCA per-repo roots
/opt/odoo/src/ipai/                           IPAI bridge modules
/opt/odoo/src/local/                          Local-only addons
```

`addons_path` is generated at build time from repos on disk (Odoo does not recurse).

## Rules

- Never bake secrets into image layers (DB creds, SMTP, API keys → runtime env vars)
- Never hardcode database names in Dockerfiles (DB is a runtime argument)
- Keep `.dockerignore` as exclude-everything-then-allowlist
- Test artifacts, `__pycache__`, `.git`, `.env` must be excluded from build context
- Health check for web role: `curl -sf http://localhost:8069/web/health`
- Docker context: always `docker --context colima-odoo` locally (never switch global context)

## Do not

- Add `apt-get install` for packages not needed by OCA/IPAI modules
- Install pip packages without `--no-cache-dir --break-system-packages`
- Change the entrypoint contract without updating `docs/architecture/ODOO_IMAGE_BUILD_SPEC.md`
- Expose ports other than 8069, 8071, 8072 without documented justification
