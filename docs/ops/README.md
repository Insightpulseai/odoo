# Ops Control Room Documentation

**Complete infrastructure for Ops Control Room + Knowledge Graph + Odoo Rationalization**

---

## Overview

This directory contains documentation for three major work streams:

1. **Ops Control Room** - Workflow orchestration with Supabase + workers
2. **Knowledge Graph** - Organizational knowledge management
3. **Odoo Rationalization** - Baseline-first module cleanup

All work is tracked in the **Execution Board** (org-level GitHub Project).

---

## Quick Navigation

### 📋 [Quick Start Guide](./QUICK_START.md)
**Single-command bootstrap for GitHub Project + Issues**

```bash
./scripts/bootstrap_execution_board.sh
```

Creates org-level project with 9 tracking issues covering all deliverables.

### 📊 [Execution Board](./EXECUTION_BOARD.md)
**Complete GitHub Projects setup guide**

- Project structure and custom fields
- 9 tracking issues (Infrastructure, Ops, Spec Kit, Odoo)
- Labels, milestones, and views
- Automation and best practices

### ✅ [Execution Checklist](../rationalization/EXECUTION_CHECKLIST.md)
**Step-by-step execution guide for Odoo rationalization**

- Pre-execution requirements (backups, health checks)
- 7-phase workflow (baseline → validation → backlog)
- Module retirement procedures (Priority 1-6)
- Health checks and rollback procedures

---

## Directory Structure

```
docs/ops/
├── README.md                    # This file (navigation)
├── QUICK_START.md               # One-command bootstrap
└── EXECUTION_BOARD.md           # Complete project setup

docs/rationalization/
├── README.md                    # Rationalization system docs
└── EXECUTION_CHECKLIST.md       # Execution procedures

docs/email/
└── Mailgun_DNS.md              # DNS and email configuration

docs/knowledge/
└── graph_seed.json             # Knowledge Graph seed data
```

---

## System Architecture

### Ops Control Room

```
┌─────────────────────────────────────────────────────────────────┐
│                      Ops Control Room                            │
├─────────────────────────────────────────────────────────────────┤
│  Control Plane (Supabase)                                       │
│  ├── ops.sessions                                               │
│  ├── ops.run_templates (timeout, step_dsl, enabled)             │
│  ├── ops.runs (status, worker_id, params, artifacts)            │
│  ├── ops.run_events (kind, payload, timestamp)                  │
│  └── ops.artifacts (storage_key, content_type)                  │
│                                                                   │
│  Workers (DigitalOcean Droplet / pm2)                           │
│  ├── Claim loop (SKIP LOCKED prevents double-run)              │
│  ├── Execute step_dsl with timeout                              │
│  ├── Heartbeat every 30s                                        │
│  └── Upload artifacts to Supabase Storage                       │
│                                                                   │
│  UI (Vercel)                                                     │
│  ├── Runboard dashboard (realtime <2s updates)                  │
│  ├── Event timeline per run                                     │
│  └── Artifact download links                                    │
└─────────────────────────────────────────────────────────────────┘
```

### Knowledge Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                      Knowledge Graph                             │
├─────────────────────────────────────────────────────────────────┤
│  Schema (Supabase)                                              │
│  ├── kg.nodes (id, kind, name, ref, props)                      │
│  │   └── Kinds: Repo, SpecBundle, Module, App, Workflow, Script │
│  ├── kg.edges (src, rel, dst, props)                            │
│  │   └── Rels: HAS_SPEC, DEPLOYS, RUNS_ON, DEPENDS_ON          │
│  └── kg.sources (hash, fetched_at, url, content)                │
│                                                                   │
│  Ingestion (Python scripts)                                      │
│  ├── Local filesystem scan (spec/, addons/, apps/)              │
│  ├── GitHub GraphQL (repos, issues, PRs, workflows)             │
│  └── Supabase metadata (schemas, functions, policies)           │
│                                                                   │
│  Outputs                                                         │
│  ├── docs/INDEX.md (318 entries)                                │
│  └── docs/knowledge/graph_seed.json (318 nodes, 317 edges)      │
└─────────────────────────────────────────────────────────────────┘
```

### Odoo Rationalization

```
┌─────────────────────────────────────────────────────────────────┐
│                  Odoo Module Rationalization                     │
├─────────────────────────────────────────────────────────────────┤
│  Policy: Config → OCA → Delta (ipai_*)                          │
│                                                                   │
│  Phase 1: Baseline Installation                                 │
│  ├── Install Odoo CE core (base, account, sale, etc.)           │
│  └── Install OCA Must-Have (financial_report, tier_validation)  │
│                                                                   │
│  Phase 2: OCA Validation Schema                                 │
│  ├── oca.module_index (OCA catalog with keywords)               │
│  ├── oca.custom_module_signatures (ipai_* features)             │
│  ├── oca.validation_results (match confidence)                  │
│  └── oca.module_footprints (UI vs business logic)               │
│                                                                   │
│  Phase 3: Feature Signature Generation                          │
│  ├── Extract from Odoo database (models, views, menus)          │
│  ├── Generate keywords from text fields                         │
│  └── Compute Jaccard similarity vs OCA                          │
│                                                                   │
│  Phase 4: Retire Backlog Generation                             │
│  ├── Priority 1: RETIRE (UI-only + OCA match ≥0.7)              │
│  ├── Priority 2: REDUCE (UI-only + OCA match ≥0.4)              │
│  └── Priority 3-6: REDUCE/KEEP based on business logic          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Scripts

