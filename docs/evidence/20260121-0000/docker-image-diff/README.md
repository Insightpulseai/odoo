# Docker Image Diff Evidence

**Scope:** Docker Image Comparison Tooling
**Date:** 2026-01-21
**Status:** Tooling Shipped (awaiting runtime execution)

## What Was Shipped

### 1. Image Diff Script
- **Path:** `scripts/ci/docker-image-diff.sh`
- **Purpose:** Compare two Docker images at multiple levels:
  - Layer history
  - Filesystem (addons, config, python packages)
  - Runtime (pip packages, odoo version, env vars)

### 2. CI Workflow
- **Path:** `.github/workflows/image-diff.yml`
- **Triggers:**
  - Manual dispatch with custom image inputs
  - Auto-triggered after successful `build-unified-image` workflow
- **Outputs:**
  - Markdown diff report
  - JSON summary for automation
  - Optional PR comment

## Usage

### Manual Execution
```bash
# Compare production vs edge
./scripts/ci/docker-image-diff.sh \
  ghcr.io/jgtolentino/odoo-ce:latest \
  ghcr.io/jgtolentino/odoo-ce:edge-standard \
  /tmp/diff-output

# Compare specific versions
./scripts/ci/docker-image-diff.sh \
  ghcr.io/jgtolentino/odoo-ce:prod-20260121-2317 \
  ghcr.io/jgtolentino/odoo-ce:custom-target \
  /tmp/diff-output
```

### CI Workflow
```bash
# Trigger via GitHub CLI
gh workflow run image-diff.yml \
  -f live_image="ghcr.io/jgtolentino/odoo-ce:latest" \
  -f target_image="ghcr.io/jgtolentino/odoo-ce:edge-standard"
```

## Evidence Placeholders

When the script runs in an environment with Docker access, the following files will be generated:

```
<output_dir>/
├── history/
│   ├── live.history.txt
│   ├── target.history.txt
│   └── history.diff
├── runtime/
│   ├── live.pip.txt
│   ├── target.pip.txt
│   ├── pip.diff
│   ├── live.odoo-version.txt
│   ├── target.odoo-version.txt
│   ├── odoo-version.diff
│   ├── live.env.txt
│   ├── target.env.txt
│   └── env.diff
├── filesystem/
│   ├── _mnt_extra-addons.diff
│   ├── _etc_odoo.diff
│   ├── odoo.conf.diff
│   └── ...
└── summary/
    ├── DIFF_REPORT.md
    ├── diff_summary.json
    ├── live.id.txt
    ├── target.id.txt
    └── size.txt
```

## Verification Commands

After running the diff, verify the target image:

```bash
# Smoke test
docker run --rm <target_image> odoo --version

# DB connection test
docker run --rm \
  -e DB_HOST="$DB_HOST" \
  -e DB_PORT="$DB_PORT" \
  -e DB_USER="$DB_USER" \
  -e DB_PASSWORD="$DB_PASSWORD" \
  <target_image> \
  odoo -d $ODOO_DB --log-level=info --stop-after-init
```

## Deployment Flow

1. Run image diff
2. Review `DIFF_REPORT.md`
3. Verify no unexpected changes
4. Deploy target as new production:
   ```bash
   docker tag <target_image> ghcr.io/jgtolentino/odoo-ce:prod
   docker push ghcr.io/jgtolentino/odoo-ce:prod
   ```

## Rollback

```bash
# Retag previous image as prod
docker tag <previous_live_image> ghcr.io/jgtolentino/odoo-ce:prod
docker push ghcr.io/jgtolentino/odoo-ce:prod
```
