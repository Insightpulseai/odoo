# Odoo ERP MCP Server

Model Context Protocol (MCP) server for Odoo CE 18.0 integration with Philippine BIR tax compliance automation.

## Features

✅ **13 Tools Implemented** (50+ planned):

### Accounting (3 tools)
- `odoo:account:create-journal-entry` - Create journal entries with balance validation
- `odoo:account:query-ap-aging` - Accounts payable aging reports
- `odoo:account:list-journals` - List available journals

### BIR Compliance (3 tools)
- `odoo:bir:generate-1601c` - Monthly withholding tax (1601-C)
- `odoo:bir:query-deadlines` - Upcoming filing deadlines
- `odoo:bir:batch-generate` - Multi-employee batch processing

### Employee Context
- **11 employees** supported: CKVC, RIM, BOM, LAS, RMQB, JMSM, JAP, JPAL, JLI, JRMO, CSD
- Automatic user_id resolution with caching
- Multi-employee batch operations

## Quick Start

### Installation

```bash
cd mcp/servers/odoo-erp-server
npm install
npm run build
```

### Configuration

```bash
cp .env.example .env
# Edit .env with your Odoo credentials:
# ODOO_URL=https://erp.insightpulseai.net
# ODOO_DB=production
# ODOO_USERNAME=admin
# ODOO_PASSWORD=your_password
```

### Running Locally

```bash
npm start
```

### Claude Code Integration

Add to `~/.claude/mcp-servers.json`:

```json
{
  "mcpServers": {
    "odoo-erp": {
      "command": "node",
      "args": ["/Users/tbwa/Documents/GitHub/odoo-ce/mcp/servers/odoo-erp-server/dist/index.js"],
      "env": {
        "ODOO_URL": "https://erp.insightpulseai.net",
        "ODOO_DB": "production",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "${ODOO_PASSWORD}"
      }
    }
  }
}
```

Set password in shell:
```bash
export ODOO_PASSWORD="your_admin_password"
```

## Example Usage

### Create Journal Entry

```
User: "Create a journal entry for accrued rent expense PHP 50,000"

Claude: [Uses odoo:account:create-journal-entry]

✅ Journal entry created successfully

Details:
- Move ID: 12345
- Date: 2025-11-30
- Reference: Accrued rent expense
- Total Debit: PHP 50,000.00
- Total Credit: PHP 50,000.00
- Lines: 2

View in Odoo: /web#id=12345&model=account.move
```

### Generate BIR 1601-C

```
User: "Generate 1601-C for RIM covering November 2025"

Claude: [Uses odoo:bir:generate-1601c]

✅ BIR Form 1601-C Generated

Employee: RIM (Rey Meran)
Period: 2025-11
Transactions: 47
Total Tax Withheld: PHP 125,456.78

Summary by ATC:
| ATC Code | Count | Tax Base | Tax Withheld |
| WC010 | 30 | PHP 500,000.00 | PHP 0.00 |
| WI010 | 17 | PHP 1,000,000.00 | PHP 125,456.78 |

Next Steps:
1. Review in Odoo
2. Approve for filing (deadline: 2025-12-10)
3. Upload to BIR eBIRForms portal
```

### Query BIR Deadlines

```
User: "What BIR deadlines are coming up?"

Claude: [Uses odoo:bir:query-deadlines]

# Upcoming BIR Deadlines (Next 7 Days)

| Form | Deadline | Prep By | Review By | Status | Employee |
| 1601-C | 2025-12-10 | 2025-12-06 | 2025-12-08 | ✅ filed | RIM |
| 2550Q | 2025-12-15 | 2025-12-11 | 2025-12-13 | ⚠️ not_started | CKVC |

Action Required:
- 2550Q (2025-12-15): Start preparation now
```

## Development

### Build

```bash
npm run build
```

### Watch Mode

```bash
npm run dev
```

### Testing

```bash
npm test
```

### Linting

```bash
npm run lint
npm run format
```

## Architecture

```
src/
├── index.ts              # MCP server entry point
├── odoo-client.ts        # XML-RPC client wrapper
├── types/
│   └── odoo.d.ts         # TypeScript definitions
├── utils/
│   └── employee-resolver.ts  # Employee code → user_id mapping
└── tools/
    ├── account.ts        # Accounting tools
    ├── bir.ts            # BIR compliance tools
    ├── partner.ts        # Partner/vendor tools (TODO)
    └── project.ts        # Project management tools (TODO)
```

## Roadmap

### Phase 1: MVP (Current)
- [x] Odoo XML-RPC client
- [x] Employee code resolver
- [x] Core accounting tools (JE, AP aging)
- [x] BIR 1601-C generation
- [x] Deadline monitoring
- [ ] Partner/vendor tools
- [ ] Project task tools

### Phase 2: Complete BIR Support
- [ ] All 36 BIR form types
- [ ] TIN validation
- [ ] eBIRForms JSON validation
- [ ] Automatic alphalist generation
- [ ] n8n workflow triggers

### Phase 3: Optimization
- [ ] Redis caching layer
- [ ] Connection pooling
- [ ] Performance profiling
- [ ] Load testing

### Phase 4: Production
- [ ] Deploy to DigitalOcean
- [ ] CI/CD pipeline
- [ ] Monitoring and alerting
- [ ] User documentation

## Contributing

See `spec/odoo-mcp-server/plan.md` for detailed implementation plan.

## License

AGPL-3.0 (matching Odoo CE)

## Support

- **Specification**: `spec/odoo-mcp-server/`
- **Issues**: https://github.com/jgtolentino/odoo-ce/issues
- **Contact**: Jake Tolentino (@jgtolentino)