### Bootstrap & Setup

| Script | Purpose |
|--------|---------|
| `scripts/bootstrap_execution_board.sh` | Create org project + issues |
| `scripts/install_baseline.sh` | Install Odoo CE + OCA Must-Have |
| `scripts/generate_repo_index.py` | Generate docs/INDEX.md + graph_seed.json |
| `scripts/ingest_knowledge_graph.py` | Populate kg.nodes/edges from sources |

### Rationalization

| Script | Purpose |
|--------|---------|
| `scripts/execute_rationalization.sh` | Complete 7-phase workflow |
| `scripts/generate_module_signatures.py` | Extract feature signatures from Odoo DB |
| `scripts/odoo_rationalization.sh` | Footprint analysis (deprecated - use execute_rationalization.sh) |

### Validation

| Script | Purpose |
|--------|---------|
| `scripts/validate_spec_kit.py` | Validate spec bundle structure |
| `scripts/check_undocumented_specs.py` | Find undocumented spec bundles |
| `scripts/generate_spec_report.py` | Generate spec validation report |

### Verification

| Script | Purpose |
|--------|---------|
| `scripts/repo_health.sh` | Check repository structure |
| `scripts/spec_validate.sh` | Validate spec completeness |
| `scripts/ci_local.sh` | Run local CI checks |

---

## Database Migrations

### Supabase Migrations

| Migration | Schema | Tables |
|-----------|--------|--------|
| `20260108_ops_schema.sql` | ops | sessions, run_templates, runs, run_events, artifacts |
| `20260108_kg_schema.sql` | kg | nodes, edges, sources |
| `20260108_oca_validation.sql` | oca | module_index, custom_module_signatures, validation_results, module_footprints |

### Application Order

```bash
# 1. Apply Supabase migrations
psql "$POSTGRES_URL" -f db/migrations/20260108_ops_schema.sql
psql "$POSTGRES_URL" -f db/migrations/20260108_kg_schema.sql

# 2. Apply Odoo migrations (on droplet)
ssh root@178.128.112.214 "docker exec odoo-erp-prod bash -c \"\
  psql -h db -U postgres -d odoo -f /tmp/oca_validation.sql\
\""
```

---

## Execution Phases

### Phase 1: Infrastructure Foundation (P0)

**Duration**: ~1 hour

1. Apply Supabase schemas (ops, kg)
2. Update DNS records (all subdomains → 178.128.112.214)
3. Deploy nginx configuration
4. Verify SSL certificates
5. Test service accessibility

**Verification**:
```bash
# DNS
dig +short erp.insightpulseai.net  # Should return 178.128.112.214

# Services
curl -I https://erp.insightpulseai.net    # Should return 200
curl -I https://n8n.insightpulseai.net    # Should return 200
curl -I https://superset.insightpulseai.net  # Should return 200
```

### Phase 2: Odoo Rationalization (P0)

**Duration**: ~2 hours (automated)

1. Remove invalid module name (ipai_month_end_closing.backup)
2. Install baseline (CE + OCA Must-Have)
3. Apply OCA validation schema
4. Generate feature signatures
5. Run OCA validation
6. Generate footprint analysis
7. Generate retire backlog

**Command**:
```bash
./scripts/execute_rationalization.sh
```

