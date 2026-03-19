# DigitalOcean Cost Optimization Guide

## Overview

This document describes the cost optimization strategy for InsightPulse AI's DigitalOcean infrastructure. The approach follows SSOT (Single Source of Truth) principles: all configuration lives in Git, UIs are views, secrets in secret stores.

## Infrastructure Inventory

| Component | Location | Size | Purpose |
|-----------|----------|------|---------|
| `odoo-erp-prod` | SGP1 (159.223.75.148) | 4GB RAM / 80GB Disk | Odoo ERP, Mattermost, n8n, auth |
| `ocr-service-droplet` | SGP1 (188.166.237.231) | 8GB RAM / 80GB Disk | OCR Service, Agent Service, Affine |
| `plane-ce-prod` | SFO2 (167.99.104.239) | 2GB RAM / 90GB Disk | Plane CE project management |
| `odoo-db-sgp1` | Managed Postgres | - | Odoo database |
| Supabase | External | - | App data, Edge Functions |

## Architecture Decision: Keep Separate

### Why NOT Merge Droplets

After analysis, we recommend **keeping Odoo and Plane on separate droplets**:

1. **Failure Isolation**: One droplet down = one service down, not both
2. **Resource Contention**: Odoo memory spikes won't starve Plane
3. **Independent Scaling**: Can resize each independently
4. **Latency Sensitivity**: Odoo is stateful and latency-sensitive

### Where Real Savings Come From

The biggest cost savings are NOT from merging droplets, but from:

1. **Disk Cleanup** - Docker images, logs, journals filling disk
2. **VPC Sprawl** - Empty PR VPCs accumulating
3. **Snapshot Drift** - No retention policy, snapshots growing
4. **OCR Artifacts** - Blobs stored on droplet disk instead of Spaces

## Target Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COST-OPTIMIZED END STATE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ALWAYS-ON (Prod - SGP1)                                            │
│  ══════════════════════                                              │
│  odoo-erp-prod (4GB) ─── Managed Postgres (odoo-db-sgp1)            │
│  plane-ce-prod (2GB) ─── Supabase Postgres (plane_workspace)        │
│                                                                      │
│  BURST/BATCH (Ephemeral)                                            │
│  ═══════════════════════                                             │
│  OCR/ETL workers ─── DO Spaces (artifacts) ─── Queue-based jobs     │
│                                                                      │
│  STORAGE (Spaces)                                                    │
│  ════════════════                                                    │
│  ├── ocr-artifacts/     ← OCR outputs (NOT droplet disk)            │
│  ├── backups/           ← Encrypted DB dumps                        │
│  └── logs-archive/      ← Rotated logs                              │
│                                                                      │
│  NETWORKING                                                          │
│  ══════════════                                                      │
│  One VPC per region (default-sgp1) ← NO pr-* sprawl                 │
│                                                                      │
│  BACKUPS                                                             │
│  ═════════                                                           │
│  2-3 "gold" snapshots per droplet (tagged)                          │
│  Managed DB PITR for Postgres                                       │
│  Delete snapshots older than 60 days                                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Optimization Scripts

All scripts are located in `scripts/infra/` and support `--dry-run` mode.

### 1. Disk Cleanup (`do_disk_cleanup.sh`)

Reclaims disk space on droplets:

```bash
# Preview changes
./scripts/infra/do_disk_cleanup.sh --dry-run

# Run cleanup
./scripts/infra/do_disk_cleanup.sh

# Remote execution
ssh root@188.166.237.231 'bash -s' < ./scripts/infra/do_disk_cleanup.sh
```

**What it cleans:**
- Docker images, containers, volumes (unused)
- Journal logs older than 7 days
- Log files larger than 100MB
- APT cache
- Temp files older than 7 days

### 2. VPC Cleanup (`do_prune_empty_vpcs.sh`)

Removes empty VPCs (especially PR-generated ones):

```bash
# Preview what would be deleted
./scripts/infra/do_prune_empty_vpcs.sh --dry-run

# Delete empty pr-* VPCs
./scripts/infra/do_prune_empty_vpcs.sh --force

# Delete ALL empty VPCs (careful!)
./scripts/infra/do_prune_empty_vpcs.sh --all-empty --force
```

**Safety:**
- Only deletes VPCs with 0 attached resources
- Requires `--force` for actual deletion
- Default pattern: `^pr-` (PR-generated VPCs)

### 3. Snapshot Retention (`do_prune_snapshots.sh`)

Enforces snapshot retention policy:

```bash
# List gold snapshots (protected)
./scripts/infra/do_prune_snapshots.sh --list-gold

# List deletable snapshots
./scripts/infra/do_prune_snapshots.sh --list-deletable

# Preview cleanup
./scripts/infra/do_prune_snapshots.sh --dry-run

# Delete snapshots older than 60 days
./scripts/infra/do_prune_snapshots.sh --retention-days 60 --force
```

