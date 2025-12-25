# IPAI Module Suite - Security Model

## Overview

The IPAI module suite implements comprehensive security controls through:
- **Role-Based Access Control (RBAC)**: Hierarchical security groups with implied permissions
- **Record Rules**: Row-level security filtering data by user, team, or organizational context
- **Model Access Rights**: CRUD permissions at the model level (ir.model.access.csv)
- **Field-Level Security**: Restricted fields via groups attribute in view definitions
- **Multi-Agency Support**: Data isolation for multi-organization deployments

**Odoo Version**: 18.0 Community Edition
**Production Database**: `odoo` (159.223.75.148)
**Security Philosophy**: Least privilege with role escalation paths

---

## Unified Security Roles Matrix

### Standard Security Hierarchy

All IPAI modules follow a consistent 3-tier security model:

| Role Level | Permissions | Use Cases |
|------------|-------------|-----------|
| **User** | Read own data, create/edit own records, submit for approval | Employees, team members, general users |
| **Manager** | All User permissions + approve/manage team data | Supervisors, department heads, team leads |
| **Administrator** | All Manager permissions + configure module, delete records | System admins, module owners, IT staff |

### Cross-Module Unified Roles

| Unified Role | Finance Modules | Asset Management | Expense Management | WorkOS/Collaboration |
|--------------|----------------|------------------|-------------------|---------------------|
| **Admin** | Finance Director | Asset Administrator | Finance Director | Workspace Admin |
| **Manager** | Finance Manager | Asset Manager | Expense Manager | Team Lead |
| **User** | Accountant | Asset User | Employee | Collaborator |
| **Viewer** | Auditor | - | - | Guest |

---

## Per-Module Security Groups

### Finance Layer

#### ipai_finance_ppm (Finance Project Portfolio Management)

**Security Groups**: Uses standard Odoo groups

| Group | Technical ID | Access Level | Description |
|-------|-------------|--------------|-------------|
| User | `base.group_user` | Read/Write | All authenticated users can manage finance tasks |

**Record Rules**: None (all users have full access)

**Models Protected**:
- `ipai.finance.person` - Finance team members
- `ipai.finance.task.template` - Task templates for month-end closing
- `ipai.bir.form.schedule` - BIR filing schedule and deadlines
- `ipai.bir.process.step` - BIR process workflow steps
- `finance.ppm.dashboard` - Read-only dashboard access
- `finance.bir.deadline` - BIR deadline tracking

**Access Pattern**:
```csv
model,group,read,write,create,delete
ipai.finance.person,base.group_user,✓,✓,✓,✓
finance.ppm.dashboard,base.group_user,✓,✗,✗,✗
```

**TODO**: Implement role-based access for Finance Supervisor, Senior Finance Manager, Finance Director.

---

#### ipai_expense (Expense & Travel Management)

**Security Groups**:

| Group | Technical ID | Implied Groups | Description |
|-------|-------------|----------------|-------------|
| Employee (User) | `group_ipai_expense_user` | `hr_expense.group_hr_expense_user` | Create and submit own expenses |
| Manager | `group_ipai_expense_manager` | Employee + `hr_expense.group_hr_expense_team_approver` | Approve team expenses |
| Finance Director | `group_ipai_expense_finance` | Manager + `hr_expense.group_hr_expense_manager` | Approve all, post to GL |

**Record Rules**:

1. **Employee: Own Expenses Only**
   - Domain: `[('employee_id.user_id', '=', user.id)]`
   - Permissions: Read, Write, Create, Delete (own records only)

2. **Manager: Team Expenses**
   - Domain: `[('employee_id.parent_id.user_id', '=', user.id)]`
   - Permissions: Read, Write (team records, cannot create for others)

3. **Finance: All Expenses**
   - Domain: `[(1, '=', 1)]` (no filtering)
   - Permissions: Read, Write, Create, Delete (all records)

**Models Protected**:
- `hr.expense` - Individual expense lines
- `ipai.travel.request` - Travel request forms
- `hr.expense.sheet` - Expense reports (inherited from `hr_expense`)

**Workflow Gates**:
- **Draft → Submitted**: Employee-initiated
- **Submitted → Approved**: Manager-approved (requires `group_ipai_expense_manager`)
- **Approved → Posted**: Finance-posted (requires `group_ipai_expense_finance`)

