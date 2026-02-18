# IPAI PPM + OKR (CE-only)

Complete enterprise-grade Portfolio/Program/Project Management with OKR tracking for Odoo CE.

## Features

### Portfolio & Program Governance

- **Portfolio Management**: Strategic themes, value statements, RAG status
- **Program Management**: Multi-project programs with governance
- **Project Meta**: Business case, strategic scoring, budget tracking

### Project Execution

- **Workstreams**: Organize work into logical streams
- **Epics**: Large features with story points
- **Risk Management**: Probability × Impact scoring with mitigation plans
- **Issue Tracking**: Severity-based issue management
- **Change Requests**: Impact analysis and approval workflow

### Resource & Budget

- **Resource Allocation**: Role-based allocation with cost/bill rates
- **Budget Tracking**: CAPEX/OPEX budgets with forecast vs actual
- **Budget Lines**: Categorized budget items (labor, software, vendor, travel)

### OKR System

- **Cycles**: Quarterly or custom OKR cycles
- **Objectives**: Hierarchical objectives with portfolio/program/project scoping
- **Key Results**: Measurable KRs with baseline/target/current tracking
- **Check-ins**: Regular progress updates with confidence scoring
- **Initiatives**: Link OKRs to actual projects and tasks

## Architecture

### Data Model

See [`spec/ppm_okr.dbml`](spec/ppm_okr.dbml) for the complete DBML schema.

**Key Relationships**:

```
Portfolio
  └─ Program
       └─ Project (via ppm.project.meta)
            ├─ Workstreams
            │    └─ Epics
            │         └─ Tasks
            ├─ Risks
            ├─ Issues
            ├─ Change Requests
            ├─ Resource Allocations
            └─ Budget

OKR Cycle
  └─ Objectives (can scope to Portfolio/Program/Project)
       ├─ Key Results
       │    ├─ Check-ins
       │    └─ Initiatives → Projects/Tasks
       └─ Child Objectives
```

### Models

**PPM Models**:

- `ppm.portfolio` - Portfolio governance
- `ppm.program` - Program management
- `ppm.project.meta` - 1:1 extension of `project.project`
- `ppm.workstream` - Work organization
- `ppm.epic` - Large features
- `ppm.risk` - Risk register
- `ppm.issue` - Issue tracking
- `ppm.change.request` - Change management
- `ppm.budget` + `ppm.budget.line` - Budget tracking
- `ppm.resource.role` + `ppm.resource.allocation` - Resource planning

**OKR Models**:

- `okr.cycle` - OKR time periods
- `okr.objective` - Objectives with progress tracking
- `okr.key.result` - Measurable key results
- `okr.checkin` - Progress check-ins
- `okr.initiative` - Execution initiatives

## Installation

1. **Add to addons path**:

   ```bash
   # Ensure addons/ipai_ppm_okr is in your addons path
   ```

2. **Install module**:

   ```bash
   odoo-bin -d <database> -u ipai_ppm_okr --stop-after-init
   ```

3. **Verify installation**:
   ```sql
   -- Check tables created
   SELECT tablename FROM pg_tables
   WHERE schemaname = 'public'
   AND tablename LIKE 'ppm_%' OR tablename LIKE 'okr_%';
   ```

## Usage

### Creating BIR Projects

Use the automation script to create Month-End Closing and BIR Tax Filing projects:

```bash
export ODOO_URL="https://erp.insightpulseai.com"
export ODOO_DB="odoo"
export ODOO_USER="admin@Insightpulseai"
export ODOO_PASS="***"

python3 addons/ipai_ppm_okr/scripts/create_projects_monthend_bir.py
```

**Month-End Closing Stages**:

1. Preparation (1 day)
2. Review (0.5 day)
3. Approval (0.5 day)
4. Done

**BIR Tax Filing Stages**:

1. Preparation (BIR deadline − 4 business days)
2. Report Approval (BIR deadline − 2 business days)
3. Payment Approval (BIR deadline − 1 business day)
4. Filing & Payment (On or before BIR deadline)
5. Done

### Creating OKRs

1. **Create a Cycle**:

   ```python
   cycle = env['okr.cycle'].create({
       'name': 'Q1 2026',
       'start_date': '2026-01-01',
       'end_date': '2026-03-31',
       'state': 'active',
   })
   ```

2. **Create an Objective**:

   ```python
   objective = env['okr.objective'].create({
       'cycle_id': cycle.id,
       'title': 'Achieve 100% BIR compliance',
       'owner_user_id': env.user.id,
       'project_id': bir_project.id,  # Link to BIR project
   })
   ```

3. **Create Key Results**:

   ```python
   kr = env['okr.key.result'].create({
       'objective_id': objective.id,
       'title': '100% on-time BIR filings',
       'metric_type': 'percent',
       'baseline_value': 85.0,
       'target_value': 100.0,
       'current_value': 85.0,
   })
   ```

4. **Log Check-ins**:
   ```python
   env['okr.checkin'].create({
       'key_result_id': kr.id,
       'value': 92.0,  # Current progress
       'confidence': '4',
       'comment': 'Filed 11/12 returns on time this month',
   })
   ```

## Development

### Generate ERD

```bash
# Install dbdocs CLI
npm install -g dbdocs

# Generate ERD from DBML
dbdocs build addons/ipai_ppm_okr/spec/ppm_okr.dbml
```

### Testing

```bash
# Run module tests
odoo-bin -d test_db --test-enable --stop-after-init -u ipai_ppm_okr
```

## License

LGPL-3.0

## Support

For issues or questions, contact the IPAI Platform team.