**Policy:**
- **Protected (Gold)**: Names containing `baseline`, `production-complete`, `post-migration`, `gold`, `critical`, `release`
- **Deletable**: All other snapshots older than retention period (default: 60 days)

### 4. Resource Monitoring (`do_resource_check.sh`)

Comprehensive resource report with alerts:

```bash
# Full report
./scripts/infra/do_resource_check.sh

# Quick summary
./scripts/infra/do_resource_check.sh --summary

# Include live disk checks via SSH
./scripts/infra/do_resource_check.sh --check-remote

# Markdown output for docs
./scripts/infra/do_resource_check.sh --format markdown
```

**Checks:**
- Droplet count and status
- VPC sprawl (pr-* count)
- Snapshot count and size
- Disk usage (with `--check-remote`)
- Docker usage (with `--check-remote`)

## OCR Artifacts Migration

OCR outputs should be stored in DO Spaces, not droplet disk.

**Configuration:** `config/spaces/ocr-artifacts.yaml`

### Setup Steps

1. Create Spaces bucket:
   ```bash
   doctl spaces create ipai-ocr-artifacts --region sgp1
   ```

2. Configure OCR service to write to Spaces:
   ```bash
   export SPACES_ENDPOINT=https://sgp1.digitaloceanspaces.com
   export SPACES_BUCKET=ipai-ocr-artifacts
   export SPACES_ACCESS_KEY=<from-secret-store>
   export SPACES_SECRET_KEY=<from-secret-store>
   ```

3. Migrate existing artifacts:
   ```bash
   s3cmd sync /opt/ocr-artifacts/ s3://ipai-ocr-artifacts/raw/ \
     --host=sgp1.digitaloceanspaces.com \
     --host-bucket="%(bucket)s.sgp1.digitaloceanspaces.com"
   ```

### Cost Comparison

| Storage | Cost/GB/month | Notes |
|---------|---------------|-------|
| Droplet Disk | ~$0.10 | Part of droplet cost |
| DO Spaces | $0.02 | 80% cheaper |

For 50GB of OCR artifacts: **$4/month saved**.

## Verification Commands

### After Disk Cleanup
```bash
ssh root@188.166.237.231 "df -h && docker system df"
# Expect: Disk usage < 70%
```

### After VPC Prune
```bash
doctl vpcs list --format Name,Region | grep -c "^pr-"
# Expect: 0 (no pr-* VPCs remaining)
```

### After Snapshot Prune
```bash
doctl compute image list-user --no-header | wc -l
# Expect: Reduced count (only gold snapshots)
```

### Health Check
```bash
curl -sI https://erp.insightpulseai.net/web/login | head -n 1
curl -sI http://167.99.104.239/ | head -n 1
# Expect: HTTP 200 for both
```

## Scheduled Maintenance

| Task | Frequency | Script |
|------|-----------|--------|
| Disk cleanup | Weekly | `do_disk_cleanup.sh` |
| VPC prune | Weekly | `do_prune_empty_vpcs.sh` |
| Snapshot prune | Monthly | `do_prune_snapshots.sh` |
| Resource report | Daily | `do_resource_check.sh` |

### Cron Example

```bash
# Add to root crontab on management host
0 2 * * 0 /path/to/scripts/infra/do_disk_cleanup.sh >> /var/log/do-cleanup.log 2>&1
0 3 * * 0 /path/to/scripts/infra/do_prune_empty_vpcs.sh --force >> /var/log/do-cleanup.log 2>&1
0 4 1 * * /path/to/scripts/infra/do_prune_snapshots.sh --force >> /var/log/do-cleanup.log 2>&1
0 6 * * * /path/to/scripts/infra/do_resource_check.sh --summary >> /var/log/do-resource.log 2>&1
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Accidental snapshot deletion | Only delete non-"gold" tagged snapshots |
| VPC deletion breaks service | Only delete VPCs with 0 attached resources |
| Disk cleanup removes needed data | Docker prune is safe; only removes unused |
| Spaces migration breaks OCR | Test with new artifacts first, keep old on disk temporarily |

## SSOT Principles

1. **Git is Truth**: All configuration in Git, not dashboards
2. **Scripts are Idempotent**: Safe to run multiple times
3. **Dry Run First**: Always preview before applying
4. **Evidence Required**: Verify after each change
5. **Secrets Separate**: Never in Git, always in secret stores

## Related Files

| File | Purpose |
|------|---------|
| `scripts/infra/do_disk_cleanup.sh` | Disk cleanup script |
| `scripts/infra/do_prune_empty_vpcs.sh` | VPC cleanup script |
| `scripts/infra/do_prune_snapshots.sh` | Snapshot retention script |
| `scripts/infra/do_resource_check.sh` | Resource monitoring script |
| `config/spaces/ocr-artifacts.yaml` | Spaces bucket configuration |
| `CLAUDE.md` | Infrastructure inventory |