**Access Pattern**:
```
Employee (RIM):
  - Can see: Own expenses (employee_id.user_id = RIM's user ID)
  - Can edit: Own draft expenses
  - Can submit: Own expenses for approval

Manager (CKVC):
  - Can see: RIM's expenses (RIM.parent_id = CKVC)
  - Can approve: Team expenses up to threshold
  - Cannot create: Expenses for team members

Finance (JAP):
  - Can see: All expenses (no filtering)
  - Can approve: Any expense (override manager approval)
  - Can post: Expenses to general ledger
  - Can delete: Any expense record
```

---

#### ipai_bir_compliance (BIR Tax Filing Compliance)

**Security Groups**:

| Group | Technical ID | Implied Groups | Description |
|-------|-------------|----------------|-------------|
| User | `group_bir_user` | - | View BIR forms and schedules |
| Finance Officer | `group_bir_finance` | User | Prepare and file BIR forms |
| Finance Director | `group_bir_director` | Finance Officer | Approve BIR filings |

**Record Rules**:

1. **User: Read-Only BIR Forms**
   - Domain: `[(1, '=', 1)]`
   - Permissions: Read (no write/create/delete)

2. **Finance Officer: Prepare BIR Forms**
   - Domain: `[('state', 'in', ['draft', 'in_progress'])]`
   - Permissions: Read, Write, Create (draft and in-progress forms)

3. **Finance Director: Approve All**
   - Domain: `[(1, '=', 1)]`
   - Permissions: Read, Write, Create, Delete (all states)

**Models Protected**:
- `ipai.bir.form` - BIR form definitions (1601-C, 2550Q, etc.)
- `ipai.bir.schedule` - Filing schedule and deadlines
- `ipai.bir.computation` - Tax computation worksheets

**Workflow Gates**:
- **Draft → In Progress**: Finance Officer-initiated
- **In Progress → Review**: Finance Officer-completed
- **Review → Approved**: Finance Director-approved
- **Approved → Filed**: Finance Officer-submitted to BIR

**Multi-Employee Security**:

8 employees tracked separately:
- RIM (Rafael Martinez) - Employee
- CKVC (Christian Cruz) - Manager
- BOM (Brian Mercado) - Employee
- JPAL (Joseph Palma) - Employee
- JLI (Justin Li) - Employee
- JAP (Jake Palma) - Finance Director
- LAS (Luis Santos) - Employee
- RMQB (Robert Quebral) - Employee

Record rules filter by `employee_id` to ensure employees only see their own tax records.

---

### Asset Management Layer

#### ipai_assets (Equipment/Asset Checkout Tracking)

**Security Groups**:

| Group | Technical ID | Implied Groups | Description |
|-------|-------------|----------------|-------------|
| Asset User | `group_assets_user` | - | Check out and reserve assets |
| Asset Manager | `group_assets_manager` | Asset User | Manage assets, approve checkouts |
| Asset Administrator | `group_assets_admin` | Asset Manager | Full configuration access |

**Record Rules**: None (model access controls are sufficient)

**Models Protected**:
- `ipai.asset.category` - Asset categories
- `ipai.asset` - Asset master records
- `ipai.asset.checkout` - Checkout transactions
- `ipai.asset.reservation` - Asset reservations

**Access Pattern**:
```csv
model,User,Manager,Admin
ipai.asset.category,R,RWC,RWCD
ipai.asset,R,RWC,RWCD
ipai.asset.checkout,RWC,RWCD,RWCD
ipai.asset.reservation,RWC,RWCD,RWCD
```
*R=Read, W=Write, C=Create, D=Delete*

**Workflow Gates**:
- **Available → Reserved**: User-initiated reservation
- **Reserved → Checked Out**: Manager-approved checkout
- **Checked Out → Returned**: User-initiated return
- **Returned → Available**: Manager-confirmed availability

---

### WorkOS Layer

#### ipai_workspace_core (Workspace Collaboration Core)

**Security Groups**: Uses standard Odoo groups

| Group | Technical ID | Access Level | Description |
|-------|-------------|--------------|-------------|
| User | `base.group_user` | Read/Write | All authenticated users |

**Record Rules**: None (collaborative environment, no data isolation)

**Models Protected**:
- `ipai.workspace.page` - Workspace pages
- `ipai.workspace.block` - Content blocks
- `ipai.workspace.database` - Workspace databases

