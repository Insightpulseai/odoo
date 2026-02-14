# Odoo.sh Replacement Implementation Tracker

**Status**: Week 1 In Progress
**Target**: 95% Odoo.sh feature parity in 6 weeks
**Last Updated**: 2026-02-15

---

## Implementation Timeline

| Week | Deliverables | Spec | Status |
|------|------------|------|--------|
| 0 | GHCR workflow, Codespaces, branch protections | odoo-sh-clone Phase 0 | 🟡 In Progress |
| 1-2 | Core schema (9 ops.* tables), project/environment models | odooops-sh Weeks 1-2 | 🔴 Not Started |
| 2 | Docker Compose runtime bundle | odoo-sh-clone Phase 2 | 🔴 Not Started |
| 3 | RPC functions, Staging clone logic | odooops-sh Week 3 + odoo-sh-clone Phase 3 | 🔴 Not Started |
| 4 | CI integration, Backup/restore | odooops-sh + odoo-sh-clone Week 4 | 🔴 Not Started |
| 5 | Documentation, Upgrade advisor | odooops-sh + odoo-sh-clone Week 5 | 🔴 Not Started |
| 6 | Integration testing, CLI commands | odooops-sh + odoo-sh-clone Week 6 | 🔴 Not Started |

---

## Week 1: Breaking Changes + Spec Kit Setup

**Spec**: `/spec/odooops-sh/plan.md` Week 1

### Tasks

- [ ] **1.1** Review `/spec/odooops-sh/constitution.md`
- [ ] **1.2** Review `/spec/odooops-sh/prd.md`
- [ ] **1.3** Review `/spec/odooops-sh/plan.md`
- [ ] **1.4** Review `/spec/odooops-sh/tasks.md`
- [ ] **1.5** Identify breaking changes from existing patterns
- [ ] **1.6** Create migration plan for existing ops infrastructure
- [ ] **1.7** Set up Supabase project for ops.* schema
- [ ] **1.8** Create initial ops.* migration files
- [ ] **1.9** Document breaking changes in CHANGELOG
- [ ] **1.10** Update project tracking

### Deliverables

1. **Breaking Changes Document** - `docs/implementation/breaking-changes-week1.md`
2. **Supabase Setup** - ops.* schema project configured
3. **Migration Files** - Initial ops.* table migrations
4. **Spec Kit Validation** - All 4 spec files reviewed and validated

### Success Criteria

- ✅ All breaking changes documented
- ✅ Supabase project created and accessible
- ✅ ops.* migration files created (ready for Week 2)
- ✅ Team aligned on spec kit requirements

---

## Week 2: Core Schema (9 ops.* Tables)

**Spec**: `/spec/odooops-sh/plan.md` Week 2

### Tasks

- [ ] **2.1** Create `ops.projects` table
- [ ] **2.2** Create `ops.environments` table
- [ ] **2.3** Create `ops.workflows` table
- [ ] **2.4** Create `ops.runs` table
- [ ] **2.5** Create `ops.run_events` table
- [ ] **2.6** Create `ops.run_logs` table
- [ ] **2.7** Create `ops.run_artifacts` table
- [ ] **2.8** Create `ops.upgrade_advisories` table
- [ ] **2.9** Create `ops.project_memberships` table
- [ ] **2.10** Implement RLS policies for all tables
- [ ] **2.11** Create database indexes
- [ ] **2.12** Validate schema with test data

### Success Criteria

- ✅ All 9 tables created in Supabase
- ✅ RLS policies enforced
- ✅ Test data validates schema design

---

## Week 3: RPC Functions + Staging Clone

**Spec**: `/spec/odooops-sh/plan.md` Week 3 + `/spec/odoo-sh-clone/plan.md` Phase 3

### Tasks

- [ ] **3.1** Create RPC functions (6 functions)
- [ ] **3.2** Implement staging clone workflow
- [ ] **3.3** Test RPC endpoints
- [ ] **3.4** Validate staging clone process

### Success Criteria

- ✅ All 6 RPC functions operational
- ✅ Staging clone workflow tested

---

## Progress Tracking

### Completed

*None yet*

### In Progress

- **Week 0**: GHCR workflow setup

### Blocked

*None*

---

## Quick Reference

### Specs

- `/spec/odooops-sh/` - Core control plane (9 ops.* tables, 6 RPC functions)
- `/spec/odoo-sh-clone/` - Developer UX (branches, staging, backups)

### Verification Commands

```bash
# Check Supabase schema
supabase db dump --schema ops

# Verify GHCR workflow
gh workflow list | grep "Build Docker"

# Test CLI commands (Week 6+)
ops project list
ops run list --project <project-id>
```

### Resources

- Supabase Project: `spdtwktxdalcfigzeqrz`
- GitHub Repo: `Insightpulseai/odoo`
- Alignment Doc: `/docs/architecture/odoo-sh-parity.md` (to be created)

---

## Notes

- OCA installation running in parallel (Track A)
- No architectural changes needed - 95% coverage achieved via existing specs
- Only 1 new module required post-MVP: `ipai_ops_monitoring` (Week 7+)
