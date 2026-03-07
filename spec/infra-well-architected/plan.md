# Plan: Infrastructure Well-Architected Assessment System

## Overview

Implement `check_infra_waf.py` to audit the DigitalOcean/Docker/Cloudflare stack against the five Well-Architected pillars defined in the PRD.

## Phase 1 — Core Library (`lib.py`)

- Define pillar weights: Reliability (0.25), Security (0.25), Cost (0.20), Ops Excellence (0.15), Performance (0.15).
- Implement YAML/HCL file parsers for `docker-compose.prod.yaml` and `*.tf` files.
- Build a scoring engine that normalizes check results into a 0–1 scale per pillar.

## Phase 2 — Check Implementations

- Reliability checks: container restart policies, healthcheck definitions, backup volume mounts.
- Security checks: secret references (no hardcoded values), TLS config, firewall rule presence.
- Cost checks: droplet size vs. resource usage heuristics, Cloudflare caching headers.
- Ops Excellence checks: logging driver config, image tag pinning (no `latest`), state locking in Terraform.
- Performance checks: named volume configuration, CDN/cache rule presence.

## Phase 3 — Reporting

- Console summary with per-pillar scores and overall weighted score.
- JSON evidence output saved to `web/docs/evidence/` with timestamp.
- Exit code: 0 if overall score >= 0.7, 1 otherwise.

## Dependencies

- `pyyaml` for Docker Compose parsing.
- `python-dotenv` for environment variable handling.
- Standard library `json`, `pathlib`, `re` for Terraform HCL parsing.

## Risks

- HCL parsing without a dedicated library may miss edge cases; mitigate with regex + known patterns.
- API mode (doctl) deferred to future phase to reduce initial scope.