**Access Pattern**:
```
Collaborative Model:
  - All users can create pages
  - All users can edit pages
  - No record-level restrictions (like Notion)
  - Sharing/permissions managed at page level (future enhancement)
```

**TODO**: Implement page-level permissions (public, private, shared).

---

## Record Rule Patterns

### Pattern 1: Own Records Only (Employee Model)

**Use Case**: Employees can only see/edit their own records (expenses, timesheets, tasks).

**Domain Filter**:
```python
[('employee_id.user_id', '=', user.id)]
```

**Example**: `ipai_expense` - Employees see only their own expenses.

---

### Pattern 2: Team Records (Manager Model)

**Use Case**: Managers can see/edit records from their direct reports.

**Domain Filter**:
```python
[('employee_id.parent_id.user_id', '=', user.id)]
```

**Example**: `ipai_expense` - Managers see expenses from team members where `employee.parent_id` points to the manager.

---

### Pattern 3: All Records (Admin Model)

**Use Case**: Administrators/Finance Directors can see all records without filtering.

**Domain Filter**:
```python
[(1, '=', 1)]  # Always true - no filtering
```

**Example**: `ipai_expense` - Finance Directors see all expenses across all employees.

---

### Pattern 4: Conditional Access by State

**Use Case**: Users can edit draft records, managers can approve submitted records.

**Domain Filters**:
```python
# Users: Draft and in-progress only
[('state', 'in', ['draft', 'in_progress']), ('employee_id.user_id', '=', user.id)]

# Managers: Submitted records from team
[('state', '=', 'submitted'), ('employee_id.parent_id.user_id', '=', user.id)]

# Finance: All states
[(1, '=', 1)]
```

**Example**: `ipai_bir_compliance` - Finance Officers prepare drafts, Finance Director approves all states.

---

## Cross-Module Interactions

### Finance PPM + Expense Integration

**Scenario**: Finance PPM creates month-end closing tasks, Expense module provides data.

**Security Considerations**:
- Finance PPM tasks are visible to all users (`base.group_user`)
- Expense data is filtered by employee (`employee_id.user_id = user.id`)
- Finance Director can see PPM tasks AND all expenses (requires both `group_bir_director` + `group_ipai_expense_finance`)

**Access Control Flow**:
```
1. Finance Supervisor (RIM) creates month-end closing task in Finance PPM
   → Requires: base.group_user
   → Can see: All PPM tasks

2. Accountant (BOM) submits expense for reimbursement
   → Requires: group_ipai_expense_user
   → Can see: Own expenses only

3. Finance Director (JAP) reviews expense as part of month-end close
   → Requires: group_ipai_expense_finance + base.group_user
   → Can see: All expenses + all PPM tasks
```

---

### Asset Management + Project Integration

**Scenario**: Project tasks require asset checkout (e.g., camera equipment for client shoot).

**Security Considerations**:
- Project tasks are visible to project members (`project.group_project_user`)
- Asset checkouts require `group_assets_user` (separate from project access)
- Users need BOTH groups to link assets to projects

**Access Control Flow**:
```
1. Project User creates task "Client Photoshoot"
   → Requires: project.group_project_user
   → Can see: Own project tasks

2. Project User reserves camera equipment
   → Requires: group_assets_user
   → Can see: Available assets, own checkouts

3. Asset Manager approves camera checkout
   → Requires: group_assets_manager
   → Can see: All checkouts, approve/deny
```

---

## Multi-Agency Security (Production)

**Current Production Setup**:
- **Database**: `odoo` (single database, multi-agency via record rules)
- **Agencies**: 8 employees representing different agencies/brands
- **Security Model**: Employee-based filtering (`employee_id.user_id`)

**Multi-Agency Record Rules**:

### Agency A (CKVC's Team)
```python
# Domain for Agency A Manager (CKVC)
[('employee_id.parent_id.user_id', '=', CKVC_user_id)]

# Employees under CKVC: RIM, BOM, JPAL
```

### Agency B (JAP's Team)
```python
# Domain for Agency B Finance Director (JAP)
[(1, '=', 1)]  # Finance Director sees all agencies

# Employees under JAP: JLI, LAS, RMQB
```

