# ODOO_CE_INTEGRATION.md — Strategic Separation with Operational Integration

---

**Purpose**: Document the integration strategy between `odoo-ce` (canonical production repo) and `ipai-learn` (learning management sandbox), ensuring clean separation of concerns while enabling seamless runtime coordination.

**Last Updated**: 2026-01-26
**Version**: 1.0.0

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Integration Strategy                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   odoo-ce (Production)          ◄─────►          ipai-learn (LMS)   │
│   ├── addons/ipai/              │ Volume Mounts  ├── src/           │
│   ├── CLAUDE.md                 │ References     ├── modules/       │
│   └── specs/                    │ Parity Audits  └── docs/          │
│                                  │                                   │
│   Governance:                    │                Governance:        │
│   - Production readiness         │                - Learning focus   │
│   - OCA compliance               │                - Experimental     │
│   - Multi-edition support        │                - Single edition   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Strategic Separation (Why Two Repos)

### odoo-ce: Canonical Production Repository

**Location**: `~/Documents/GitHub/odoo-ce/`
**Primary Purpose**: Production-ready Odoo CE 18 with enterprise parity
**Scope**: Multi-edition (core, marketing, accounting), 80+ IPAI modules, OCA integration

**Key Characteristics**:
- **Production Focus**: Deployment-ready with complete CI/CD pipelines (47 workflows)
- **Enterprise Architecture**: Multi-edition support, shared PostgreSQL, advanced orchestration
- **OCA Compliance**: Strict adherence to OCA conventions, automated compliance gates
- **Multi-Team Coordination**: Finance, marketing, accounting domain expertise
- **Comprehensive Documentation**: Architecture guides, runbooks, data model artifacts
- **Infrastructure Integration**: DigitalOcean, Supabase, n8n, Mattermost, MCP servers

**Governance Model**:
- Changes require spec bundles (`spec/` directory)
- All gates must pass before merge (quality, security, visual parity)
- Deployment automation with rollback procedures
- Multi-stakeholder approval for breaking changes

### ipai-learn: Learning Management Sandbox

**Location**: `~/Documents/GitHub/ipai-learn/`
**Primary Purpose**: Learning platform development and experimentation
**Scope**: Single edition, focused LMS modules, rapid iteration

**Key Characteristics**:
- **Learning Focus**: Educational content, course management, student workflows
- **Experimental Freedom**: Rapid prototyping without production constraints
- **Single Edition**: Simplified architecture for faster development cycles
- **Independent Evolution**: Can adopt new patterns without affecting production
- **Developer Experience**: Hot-reload, minimal setup, clear documentation
- **Educational Content**: Built-in tutorials, examples, learning paths

**Governance Model**:
- Lower barrier to experimentation
- Faster iteration cycles
- Independent versioning
- Simplified approval process

---

## Operational Integration (How They Work Together)

### 1. Volume Mounts (Runtime Coordination)

**Strategy**: Share code at runtime via Docker volume mounts without merging repositories.

**Implementation**:

```yaml
# ipai-learn/docker-compose.yml
services:
  odoo:
    volumes:
      # Mount ipai-learn modules
      - ./modules:/mnt/extra-addons/ipai-learn:ro

      # Mount shared odoo-ce addons (read-only reference)
      - ../odoo-ce/addons/ipai:/mnt/extra-addons/ipai:ro
      - ../odoo-ce/addons/oca:/mnt/extra-addons/oca:ro
```

**Benefits**:
- **Zero Code Duplication**: No need to copy modules between repos
- **Instant Sync**: Changes in odoo-ce immediately visible in ipai-learn
- **Read-Only Safety**: ipai-learn can reference but not modify production code
- **Selective Integration**: Choose which modules to mount

**Use Cases**:
- Testing LMS modules against production infrastructure modules
- Reusing OCA modules without duplication
- Validating compatibility before production promotion

### 2. Cross-References (Documentation Links)

**Strategy**: Maintain explicit documentation links between repos without tight coupling.

**Implementation**:

```markdown
<!-- ipai-learn/docs/integration/ODOO_CE_REFERENCES.md -->
# Production Module References

## Infrastructure Modules (Read-Only)
- `ipai_platform_workflow` → `../odoo-ce/addons/ipai/ipai_platform_workflow/`
- `ipai_platform_approvals` → `../odoo-ce/addons/ipai/ipai_platform_approvals/`

## OCA Dependencies
- `project_*` modules → `../odoo-ce/addons/oca/project/`
- `hr_timesheet_*` modules → `../odoo-ce/addons/oca/hr-timesheet/`

## Documentation
- Architecture guides → `../odoo-ce/docs/architecture/`
- Data models → `../odoo-ce/docs/data-model/`
```

