# Enterprise Test Integration Strategy

**Last Updated**: 2026-01-27
**Stack**: Vercel Enterprise + Supabase + Odoo CE 18 + Databricks + Fivetran

---

## Test Inventory Summary

**Total Test Assets**: 4,550

- **Python Tests**: 2,188 (pytest, Odoo TransactionCase/HttpCase)
- **JavaScript/TypeScript Tests**: 28 (jest/vitest)
- **Test Configurations**: 2,106 (pyproject.toml, jest.config, .pre-commit-config)
- **CI/CD Workflows**: 133 GitHub Actions
- **Gate/Verification Scripts**: 95 (health checks, audits, parity tests)
- **Odoo Module Manifests**: 2,130 (OCA + IPAI modules)

---

## Testing Architecture

### 1. **Layered Testing Strategy**

```
┌─────────────────────────────────────────────────────────────┐
│                 PRODUCTION MONITORING                        │
│  Finance PPM Health | Odoo Smoke | Stack Verification       │
└─────────────────────────────────────────────────────────────┘
                            ▲
┌─────────────────────────────────────────────────────────────┐
│                    E2E/INTEGRATION GATES                     │
│  Parity Tests (31) | Compose Topology | Module Drift        │
└─────────────────────────────────────────────────────────────┘
                            ▲
┌─────────────────────────────────────────────────────────────┐
│                    PR PREVIEW VALIDATION                     │
│  Vercel Preview | Supabase Branching | Schema Checks        │
└─────────────────────────────────────────────────────────────┘
                            ▲
┌─────────────────────────────────────────────────────────────┐
│                    QUALITY GATES (CI)                        │
│  Lint | TypeCheck | Unit Tests | Security Scans             │
└─────────────────────────────────────────────────────────────┘
```

### 2. **Test Categories**

| Category | Count | Purpose | Automation |
|----------|-------|---------|------------|
| **Unit Tests** | 2,216 | Function/module correctness | CI on every PR |
| **CI Gates** | 133 | Policy enforcement, quality standards | Blocking PR merge |
| **Verification Scripts** | 95 | Deployment validation, health checks | Post-deploy |
| **Parity Tests** | 31 | EE → CE+OCA feature equivalence | Weekly + release |
| **Health Checks** | 6 | Production monitoring | Scheduled (hourly) |
| **Audit Scripts** | 13 | Compliance, security, configuration | On-demand + weekly |

---

## Integration with Enterprise Stack

### Vercel Enterprise Integration

**Current State**: Limited Vercel Sandbox usage
**Recommended**: Implement safe execution of AI-generated code via Vercel Sandbox

#### Proposed CI Workflow Enhancement

```yaml
# .github/workflows/ci-gates.yml
jobs:
  sandbox-smoke:
    runs-on: ubuntu-latest
    needs: [quality]
    if: ${{ secrets.VERCEL_TOKEN != '' }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm i -D @vercel/sandbox ms
      - name: Run Vercel Sandbox smoke
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_TEAM_ID: ${{ secrets.VERCEL_TEAM_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
        run: node scripts/ci/vercel_sandbox_smoke.mjs
```

**Benefits**:
- Safe execution of untrusted code (AI agents, user scripts)
- Ephemeral compute for risky operations
- No need to expose production secrets to sandboxes

---

### Supabase Integration

**Current State**: Extensive integration with migration validation

**Existing Workflows**:
- `supabase-db-pr-check.yml` - Validates migrations before merge
- `supabase-preview-ci.yml` - Tests against preview branches
- `supabase-sql-rls-checks.yml` - Row-level security validation

**Test Coverage**:
```bash
# Migration smoke tests
tests/sql/00_smoke.sql

# Database verification
scripts/db_verify.sh
scripts/verify_supabase_full.sh
scripts/supabase/checks.sh
```

