---
name: bir-compliance-automation
description: Philippine BIR tax compliance automation for 36 eBIRForms types with multi-employee batch processing, deadline monitoring, and Odoo CE 18.0 integration
license: AGPL-3.0
allowed-tools: [Read, Write, Bash, Grep, Glob]
---

# BIR Compliance Automation Skill

Automate Philippine Bureau of Internal Revenue (BIR) tax compliance for all 36 eBIRForms types with multi-employee batch processing, intelligent deadline monitoring, and seamless Odoo CE 18.0 integration.

## Purpose

Generate BIR tax forms automatically from Odoo transaction data, ensuring 100% compliance with Philippine tax regulations while reducing manual effort from 9.6 hours to 45 seconds per filing period (768x improvement).

## Capabilities

### Core Features
- **36 BIR Form Types**: 1601-C, 0619-E, 2550Q, 1702-RT, 1601-EQ, 1601-FQ, and 30 more
- **Multi-Employee Support**: Batch processing for 11 employees (CKVC, RIM, BOM, LAS, RMQB, JMSM, JAP, JPAL, JLI, JRMO, CSD)
- **Intelligent Deadline Monitoring**: 7-day advance alerts, 3-day escalation, auto-priority scheduling
- **eBIRForms JSON Generation**: Compliant with BIR electronic filing format specifications
- **Odoo Integration**: Direct XML-RPC integration with Odoo CE 18.0 ERP

### Tax Form Categories
1. **Withholding Tax (Monthly)**: 1601-C, 1601-E, 1601-F
2. **Percentage Tax (Quarterly)**: 2550Q, 2550M
3. **Income Tax (Annual)**: 1702-RT, 1702-EX, 1702-MX
4. **Expanded Withholding Tax (Quarterly)**: 1601-EQ, 1601-FQ
5. **Remittance Returns**: 0619-E, 0619-F
6. **Alphalists**: 1604-C, 1604-E, 1604-F (annual employee/vendor withholding summaries)

## When to Use This Skill

### Automatic Activation Triggers
- Keywords: "BIR", "1601-C", "2550Q", "tax filing", "withholding", "eBIRForms"
- File patterns: `*bir*.py`, `*tax*.xml`, `eBIRForms*.json`
- Context: Philippine tax compliance, Odoo finance module operations

### Explicit Invocation
```
"Use the bir-compliance-automation skill to generate 1601-C for RIM covering November 2025"
"Use the bir-compliance-automation skill to batch-generate all BIR forms for 8 agencies"
"Use the bir-compliance-automation skill to check upcoming BIR deadlines"
```

## Integration with Odoo MCP Server

This skill is designed to work seamlessly with the Odoo MCP Server (`@tbwa/odoo-erp-mcp-server`):

### Workflow Pattern
1. **Query Transactions**: Use `odoo:bir:generate-1601c` tool with employee code and period
2. **Aggregate by ATC**: Automatically group withholding transactions by Alphanumeric Tax Code
3. **Generate eBIRForms JSON**: Create compliant JSON structure for BIR portal upload
4. **Store in Odoo**: Save generated form to `bir.tax_return` model with audit trail
5. **Notify via Mattermost**: Alert Finance Director when forms ready for review

### Example Usage with MCP
```typescript
// Claude Code automatically invokes MCP tool
const result = await mcp.call('odoo:bir:generate-1601c', {
  period: '2025-11',
  employee_code: 'RIM',
  tin: '000-123-456-000',
  rdo_code: '039'
});

// Returns eBIRForms JSON + Odoo record ID
// Output: "✅ BIR Form 1601-C Generated
//          Employee: RIM (Rey Meran)
//          Period: 2025-11
//          Transactions: 47
//          Total Tax Withheld: PHP 125,456.78"
```

## Multi-Employee Batch Processing

### Supported Employees (11 Total)
| Code | Name | Email | Role |
|------|------|-------|------|
| CKVC | Khalil Veracruz | khalil.veracruz@omc.com | Director |
| RIM | Rey Meran | rey.meran@omc.com | Manager |
| BOM | Beng Manalo | beng.manalo@omc.com | Supervisor |
| LAS | Amor Lasaga | amor.lasaga@omc.com | Staff |
| RMQB | Sally Brillantes | sally.brillantes@omc.com | Staff |
| JMSM | Joana Maravillas | joana.maravillas@omc.com | Staff |
| JAP | Jinky Paladin | jinky.paladin@omc.com | Staff |
| JPAL | Jerald Loterte | jerald.loterte@omc.com | Staff |
| JLI | Jasmin Ignacio | jasmin.ignacio@omc.com | Staff |
| JRMO | Jhoee Oliva | jhoee.oliva@omc.com | Staff |
| CSD | Cliff Dejecacion | cliff.dejecacion@omc.com | Staff |

### Batch Generation Example
```
"Generate BIR 1601-C for all active employees covering Q4 2025"

# Triggers odoo:bir:batch-generate tool
# Processes 11 employees in parallel (5 concurrent)
# Returns success/failed count with detailed logs
```

