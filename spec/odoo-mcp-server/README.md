# Odoo MCP Server + BIR Compliance Skill

Complete specification for Odoo CE 18.0 XML-RPC integration via Model Context Protocol (MCP) with Philippine BIR tax compliance automation.

## Overview

This specification addresses the critical gap in Anthropic's MCP ecosystem: **direct Odoo ERP integration**. It enables Claude Code to perform routine finance operations via natural language without manual UI navigation.

## What's Inside

### 1. Odoo MCP Server (`spec/odoo-mcp-server/`)

**Purpose**: XML-RPC MCP server exposing 50+ Odoo operations

**Key Features**:
- ✅ Direct journal entry creation
- ✅ AP/AR aging queries without SQL
- ✅ Multi-employee context switching
- ✅ BIR form generation (36 eBIRForms types)
- ✅ Month-end task orchestration
- ✅ Real-time deadline monitoring

**Tech Stack**:
- Node.js 20+ or Python 3.11+
- @modelcontextprotocol/sdk
- Odoo XML-RPC client
- TypeScript for type safety

### 2. BIR Compliance Skill (`~/.claude/superclaude/skills/finance/bir-compliance-automation/`)

**Purpose**: Philippine tax compliance automation with multi-employee support

**Supported Forms** (36 total):
- Withholding Tax: 1600, 1601-C, 1601-E, 1601-F, 1604-CF, 1604-E
- VAT: 2550M, 2550Q, 2551M, 2551Q
- Income Tax: 1700, 1701, 1702, 1702-RT, 1702-EX
- Capital Gains: 1706, 1707
- Estate Tax: 1800, 1801
- Excise Tax: 2200-A, 2200-P, 2200-T, 2200-M, 2200-AN
- Documentary Stamp Tax: 2000, 2000-OT
- Information Returns: 0619-E, 0619-F

**Key Workflows**:
- Monthly 1601-C generation (8 employees in parallel)
- BIR deadline monitoring with Mattermost alerts
- TIN validation per BIR specifications
- eBIRForms JSON generation
- Multi-approval workflow (Prep → Review → Approve)

## Critical Architecture Decision: Employee Codes vs Agencies

**User Question**: "employee codes not agency"

**Clarification**: This specification distinguishes between:

### Employee Codes (TBWA Finance SSC Staff)
- **Definition**: Internal TBWA staff identifiers
- **Examples**: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB (8 total)
- **Purpose**: Who is filing/processing the tax return
- **Odoo Model**: `ipai.employee_code` (maps to `res.users`)

### Agency IDs (Legal Entities/Clients)
- **Definition**: Legal entity/client identifiers
- **Examples**: Company names, TINs, RDO codes
- **Purpose**: What entity the tax return is for
- **Odoo Model**: `res.partner` (standard Odoo partner)

### Example Workflow
```
Employee: RIM (Rigel Ian M. - Finance Manager)
  → Files BIR 1601-C for Agency: CKVC (Christine K. - as legal entity)
  → Uses CKVC's TIN: 123-456-789-000
  → Uses CKVC's RDO code: 039 (Makati)
  → Audit trail shows: Prepared by RIM, For entity CKVC
```

This resolves the common confusion where employee codes (internal staff) were being used as agency identifiers (legal entities).

## File Structure

```
spec/odoo-mcp-server/
├── README.md              # This file
├── constitution.md        # Non-negotiable rules
├── prd.md                 # Product requirements (50+ tools)
└── plan.md                # 8-week implementation plan

~/.claude/superclaude/skills/finance/bir-compliance-automation/
├── SKILL.md               # BIR compliance skill specification
└── .skillrc               # Skill configuration

mcp/servers/odoo-erp-server/  # Implementation (to be created)
├── src/
│   ├── index.ts           # MCP server entry point
│   ├── odoo-client.ts     # XML-RPC wrapper
│   ├── tools/             # 50+ tool implementations
│   │   ├── account.ts     # Accounting operations
│   │   ├── partner.ts     # Vendor/customer queries
│   │   ├── project.ts     # Task management
│   │   └── bir.ts         # BIR compliance
│   └── utils/
│       └── employee-resolver.ts  # Employee code → user_id mapping
└── tests/
    ├── integration/
    └── unit/
```

## Quick Start

### Local Development

1. **Install dependencies**:
```bash
cd mcp/servers/odoo-erp-server
pnpm install
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your Odoo credentials
```

3. **Build and test**:
```bash
pnpm build
pnpm test
```

4. **Run locally**:
```bash
pnpm start
```

5. **Configure Claude Code**:
```json
{
  "mcpServers": {
    "odoo-erp": {
      "command": "node",
      "args": ["dist/index.js"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "production"
      }
    }
  }
}
```

### Example Usage

**Create Journal Entry**:
```
User: "Create a journal entry for accrued rent expense PHP 50,000"

Claude: Using odoo:account:create-journal-entry...

✅ Journal entry created

Move ID: 12345
Total Debit: 50000.00
Total Credit: 50000.00
Reference: Accrued rent expense - December 2025

View in Odoo: /web#id=12345&model=account.move
```

