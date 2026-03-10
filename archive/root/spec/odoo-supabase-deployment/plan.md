# Plan: Odoo + Supabase Monorepo Production Deployment Research

## Overview

Conduct structured research into production deployment best practices for Odoo CE 19 on DigitalOcean with Supabase, benchmarked against mature OCA integrator patterns.

## Phase 1 — Research Collection

- Survey deployment patterns from Camptocamp, Acsone, and Tecnativa public repos and blog posts.
- Document Docker Compose patterns: multi-stage builds, health checks, resource limits, logging.
- Catalog PostgreSQL tuning parameters for Odoo workloads (shared_buffers, work_mem, effective_cache_size).
- Review OWASP Top 10 and CIS Docker Benchmark applicability to the current stack.

## Phase 2 — Gap Analysis

- Compare current `docker-compose.prod.yaml` against collected best practices.
- Identify missing security hardening (network segmentation, read-only filesystems, capability drops).
- Assess backup strategy: current vs. recommended (WAL archiving, point-in-time recovery).
- Evaluate monitoring gaps: metrics collection, alerting, log aggregation.

## Phase 3 — Cost Model

- Inventory current DigitalOcean resources (droplets, volumes, snapshots, bandwidth).
- Build monthly cost model with line items.
- Identify optimization opportunities (reserved instances, right-sizing, Cloudflare caching offload).

## Phase 4 — Recommendations Document

- Produce prioritized recommendation list: P0 (security), P1 (reliability), P2 (cost), P3 (performance).
- Each recommendation includes: current state, target state, config change or script, estimated effort.
- Output as `docs/ops/DEPLOYMENT_HARDENING.md`.

## Deliverables

- Research notes in `spec/odoo-supabase-deployment/research.md`.
- Gap analysis matrix.
- Cost model spreadsheet (CSV or markdown table).
- Prioritized recommendations document.