**Enhancement Opportunities**:
1. **Preview Branching**: Enable Supabase preview branches for every PR
2. **Schema Drift Detection**: Automated schema comparison (current vs expected)
3. **RLS Testing**: Comprehensive RLS policy validation with test users

---

### Odoo CE 18 Integration

**Current State**: Comprehensive Odoo-specific testing

**Test Structure**:
- **Module Tests**: 2,188 Python test files (Odoo TransactionCase, HttpCase)
- **Parity Tests**: 31 feature tests validating EE → CE+OCA equivalence
- **CI Gates**: Module drift, OCA compliance, installability checks

**Key Workflows**:
```
odoo-ci-gate.yml          → Module install validation
odoo-module-install-gate.yml → Installability checks
modules-audit-drift.yml    → Detect module changes without tests
ee-parity-gate.yml         → EE feature parity validation
```

**Health Checks**:
```bash
# Production health monitoring
scripts/healthcheck_odoo.sh
scripts/finance_ppm_health_check.sh  # 8/12/144/36/36 validation

# Smoke tests
scripts/ci_smoke_test.sh
scripts/odoo_smoke_close.sh
```

---

### Databricks Integration

**Current State**: Basic CI/CD for Databricks Asset Bundles (DAB)

**Existing Workflows**:
- `databricks-ci.yml` - Validates bundle configuration
- `databricks-dab-ci.yml` - DAB-specific CI checks
- `databricks-deploy-{dev,staging,prod}.yml` - Environment-specific deploys

**Test Coverage**:
```python
# Unit tests
infra/databricks/tests/unit/test_config.py

# Smoke tests
infra/databricks/scripts/smoke.sh
```

**Enhancement Opportunities**:
1. **Data Quality Tests**: dbt expectations, Great Expectations integration
2. **Pipeline Health**: Airflow/Fivetran job success rate monitoring
3. **Schema Drift**: Delta table schema validation against expected definitions

---

## MCP Gateway Integration (Proposed)

**Purpose**: Centralize tool access, reduce secret sprawl, enable safe agent execution

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│          Claude Desktop / VS Code / Agents              │
└─────────────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│              MCP Gateway (Port 8766)                     │
│  - Authentication (Bearer tokens)                       │
│  - Routing (server lifecycle management)                │
│  - Logging (audit trail)                                │
│  - Rate limiting                                         │
└─────────────────────────────────────────────────────────┘
        ▼                                  ▼
┌────────────────────┐        ┌──────────────────────────┐
│  External MCPs     │        │    Custom MCPs           │
│  - Supabase        │        │    - Odoo ERP            │
│  - GitHub          │        │    - DigitalOcean        │
│  - Figma           │        │    - Superset            │
└────────────────────┘        └──────────────────────────┘
```

### Health Check Integration

```bash
# scripts/ci/mcp_gateway_smoke.sh
#!/usr/bin/env bash
set -euo pipefail

: "${MCP_GATEWAY_URL:?Missing MCP_GATEWAY_URL}"
: "${MCP_GATEWAY_TOKEN:?Missing MCP_GATEWAY_TOKEN}"

code="$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer ${MCP_GATEWAY_TOKEN}" \
  "${MCP_GATEWAY_URL}")"

if [[ "$code" != "200" && "$code" != "404" ]]; then
  echo "MCP Gateway unexpected HTTP $code"
  exit 1
fi

