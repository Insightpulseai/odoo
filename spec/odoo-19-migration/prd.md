# Odoo 19 Migration — Product Requirements Document

---

**Status**: DRAFT
**Owner**: Jake Tolentino
**Created**: 2026-01-26
**Target**: Q3-Q4 2026 (pending Odoo 19 CE release)

---

## Executive Summary

Migrate the odoo-ce production stack from Odoo 18 CE to Odoo 19 CE, preserving all 80+ IPAI custom modules, 12+ OCA dependencies, and external integrations (n8n, Mattermost, Supabase, MCP servers).

### Business Value

| Metric | Current (Odoo 18) | Target (Odoo 19) | Improvement |
|--------|-------------------|------------------|-------------|
| Performance | Baseline | +15% faster | Page loads, API response |
| Features | 18.0 feature set | 19.0 enhancements | New UI, workflows |
| Security | 18.0 patches | 19.0 security model | Latest CVE fixes |
| Support | Community support | Extended lifecycle | 3+ years support |

---

## Problem Statement

### Current State

- **Odoo Version**: 18.0 CE
- **Custom Modules**: 80+ IPAI modules across 10 domains
- **OCA Dependencies**: 12 repositories (web, account, sale, purchase, etc.)
- **External Integrations**: n8n (workflows), Mattermost (ChatOps), Supabase (external data), MCP (AI agents)
- **Database**: PostgreSQL 15 with 3 editions (Core, Marketing, Accounting)

### Pain Points

1. **Feature Gap**: Odoo 19 introduces improvements not available in 18
2. **OCA Alignment**: OCA community migrating to 19.0 branches
3. **Security**: New security features in 19.0
4. **Performance**: Framework optimizations in 19.0

### Opportunity

Odoo 19 CE (expected Q2-Q3 2026) will provide:
- OWL 2.x framework improvements
- Enhanced asset bundling
- New form/list view features
- Improved multi-company handling
- Better REST API capabilities

---

## Requirements

### Functional Requirements

#### FR-1: Module Migration

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | All IPAI modules functional on Odoo 19 | P0 |
| FR-1.2 | All OCA dependencies upgraded to 19.0 | P0 |
| FR-1.3 | Custom views compatible with OWL 2.x | P0 |
| FR-1.4 | Python code compatible with Odoo 19 API | P0 |

#### FR-2: Data Migration

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | All transactional data preserved | P0 |
| FR-2.2 | All attachments/documents migrated | P0 |
| FR-2.3 | All user accounts and permissions preserved | P0 |
| FR-2.4 | Audit trail continuity maintained | P0 |

#### FR-3: Integration Continuity

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | n8n workflows continue functioning | P0 |
| FR-3.2 | Mattermost ChatOps operational | P0 |
| FR-3.3 | Supabase sync tables compatible | P0 |
| FR-3.4 | MCP server connections maintained | P0 |

#### FR-4: New Features (Odoo 19 Specific)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Adopt OWL 2.x component patterns | P1 |
| FR-4.2 | Enable new form view features | P2 |
| FR-4.3 | Implement enhanced REST API endpoints | P2 |
| FR-4.4 | Utilize improved asset bundling | P2 |

### Non-Functional Requirements

#### NFR-1: Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1.1 | Page load time | ≤2s (P95) |
| NFR-1.2 | API response time | ≤500ms (P95) |
| NFR-1.3 | Batch job execution | ≤10% regression |
| NFR-1.4 | Memory footprint | ≤20% increase |

#### NFR-2: Availability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-2.1 | Migration downtime | ≤4 hours |
| NFR-2.2 | Rollback time | ≤4 hours |
| NFR-2.3 | Post-migration uptime | 99.9% |

#### NFR-3: Security

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-3.1 | No security regressions | 100% |
| NFR-3.2 | RLS policies preserved | 100% |
| NFR-3.3 | Audit logging continuity | 100% |

---

## User Stories

### Epic: Module Developer

```
US-1: As a module developer, I want clear migration guidelines
      so that I can update IPAI modules for Odoo 19 compatibility.

Acceptance Criteria:
- Migration guide documents API changes
- Code examples for common patterns
- Automated compatibility checker
```

### Epic: System Administrator

```
US-2: As a system administrator, I want automated migration scripts
      so that I can execute the upgrade with minimal manual steps.

Acceptance Criteria:
- Single-command migration execution
- Progress monitoring dashboard
- Automatic rollback on failure
```

### Epic: End User

```
US-3: As an end user, I want zero disruption to my daily workflows
      so that I can continue working after migration.

Acceptance Criteria:
- All bookmarks/favorites preserved
- Custom filters/searches retained
- Keyboard shortcuts unchanged
```

### Epic: Integration Owner

```
US-4: As an integration owner, I want backward-compatible APIs
      so that n8n/Mattermost/MCP integrations continue working.

Acceptance Criteria:
- XML-RPC endpoints unchanged
- REST API backward compatible
- Webhook signatures preserved
```

