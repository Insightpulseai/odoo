# Odoo 19 Migration — Constitution

---

**Purpose**: Define non-negotiable rules and constraints for the Odoo 18 → 19 CE migration.
**Last Updated**: 2026-01-26
**Status**: DRAFT

---

## Non-Negotiables

### 1. CE-Only Constraint

```
RULE: No Enterprise modules or odoo.com IAP dependencies.
ENFORCEMENT: CI gate blocks any import from enterprise/* or odoo.com/iap/*
```

The entire stack MUST remain Odoo Community Edition. Any feature backported from Odoo 19 Enterprise MUST be reimplemented as CE-compatible IPAI modules.

### 2. Zero Data Loss

```
RULE: All production data MUST be preserved through migration.
ENFORCEMENT: Pre-migration backup + post-migration verification checksums.
```

Migration scripts MUST:
- Create full database backup before any migration step
- Validate record counts pre/post migration
- Verify financial data integrity (GL balances, trial balance)
- Confirm attachment/document preservation

### 3. Module Compatibility

```
RULE: All 80+ IPAI modules MUST pass unit tests on Odoo 19 before production cutover.
ENFORCEMENT: CI matrix testing against both Odoo 18 and 19 during transition.
```

No module may be deployed to Odoo 19 production without:
- All existing unit tests passing
- Visual regression tests passing
- Integration tests with OCA dependencies passing

### 4. OCA Alignment

```
RULE: Prefer OCA modules over custom IPAI implementations.
ENFORCEMENT: Module audit before migration to identify OCA replacements.
```

Migration priority:
1. **Config** — Use Odoo 19 built-in configuration
2. **OCA** — Upgrade to OCA 19.0 branches
3. **Delta** — Only migrate custom ipai_* where no OCA alternative exists

### 5. Rollback Capability

```
RULE: Full rollback to Odoo 18 MUST be possible within 4 hours.
ENFORCEMENT: Maintain parallel Odoo 18 environment for 30 days post-migration.
```

Rollback requirements:
- Database snapshot at T-0 (migration start)
- Docker image pinned at Odoo 18.0
- Documented rollback procedure tested pre-migration

### 6. No Breaking Changes to External Integrations

```
RULE: n8n, Mattermost, Supabase, and MCP integrations MUST continue working.
ENFORCEMENT: Integration test suite against all external systems.
```

APIs that MUST remain stable:
- XML-RPC endpoints for n8n workflows
- REST API endpoints for MCP servers
- Webhook endpoints for Mattermost ChatOps
- Database schema for Supabase sync tables

### 7. Performance Parity

```
RULE: Odoo 19 MUST match or exceed Odoo 18 performance benchmarks.
ENFORCEMENT: Load testing with production-equivalent data before cutover.
```

Benchmarks:
- Page load time: ≤2 seconds (P95)
- API response time: ≤500ms (P95)
- Batch processing: ≤10% regression allowed
- Memory usage: ≤20% increase allowed

---

## Constraints

### Timeline Constraints

| Milestone | Hard Deadline | Reason |
|-----------|---------------|--------|
| Odoo 19 CE availability | Must wait for official release | Cannot use pre-release in production |
| OCA 19.0 branches | Must wait for OCA migration | 12+ OCA repos in stack |
| BIR compliance | Q1 fiscal year end | Cannot disrupt tax filing |
| Production cutover | Weekend only | Minimize business disruption |

### Technical Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| PostgreSQL 15 required | Current stack uses PG 15 ✓ | No action needed |
| Python 3.10+ required | Current stack uses 3.10 ✓ | No action needed |
| Node.js 18+ for assets | Current stack uses 18 ✓ | No action needed |
| OWL 2.x framework | View layer rewrite may be needed | Audit all custom views |

### Resource Constraints

| Resource | Limit | Justification |
|----------|-------|---------------|
| Development hours | 250 max | Budget constraint |
| Downtime window | 4 hours max | SLA requirement |
| Parallel infrastructure | 30 days | Cost optimization |
| External consultant | 0 hours | In-house only |

---

## Prohibited Actions

### Never Do

1. **Never migrate production without staging validation**
   - All migrations MUST pass staging first
   - Staging data MUST be production-equivalent

2. **Never skip OCA module compatibility audit**
   - Some OCA modules may not have 19.0 branches
   - Must identify alternatives or forks before migration

3. **Never disable security features during migration**
   - RLS policies remain active
   - Authentication remains enforced
   - Audit logging continues

4. **Never modify core Odoo files**
   - All customizations via IPAI modules
   - No monkey-patching base classes

5. **Never migrate on month-end or fiscal deadlines**
   - Blackout: Last 5 days of each month
   - Blackout: Q1-Q4 fiscal close periods
   - Blackout: BIR filing deadlines

---

## Acceptance Criteria

Migration is complete when:

- [ ] All 80+ IPAI modules installed and functional on Odoo 19
- [ ] All OCA dependencies upgraded to 19.0 branches
- [ ] All unit tests passing (100%)
- [ ] All integration tests passing (100%)
- [ ] Visual regression tests passing (95%+)
- [ ] Performance benchmarks met
- [ ] External integrations verified
- [ ] Production data migrated and validated
- [ ] Rollback procedure tested and documented
- [ ] Team training completed
- [ ] Documentation updated

---

## Governance

### Decision Authority

| Decision | Authority | Escalation |
|----------|-----------|------------|
| Migration go/no-go | Tech Lead | CTO |
| Rollback trigger | On-call engineer | Tech Lead |
| Scope changes | Product Owner | Steering Committee |
| Budget changes | Finance | Executive |

### Change Control

Any changes to this constitution require:
1. Written justification
2. Impact analysis
3. Approval from Tech Lead + Product Owner
4. Documentation update
5. Team notification

---

*Last reviewed: 2026-01-26*
*Next review: Before migration kickoff*