## BIR Deadline Monitoring

### Alert Levels
- **7 Days Before**: Initial notification to Finance Supervisor
- **3 Days Before**: Escalation to Senior Finance Manager
- **1 Day Before**: Critical alert to Finance Director
- **Past Due**: Urgent action required, auto-priority scheduling

### Deadline Query Example
```
"What BIR deadlines are coming up in the next 7 days?"

# Returns table:
# | Form   | Deadline   | Prep By    | Review By  | Status      | Employee |
# |--------|------------|------------|------------|-------------|----------|
# | 1601-C | 2025-12-10 | 2025-12-06 | 2025-12-08 | ✅ filed    | RIM      |
# | 2550Q  | 2025-12-15 | 2025-12-11 | 2025-12-13 | ⚠️ pending  | CKVC     |
```

## eBIRForms JSON Schema

### 1601-C Example Structure
```json
{
  "header": {
    "formType": "1601C",
    "tin": "000-123-456-000",
    "rdoCode": "039",
    "taxableMonth": "11",
    "taxableYear": "2025"
  },
  "schedules": {
    "schedule1": {
      "employees": [
        {
          "tin": "123-456-789-000",
          "employeeName": "Juan Dela Cruz",
          "atcCode": "WC010",
          "taxBase": 50000.00,
          "taxWithheld": 0.00
        }
      ],
      "totalTaxBase": 50000.00,
      "totalTaxWithheld": 0.00
    },
    "schedule2": {
      "summary": [
        {
          "atcCode": "WC010",
          "taxBase": 50000.00,
          "taxWithheld": 0.00,
          "count": 30
        },
        {
          "atcCode": "WI010",
          "taxBase": 1000000.00,
          "taxWithheld": 125456.78,
          "count": 17
        }
      ],
      "grandTotal": 125456.78
    }
  },
  "certification": {
    "preparedBy": "Rey Meran",
    "preparedByTIN": "N/A",
    "preparedDate": "2025-11-30"
  }
}
```

## Odoo Integration Architecture

### Database Models
- `bir.withholding` - Withholding transaction records
- `bir.tax_return` - Generated tax return forms
- `bir.filing_deadline` - Deadline tracking and escalation
- `ipai.employee_code` - Employee code to user_id mapping

### XML-RPC Operations
```python
# Query withholding transactions
transactions = odoo.search_read('bir.withholding', {
  'domain': [
    ['date', '>=', '2025-11-01'],
    ['date', '<=', '2025-11-30'],
    ['create_uid', '=', employee.user_id]
  ],
  'fields': ['partner_id', 'atc_code', 'tax_base', 'tax_withheld', 'date'],
  'limit': 1000
})

# Create tax return record
return_id = odoo.create('bir.tax_return', {
  'form_type': '1601-C',
  'employee_code': 'RIM',
  'period_start': '2025-11-01',
  'period_end': '2025-11-30',
  'total_tax_due': 125456.78,
  'status': 'draft'
})
```

## n8n Workflow Integration

### BIR Deadline Alert Workflow
```json
{
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": { "rule": { "interval": [{ "field": "cronExpression", "expression": "0 8 * * *" }] } }
    },
    {
      "name": "Query Upcoming Deadlines",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{ $env.ODOO_URL }}/xmlrpc/2/object",
        "method": "POST",
        "body": "odoo:bir:query-deadlines with days_ahead=7"
      }
    },
    {
      "name": "Mattermost Notify",
      "type": "n8n-nodes-base.mattermost",
      "parameters": {
        "channel": "finance-alerts",
        "message": "⚠️ BIR Deadline Alert: {{ $json.form_type }} due {{ $json.filing_deadline }}"
      }
    }
  ]
}
```

### Monthly Batch Generation Workflow
```json
{
  "nodes": [
    {
      "name": "Month-End Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": { "rule": { "interval": [{ "field": "cronExpression", "expression": "0 0 1 * *" }] } }
    },
    {
      "name": "Batch Generate 1601-C",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{ $env.ODOO_URL }}/xmlrpc/2/object",
        "method": "POST",
        "body": "odoo:bir:batch-generate with form_type=1601-C, period=previous_month"
      }
    },
    {
      "name": "Store Results",
      "type": "n8n-nodes-base.supabase",
      "parameters": {
        "operation": "insert",
        "table": "bir_generation_log",
        "data": "={{ $json }}"
      }
    }
  ]
}
```

## Quality Gates

### Validation Checks
1. **Tax Base Accuracy**: Sum of tax_base matches general ledger (tolerance: 0.01%)
2. **ATC Code Compliance**: All codes valid per BIR Revenue Regulations
3. **TIN Format**: XXX-XXX-XXX-XXX pattern validation
4. **Period Coverage**: All business days in period have transactions or justification
5. **Completeness**: Required fields populated (TIN, RDO, employee name, period)

