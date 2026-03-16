# Canonical Runtime Image

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2026-03-07

## Purpose

Define the single approved production runtime image for the InsightPulseAI Odoo platform. This image replaces all prior marketplace, generic, or `edge-standard` image conventions.

## Canonical Image

| Property | Value |
|----------|-------|
| Image name | `ipai-odoo-runtime` |
| GHCR | `ghcr.io/insightpulseai/ipai-odoo-runtime` |
| DOCR | `registry.digitalocean.com/insightpulseai/ipai-odoo-runtime` |
| Base | `odoo:19` (Odoo Community Edition) |
| Dockerfile | `docker/Dockerfile.unified` |
| Build profiles | `standard` (production default), `parity` (full EE-parity OCA set) |

## Base Image

The runtime is built on the official Odoo CE 19 Docker image (`odoo:19`). No Enterprise code is included. No third-party packaged distributions or marketplace VM images are used as the production base.

## Layering

The image layers, from bottom to top:

1. **Odoo CE 19 base** — official `odoo:19` image
2. **System dependencies** — build-essential, libpq, libxml2, etc.
3. **OCA Python dependencies** — REST framework, apispec, cerberus, etc.
4. **OCA modules (flattened)** — all OCA submodule repos flattened into `/opt/odoo/addons/oca`
5. **OCA module Python deps** — per-module `requirements.txt` files
6. **IPAI custom modules** — copied into `/opt/odoo/addons/ipai`
7. **IPAI module Python deps** — per-module `requirements.txt` files
8. **Production config** — `config/prod/odoo.conf` baked at `/etc/odoo/odoo.conf`

## Required Addon Path Order

This is an SSOT invariant. All configs, images, and compose files must preserve this order:

```
/usr/lib/python3/dist-packages/odoo/addons   # Odoo CE core
/opt/odoo/addons/oca                          # OCA (flattened)
/opt/odoo/addons/ipai                         # IPAI custom
```

## Tag Patterns

| Tag | Meaning | Example |
|-----|---------|---------|
| `prod-YYYYMMDD-HHMM` | Production release (timestamped) | `prod-20260307-0241` |
| `sha-<7char>` | Commit-pinned build | `sha-a37cee1` |
| `latest` | Most recent main-branch build | `latest` |
| `19.0-standard` | Version channel (standard profile) | `19.0-standard` |
| `19.0-parity` | Version channel (parity profile) | `19.0-parity` |
| `stage` | Staging build | `stage` |

Tags are environment-neutral. The same image is promoted across environments without rebuild.

## Allowed `ipai_*` Module Usage

Modules in `addons/ipai/` that get baked into the image must be:

- External service connectors (Slack, OIDC, payment gateways)
- API bridges (MCP, REST controllers for non-Odoo clients)
- AI/ML tools (OCR pipelines, document processing, embedding services)
- BIR compliance (Philippine-specific tax/regulatory modules)
- Dependency-only meta bundles
- Platform glue explicitly approved by repo policy

## Forbidden `ipai_*` Module Usage

The image must NOT contain `ipai_*` modules that:

- Recreate Enterprise features that belong in CE or OCA
- Implement broad business logic forks of standard Odoo modules
- Duplicate existing OCA module functionality
- Introduce hidden runtime side effects outside governed entrypoints

## What Must NOT Be Baked Into the Image

- Secrets (passwords, API keys, tokens)
- Production hostnames or per-environment URLs
- Per-environment database credentials
- Mutable customer-specific configuration
- Filestore data
- Tenant-specific customization
- Ad hoc one-off patches without contract documentation

## What Is Injected at Deploy Time

- Environment variables for database connection
- `ODOO_ADMIN_PASSWORD` and other runtime secrets
- Per-environment config overrides (via volume mount or env vars)
- TLS certificates and domain routing (handled by reverse proxy)

## Non-Canonical Image Sources

The following are explicitly **not** the canonical production runtime:

- Websoft9 or other marketplace VM images
- Third-party packaged Odoo distributions
- `edge-standard` or other generic image names from prior conventions
- Direct `odoo:19` without the IPAI build layers

These may be used for benchmarking or comparison only. They must not define addon path order, module policy, release provenance, deployment expectations, or database naming for the production platform.

## Runtime Build Ownership

The runtime image is owned by this repository and must be built from this repo's contracts. The build pipeline is:

1. **Build**: `docker build -f docker/Dockerfile.unified .` (or CI equivalent)
2. **Tag**: Commit SHA + timestamp + channel tags
3. **Scan**: Trivy/Grype vulnerability scan
4. **Sign**: Cosign supply chain attestation
5. **Push**: Dual-registry push (GHCR + DOCR)
6. **Deploy**: Compose/Container Apps update with health check gate

## CI Workflows

| Workflow | Purpose |
|----------|---------|
| `build-unified-image.yml` | Matrix build (standard + parity), smoke test, SBOM, attestation |
| `docker-build-odoo.yml` | OIDC-authenticated build with Trivy scan and Cosign signing |
| `cd-docr-deploy.yml` | Dual-registry push, SSH deploy to production, release creation |

## References

- `docker/Dockerfile.unified` — canonical Dockerfile
- `docker/compose/prod.yml` — production compose
- `docker/compose/stage.yml` — staging compose
- `config/prod/odoo.conf` — production Odoo config
- `config/stage/odoo.conf` — staging Odoo config
- `docs/architecture/ADDONS_STRUCTURE_BOUNDARY.md` — addon placement rules
- `spec/odoo-erp-saas/prd.md` — ERP SaaS product requirements
