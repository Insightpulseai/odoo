# Addons Structure Boundary (SSOT)

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2026-02-20

## Purpose

This document defines the canonical directory taxonomy and boundary rules for Odoo modules in this repository. It serves as the single source of truth for determining where new modules belong and how to enforce structural invariants.

## Directory Taxonomy

### `addons/odoo/` (Upstream Core)

**Purpose**: Odoo Community Edition core modules (read-only reference)

**Characteristics**:
- Shipped with Odoo CE distributions
- Never modified in this repository
- Updated only via upstream version bumps

**Examples**: `base`, `account`, `sale`, `stock`, `hr`

**Governance**: Upstream-controlled, no local modifications allowed

---

### `addons/oca/` (EE Parity Layer)

**Purpose**: Modules implementing Odoo Enterprise Edition feature parity using OCA patterns

**Characteristics**:
- **OCA module first**: Prefer existing OCA modules over custom implementations
- **EE feature equivalence**: Implements features from Odoo Enterprise Edition
- **Community-standard patterns**: Follows OCA development guidelines
- **Integration-agnostic**: Core business logic without external service dependencies

**Examples**:
- `oca/subscription_*` (subscription management - EE parity)
- `oca/helpdesk_*` (helpdesk - EE parity)
- `oca/knowledge_*` (knowledge base - EE parity)
- `oca/sign_*` (document signing - EE parity)

**Naming Convention**: `<oca_module_name>` or `ipai_ee_<feature>` if no OCA equivalent exists

**Governance**: OCA-first policy (see constitution §4.2)

---

### `addons/ipai/` (Integration Bridges)

**Purpose**: Modules connecting Odoo to external services and systems

**Allowed Categories**:
1. **External Service Connectors**: Slack, Auth0, OIDC providers, payment gateways
2. **API Bridges**: MCP, REST controllers for non-Odoo clients
3. **AI/ML Tools**: OCR pipelines, document processing, embedding services
4. **BIR Compliance**: Philippine-specific tax/regulatory modules
5. **Data Integration**: ETL connectors, sync engines, webhook receivers

**Forbidden Categories**:
- ❌ EE feature parity (belongs in `addons/oca/`)
- ❌ General business logic (belongs in `addons/oca/`)
- ❌ OCA module duplicates (extend existing OCA modules instead)

**Examples**:
- `ipai_slack_connector` (Slack API integration)
- `ipai_auth_oidc` (OIDC authentication bridge)
- `ipai_mcp_bridge` (MCP server integration)
- `ipai_bir_compliance` (BIR tax filing automation)
- `ipai_ocr_expense` (OCR expense automation glue)

**Naming Convention**: `ipai_<service>_<feature>` or `ipai_<domain>_<feature>`

**Governance**: Justification required (see constitution §4.3)

---

### `addons/ipai_meta/` (Meta Modules)

**Purpose**: Repository infrastructure and development tooling

**Characteristics**:
- **Non-business logic**: Testing frameworks, CI helpers, development utilities
- **Repository-specific**: Not intended for external distribution
- **Internal tooling**: Module generators, scaffolding, development aids

**Examples**:
- `ipai_meta_test_runner` (custom test framework)
- `ipai_meta_module_generator` (module scaffolding tool)
- `ipai_meta_ci_helpers` (CI/CD integration utilities)

**Naming Convention**: `ipai_meta_<purpose>`

**Governance**: Internal tooling only, no external dependencies

---

## Boundary Rules (Hard Constraints)

### Rule 1: Parity Location Invariant

**Statement**: All modules implementing Odoo Enterprise Edition feature parity MUST reside in `addons/oca/`.

**Rationale**:
- OCA modules provide community-vetted implementations
- Reduces maintenance burden (shared upstream)
- Avoids duplication and fragmentation

**Enforcement**: CI keyword detection + manifest parsing

**Examples**:
- ✅ `addons/oca/subscription_management` (EE parity)
- ❌ `addons/ipai/ipai_subscriptions` (wrong location)

---

### Rule 2: Integration Scope Constraint

**Statement**: Modules in `addons/ipai/` MUST be integration bridges or external service connectors ONLY.

**Rationale**:
- Prevents namespace pollution with business logic
- Maintains clear separation of concerns
- Facilitates migration to OCA equivalents

