---
name: odoo-ci-optimization
description: Elite Odoo CI/CD and testing optimization patterns based on Odoo Experience 2025. Use for reducing test boot times, parallelizing execution, and using minimal Docker images.
license: AGPL-3
metadata:
  author: InsightPulseAI
  version: "1.0.0"
---

# Odoo CI/CD Optimization

Strategies for high-speed testing and efficient resource utilization in Odoo environments.

## 1. Minimal Odoo Image for Testing

- **Objective**: Reduce boot time from 20s+ to < 6s.
- **Pattern**:
  - Use a base image without unnecessary system dependencies (e.g., nodejs, large fonts).
  - Pre-install core Python dependencies in the Docker layer.
  - Skip full Odoo installation; only copy the necessary source code.
  - Use a pre-warmed PostgreSQL instance or an in-memory database if suitable.

## 2. Testcontainers Pattern

- **Objective**: Isolated, reproducible environments for every test suite.
- **Pattern**:
  - Use the `testcontainers` Python library to spin up disposable Postgres containers on-demand.
  - Parallelize test execution across multiple containers.
  - Ensure each container is completely destroyed after the test run to avoid state leakage.

## 3. Parallel Execution

- **Objective**: Drastically reduce CI pipeline duration.
- **Pattern**:
  - Shard unit tests by module or tag.
  - Use `pytest-xdist` or custom orchestration to run multiple Odoo instances concurrently.
  - Aggregate coverage and results at the end of the pipeline.

## 4. CI Gating Policies

- **Parity Gate**: Enforce 100% Tier-0 parity before allowing merges.
- **Determinism**: Mark tests as "flaky" or "deterministic". CI must fail on any deterministic failure.

## Implementation Checklist

- [ ] Is the Odoo image optimized for size (Alpine/Slim base)?
- [ ] Are Postgres containers managed via Testcontainers or similar lifecycle tools?
- [ ] Is parallelization enabled for the test runner?
- [ ] Are boot times monitored and compared against the 6s benchmark?