**Generate BIR Form 1601-C**:
```
User: "Generate 1601-C for RIM covering November 2025"

Claude: Using BIR compliance skill with odoo:bir:generate-1601c...

✅ BIR Form 1601-C generated

Employee: RIM (Rigel Ian M.)
Period: 2025-11
Transactions: 47 withholding entries
Total tax withheld: PHP 125,456.78

📋 Summary by ATC:
- WC010: PHP 0.00 (exempt compensation)
- WC020: PHP 12,345.67 (13th month pay)
- WI010: PHP 113,111.11 (professional fees)

📎 eBIRForms JSON: [attached]

View in Odoo: /web#id=67890&model=bir.tax_return

Next steps:
1. Review in Odoo
2. Approve for filing (deadline: 2025-12-10)
3. Upload to BIR portal (automated via n8n)
```

**Query BIR Deadlines**:
```
User: "What BIR deadlines are coming up?"

Claude: Using odoo:bir:query-deadlines...

⚠️ Upcoming deadlines (next 7 days):

| Form | Deadline | Employee | Agency | Status |
|------|----------|----------|--------|--------|
| 1601-C | 2025-12-10 | RIM | CKVC | ✅ Ready |
| 0619-E | 2025-12-12 | BOM | JPAL | 🔄 In Progress |
| 2550Q | 2025-12-15 | CKVC | RIM | ⚠️ Not Started |

🚨 Action required:
- 2550Q (CKVC) needs to start preparation (8 days remaining)

Mattermost notifications sent to @RIM, @BOM, @CKVC
```

## Integration Points

### 1. n8n Workflows
- BIR deadline monitoring (daily cron)
- Multi-employee form generation (webhook trigger)
- Mattermost notifications on status changes

### 2. Supabase Task Queue
- Async BIR form uploads to portal
- Retry logic for failed operations
- Audit trail persistence

### 3. Mattermost
- Real-time deadline alerts (@mentions)
- Approval workflow notifications
- Escalation to Finance Director

### 4. Apache Superset
- BIR compliance dashboard
- Tax computation validation reports
- Multi-employee performance metrics

## Performance Targets

| Operation | Target (P95) |
|-----------|--------------|
| Simple query (1 record) | <500ms |
| Complex query (100 records) | <2s |
| Create journal entry | <3s |
| Batch expense creation (10 records) | <8s |
| BIR form generation | <15s |
| Multi-employee batch (8 forms) | <60s |

## Security & Compliance

### Credentials Management
- ✅ Environment variables only (never hardcode)
- ✅ macOS Keychain for local dev
- ✅ DigitalOcean secrets for production
- ✅ Session-based auth with auto-reconnect

### Data Privacy
- ✅ Employee codes are NOT PII (safe to log)
- ✅ Partner TINs are PII (redacted from logs)
- ✅ Financial amounts logged at summary level only
- ✅ Audit trail for all mutations (`mail.message`)

### BIR Compliance
- ✅ eBIRForms JSON schema validation
- ✅ Official ATC (tax code) rate tables
- ✅ Multi-approval workflow enforcement
- ✅ Historical versioning for amendments

## Next Steps

### Phase 1: MVP (Week 1-2)
- [ ] Implement XML-RPC client with connection pooling
- [ ] Create employee code resolver with caching
- [ ] Build core accounting tools (JE, AP aging)
- [ ] Setup local development environment

### Phase 2: BIR Integration (Week 3-4)
- [ ] Implement BIR form generation tools
- [ ] Add deadline monitoring queries
- [ ] Create multi-employee batch operations
- [ ] Integrate with n8n workflows

### Phase 3: Testing & Optimization (Week 5-6)
- [ ] Write integration tests (100% tool coverage)
- [ ] Implement Redis caching layer
- [ ] Performance profiling and tuning
- [ ] Load testing (100 concurrent queries)

### Phase 4: Production Deployment (Week 7-8)
- [ ] Deploy to DigitalOcean App Platform
- [ ] Setup CI/CD pipeline (GitHub Actions)
- [ ] Configure monitoring and alerting
- [ ] User training and documentation

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
- Zero data integrity issues
- <1% error rate for BIR form generation
- >95% user satisfaction score

## Contributing

All changes must follow the agent workflow pattern:

```bash
# 1. Explore
ls -la spec/odoo-mcp-server/

# 2. Plan
cat spec/odoo-mcp-server/plan.md

# 3. Implement
cd mcp/servers/odoo-erp-server
pnpm build

# 4. Verify
pnpm test
./scripts/ci_local.sh

# 5. Commit
git add .
git commit -m "feat(mcp): implement odoo accounting tools"
```

## License

AGPL-3.0 (matching Odoo CE license)

## References

- **Anthropic MCP SDK**: https://github.com/anthropics/mcp-sdk
- **Odoo XML-RPC Documentation**: https://www.odoo.com/documentation/18.0/developer/reference/external_api.html
- **BIR eBIRForms**: https://www.bir.gov.ph/ebirforms
- **TBWA Finance SOPs**: (internal documentation)

---

**Questions or issues?** File a GitHub issue or contact Jake Tolentino (@jgtolentino)