**Enforcement**: Justification file requirement + CI validation

**Examples**:
- ✅ `addons/ipai/ipai_slack_connector` (external integration)
- ❌ `addons/ipai/ipai_custom_crm` (business logic - belongs in OCA)

---

### Rule 3: No Hybrid Modules

**Statement**: A module cannot be both EE parity AND an integration bridge.

**Rationale**:
- Forces architectural clarity
- Prevents dual-purpose modules that violate single responsibility
- Simplifies dependency management

**Resolution**: Split into two modules:
- `addons/oca/<feature>` (EE parity logic)
- `addons/ipai/ipai_<service>_<feature>` (integration bridge)

**Example**:
- ❌ `ipai_slack_helpdesk` (hybrid: helpdesk EE parity + Slack integration)
- ✅ Split into:
  - `addons/oca/helpdesk_slack` (EE parity with Slack extension)
  - `addons/ipai/ipai_slack_connector` (reusable Slack bridge)

---

## Decision Trees

### New Module Placement: Where Does It Go?

```
START: I need to create a new Odoo module.

Q1: Does it implement an Odoo Enterprise Edition feature?
├─ YES → Use `addons/oca/`
│         └─ Check for existing OCA module first
│         └─ If no OCA module, create `ipai_ee_<feature>` in `addons/oca/`
│
└─ NO  → Q2: Is it an integration with an external service?
          ├─ YES → Use `addons/ipai/ipai_<service>_<feature>`
          │         └─ Create PARITY_CONNECTOR_JUSTIFICATION.md
          │         └─ Document external dependencies
          │
          └─ NO  → Q3: Is it repository infrastructure/tooling?
                    ├─ YES → Use `addons/ipai_meta/ipai_meta_<purpose>`
                    │
                    └─ NO  → ❌ STOP: Module is general business logic
                              └─ Use `addons/oca/` or extend existing OCA module
```

### Existing Module Classification: Should It Move?

```
START: I found a module in the wrong location.

Q1: Is it in baseline exceptions (parity_boundaries_baseline.json)?
├─ YES → Migration optional (defer for incremental cleanup)
│
└─ NO  → MUST migrate before merge

Q2: Where does it belong?
├─ Contains EE keywords (subscription, helpdesk, knowledge, sign, etc.)
│   └─ Move to `addons/oca/`
│
├─ External service integration (Slack, OIDC, payment gateway, etc.)
│   └─ Keep in `addons/ipai/`
│   └─ Verify PARITY_CONNECTOR_JUSTIFICATION.md exists
│
└─ General business logic (no EE parity, no external integration)
    └─ Move to `addons/oca/` or deprecate
```

---

## Migration Strategy

### Baseline Tolerance Policy

**Current State**: 45 existing violations tracked in `scripts/ci/baselines/parity_boundaries_baseline.json`

**Policy**:
- **Existing violations**: Allowed to remain (grandfathered)
- **New violations**: Blocked by CI (must fix before merge)
- **Migration cadence**: Incremental over 6 months
- **Baseline review**: First Monday of each month

**Rationale**: Avoid forced migrations and repository churn while preventing new violations.

---

### New Module Requirements

**Effective**: Immediately (applies to all new modules after 2026-02-20)

**Requirements**:
1. ✅ **Correct location**: Follow decision tree (no exceptions)
2. ✅ **Justification file**: `PARITY_CONNECTOR_JUSTIFICATION.md` for `addons/ipai/` modules
3. ✅ **CI validation**: Must pass `check_parity_boundaries.sh` before merge
4. ✅ **Documentation**: README.md explaining purpose and classification

**Enforcement**: CI blocks merges with new violations

---

### Incremental Migration Workflow

**For Baseline Violations**:

1. **Classify**: Determine correct location using decision tree
2. **Plan**: Create migration plan (dependencies, data migration, tests)
3. **Execute**: Move module + update imports + update docs
4. **Verify**: Run full test suite + CI validation
5. **Update Baseline**: Remove from `parity_boundaries_baseline.json`
6. **Commit**: `refactor(repo): migrate <module> to correct location (parity boundary)`

**Timeline**: 6 months (7-8 modules per month)

**Priority Order**:
1. High-impact modules (many dependents)
2. EE parity modules in wrong location
3. Deprecated modules (cleanup candidates)
4. Low-impact modules (few/no dependents)