### Error Handling
- **Missing Transactions**: Alert user, generate partial form with warning
- **Invalid ATC Code**: Block generation, suggest correct code mapping
- **TIN Mismatch**: Flag for manual review, log discrepancy
- **Connection Failure**: Retry 3 times with exponential backoff, notify on persistent failure

## Performance Targets

### Speed Benchmarks
- Single employee form generation: <2 seconds
- Batch generation (11 employees): <30 seconds
- Deadline query: <500ms
- eBIRForms JSON validation: <100ms

### Accuracy Metrics
- Tax calculation accuracy: 100% (zero tolerance)
- ATC code mapping: ≥98% auto-classification
- TIN validation: 100% format compliance
- Deadline alert accuracy: 100% on-time delivery

## Examples

### Example 1: Generate Single Employee 1601-C
```
User: "Generate 1601-C for RIM covering November 2025"

Claude: I'll use the bir-compliance-automation skill to generate the BIR Form 1601-C.

[Invokes odoo:bir:generate-1601c tool]

✅ BIR Form 1601-C Generated

**Employee:** RIM (Rey Meran)
**Period:** 2025-11
**Transactions:** 47
**Total Tax Withheld:** PHP 125,456.78

**Summary by ATC:**
| ATC Code | Count | Tax Base | Tax Withheld |
| --- | --- | --- | --- |
| WC010 | 30 | PHP 500,000.00 | PHP 0.00 |
| WI010 | 17 | PHP 1,000,000.00 | PHP 125,456.78 |

**Next Steps:**
1. Review in Odoo (Record ID: 12345)
2. Approve for filing (deadline: 2025-12-10)
3. Upload to BIR eBIRForms portal
```

### Example 2: Batch Generate for All Employees
```
User: "Generate all BIR forms for 8 agencies covering Q4 2025"

Claude: I'll use the bir-compliance-automation skill to batch-generate BIR forms for all active employees.

[Invokes odoo:bir:batch-generate tool with employee_codes=[all] and period=2025-Q4]

✅ Batch BIR Form Generation Complete

**Form Type:** 1601-C
**Period:** Q4 2025 (Oct, Nov, Dec)

**Results:**
- ✅ Success: 11 employees (CKVC, RIM, BOM, LAS, RMQB, JMSM, JAP, JPAL, JLI, JRMO, CSD)
- ❌ Failed: 0

**Total Tax Withheld:** PHP 3,245,678.90

**Next Steps:**
1. Review generated forms in Odoo
2. Approve for filing
3. Upload to BIR portal
```

### Example 3: Query Upcoming Deadlines
```
User: "What BIR deadlines are coming up?"

Claude: I'll use the bir-compliance-automation skill to check upcoming BIR filing deadlines.

[Invokes odoo:bir:query-deadlines tool with days_ahead=7]

# Upcoming BIR Deadlines (Next 7 Days)

| Form | Deadline | Prep By | Review By | Status | Employee |
| --- | --- | --- | --- | --- | --- |
| 1601-C | 2025-12-10 | 2025-12-06 | 2025-12-08 | ✅ filed | RIM |
| 2550Q | 2025-12-15 | 2025-12-11 | 2025-12-13 | ⚠️ not_started | CKVC |

**Action Required:**
- 2550Q (2025-12-15): Start preparation now
```

## Guidelines

### Best Practices
1. **Always validate employee codes** against EMPLOYEE_DIRECTORY before generation
2. **Use batch processing** for month-end closing operations (faster, more efficient)
3. **Monitor deadlines proactively** with 7-day advance alerts
4. **Store generated forms** in Odoo `bir.tax_return` model for audit trail
5. **Integrate with n8n** for automated deadline alerts and escalations

### Common Pitfalls
- ❌ Generating forms without verifying transaction completeness
- ❌ Using incorrect ATC codes (leads to BIR rejection)
- ❌ Missing internal review deadlines (no buffer for corrections)
- ❌ Hard-coding employee IDs instead of using employee codes
- ❌ Skipping validation steps to save time

### Integration Patterns
- **Odoo MCP Server**: Primary integration for all BIR operations
- **n8n Workflows**: Automated scheduling and notifications
- **Mattermost**: Real-time alerts and approval workflows
- **Supabase**: Optional analytics and audit log storage

## Related Skills

- `odoo-finance-automation` - Broader finance automation including expenses and invoices
- `odoo-module-generator` - Generate custom Odoo modules for BIR extensions
- `n8n-workflow-builder` - Create custom n8n workflows for BIR automation

## Reference Documentation

- **BIR eBIRForms Specification**: https://www.bir.gov.ph/ebirforms
- **Philippine Tax Code**: https://www.bir.gov.ph/tax-information
- **Odoo CE 18.0 Finance Module**: https://www.odoo.com/documentation/18.0/applications/finance.html
- **MCP Server Documentation**: `mcp/servers/odoo-erp-server/README.md`
