# Vercel Monorepo Contract

**Status**: Active
**SSOT**: `ssot/vercel/projects.yaml`
**CI Guard**: `scripts/ci/check_vercel_monorepo_ssot.py`
**Reference**: https://vercel.com/docs/monorepos

---

## Overview

This repository is a pnpm workspaces monorepo accelerated by Turborepo. Vercel is the canonical
deployment platform for all user-facing applications. Deployable apps live under `apps/`; shared
libraries live under `packages/`. All Vercel project settings are declared in
`ssot/vercel/projects.yaml` — not in the Vercel dashboard, not in individual `vercel.json` files.

---

## Project Structure

```
/
├── apps/                      # Deployable applications (Vercel-owned)
│   ├── ops-console/           # Ops dashboard — deployed to Vercel
│   ├── web/                   # Marketing / public site
│   └── <other-apps>/
├── packages/                  # Shared libraries (not deployed directly)
│   ├── ui/                    # Shared React component library
│   ├── config/                # Shared tsconfig, eslint, etc.
│   └── <other-packages>/
├── turbo.json                 # Turborepo pipeline definitions
├── pnpm-workspace.yaml        # Workspace package paths
└── ssot/vercel/
    └── projects.yaml          # Canonical Vercel project registry (SSOT)
```

### Rule: `apps/` is for deployables, `packages/` is for shared code

- Every path registered in `ssot/vercel/projects.yaml` under `root_directory` MUST start with `apps/`.
- Shared code in `packages/` is consumed at build time; it is never deployed as a standalone Vercel
  project.

---

## Vercel Project Linking

Projects are linked at the **repository root**, not from a subdirectory:

```bash
# Correct — run from repo root
vercel link --repo

# Incorrect — do not link from within apps/my-app/
cd apps/my-app && vercel link   # forbidden
```

Linking from a subdirectory creates orphaned project configurations that bypass the SSOT registry.
All linking must produce an entry in `ssot/vercel/projects.yaml`.

---

## "Include Files Outside Root" Requirement

Vercel builds each app in isolation using its `root_directory`. When an app imports from
`packages/*`, the Vercel build context must be expanded to include the workspace root.

**Rule**: Any app that sets `uses_packages: true` in `ssot/vercel/projects.yaml` MUST also set
`include_files_outside_root: true`.

Failure to enable this flag causes build failures because Vercel cannot resolve `packages/*`
imports at build time. The CI guard (`check6` in `check_vercel_monorepo_ssot.py`) enforces this
invariant automatically.

```yaml
# ssot/vercel/projects.yaml — example compliant entry
projects:
  - name: ops-console
    root_directory: apps/ops-console
    uses_packages: true
    include_files_outside_root: true   # required when uses_packages is true
    ignored_build: npx turbo-ignore
```

---

## Turborepo Integration

### Build Commands

All Vercel build commands MUST use `turbo build` with a `--filter` flag targeting the specific app:

```bash
# Correct — scoped to the specific app
turbo build --filter=ops-console

# Incorrect — builds everything
turbo build
```

The `turbo.json` at the repo root defines the pipeline. Vercel's build command for each project
must reference this pipeline to enable cache hits across branches and deployments.

### `turbo.json` Requirement

If `turborepo: true` is set at the monorepo level in `ssot/vercel/projects.yaml`, the file
`turbo.json` MUST exist at the repo root. The CI guard (check 4) enforces this.

---

## turbo-ignore for Intelligent Ignored Builds

Vercel supports a custom "Ignored Build Step" command. Use `turbo-ignore` to prevent Vercel from
building an app when none of its source files (or the files of its transitive dependencies) have
changed:

```bash
# In ssot/vercel/projects.yaml under ignored_build:
npx turbo-ignore
```

`turbo-ignore` inspects the Turborepo dependency graph and exits with code 1 (skip build) when
the affected subgraph has not changed since the last successful deployment.

Every project registered in `ssot/vercel/projects.yaml` MUST declare `ignored_build` (CI check 6).
Omitting it means every push triggers a full rebuild of every app regardless of what changed.

---

## `vercel.json` Is Not the Authority for Build Settings

In a standard single-project repository, `vercel.json` is the configuration file. In this monorepo,
it is NOT the authoritative source for build settings such as:

- `buildCommand`
- `outputDirectory`
- `installCommand`
- `ignoreCommand`

The single authority for all of the above is `ssot/vercel/projects.yaml`. Project-level
`vercel.json` files may exist in `apps/<name>/` for routing rules (`rewrites`, `redirects`,
`headers`) only.

| Setting | Authoritative location |
|---------|------------------------|
| `buildCommand` | `ssot/vercel/projects.yaml` |
| `outputDirectory` | `ssot/vercel/projects.yaml` |
| `installCommand` | `ssot/vercel/projects.yaml` |
| `ignoreCommand` / `ignoredBuildStep` | `ssot/vercel/projects.yaml` (`ignored_build`) |
| `rewrites` / `redirects` / `headers` | `apps/<name>/vercel.json` (routing only) |
| Environment variable names | `ssot/vercel/projects.yaml` + Vercel dashboard (values) |
| Environment variable values | Vercel dashboard (never in files) |

---

## Deployment Platform Policy

**Vercel is the canonical platform for all `apps/*`.**

DigitalOcean App Platform is NOT used for any application rooted under `apps/`. Historical
DO App Platform deployments for Node.js/Next.js workloads have been retired.

| App type | Platform |
|----------|----------|
| Next.js / React (all `apps/*`) | Vercel |
| Odoo ERP (Python) | DigitalOcean Droplet (self-hosted) |
| n8n automation | DigitalOcean Droplet (self-hosted) |
| Python microservices (non-Next.js) | DigitalOcean App Platform |

---

## CI Guard

The validator `scripts/ci/check_vercel_monorepo_ssot.py` enforces six invariants on every pull
request that touches `ssot/vercel/**`, `pnpm-workspace.yaml`, or `turbo.json`:

| Check | Invariant |
|-------|-----------|
| 1 | `ssot/vercel/projects.yaml` exists and is valid YAML |
| 2 | Every `projects[].root_directory` starts with `apps/` |
| 3 | `uses_packages: true` implies `include_files_outside_root: true` |
| 4 | `turborepo: true` at monorepo level implies `turbo.json` exists at repo root |
| 5 | `pnpm-workspace.yaml` exists and contains patterns for both `apps/*` and `packages/*` |
| 6 | Every project declares `ignored_build` |

Run locally:

```bash
pip install pyyaml
python scripts/ci/check_vercel_monorepo_ssot.py --repo-root .
```

---

## Verification Checklist

Before merging any change to `ssot/vercel/projects.yaml` or related monorepo config:

- [ ] `python scripts/ci/check_vercel_monorepo_ssot.py` exits 0 with all 6 checks PASS
- [ ] `pnpm-workspace.yaml` contains `apps/*` and `packages/*` patterns
- [ ] `turbo.json` exists at repo root and defines a `build` pipeline task
- [ ] Every new app entry in `projects.yaml` declares `ignored_build: npx turbo-ignore`
- [ ] Any app importing `packages/*` has `include_files_outside_root: true` in the SSOT

---

## Reference

- Vercel Monorepos documentation: https://vercel.com/docs/monorepos
- Turborepo docs: https://turbo.build/repo/docs
- turbo-ignore docs: https://turbo.build/repo/docs/reference/turbo-ignore
- SSOT file: `ssot/vercel/projects.yaml`
- CI guard: `scripts/ci/check_vercel_monorepo_ssot.py`
- GitHub Actions job: `vercel-monorepo-ssot` in `.github/workflows/ssot-gates.yml`
