# Odoo MCP Server - Product Requirements

## Overview

MCP server that exposes Odoo CE 18.0 functionality through natural language interface, eliminating manual UI navigation for routine finance operations.

## User Stories

### Finance Operations

**US-001: Create Journal Entry**
```
As a Finance Manager
I want Claude to create journal entries via conversation
So that I don't have to manually navigate Odoo's accounting UI

Acceptance:
- Claude can parse natural language JE specifications
- Supports multi-line entries with debit/credit validation
- Auto-populates tax codes for BIR compliance
- Returns Odoo move ID and audit trail link
```

**US-002: Query AP Aging**
```
As a Finance Manager
I want Claude to query vendor payables by aging bucket
So that I can get instant answers without running reports

Acceptance:
- Returns aging in standard buckets (current, 30, 60, 90, 90+ days)
- Filters by employee code or agency
- Includes vendor TIN and contact details
- Formatted as markdown table or JSON
```

**US-003: Multi-Employee Expense Processing**
```
As a Finance SSC Manager
I want Claude to process expenses for 8 employees in parallel
So that month-end close completes faster

Acceptance:
- Batch create expense records from OCR results
- Route to appropriate employee's approval queue
- Enforce employee-specific budgets and policies
- Generate consolidated summary report
```

### BIR Compliance

**US-004: Generate 1601-C Form**
```
As a Tax Compliance Officer
I want Claude to generate monthly withholding tax returns
So that I meet BIR deadlines without manual data entry

Acceptance:
- Queries all withholding transactions for period
- Aggregates by ATC (tax code) per employee
- Generates eBIRForms-compliant JSON output
- Creates Odoo document attachment (PDF + dat file)
```

**US-005: BIR Deadline Monitoring**
```
As a Finance Director
I want Claude to alert me about upcoming BIR deadlines
So that I never miss filing deadlines

Acceptance:
- Queries `bir.filing_deadline` model
- Returns deadlines within next 7 days
- Includes form name, deadline date, responsible person
- Triggers Mattermost notification if <3 days
```

### Project Management

**US-006: Month-End Task Orchestration**
```
As a Finance Manager
I want Claude to create month-end close task checklist
So that all closing steps are tracked systematically

Acceptance:
- Creates task hierarchy from template
- Assigns to appropriate team members
- Sets dependencies (e.g., bank recon before JEs)
- Tracks completion percentage in real-time
```

**US-007: Query Project Task Status**
```
As a Finance SSC Manager
I want Claude to query overdue tasks across all employees
So that I can identify bottlenecks

Acceptance:
- Filters tasks by status, assignee, deadline
- Groups by employee code or project
- Includes task priority and estimated hours
- Returns markdown table with actionable links
```

## Tool Specifications

### Core Tools (Priority 1)

#### odoo:account:create-journal-entry
```typescript
{
  name: "odoo:account:create-journal-entry",
  description: "Create a journal entry (account.move)",
  inputSchema: {
    date: "YYYY-MM-DD",
    journal_id: number,  // or journal code
    ref: string,
    line_ids: Array<{
      account_id: number,  // or account code
      name: string,
      debit: number,
      credit: number,
      partner_id?: number,
      tax_ids?: number[]
    }>,
    employee_code?: string,  // RIM, CKVC, etc.
    agency_id?: number
  }
}
```

#### odoo:partner:query-vendors
```typescript
{
  name: "odoo:partner:query-vendors",
  description: "Query vendors with optional filters",
  inputSchema: {
    filters?: {
      name?: string,          // Fuzzy search
      tin?: string,           // Exact match
      payment_term?: string,  // '30 days', '60 days'
      employee_code?: string, // Assigned employee
      is_active?: boolean
    },
    fields?: string[],  // Default: name, tin, email, phone
    limit?: number,     // Default: 100
    offset?: number
  }
}
```

#### odoo:account:query-ap-aging
```typescript
{
  name: "odoo:account:query-ap-aging",
  description: "Get accounts payable aging report",
  inputSchema: {
    as_of_date: "YYYY-MM-DD",
    employee_code?: string,
    agency_id?: number,
    buckets?: number[],  // Default: [0, 30, 60, 90]
    include_details?: boolean  // Include invoice breakdown
  }
}
```

