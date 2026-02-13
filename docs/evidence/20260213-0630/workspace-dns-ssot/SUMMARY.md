# Workspace Naming & DNS SSOT Implementation

**Date**: 2026-02-13 06:30 UTC
**Scope**: Phase 1 (Workspace Standardization) + Phase 4 (Infrastructure SSOT)

---

## Changes Implemented

### 1. Workspace Naming Standardization

**Objective**: Establish "ipai" as canonical workspace identifier.

**Changes**:
- `docker-compose.yml`: Renamed project from "odoo" to "ipai"
- Network: `odoo-network` → `ipai-network`
- Volumes: `odoo-pgdata` → `ipai-pgdata`, `odoo-redisdata` → `ipai-redisdata`, etc.
- DevContainer: `InsightPulseAI-Odoo-DevContainer` → `ipai-devcontainer`

**Verification**:
```bash
# Docker Compose project name
docker compose ps  # Shows project: ipai

# Network name
docker network ls | grep ipai  # Shows ipai-network

# Volume names
docker volume ls | grep ipai  # Shows ipai-pgdata, ipai-redisdata, ipai-web-data

# DevContainer name
cat .devcontainer/devcontainer.json | jq '.name'  # Returns "ipai-devcontainer"
```

### 2. Infrastructure SSOT Consolidation

**Objective**: Create single authoritative subdomain registry with sync enforcement.

**Created**:
1. `infra/dns/subdomain-registry.yaml` — SSOT for all DNS configuration
2. `scripts/generate-dns-artifacts.sh` — Generator producing Terraform + JSON
3. `.github/workflows/dns-sync-check.yml` — CI enforcement preventing manual drift

**Generated Artifacts**:
1. `infra/cloudflare/envs/prod/subdomains.auto.tfvars` — Terraform input
2. `docs/architecture/runtime_identifiers.json` — Runtime reference
3. `infra/dns/dns-validation-spec.json` — CI validation spec

**Documentation**:
- `infra/dns/README.md` — DNS SSOT workflow
- `docs/ai/WORKSPACE_NAMING.md` — Workspace naming convention

**CLAUDE.md Updates**:
- Added DNS SSOT workflow reference
- Added workspace naming convention
- Updated Quick Reference table

---

## Verification Results

### Workspace Naming

✅ Docker Compose project: `ipai`
✅ Network: `ipai-network`
✅ Volumes: `ipai-pgdata`, `ipai-redisdata`, `ipai-web-data`, `ipai-pgadmin-data`
✅ DevContainer: `ipai-devcontainer`

### DNS SSOT

✅ Generator script executable
✅ Terraform variables generated (7 active A records)
✅ Runtime JSON generated (8 active services + 1 deprecated)
✅ Validation spec generated
✅ CI workflow created

**Subdomain Count**:
- YAML source: 9 total (8 active + 1 planned)
- Generated Terraform: 7 A records
- Generated JSON: 8 services
- Deprecated: 1 (affine)

---

## Files Modified

1. `docker-compose.yml` — Project name, network, volumes
2. `.devcontainer/devcontainer.json` — Container name
3. `CLAUDE.md` — DNS SSOT section, workspace naming

## Files Created

1. `infra/dns/subdomain-registry.yaml` — DNS SSOT
2. `infra/dns/README.md` — DNS workflow docs
3. `scripts/generate-dns-artifacts.sh` — Generator
4. `.github/workflows/dns-sync-check.yml` — CI enforcement
5. `docs/ai/WORKSPACE_NAMING.md` — Workspace convention

## Files Generated

1. `infra/cloudflare/envs/prod/subdomains.auto.tfvars` — Terraform input
2. `docs/architecture/runtime_identifiers.json` — Runtime reference
3. `infra/dns/dns-validation-spec.json` — Validation spec

---

## Next Steps

### Phase 2: Repo Naming Migration
- Rename repo: `odoo` → `app-odoo`
- Update all references in CI, docs, scripts
- Create repo naming documentation

### Phase 3: Governance Replication
- Create `.github` org repo
- Reusable workflows for governance enforcement
- CLAUDE.md template
- WAF docs template

### Phase 5: Well-Architected Alignment
- Add GitHub topics (waf-*, app-repo, etc.)
- Create WAF docs in all repos
- Org-wide WAF dashboard

---

## Evidence

All changes committed to repo with evidence in:
`docs/evidence/20260213-0630/workspace-dns-ssot/`