---

## Enforcement Mechanisms

### CI Validation (`check_parity_boundaries.sh`)

**Triggers**:
- Every PR to `main`
- Pre-commit hook (optional local enforcement)
- Weekly baseline audit (scheduled CI job)

**Checks**:
1. **Keyword Detection**: Flag EE-related terms in `addons/ipai/`
   - Keywords: `subscription`, `forecast`, `planning`, `consolidation`, `helpdesk`, `knowledge`, `sign`, `studio`, `voip`, `documents`, `appointment`, `rental`, `social`, `whatsapp`
2. **Manifest Parsing**: Detect Enterprise dependencies
   - Search for `web_enterprise`, `base_enterprise` in `__manifest__.py`
3. **Justification File**: Verify `PARITY_CONNECTOR_JUSTIFICATION.md` exists for non-allowlisted `addons/ipai/` modules
4. **Baseline Comparison**: Allow existing violations, block new ones

**Modes**:
- `ci`: Default (fail on new violations)
- `pre-commit`: Local dev (same as ci, faster feedback)
- `update-baseline`: Regenerate baseline after approved migrations

**Exit Codes**:
- `0`: Pass (no new violations)
- `1`: Fail (new violations detected)

---

### Pre-Commit Hook (Optional)

**Installation** (optional for developers):

```bash
# Add to .git/hooks/pre-commit
#!/usr/bin/env bash
./scripts/ci/check_parity_boundaries.sh pre-commit
```

**Benefits**:
- Catch violations before CI
- Faster feedback loop
- Reduces CI build failures

---

### Monthly Baseline Review

**Schedule**: First Monday of each month

**Process**:
1. Load `parity_boundaries_baseline.json`
2. Review baseline count vs. target (7-8 migrations per month)
3. Prioritize migrations for next sprint
4. Update migration tracker (GitHub project board)
5. Update baseline after migrations

**Goal**: Zero baseline violations by 2026-08-20 (6 months)

---

## EE Parity Keywords (Detection List)

**Critical Keywords** (high confidence EE parity):
- `subscription`, `subscriptions`
- `forecast`, `forecasting`
- `planning`, `planner`
- `consolidation`, `consolidated`
- `helpdesk`, `ticket`
- `knowledge`, `wiki`
- `sign`, `signature`, `esignature`
- `studio`, `builder`
- `voip`, `phone`, `call`
- `documents`, `document_management`
- `appointment`, `booking`, `calendar_appointment`
- `rental`, `rentals`
- `social`, `social_media`
- `whatsapp`

**Contextual Keywords** (require manifest check):
- `enterprise`, `ent`, `ee`
- `web_enterprise`, `base_enterprise`
- `web_studio`, `web_mobile`

**Exclusions** (allowed in ipai namespace):
- `integration`, `bridge`, `connector`
- `api`, `rest`, `webhook`
- `ocr`, `ai`, `ml`, `llm`
- `bir`, `compliance`, `tax`

---

## References

### Constitution Cross-References
- **Article 4**: Structural Boundaries (defined in `spec/odoo-ee-parity-seed/constitution.md`)
- **§4.1**: Directory Taxonomy
- **§4.2**: Parity Location Invariant
- **§4.3**: Integration Scope Constraint
- **§4.4**: Baseline Tolerance Policy
- **§4.5**: Enforcement Chain

### Related Documentation
- `docs/ai/IPAI_MODULES.md` - Module naming conventions
- `docs/ai/EE_PARITY.md` - EE parity strategy
- `docs/ai/OCA_WORKFLOW.md` - OCA module development workflow
- `spec/odoo-ee-parity-seed/` - EE parity seed generator

### CI Files
- `.github/workflows/parity-boundaries.yml` - CI workflow
- `scripts/ci/check_parity_boundaries.sh` - Enforcement script
- `scripts/ci/baselines/parity_boundaries_baseline.json` - Baseline tracking

---

## Changelog

### v1.0.0 (2026-02-20)
- Initial release
- Define directory taxonomy (odoo, oca, ipai, ipai_meta)
- Establish boundary rules (3 hard constraints)
- Document decision trees
- Define migration strategy (baseline tolerance policy)
- Specify enforcement mechanisms (CI validation, pre-commit hooks, monthly review)