### BIR Compliance Tools (Priority 2)

#### odoo:bir:generate-1601c
```typescript
{
  name: "odoo:bir:generate-1601c",
  description: "Generate BIR Form 1601-C (Monthly Withholding Tax)",
  inputSchema: {
    period: "YYYY-MM",
    employee_code: string,  // REQUIRED
    tin: string,            // Company TIN
    rdo_code: string,       // e.g., "039"
    include_alphalist?: boolean
  }
}
```

#### odoo:bir:query-deadlines
```typescript
{
  name: "odoo:bir:query-deadlines",
  description: "Query upcoming BIR filing deadlines",
  inputSchema: {
    days_ahead?: number,  // Default: 7
    form_types?: string[],  // Filter by form (1601-C, 2550Q, etc.)
    employee_code?: string,
    status?: "pending" | "filed" | "overdue"
  }
}
```

### Project Management Tools (Priority 3)

#### odoo:project:create-task
```typescript
{
  name: "odoo:project:create-task",
  description: "Create project task (e.g., month-end checklist)",
  inputSchema: {
    project_id: number,
    name: string,
    description?: string,
    user_id?: number,     // Assignee (from employee_code)
    date_deadline?: "YYYY-MM-DD",
    parent_id?: number,   // For subtasks
    employee_code?: string
  }
}
```

#### odoo:project:query-tasks
```typescript
{
  name: "odoo:project:query-tasks",
  description: "Query project tasks with filters",
  inputSchema: {
    filters?: {
      employee_code?: string,
      project_id?: number,
      status?: "pending" | "in_progress" | "done",
      overdue?: boolean,
      priority?: "low" | "medium" | "high"
    },
    sort_by?: "deadline" | "priority" | "created_date",
    limit?: number
  }
}
```

### Utility Tools (Priority 4)

#### odoo:core:search-records
```typescript
{
  name: "odoo:core:search-records",
  description: "Generic search across any Odoo model",
  inputSchema: {
    model: string,          // e.g., "account.move"
    domain: Array<[string, string, any]>,  // Odoo domain
    fields?: string[],
    limit?: number,
    offset?: number,
    order?: string          // e.g., "date desc"
  }
}
```

#### odoo:core:execute-action
```typescript
{
  name: "odoo:core:execute-action",
  description: "Execute Odoo server action or button",
  inputSchema: {
    model: string,
    record_id: number,
    action: string,         // e.g., "action_post", "action_validate"
    context?: Record<string, any>
  }
}
```

## Data Model Extensions

### Employee Code Mapping

**New Odoo Model**: `ipai.employee_code`

```python
class EmployeeCode(models.Model):
    _name = 'ipai.employee_code'
    _description = 'Employee Code to User Mapping'

    code = fields.Char(required=True, index=True)  # RIM, CKVC, etc.
    user_id = fields.Many2one('res.users', required=True)
    agency_ids = fields.Many2many('res.partner', string='Assigned Agencies')
    active = fields.Boolean(default=True)
```

**Usage in MCP Tools**:
```typescript
// Resolve employee code to user_id before operations
const userId = await resolveEmployeeCode("RIM");

// Execute operations with proper context
await odoo.execute_kw(
  'account.move', 'create', [moveData],
  { su: true, allowed_company_ids: companyIds, uid: userId }
);
```

### Multi-Agency Context

**Odoo Context Keys**:
- `allowed_company_ids`: List of company IDs user can access
- `employee_code`: Custom context for filtering/routing
- `force_company`: Override default company for operation

**RLS Implementation**:
```python
# In Odoo model security
@api.model
def _search(self, args, ...):
    args = self._apply_employee_code_filter(args)
    return super()._search(args, ...)

def _apply_employee_code_filter(self, args):
    employee_code = self.env.context.get('employee_code')
    if employee_code:
        employee = self.env['ipai.employee_code'].search([('code', '=', employee_code)])
        if employee:
            args += [('create_uid', '=', employee.user_id.id)]
    return args
```

## Integration Workflows

### 1. Expense Processing Pipeline
```
OCR Result → n8n Webhook → MCP Tool (odoo:expense:create)
                                ↓
                         Odoo Expense Record
                                ↓
                         Approval Queue (by employee)
                                ↓
                         n8n → Mattermost Notification
```