**Benefits**:
- **Single Source of Truth**: Always reference canonical location
- **Clear Dependency Tracking**: Explicit documentation of what's shared
- **Maintenance Clarity**: Know which modules to sync when updating
- **Onboarding Support**: New developers understand architecture quickly

**Use Cases**:
- Developer onboarding (understand full stack)
- Dependency audits (what relies on what)
- Documentation maintenance (keep references current)

### 3. Parity Audits (Quality Gates)

**Strategy**: Automated scripts validate consistency between repos without enforcing identical structure.

**Implementation**:

```bash
#!/bin/bash
# ipai-learn/scripts/audit/odoo_ce_parity.sh

# Check module compatibility
echo "Checking module version parity..."
ODOO_CE_MODULES="../odoo-ce/addons/ipai"
IPAI_LEARN_MODULES="./modules"

# Compare manifest versions
for module in "$IPAI_LEARN_MODULES"/*; do
  module_name=$(basename "$module")
  if [ -d "$ODOO_CE_MODULES/$module_name" ]; then
    odoo_ce_version=$(grep "'version':" "$ODOO_CE_MODULES/$module_name/__manifest__.py" | cut -d"'" -f4)
    ipai_learn_version=$(grep "'version':" "$module/__manifest__.py" | cut -d"'" -f4)

    if [ "$odoo_ce_version" != "$ipai_learn_version" ]; then
      echo "⚠️  Version mismatch: $module_name (odoo-ce: $odoo_ce_version, ipai-learn: $ipai_learn_version)"
    fi
  fi
done

# Check OCA module availability
echo "Verifying OCA dependencies..."
for oca_module in $(grep "depends.*:" "$IPAI_LEARN_MODULES"/*/\__manifest__.py | grep -oP "'[a-z_]+'" | sort -u); do
  if [ ! -d "$ODOO_CE_MODULES/../oca/*/$oca_module" ]; then
    echo "⚠️  Missing OCA module: $oca_module"
  fi
done

# Report summary
echo "✅ Parity audit complete"
```

**Audit Triggers**:
- **Pre-commit Hook**: Validate before committing changes
- **CI Pipeline**: Run on every PR to ipai-learn
- **Scheduled**: Daily audit to catch drift
- **Manual**: On-demand via `./scripts/audit/odoo_ce_parity.sh`

**Audit Checks**:
1. **Module Version Consistency**: Shared modules have matching versions
2. **OCA Dependency Availability**: All required OCA modules present
3. **Manifest Syntax**: Valid Python in all `__manifest__.py`
4. **View Conventions**: Odoo 18 conventions (no deprecated `tree` in view_mode)
5. **Documentation Links**: Cross-references valid and reachable

**Benefits**:
- **Early Detection**: Catch compatibility issues before runtime
- **Automated Enforcement**: No manual checks required
- **Clear Reporting**: Know exactly what's out of sync
- **CI Integration**: Block merges that break parity

### 4. Shared Governance (Process Coordination)

**Strategy**: Coordinate changes that affect both repos through shared process contracts without unified management.

**Implementation**:

**Promotion Path** (ipai-learn → odoo-ce):
```
1. Develop in ipai-learn (experimental)
   ├── Rapid iteration
   ├── User testing
   └── Feature validation

2. Parity audit passes
   ├── Module versions compatible
   ├── OCA dependencies satisfied
   └── Documentation updated

3. Production readiness review
   ├── Spec bundle created (odoo-ce/spec/)
   ├── CI gates pass
   ├── Security audit
   └── Performance validation

4. Promote to odoo-ce
   ├── Module copied with changelog
   ├── Tests added/updated
   ├── Deployment plan created
   └── Stakeholder approval

5. Backport to ipai-learn (optional)
   ├── Production-hardened version
   └── Updated references
```

**Change Impact Assessment**:
```yaml
# Shared in both repos: integration/CHANGE_IMPACT_TEMPLATE.yaml

breaking_change_checklist:
  - [ ] Affects shared module interfaces
  - [ ] Changes OCA dependency versions
  - [ ] Modifies database schema
  - [ ] Updates Odoo version compatibility
  - [ ] Requires configuration changes

coordination_required:
  - [ ] Update both repos simultaneously
  - [ ] Notify stakeholders in both repos
  - [ ] Update cross-references
  - [ ] Run parity audits
  - [ ] Document migration path
```

