# OCA Hydration

> How OCA addons get into `addons/oca/` — and why the directory is empty in git.

## Status Model

| Artifact | Role | Committed? |
|----------|------|------------|
| `oca-aggregate.yml` | **SSOT** — declares which OCA repos to clone, targeting Odoo 19.0 | Yes |
| `addons/oca/` | **Generated** — hydrated by git-aggregator at dev/build time | No (`.gitkeep` only) |
| `oca.lock.json` | **LEGACY** — stale 18.0-era lock file, do not use | Deprecated (see below) |

## Canonical Hydration Workflow

### Option A: Script (recommended for local dev)

```bash
# One command — idempotent, skips if already hydrated
./scripts/hydrate_oca.sh

# Force re-hydrate (re-clone all repos)
./scripts/hydrate_oca.sh --force

# Parallel jobs (default: 4)
OCA_JOBS=8 ./scripts/hydrate_oca.sh
```

### Option B: Manual git-aggregator

```bash
# 1. Install git-aggregator (once per environment)
pip install git-aggregator

# 2. Hydrate OCA repos into addons/oca/
gitaggregate -c oca-aggregate.yml          # sequential
gitaggregate -c oca-aggregate.yml -j 4     # parallel (4 jobs)

# 3. Start Odoo with the canonical addons_path order
#    CE → OCA → IPAI
```

After hydration, `addons/oca/` contains one subdirectory per OCA repo
(e.g., `addons/oca/web/`, `addons/oca/server-tools/`). Each subdirectory is
a full git clone of the corresponding OCA 19.0 branch.

## Automatic Hydration in Dev

The entrypoint hook `config/entrypoint.d/05-hydrate-oca.sh` can auto-hydrate
at container startup. It is **disabled by default** and gated by an env var:

```yaml
# In docker-compose.yml or docker-compose.override.yml:
environment:
  OCA_HYDRATE: "1"        # Enable auto-hydration at startup
  OCA_JOBS: "4"           # Parallel clone jobs (optional, default: 4)
```

**Behavior:**
- If `OCA_HYDRATE != 1` → skip silently (zero overhead)
- If `addons/oca/` already has repos → skip (idempotent, fast path)
- If `git-aggregator` is not installed → warn and continue (non-fatal)
- If hydration fails → warn and continue (Odoo starts without OCA)

**Production note:** Do not use `OCA_HYDRATE=1` in production. Production
images should bake OCA repos at Docker build time for deterministic deploys.

## Hydration Strategies by Environment

| Environment | Strategy | How |
|-------------|----------|-----|
| **Local dev** | Script or auto-hydrate | `./scripts/hydrate_oca.sh` or `OCA_HYDRATE=1` |
| **DevContainer** | Auto-hydrate on create | Add to `postCreateCommand` |
| **CI** | Hydrate + test + publish | `scripts/hydrate_oca.sh` in workflow |
| **Production** | Bake at build time | `RUN` in Dockerfile (future) |

## Docker Compose Alignment

`docker-compose.yml` mounts the hydrated directory into the container:

```yaml
volumes:
  - ./addons/oca:/mnt/oca:rw
```

The Odoo `addons_path` inside the container must include `/mnt/oca` (and its
subdirectories) between CE core and IPAI bridges.

## Canonical `addons_path` Order

All environments (dev, staging, prod) must load addons in this priority:

1. `addons/odoo` — CE core (upstream mirror)
2. `addons/oca` — OCA modules (hydrated, EE-parity)
3. `addons/ipai` — Integration bridges / compatibility shims

## Why Not Commit OCA Repos?

- OCA repos are large (hundreds of modules per repo, full git history)
- They have their own release cadence independent of this repo
- `oca-aggregate.yml` is the single source of truth for composition
- `.gitignore` ensures hydrated checkouts never pollute `git status`

## Deprecated: `oca.lock.json`

The root-level `oca.lock.json` is a **legacy artifact** from an earlier setup
targeting Odoo 18.0. It has been moved to `docs/architecture/legacy/oca.lock.18.0.json`
for historical reference.

**Do not use `oca.lock.json` for hydration.** The canonical config is
`oca-aggregate.yml` (Odoo 19.0).

If a reproducible lockfile is needed in the future, it must be generated from
`oca-aggregate.yml` and target 19.0.

## Related Documents

- [`oca-aggregate.yml`](../../oca-aggregate.yml) — SSOT for OCA repo composition
- [`scripts/hydrate_oca.sh`](../../scripts/hydrate_oca.sh) — Idempotent hydration script
- [`config/entrypoint.d/05-hydrate-oca.sh`](../../config/entrypoint.d/05-hydrate-oca.sh) — Startup hook (dev)
- [`REPO_LAYOUT.md`](REPO_LAYOUT.md) — Three-stack addon architecture rationale
- [`EE_PARITY_POLICY.md`](EE_PARITY_POLICY.md) — EE parity placement rules
- [`ADDONS_STRUCTURE_BOUNDARY.md`](ADDONS_STRUCTURE_BOUNDARY.md) — Full boundary taxonomy