echo "✅ MCP Gateway reachable (HTTP $code)"
```

---

## Testing Gaps & Recommendations

### Current Gaps

| Gap | Impact | Recommendation |
|-----|--------|----------------|
| **E2E Browser Tests** | Limited frontend regression coverage | Implement Playwright for critical user flows |
| **Load/Performance** | No baseline for scalability | Add k6/Artillery tests for API endpoints |
| **Security Scanning** | Manual pen-testing only | Integrate SAST/DAST (Snyk, Trivy, OWASP ZAP) |
| **API Contract Testing** | No schema validation | Add Pact/OpenAPI schema validation |
| **Data Quality (Databricks)** | No pipeline health metrics | Implement Great Expectations + Airflow monitors |
| **MCP Gateway** | No centralized tool governance | Deploy Docker MCP Gateway for audit/rate limiting |

### Priority Fixes

**P0 (Critical)**:
1. **Vercel Sandbox Smoke Test** - Enable safe AI code execution
2. **Supabase Preview Branching** - Prevent production schema drift
3. **MCP Gateway Health Check** - Tool access auditability

**P1 (High)**:
1. **Playwright E2E Tests** - Critical user flows (login, expense submission, BIR filing)
2. **API Contract Validation** - OpenAPI schema enforcement
3. **Data Quality Framework** - Great Expectations on Bronze/Silver/Gold layers

**P2 (Medium)**:
1. **Load Testing** - k6 tests for 1000 concurrent users
2. **Security Scanning** - Trivy container scans, Snyk dependency checks
3. **Performance Baselines** - P95/P99 latency monitoring

---

## Implementation Roadmap

### Phase 1: Critical Gaps (Weeks 1-2)

**Week 1**:
- [ ] Add Vercel Sandbox smoke test (`.github/workflows/ci-gates.yml`)
- [ ] Enable Supabase preview branching for PR checks
- [ ] Create MCP Gateway health check script

**Week 2**:
- [ ] Implement Playwright tests for 3 critical flows (login, expense, BIR)
- [ ] Add OpenAPI schema validation to API endpoints
- [ ] Deploy MCP Gateway (Docker) with basic authentication

### Phase 2: Enhanced Coverage (Weeks 3-4)

**Week 3**:
- [ ] Great Expectations for Databricks Bronze/Silver layers
- [ ] k6 load tests for top 5 API endpoints
- [ ] Trivy container scans in CI

**Week 4**:
- [ ] Snyk dependency vulnerability checks
- [ ] Performance baselines (P95/P99) for critical operations
- [ ] Security audit report generation

### Phase 3: Automation & Monitoring (Weeks 5-6)

**Week 5**:
- [ ] Automated performance regression detection
- [ ] Data quality monitoring dashboard (Superset)
- [ ] MCP Gateway audit log analysis

**Week 6**:
- [ ] Comprehensive test coverage report
- [ ] Testing documentation update
- [ ] Team training on new testing workflows

---

## Metrics & Success Criteria

### Test Coverage Targets

| Category | Current | Target | Status |
|----------|---------|--------|--------|
| Unit Tests | 2,216 files | 2,500 files | 🟢 On track |
| E2E Tests | ~10 flows | 50 flows | 🔴 Gap |
| API Contract | None | 100% endpoints | 🔴 Gap |
| Data Quality | None | 90% tables | 🔴 Gap |
| Performance | Ad-hoc | All critical paths | 🟡 Partial |
| Security | Manual | Automated SAST/DAST | 🔴 Gap |

### Quality Gates (PR Merge Requirements)

**Mandatory**:
- ✅ All unit tests pass
- ✅ Lint/typecheck clean
- ✅ No security vulnerabilities (high/critical)
- ✅ Module drift gate passes (Odoo)
- ✅ Parity tests pass (if EE-related changes)

**Recommended** (warning if failed):
- ⚠️ Code coverage >80%
- ⚠️ Performance regression <5%
- ⚠️ API contract validation passes

---

## References

- [Vercel Sandbox Documentation](https://vercel.com/docs/vercel-sandbox)
- [Docker MCP Gateway](https://docs.docker.com/ai/mcp-catalog-and-toolkit/mcp-gateway/)
- [Supabase Preview Branching](https://supabase.com/docs/guides/platform/branching)
- [Great Expectations](https://docs.greatexpectations.io/)
- [Playwright](https://playwright.dev/)
- [k6 Load Testing](https://k6.io/)

---

**Maintained by**: Platform Engineering Team
**Review Cadence**: Monthly
**Last Review**: 2026-01-27
