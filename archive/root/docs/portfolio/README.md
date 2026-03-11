# Portfolio Layer

**Purpose**: Manage investment pipeline, initiatives, and delivery roadmap

**Layer Position**: Layer 2 of 7 (Strategy → **Portfolio** → Process → Execution → Control → Evidence → Integration)

---

## Purpose & Scope

This layer translates strategic objectives into executable initiatives with:

- **Spec Bundles**: 85+ detailed feature specifications
- **Backlog**: Prioritized work queue with business value estimates
- **Roadmap**: Timeline view of deliverables across quarters
- **PPM (Project Portfolio Management)**: Investment tracking, resource allocation, value realization

---

## ID Convention

**Format**: `PORT-<YEAR>-<NUMBER>`

**Examples**:
- `PORT-2026-007` - Odoo.sh-Grade Parity initiative
- `PORT-2026-008` - BIR Compliance Automation
- `PORT-2026-009` - AI-Powered Document Intelligence

---

## Directory Structure

```
portfolio/
├── README.md                    # This file
├── specs/                       # 85+ spec bundles (migrated from /spec)
│   ├── odoo-sh-grade-parity/
│   ├── bir-compliance/
│   └── ai-document-intelligence/
├── backlog/                     # Prioritized work queue
│   └── backlog.yaml
├── roadmap.md                   # Timeline view of deliverables
├── investments.md               # Funding buckets and ROI tracking
└── ppm/                         # Project Portfolio Management
    ├── core/                    # PPM framework (migrated from /docs/ppm)
    └── finance-ppm/             # Financial PPM specifics (migrated from /docs/finance-ppm)
```

---

## Connections to Other Layers

### Upstream (Portfolio derives from these layers)

- **Strategy** (`docs/strategy/`): Portfolio initiatives execute strategic objectives
  - Example: `STRAT-PARITY-001` → `PORT-2026-007`

### Downstream (Portfolio drives these layers)

- **Process** (`docs/process/`): Initiatives require process execution
  - Example: `PORT-2026-007` → `PROC-DEV-001` (Development process)

- **Execution** (code, scripts, workflows): Initiatives implement through code
  - Example: `PORT-2026-007` → `addons/ipai/ipai_hr_expense_liquidation/`

- **Control** (`docs/control/`): Initiatives subject to control gates
  - Example: `PORT-2026-007` → `CTRL-GATE-001` (Architecture review)

- **Evidence** (`docs/evidence/`): Initiatives produce evidence artifacts
  - Example: `PORT-2026-007` → `EVID-20260212-001` (Implementation evidence)

---

## Document Format

All portfolio documents must include frontmatter:

```yaml
---
id: PORT-2026-007
type: portfolio_initiative
name: Odoo.sh-Grade Parity
status: in_progress
owner: platform_team
strategy_link: STRAT-PARITY-001
processes: [PROC-DEV-001, PROC-QA-002, PROC-DEPLOY-001]
controls: [CTRL-GATE-001, CTRL-SEC-004]
evidence: [EVID-20260212-001, EVID-20260212-002]
priority: P0
business_value: 90
effort_estimate: 120h
delivery_quarter: 2026-Q1
---
```

---

## Spec Bundle Structure

Each spec bundle follows Cursor Sovereign Spec Kit format:

```
specs/<initiative-name>/
├── 00_INDEX.md                  # Spec bundle index
├── 01_product_requirements.md   # Business requirements
├── 02_technical_specification.md
├── 03_implementation_plan.md
├── 04_test_plan.md
├── 05_deployment_plan.md
└── artifacts/                   # Supporting artifacts
```

---

## How to Contribute

### Creating New Portfolio Initiative

1. **Reference strategy**: Link to `STRAT-*` objective
2. **Generate unique ID**: Use `PORT-YYYY-NNN` format
3. **Create spec bundle**: Follow Sovereign Spec Kit structure
4. **Add to backlog**: Prioritize with business value score
5. **Update roadmap**: Place on quarterly timeline
6. **Update traceability index**: Add to `docs/TRACEABILITY_INDEX.yaml`

### Reviewing Portfolio Initiatives

- **Strategic Alignment**: Does this execute a strategic objective?
- **Business Value**: Is ROI clearly articulated and measurable?
- **Scope Clarity**: Are requirements unambiguous and testable?
- **Resource Availability**: Can we staff this with current capacity?
- **Risk Assessment**: Have dependencies and blockers been identified?

---

## PPM Framework

### Investment Buckets

```yaml
investment_buckets:
  strategic_growth: 40%      # New capabilities, competitive advantage
  operational_efficiency: 30% # Automation, process improvement
  compliance_risk: 20%        # Regulatory, security, governance
  technical_debt: 10%         # Refactoring, upgrades, maintenance
```

### Value Realization Tracking

Each initiative tracked through:
1. **Investment**: Effort estimate (hours) + resource cost
2. **Delivery**: Actual completion vs planned
3. **Outcomes**: Measured business value achieved
4. **ROI**: (Value achieved - Investment) / Investment

---

## Key Portfolio Initiatives (2026-Q1)

### Active Initiatives

| ID | Name | Status | Priority | Value | Effort | Quarter |
|----|------|--------|----------|-------|--------|---------|
| PORT-2026-007 | Odoo.sh-Grade Parity | In Progress | P0 | 90 | 120h | Q1 |
| PORT-2026-008 | BIR Compliance Automation | In Progress | P0 | 85 | 80h | Q1 |
| PORT-2026-009 | AI Document Intelligence | Planned | P1 | 80 | 100h | Q1 |

### Backlog (Next Quarter)

- PORT-2026-010: Multi-Agency Payroll Expansion
- PORT-2026-011: Real-time Analytics Dashboard
- PORT-2026-012: Vendor Portal with Privacy Controls

---

## Success Metrics

Portfolio layer effectiveness measured by:

1. **On-Time Delivery**: % of initiatives delivered by target date (Target: 80%)
2. **Value Realization**: Actual business value vs estimated (Target: 90%+)
3. **Strategic Coverage**: % of strategic objectives with active initiatives (Target: 100%)
4. **Portfolio Health**: Initiatives on-track vs at-risk ratio (Target: 4:1)

---

## References

- **Strategy Layer**: `docs/strategy/README.md`
- **Process Layer**: `docs/process/README.md`
- **Control Layer**: `docs/control/README.md`
- **Evidence Layer**: `docs/evidence/README.md`
- **Traceability Index**: `docs/TRACEABILITY_INDEX.yaml`
- **Spec Kit Template**: `templates/spec-kit/`

---

*Last updated: 2026-02-12*