**Benefits**:
- **Controlled Promotion**: Features validated before production
- **Risk Mitigation**: Breaking changes coordinated across repos
- **Clear Process**: Everyone knows promotion workflow
- **Audit Trail**: Change history preserved in both repos

---

## Integration Patterns (Common Workflows)

### Pattern 1: Reference Production Module

**Scenario**: ipai-learn needs to use production infrastructure (e.g., approval workflows)

**Steps**:
```bash
# 1. Mount production module (read-only)
# docker-compose.yml already configured

# 2. Add to ipai-learn module dependencies
# modules/ipai_lms_core/__manifest__.py
"depends": [
    "base",
    "ipai_platform_approvals",  # From odoo-ce
]

# 3. Use in code
from odoo import models, fields
from odoo.addons.ipai_platform_approvals.models.approval_workflow import ApprovalWorkflow

# 4. Document reference
# docs/integration/ODOO_CE_REFERENCES.md
- `ipai_platform_approvals` (production) → course approval workflows
```

**Benefits**: Reuse battle-tested production code without duplication

### Pattern 2: Develop and Promote

**Scenario**: New LMS feature ready for production use

**Steps**:
```bash
# 1. Develop in ipai-learn
cd ~/Documents/GitHub/ipai-learn
# ... develop feature ...

# 2. Run parity audit
./scripts/audit/odoo_ce_parity.sh

# 3. Create spec bundle in odoo-ce
cd ~/Documents/GitHub/odoo-ce
mkdir -p spec/ipai-lms-integration
cat > spec/ipai-lms-integration/prd.md << 'EOF'
# Learning Management System Integration

## Overview
Promote ipai_lms_* modules to production...
EOF

# 4. Copy module with changelog
cp -r ~/Documents/GitHub/ipai-learn/modules/ipai_lms_core addons/ipai/
git add addons/ipai/ipai_lms_core
git commit -m "feat(ipai_lms_core): promote LMS core module to production"

# 5. Add tests and documentation
# ... production-ready additions ...

# 6. Deploy via CI/CD
git push origin feat/lms-integration
# PR → review → merge → deploy
```

**Benefits**: Clear promotion path with quality gates

### Pattern 3: Sync OCA Dependencies

**Scenario**: odoo-ce updates OCA modules, ipai-learn needs to stay in sync

**Steps**:
```bash
# 1. Update in odoo-ce (canonical)
cd ~/Documents/GitHub/odoo-ce
git submodule update --remote addons/oca/project

# 2. Run parity audit in ipai-learn
cd ~/Documents/GitHub/ipai-learn
./scripts/audit/odoo_ce_parity.sh

# 3. If drift detected, update volume mount or dependencies
# No code copy needed - volume mount handles sync

# 4. Test compatibility
docker compose restart odoo
docker compose exec odoo odoo -d ipai_learn -u ipai_lms_core --stop-after-init
```

**Benefits**: Automatic sync via volume mounts, manual validation

### Pattern 4: Cross-Repo Bug Fix

**Scenario**: Bug found in shared module referenced by ipai-learn

**Steps**:
```bash
# 1. Identify module origin
# If in odoo-ce/addons/ipai/* → fix in odoo-ce
# If in ipai-learn/modules/* → fix in ipai-learn

# 2. Fix in source repo
cd ~/Documents/GitHub/odoo-ce  # or ipai-learn
# ... apply fix ...
git commit -m "fix(ipai_platform_workflow): resolve approval timeout"

# 3. Volume mount auto-syncs to ipai-learn
# No manual copy needed

# 4. Verify fix in ipai-learn
cd ~/Documents/GitHub/ipai-learn
docker compose restart odoo
./scripts/verify.sh
```

**Benefits**: Fix once, benefit everywhere

---

## Quality Gates (Integration Validation)

### Pre-Commit Checks
```bash
# Run before committing to either repo
./scripts/verify.sh

# Checks:
# - Manifest syntax validation
# - Odoo 18 conventions
# - Cross-references valid
# - No broken symlinks/volume mounts
```

### CI Pipeline Integration
```yaml
# .github/workflows/integration-validate.yml
name: Integration Validation

on: [push, pull_request]

jobs:
  parity-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Clone odoo-ce (for reference)
        run: git clone --depth 1 https://github.com/jgtolentino/odoo-ce ../odoo-ce
      - name: Run parity audit
        run: ./scripts/audit/odoo_ce_parity.sh
```