### 2. BIR Form Generation
```
Claude Command → MCP Tool (odoo:bir:generate-1601c)
                        ↓
                 Query Withholding Transactions
                        ↓
                 Aggregate by ATC
                        ↓
                 Generate JSON (eBIRForms format)
                        ↓
                 Attach to Odoo Document
                        ↓
                 Queue to Supabase (task_queue)
                        ↓
                 n8n → BIR Portal Upload
```

### 3. Month-End Closing
```
Claude: "Start month-end close for November 2025"
                        ↓
MCP Tool (odoo:project:create-task-hierarchy)
                        ↓
         ┌─────────────┴─────────────┐
         ▼                           ▼
  Bank Reconciliation        GL Reconciliation
         ↓                           ↓
  Accrual Journal Entries    Interco Eliminations
         ↓                           ↓
         └─────────────┬─────────────┘
                       ▼
              Trial Balance Lock
                       ↓
              Supabase Sync
                       ↓
              Superset Refresh
```

## Performance Targets

| Operation Type | Target (P95) | Current (Baseline) |
|----------------|--------------|---------------------|
| Simple query (1 record) | <500ms | TBD |
| Complex query (100 records) | <2s | TBD |
| Create journal entry | <3s | TBD |
| Batch expense creation (10 records) | <8s | TBD |
| BIR form generation | <15s | TBD |
| Task hierarchy creation (50 tasks) | <20s | TBD |

**Caching Strategy**:
- Chart of accounts: 1 hour TTL
- Partners/vendors: 30 minutes TTL
- BIR tax codes: 24 hours TTL
- Employee code mappings: 5 minutes TTL

## Error Handling Examples

### Invalid Employee Code
```json
{
  "error": "INVALID_EMPLOYEE_CODE",
  "message": "Employee code 'ABC' not found",
  "suggestions": ["RIM", "CKVC", "BOM", "JPAL", "JLI", "JAP", "LAS", "RMQB"],
  "actionable": "Use one of the valid employee codes above"
}
```

### Session Timeout
```json
{
  "error": "SESSION_EXPIRED",
  "message": "Odoo session expired, re-authenticating...",
  "retry": true,
  "attempt": 1,
  "max_retries": 3
}
```

### Insufficient Permissions
```json
{
  "error": "ACCESS_DENIED",
  "message": "User 'RIM' cannot create journal entries in company 'BOM'",
  "required_permission": "account.group_account_manager",
  "odoo_fault_code": "AccessError"
}
```

## Testing Strategy

### Unit Tests
- XML-RPC client connection/authentication
- Employee code resolution logic
- Domain filter construction
- Error parsing and retry logic

### Integration Tests
- Create/read/update/delete for each model
- Multi-employee context switching
- BIR form generation end-to-end
- n8n webhook triggering

### Load Tests
- 100 concurrent queries (simulated Claude requests)
- Batch operations (100+ records)
- Cache invalidation under load
- Connection pool exhaustion recovery

## Rollout Plan

### Phase 1: MVP (Week 1-2)
- ✅ Core CRUD tools (account.move, res.partner, project.task)
- ✅ Employee code mapping model
- ✅ Basic error handling and retries
- ✅ Local development setup

### Phase 2: BIR Integration (Week 3-4)
- ✅ BIR form generation tools (1601-C, 2550Q)
- ✅ Deadline monitoring
- ✅ Multi-employee batch operations
- ✅ n8n workflow triggers

### Phase 3: Optimization (Week 5-6)
- ✅ Caching layer (Redis)
- ✅ Connection pooling
- ✅ Performance profiling and tuning
- ✅ Load testing at scale

### Phase 4: Production (Week 7-8)
- ✅ Deploy to DigitalOcean App Platform
- ✅ SSE coordinator integration
- ✅ Monitoring and alerting
- ✅ User training and documentation

## Success Metrics

### Adoption
- 50% of JE creation via Claude (vs manual UI)
- 80% of AP aging queries via Claude
- 100% of BIR forms generated via automation

### Performance
- <2s query response time (P95)
- <5s mutation response time (P95)
- >99% uptime (excluding planned maintenance)

### Quality
- Zero data integrity issues (audit trail verification)
- <1% error rate for BIR form generation
- >95% user satisfaction score