**Outputs**:
- `docs/rationalization/validation_results.txt`
- `docs/rationalization/footprint_analysis.txt`
- `docs/rationalization/retire_backlog.txt`
- `docs/rationalization/FINAL_RATIONALIZATION_REPORT.md`

### Phase 3: Ops Control Room (P1)

**Duration**: ~3-4 hours

1. Ingest Knowledge Graph (repo scan + GitHub API)
2. Deploy worker implementation
3. Deploy UI Runboard
4. Test run lifecycle (pending → processing → completed)
5. Verify realtime updates

**Verification**:
```bash
# Knowledge Graph
psql "$POSTGRES_URL" -c "SELECT COUNT(*) FROM kg.nodes;"  # Should return 318

# Ops runs
psql "$POSTGRES_URL" -c "SELECT * FROM ops.runs ORDER BY created_at DESC LIMIT 10;"
```

### Phase 4: Continuous Integration (P1)

**Duration**: ~1 hour

1. Enable Spec Kit CI enforcement
2. Schedule KG ingestion (GitHub Actions)
3. Schedule rationalization reports
4. Verify CI workflows

**Workflows**:
- `.github/workflows/spec-kit-enforce.yml` (on PR)
- `.github/workflows/kg-ingestion.yml` (every 6 hours)
- `.github/workflows/rationalization-report.yml` (weekly)

---

## Key Deliverables

### Infrastructure

- ✅ DNS consolidation (8 subdomains → single droplet)
- ✅ nginx host-based routing with SSL
- ✅ Supabase ops schema (5 tables + 8 functions)
- ✅ Supabase kg schema (3 tables + 4 graph functions)

### Knowledge Graph

- ✅ Repository index (318 nodes, 317 edges)
- ✅ docs/INDEX.md (comprehensive catalog)
- ✅ docs/knowledge/graph_seed.json (version-controlled graph)
- ✅ Ingestion pipeline (change detection via hashing)

### Odoo Rationalization

- ✅ Baseline installer (CE + OCA Must-Have)
- ✅ OCA validation engine (Jaccard similarity)
- ✅ Feature signature generator (extract from Odoo DB)
- ✅ Complete workflow script (7 phases)
- ✅ Comprehensive documentation (execution checklist)

### Automation

- ✅ GitHub Project bootstrap script
- ✅ Spec Kit validation CI
- ✅ Repository health checks
- ✅ Automated documentation generation

---

## Status Summary

| Work Stream | Status | Progress |
|-------------|--------|----------|
| **Infrastructure** | ✅ Complete | DNS + nginx + SSL configured |
| **Supabase Schemas** | ✅ Complete | Migrations written |
| **Knowledge Graph** | ✅ Complete | Scripts ready |
| **Odoo Rationalization** | ✅ Complete | Full workflow ready |
| **Spec Kit CI** | ✅ Complete | Workflows exist |
| **Ops Workers** | 🟡 In Progress | Implementation pending |
| **UI Runboard** | 🟡 In Progress | Implementation pending |

**Overall Progress**: 7/9 issues complete (78%)

---

## Next Actions

### Immediate (Next Session)

1. Run bootstrap script: `./scripts/bootstrap_execution_board.sh`
2. Open project in browser and configure views
3. Review and prioritize issues
4. Execute Phase 1 (Infrastructure foundation)

### Short-term (This Week)

5. Execute Phase 2 (Odoo rationalization workflow)
6. Review retire backlog and get business approval
7. Begin Priority 1 module retirements

### Medium-term (Next 2 Weeks)

8. Complete Ops worker implementation
9. Deploy UI Runboard
10. Enable CI automation workflows

---

## Support & References

### Documentation

- [Quick Start](./QUICK_START.md) - One-command bootstrap
- [Execution Board](./EXECUTION_BOARD.md) - Complete project setup
- [Execution Checklist](../rationalization/EXECUTION_CHECKLIST.md) - Step-by-step procedures
- [Rationalization README](../rationalization/README.md) - System architecture

### External Resources

- **GitHub Projects**: https://docs.github.com/en/issues/planning-and-tracking-with-projects
- **Supabase Docs**: https://supabase.com/docs
- **OCA Community**: https://odoo-community.org
- **Odoo CE 18**: https://www.odoo.com/documentation/18.0/

### Contact

**Project Owner**: Jake Tolentino
**Repository**: https://github.com/jgtolentino/odoo-ce
**Organization**: https://github.com/Insightpulseai-net

---

**Last Updated**: 2026-01-08
**Status**: Ready for execution