**Cross-Agency Access**:
- Finance Director (JAP) can see ALL agencies (domain: `[(1, '=', 1)]`)
- Managers (CKVC) can only see their own agency (domain: `[('employee_id.parent_id.user_id', '=', user.id)]`)
- Employees (RIM, BOM, JPAL) can only see their own records (domain: `[('employee_id.user_id', '=', user.id)]`)

**Production Verification**:
```sql
-- Check employee assignments
SELECT u.login, e.name, e.parent_id, e.company_id
FROM res_users u
JOIN hr_employee e ON e.user_id = u.id
WHERE u.login IN ('RIM', 'CKVC', 'BOM', 'JPAL', 'JLI', 'JAP', 'LAS', 'RMQB');

-- Verify expense visibility (as RIM)
SET SESSION ROLE 'RIM';
SELECT COUNT(*) FROM hr_expense;  -- Should return only RIM's expenses

-- Verify expense visibility (as CKVC - Manager)
SET SESSION ROLE 'CKVC';
SELECT COUNT(*) FROM hr_expense;  -- Should return CKVC + team (RIM, BOM, JPAL) expenses

-- Verify expense visibility (as JAP - Finance Director)
SET SESSION ROLE 'JAP';
SELECT COUNT(*) FROM hr_expense;  -- Should return all 24 expenses
```

---

## Security Audit Procedures

### 1. Group Assignment Verification

**Objective**: Ensure users have correct group memberships.

**SQL Query**:
```sql
-- List all IPAI security groups and their members
SELECT
  g.name AS group_name,
  g.full_name AS full_name,
  u.login AS user_login,
  u.name AS user_name
FROM res_groups g
LEFT JOIN res_groups_users_rel gur ON gur.gid = g.id
LEFT JOIN res_users u ON u.id = gur.uid
WHERE g.name LIKE '%ipai%' OR g.name LIKE '%asset%' OR g.name LIKE '%expense%'
ORDER BY g.name, u.login;
```

**Expected Results**:
- All employees should have `group_ipai_expense_user`
- Managers (CKVC) should have `group_ipai_expense_manager`
- Finance Directors (JAP) should have `group_ipai_expense_finance`

---

### 2. Record Rule Effectiveness Test

**Objective**: Verify record rules correctly filter data by user.

**Test Procedure**:
```bash
# Test as Employee (RIM)
odoo-bin shell -d odoo -c /etc/odoo/odoo.conf
>>> env = odoo.api.Environment(cr, RIM_user_id, {})
>>> expenses = env['hr.expense'].search([])
>>> print(f"RIM sees {len(expenses)} expenses")  # Should see only own expenses

# Test as Manager (CKVC)
>>> env = odoo.api.Environment(cr, CKVC_user_id, {})
>>> expenses = env['hr.expense'].search([])
>>> print(f"CKVC sees {len(expenses)} expenses")  # Should see team expenses (RIM, BOM, JPAL)

# Test as Finance Director (JAP)
>>> env = odoo.api.Environment(cr, JAP_user_id, {})
>>> expenses = env['hr.expense'].search([])
>>> print(f"JAP sees {len(expenses)} expenses")  # Should see all 24 expenses
```

---

### 3. Model Access Rights Audit

**Objective**: Ensure ir.model.access.csv correctly restricts CRUD operations.

**SQL Query**:
```sql
-- List all IPAI model access rules
SELECT
  a.name AS access_rule,
  m.model AS model_name,
  g.name AS group_name,
  a.perm_read AS read,
  a.perm_write AS write,
  a.perm_create AS create,
  a.perm_unlink AS delete
FROM ir_model_access a
JOIN ir_model m ON m.id = a.model_id
LEFT JOIN res_groups g ON g.id = a.group_id
WHERE m.model LIKE 'ipai%' OR m.model LIKE 'finance%'
ORDER BY m.model, g.name;
```

**Red Flags**:
- Models with no access rules (defaults to admin-only)
- Conflicting rules (same model, same group, different permissions)
- Missing group assignments (access rule with `group_id = NULL`)

---

### 4. Privilege Escalation Test

**Objective**: Verify users cannot escalate privileges via record manipulation.

**Test Cases**:

**Test 1: Employee Cannot Approve Own Expense**
```python
# As Employee (RIM)
env = odoo.api.Environment(cr, RIM_user_id, {})
expense = env['hr.expense'].search([('employee_id.user_id', '=', RIM_user_id)], limit=1)
expense.write({'state': 'approved'})  # Should raise AccessError
```