---

## Scope

### In Scope

| Category | Items |
|----------|-------|
| Modules | All 80+ IPAI modules |
| OCA | All 12 OCA repositories |
| Databases | Core, Marketing, Accounting editions |
| Integrations | n8n, Mattermost, Supabase, MCP |
| Infrastructure | Docker, DigitalOcean, PostgreSQL |

### Out of Scope

| Category | Reason |
|----------|--------|
| Enterprise features | CE-only constraint |
| New module development | Focus on migration |
| Infrastructure changes | Keep DigitalOcean stack |
| Database engine change | Stay on PostgreSQL 15 |

### Deferred

| Category | Rationale |
|----------|-----------|
| OWL 2.x rewrite of views | Phase 2 optimization |
| New Odoo 19 features | Post-migration enhancement |
| Performance optimization | Post-migration tuning |

---

## Dependencies

### External Dependencies

| Dependency | Owner | Status | Risk |
|------------|-------|--------|------|
| Odoo 19 CE release | Odoo SA | Pending | High - blocks start |
| OCA 19.0 branches | OCA | Pending | High - 12 repos needed |
| PostgreSQL 15 compatibility | PostgreSQL | Confirmed ✓ | Low |
| Python 3.10+ compatibility | Python | Confirmed ✓ | Low |

### Internal Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| IPAI module audit | Dev Team | Not started |
| Integration test suite | QA Team | Partial |
| Staging environment | DevOps | Available ✓ |
| Production backup strategy | DevOps | Defined ✓ |

---

## Success Metrics

### Launch Criteria (Must Have)

- [ ] 100% IPAI modules passing tests
- [ ] 100% OCA dependencies upgraded
- [ ] 100% data migration verified
- [ ] 100% integration tests passing
- [ ] <4 hour migration window achieved
- [ ] Rollback tested and documented

### Success Metrics (30-Day Post-Launch)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Uptime | 99.9% | Monitoring |
| User-reported bugs | <10 P2+ | Helpdesk |
| Performance regression | <10% | APM |
| Rollback events | 0 | Incident log |

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OCA module not ported to 19.0 | Medium | High | Identify alternatives, fork if needed |
| API breaking changes in Odoo 19 | Medium | High | Early testing, abstraction layers |
| Data migration errors | Low | Critical | Multiple backups, checksums, dry runs |
| Integration failures | Medium | High | Integration test suite, staged rollout |
| Performance regression | Medium | Medium | Load testing, optimization budget |
| Extended downtime | Low | High | Parallel environment, fast rollback |

---

## Timeline

### Phase 0: Preparation (Now - Odoo 19 Release)

- Monitor Odoo 19 development
- Audit IPAI modules for compatibility
- Update integration test suite
- Document current state baseline

### Phase 1: Sandbox Testing (Odoo 19 Release + 2 weeks)

- Set up Odoo 19 development sandbox
- Port critical IPAI modules
- Validate OCA dependencies
- Performance baseline

### Phase 2: Staging Migration (+ 4 weeks)

- Full module migration to staging
- Integration testing
- User acceptance testing
- Load testing

### Phase 3: Production Migration (+ 2 weeks)

- Production backup
- Migration execution
- Verification
- Monitoring

### Phase 4: Stabilization (+ 4 weeks)

- Bug fixes
- Performance tuning
- Documentation updates
- Parallel environment decommission

---

## Budget

### Development Effort

| Phase | Hours | Notes |
|-------|-------|-------|
| Preparation | 40 | Audit, planning |
| Sandbox | 60 | Module porting |
| Staging | 80 | Testing, fixes |
| Production | 30 | Migration, monitoring |
| Stabilization | 40 | Bug fixes, tuning |
| **Total** | **250** | Within constraint |

### Infrastructure Costs

| Item | Monthly | Duration | Total |
|------|---------|----------|-------|
| Parallel staging | $100 | 3 months | $300 |
| Parallel production | $200 | 1 month | $200 |
| Backup storage | $50 | 4 months | $200 |
| **Total** | | | **$700** |

---

## Stakeholders

| Role | Name | Responsibility |
|------|------|----------------|
| Product Owner | TBD | Requirements, priorities |
| Tech Lead | TBD | Architecture, decisions |
| Dev Team | TBD | Implementation |
| QA Lead | TBD | Testing strategy |
| DevOps | TBD | Infrastructure, deployment |
| End User Rep | TBD | UAT, feedback |

---

## Appendix

### A. IPAI Module Inventory

See `docs/IPAI_MODULE_INVENTORY.md` for complete list of 80+ modules.

### B. OCA Dependency List

See `oca.lock.json` for pinned OCA versions.

### C. Integration Endpoints

See `docs/INTEGRATION_ENDPOINTS.md` for API documentation.

---

*Document Version: 1.0*
*Last Updated: 2026-01-26*
