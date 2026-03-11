# Tasks: Infrastructure Well-Architected Assessment System

## Task 1: Scaffold project structure
- Create `scripts/infra/check_infra_waf.py` and `scripts/infra/lib.py`.
- Add pillar weight constants and data classes for check results.
- Status: TODO

## Task 2: Implement YAML parser for Docker Compose
- Parse `docker-compose.prod.yaml` using `pyyaml`.
- Extract service definitions, restart policies, healthchecks, volumes, environment variables.
- Status: TODO

## Task 3: Implement Terraform file scanner
- Scan `infra/` for `*.tf` files.
- Extract resource definitions, firewall rules, droplet sizes, state backend config.
- Status: TODO

## Task 4: Implement reliability checks
- Verify restart policy is `unless-stopped` or `always` for each service.
- Verify healthcheck block exists for critical services.
- Check for backup-related volume mounts or snapshot references.
- Status: TODO

## Task 5: Implement security checks
- Detect hardcoded secrets (env values that look like passwords/tokens).
- Verify TLS/SSL references in Cloudflare or nginx config.
- Check firewall rule definitions in Terraform.
- Status: TODO

## Task 6: Implement cost, ops, and performance checks
- Cost: flag oversized droplet specs, check Cloudflare cache settings.
- Ops: verify image tags are pinned (not `latest`), logging driver set, state locking enabled.
- Performance: verify named volumes, CDN cache rules present.
- Status: TODO

## Task 7: Build scoring engine and reporter
- Compute per-pillar score (0–1) based on pass/fail/warn results.
- Compute weighted overall score.
- Output console summary and JSON evidence file.
- Status: TODO

## Task 8: Add tests
- Unit tests for each check category with sample YAML/TF fixtures.
- Integration test running full audit against repo fixtures.
- Status: TODO