### Deployment Validation
```bash
# Before promoting from ipai-learn → odoo-ce
./scripts/audit/production_readiness.sh

# Checks:
# - Spec bundle exists
# - All CI gates pass
# - Security audit complete
# - Performance benchmarks met
# - Documentation complete
```

---

## Documentation Standards

### Cross-References Format
```markdown
<!-- Use canonical paths, not hardcoded absolute paths -->

✅ Correct:
`../odoo-ce/addons/ipai/ipai_platform_workflow/`

❌ Wrong:
`/Users/tbwa/Documents/GitHub/odoo-ce/addons/ipai/ipai_platform_workflow/`
```

### Module Dependency Documentation
```python
# __manifest__.py
{
    "name": "IPAI LMS Core",
    "depends": [
        "base",
        "ipai_platform_workflow",  # Production module (odoo-ce)
    ],
    # Document external dependencies in description
    "description": """
        Learning Management System Core

        External Dependencies:
        - ipai_platform_workflow (odoo-ce): Approval workflows
        - project (OCA): Project management integration
    """,
}
```

### Integration Runbooks
```markdown
<!-- docs/runbooks/INTEGRATION_WORKFLOWS.md -->

# Common Integration Workflows

## Workflow 1: Add Production Module Reference
**When**: Need to use odoo-ce infrastructure in ipai-learn
**Steps**: [detailed steps]
**Time**: 5 minutes
**Risk**: Low (read-only reference)

## Workflow 2: Promote Module to Production
**When**: ipai-learn feature ready for production
**Steps**: [detailed steps]
**Time**: 2-4 hours (including reviews)
**Risk**: Medium (requires spec bundle and testing)
```

---

## Troubleshooting

### Volume Mount Not Working
```bash
# Symptom: Module not found despite volume mount
# Cause: Incorrect path or permissions

# Fix:
docker compose down
ls -la ../odoo-ce/addons/ipai/  # Verify path exists
docker compose up -d
docker compose exec odoo ls /mnt/extra-addons/ipai/  # Verify mount
```

### Version Mismatch
```bash
# Symptom: Parity audit reports version drift
# Cause: odoo-ce updated module version, ipai-learn outdated

# Fix:
# Option 1: Update ipai-learn to match
# Option 2: Pin to specific version in volume mount (not recommended)
# Option 3: Document acceptable version range
```

### Circular Dependency
```bash
# Symptom: Module A (odoo-ce) depends on Module B (ipai-learn) which depends on Module A
# Cause: Improper separation of concerns

# Fix:
# 1. Identify shared interface/contract
# 2. Extract to separate module (e.g., ipai_integration_contracts)
# 3. Both repos depend on contracts module
# 4. Document in integration/SHARED_CONTRACTS.md
```

---

## Migration Path (Future Unification)

**Current State**: Two repos, operationally integrated
**Future Option**: Single monorepo with workspace structure

**If Unified**:
```
odoo-monorepo/
├── production/           # Current odoo-ce
│   ├── addons/ipai/
│   └── specs/
├── learning/             # Current ipai-learn
│   ├── modules/
│   └── docs/
└── shared/               # Shared contracts
    ├── interfaces/
    └── governance/
```

**Benefits of Unification**:
- Single CI/CD pipeline
- Easier dependency management
- Unified governance

**Benefits of Separation** (current):
- Independent evolution
- Simpler cognitive load
- Lower risk for experiments

**Decision Criteria**: Unify when integration overhead > separation overhead

---

## Related Documentation

**odoo-ce**:
- `CLAUDE.md` - Production execution rules
- `docs/architecture/` - System architecture
- `docs/data-model/` - Database schema
- `spec/` - Feature specifications

**ipai-learn**:
- `CLAUDE.md` - Learning sandbox rules
- `docs/runbooks/DEV_SANDBOX.md` - Daily operations
- `integration/` - Integration guides

**Shared**:
- `~/.claude/CLAUDE.md` - SuperClaude framework (global)
- `~/.claude/MCP.md` - MCP server integration
- `~/.claude/SKILLS.md` - Agent skills

---

**Summary**: odoo-ce and ipai-learn are strategically separated but operationally integrated through volume mounts, cross-references, parity audits, and shared governance. This architecture preserves clean separation of concerns while enabling seamless runtime coordination.

---

**Last Updated**: 2026-01-26
**Version**: 1.0.0
**Author**: SuperClaude Framework