**Expected**: `AccessError: You do not have permission to approve expenses.`

**Test 2: Manager Cannot Post Expenses to GL**
```python
# As Manager (CKVC)
env = odoo.api.Environment(cr, CKVC_user_id, {})
expense_sheet = env['hr.expense.sheet'].search([('state', '=', 'approve')], limit=1)
expense_sheet.action_sheet_move_create()  # Should raise AccessError
```

**Expected**: `AccessError: Only Finance Directors can post expenses to the general ledger.`

**Test 3: User Cannot Modify BIR Forms in 'Filed' State**
```python
# As Finance Officer
env = odoo.api.Environment(cr, finance_officer_user_id, {})
bir_form = env['ipai.bir.form'].search([('state', '=', 'filed')], limit=1)
bir_form.write({'amount': 99999.99})  # Should raise AccessError
```

**Expected**: `AccessError: Cannot modify filed BIR forms. Contact Finance Director.`

---

## Common Security Issues & Fixes

### Issue 1: Users Cannot See Own Records

**Symptom**: Employee (RIM) logs in, sees empty expense list despite having submitted expenses.

**Root Cause**: Missing record rule OR incorrect domain filter.

**Diagnosis**:
```sql
-- Check if record rule exists
SELECT * FROM ir_rule
WHERE name LIKE '%expense%' AND name LIKE '%own%';

-- Check domain filter
SELECT domain_force FROM ir_rule
WHERE name = 'Employee: Own Expenses Only';
-- Expected: [('employee_id.user_id', '=', user.id)]
```

**Fix**:
```xml
<!-- Ensure record rule is correctly defined in security XML -->
<record id="expense_rule_user_own" model="ir.rule">
  <field name="name">Employee: Own Expenses Only</field>
  <field name="model_id" ref="hr_expense.model_hr_expense"/>
  <field name="domain_force">[('employee_id.user_id', '=', user.id)]</field>
  <field name="groups" eval="[(4, ref('group_ipai_expense_user'))]"/>
  <field name="perm_read">True</field>
  <field name="perm_write">True</field>
  <field name="perm_create">True</field>
  <field name="perm_unlink">True</field>
</record>
```

**Verification**:
```bash
# Reinstall module to reload security rules
odoo -d odoo -i ipai_expense --stop-after-init

# Test as RIM
odoo-bin shell -d odoo
>>> env = odoo.api.Environment(cr, RIM_user_id, {})
>>> expenses = env['hr.expense'].search([])
>>> print(len(expenses))  # Should return RIM's expense count
```

---

### Issue 2: Manager Cannot Approve Team Expenses

**Symptom**: Manager (CKVC) cannot see "Approve" button on team member (RIM) expenses.

**Root Cause**: Missing group assignment OR incorrect implied_ids in group definition.

**Diagnosis**:
```sql
-- Check if CKVC has manager group
SELECT u.login, g.name
FROM res_users u
JOIN res_groups_users_rel gur ON gur.uid = u.id
JOIN res_groups g ON g.id = gur.gid
WHERE u.login = 'CKVC' AND g.name LIKE '%expense%';

-- Expected: group_ipai_expense_manager (which implies group_ipai_expense_user)
```

**Fix**:
```xml
<!-- Ensure manager group correctly implies user group -->
<record id="group_ipai_expense_manager" model="res.groups">
  <field name="name">Manager</field>
  <field name="category_id" ref="module_category_ipai_expense"/>
  <field name="implied_ids" eval="[(4, ref('group_ipai_expense_user')), (4, ref('hr_expense.group_hr_expense_team_approver'))]"/>
  <field name="comment">Can view and approve expenses for direct reports</field>
</record>
```

**Verification**:
```bash
# Upgrade module to reload groups
odoo -d odoo -u ipai_expense --stop-after-init

# Verify CKVC has both groups
odoo-bin shell -d odoo
>>> user = env['res.users'].search([('login', '=', 'CKVC')])
>>> print(user.groups_id.mapped('name'))
# Expected: ['Employee (User)', 'Manager', 'Expense / Team Approver']
```

---

### Issue 3: Finance Director Cannot See All Expenses

**Symptom**: Finance Director (JAP) only sees own expenses, not all 24 expenses.

**Root Cause**: Record rule with domain filter instead of `[(1, '=', 1)]`.

**Diagnosis**:
```sql
-- Check Finance Director record rule
SELECT domain_force FROM ir_rule
WHERE name = 'Finance: All Expenses';

-- If domain is [('employee_id.user_id', '=', user.id)], it's WRONG
-- Expected: [(1, '=', 1)]
```

**Fix**:
```xml
<!-- Ensure Finance Director rule has no domain filtering -->
<record id="expense_rule_finance_all" model="ir.rule">
  <field name="name">Finance: All Expenses</field>
  <field name="model_id" ref="hr_expense.model_hr_expense"/>
  <field name="domain_force">[(1, '=', 1)]</field>
  <field name="groups" eval="[(4, ref('group_ipai_expense_finance'))]"/>
  <field name="perm_read">True</field>
  <field name="perm_write">True</field>
  <field name="perm_create">True</field>
  <field name="perm_unlink">True</field>
</record>
```

**Verification**:
```bash
# Test as JAP
odoo-bin shell -d odoo
>>> env = odoo.api.Environment(cr, JAP_user_id, {})
>>> expenses = env['hr.expense'].search([])
>>> print(len(expenses))  # Should return 24 (all expenses in production)
```

---

## Production Security Checklist

**Pre-Deployment** (must complete before go-live):

- [ ] All security groups defined in `security/*.xml`
- [ ] All model access rules defined in `security/ir.model.access.csv`
- [ ] All record rules tested with SQL queries (own/team/all patterns)
- [ ] Group hierarchies verified (`implied_ids` correct)
- [ ] Multi-agency isolation confirmed (employee-based filtering)
- [ ] Privilege escalation tests passed (users cannot bypass approval workflows)

**Post-Deployment** (verify after module install/upgrade):

- [ ] Security groups visible in Settings → Users & Companies → Groups
- [ ] Test users can log in and see appropriate data
- [ ] Manager approval workflows function correctly
- [ ] Finance Director can access all records
- [ ] Employees cannot see other employees' data (unless manager)
- [ ] Record rule audit queries return expected results

**Monthly Audit** (security review):

- [ ] User-group assignments reviewed (new employees, promotions, terminations)
- [ ] Record rule effectiveness tested (spot-check 3 employees)
- [ ] Model access rights audit (no orphaned rules)
- [ ] Privilege escalation tests re-run (security regression check)

---

## Security Best Practices

### 1. Principle of Least Privilege
- **Default**: Deny all access unless explicitly granted
- **Implementation**: Start with no groups, add groups incrementally
- **Verification**: Test with new user account (should see nothing initially)

### 2. Defense in Depth
- **Model Access**: First line of defense (ir.model.access.csv)
- **Record Rules**: Second line (row-level filtering)
- **Field-Level**: Third line (groups attribute in views)
- **Business Logic**: Fourth line (Python constraints in models)

### 3. Regular Security Audits
- **Monthly**: User-group assignments review
- **Quarterly**: Record rule effectiveness testing
- **Annually**: Full security model review and update

### 4. Document Security Decisions
- **Why**: Explain rationale for group hierarchies
- **What**: Document which roles have which permissions
- **How**: Include verification procedures for each rule

### 5. Test Security Changes
- **Unit Tests**: Write tests for record rules
- **Integration Tests**: Test cross-module security interactions
- **User Acceptance**: Have real users validate access levels

---

## Next Steps

1. **Review [OPERATIONS_RUNBOOK.md](./OPERATIONS_RUNBOOK.md)** for deployment procedures and security verification
2. **Implement Missing Security**: Add Finance Supervisor, Senior Finance Manager roles to `ipai_finance_ppm`
3. **Enhance WorkOS Security**: Add page-level permissions (public, private, shared)
4. **Automate Security Audits**: Create cron job to run monthly security audit queries
5. **Document Security Exceptions**: Maintain changelog of security model changes

---

## Support

For security issues:
1. Check [GitHub Issues](https://github.com/jgtolentino/odoo-ce/issues?q=label%3Asecurity)
2. Review [CHANGELOG.md](./CHANGELOG.md) for recent security updates
3. Contact: Jake Tolentino (Finance SSC Manager / Odoo Developer)
