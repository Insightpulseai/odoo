# Odoo MCP Server - Implementation Plan

## Phase 1: Foundation (Week 1-2)

### 1.1 Project Setup
```bash
# Create MCP server package
cd mcp/servers/
mkdir odoo-erp-server
cd odoo-erp-server

# Initialize Node.js project
pnpm init
pnpm add @modelcontextprotocol/sdk xmlrpc odoo-xmlrpc

# TypeScript setup
pnpm add -D typescript @types/node
npx tsc --init
```

**Directory Structure**:
```
mcp/servers/odoo-erp-server/
├── src/
│   ├── index.ts              # Main MCP server entry point
│   ├── odoo-client.ts        # XML-RPC client wrapper
│   ├── tools/
│   │   ├── account.ts        # Accounting tools
│   │   ├── partner.ts        # Partner/vendor tools
│   │   ├── project.ts        # Project management tools
│   │   └── bir.ts            # BIR compliance tools
│   ├── utils/
│   │   ├── employee-resolver.ts  # Employee code → user_id mapping
│   │   ├── domain-builder.ts    # Odoo domain filter builder
│   │   └── error-handler.ts     # Error parsing and retry logic
│   └── types/
│       └── odoo.d.ts         # Odoo type definitions
├── tests/
│   ├── integration/
│   └── unit/
├── package.json
├── tsconfig.json
└── README.md
```

### 1.2 Odoo XML-RPC Client

**File**: `src/odoo-client.ts`

```typescript
import xmlrpc from 'xmlrpc';

interface OdooConfig {
  url: string;
  db: string;
  username: string;
  password: string;
}

export class OdooClient {
  private commonClient: xmlrpc.Client;
  private objectClient: xmlrpc.Client;
  private uid: number | null = null;

  constructor(private config: OdooConfig) {
    this.commonClient = xmlrpc.createClient({
      host: new URL(config.url).hostname,
      port: new URL(config.url).port || 80,
      path: '/xmlrpc/2/common'
    });

    this.objectClient = xmlrpc.createClient({
      host: new URL(config.url).hostname,
      port: new URL(config.url).port || 80,
      path: '/xmlrpc/2/object'
    });
  }

  async authenticate(): Promise<number> {
    if (this.uid) return this.uid;

    return new Promise((resolve, reject) => {
      this.commonClient.methodCall('authenticate', [
        this.config.db,
        this.config.username,
        this.config.password,
        {}
      ], (error, uid) => {
        if (error) reject(error);
        else {
          this.uid = uid;
          resolve(uid);
        }
      });
    });
  }

  async execute_kw<T>(
    model: string,
    method: string,
    args: any[] = [],
    kwargs: Record<string, any> = {}
  ): Promise<T> {
    const uid = await this.authenticate();

    return new Promise((resolve, reject) => {
      this.objectClient.methodCall('execute_kw', [
        this.config.db,
        uid,
        this.config.password,
        model,
        method,
        args,
        kwargs
      ], (error, result) => {
        if (error) reject(this.parseOdooError(error));
        else resolve(result);
      });
    });
  }

  async search_read<T>(
    model: string,
    domain: any[] = [],
    fields: string[] = [],
    limit: number = 100,
    offset: number = 0,
    context: Record<string, any> = {}
  ): Promise<T[]> {
    return this.execute_kw<T[]>(model, 'search_read', [domain], {
      fields,
      limit,
      offset,
      context
    });
  }

  async create(
    model: string,
    values: Record<string, any>,
    context: Record<string, any> = {}
  ): Promise<number> {
    return this.execute_kw<number>(model, 'create', [values], { context });
  }

  async write(
    model: string,
    ids: number[],
    values: Record<string, any>,
    context: Record<string, any> = {}
  ): Promise<boolean> {
    return this.execute_kw<boolean>(model, 'write', [ids, values], { context });
  }

  private parseOdooError(error: any): Error {
    // Parse Odoo XML-RPC fault codes
    if (error.faultString) {
      const match = error.faultString.match(/AccessError|ValidationError|UserError/);
      if (match) {
        return new Error(`Odoo ${match[0]}: ${error.faultString}`);
      }
    }
    return new Error(error.message || 'Unknown Odoo error');
  }
}
```

### 1.3 Employee Code Resolver

**File**: `src/utils/employee-resolver.ts`

```typescript
import { OdooClient } from '../odoo-client';

interface EmployeeMapping {
  code: string;
  user_id: number;
  user_name: string;
  agency_ids: number[];
}

export class EmployeeResolver {
  private cache = new Map<string, EmployeeMapping>();
  private cacheTTL = 5 * 60 * 1000; // 5 minutes
  private cacheTimestamps = new Map<string, number>();

  constructor(private odoo: OdooClient) {}

  async resolve(employeeCode: string): Promise<EmployeeMapping> {
    // Check cache first
    const cached = this.getFromCache(employeeCode);
    if (cached) return cached;

    // Query Odoo
    const employees = await this.odoo.search_read<any>(
      'ipai.employee_code',
      [['code', '=', employeeCode]],
      ['code', 'user_id', 'agency_ids'],
      1
    );

    if (!employees.length) {
      throw new Error(
        `Invalid employee code: ${employeeCode}\n` +
        `Valid codes: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB`
      );
    }

    const mapping: EmployeeMapping = {
      code: employees[0].code,
      user_id: employees[0].user_id[0],
      user_name: employees[0].user_id[1],
      agency_ids: employees[0].agency_ids
    };

    // Update cache
    this.cache.set(employeeCode, mapping);
    this.cacheTimestamps.set(employeeCode, Date.now());

    return mapping;
  }

  private getFromCache(employeeCode: string): EmployeeMapping | null {
    const timestamp = this.cacheTimestamps.get(employeeCode);
    if (!timestamp || Date.now() - timestamp > this.cacheTTL) {
      this.cache.delete(employeeCode);
      this.cacheTimestamps.delete(employeeCode);
      return null;
    }
    return this.cache.get(employeeCode) || null;
  }
}
```

### 1.4 MCP Server Entry Point

**File**: `src/index.ts`

```typescript
#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

import { OdooClient } from './odoo-client.js';
import { EmployeeResolver } from './utils/employee-resolver.js';
import { registerAccountTools } from './tools/account.js';
import { registerPartnerTools } from './tools/partner.js';
import { registerProjectTools } from './tools/project.js';
import { registerBIRTools } from './tools/bir.js';

const server = new Server(
  {
    name: 'odoo-erp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Initialize Odoo client
const odoo = new OdooClient({
  url: process.env.ODOO_URL || 'http://localhost:8069',
  db: process.env.ODOO_DB || 'production',
  username: process.env.ODOO_USERNAME!,
  password: process.env.ODOO_PASSWORD!,
});

const employeeResolver = new EmployeeResolver(odoo);

// Register all tools
const tools = [
  ...registerAccountTools(odoo, employeeResolver),
  ...registerPartnerTools(odoo, employeeResolver),
  ...registerProjectTools(odoo, employeeResolver),
  ...registerBIRTools(odoo, employeeResolver),
];

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const tool = tools.find((t) => t.name === request.params.name);
  if (!tool) {
    throw new Error(`Tool not found: ${request.params.name}`);
  }

  // Execute tool handler
  return tool.handler(request.params.arguments || {});
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Odoo ERP MCP server running on stdio');
}

main().catch(console.error);
```

## Phase 2: Core Tools (Week 2-3)

### 2.1 Accounting Tools

**File**: `src/tools/account.ts`

```typescript
import { OdooClient } from '../odoo-client';
import { EmployeeResolver } from '../utils/employee-resolver';

export function registerAccountTools(
  odoo: OdooClient,
  employeeResolver: EmployeeResolver
) {
  return [
    {
      name: 'odoo:account:create-journal-entry',
      description: 'Create a journal entry (account.move)',
      inputSchema: {
        type: 'object',
        properties: {
          date: {
            type: 'string',
            description: 'Entry date (YYYY-MM-DD)',
          },
          journal_id: {
            type: 'number',
            description: 'Journal ID or code',
          },
          ref: {
            type: 'string',
            description: 'Reference/memo',
          },
          line_ids: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                account_id: { type: 'number' },
                name: { type: 'string' },
                debit: { type: 'number' },
                credit: { type: 'number' },
                partner_id: { type: 'number' },
              },
            },
          },
          employee_code: {
            type: 'string',
            description: 'Employee code (RIM, CKVC, etc.)',
          },
        },
        required: ['date', 'journal_id', 'line_ids'],
      },
      handler: async (args: any) => {
        // Resolve employee code
        let context = {};
        if (args.employee_code) {
          const employee = await employeeResolver.resolve(args.employee_code);
          context = { uid: employee.user_id };
        }

        // Validate debit/credit balance
        const totalDebit = args.line_ids.reduce((sum: number, line: any) =>
          sum + (line.debit || 0), 0
        );
        const totalCredit = args.line_ids.reduce((sum: number, line: any) =>
          sum + (line.credit || 0), 0
        );

        if (Math.abs(totalDebit - totalCredit) > 0.01) {
          throw new Error(
            `Journal entry unbalanced: Debit ${totalDebit} != Credit ${totalCredit}`
          );
        }

        // Create journal entry
        const moveId = await odoo.create('account.move', {
          date: args.date,
          journal_id: args.journal_id,
          ref: args.ref,
          line_ids: args.line_ids.map((line: any) => [0, 0, {
            account_id: line.account_id,
            name: line.name,
            debit: line.debit || 0,
            credit: line.credit || 0,
            partner_id: line.partner_id,
          }]),
        }, context);

        return {
          content: [
            {
              type: 'text',
              text: `✅ Journal entry created\n\n` +
                    `Move ID: ${moveId}\n` +
                    `Total Debit: ${totalDebit.toFixed(2)}\n` +
                    `Total Credit: ${totalCredit.toFixed(2)}\n` +
                    `Reference: ${args.ref}\n\n` +
                    `View in Odoo: /web#id=${moveId}&model=account.move`,
            },
          ],
        };
      },
    },
    {
      name: 'odoo:account:query-ap-aging',
      description: 'Get accounts payable aging report',
      inputSchema: {
        type: 'object',
        properties: {
          as_of_date: {
            type: 'string',
            description: 'As of date (YYYY-MM-DD)',
          },
          employee_code: {
            type: 'string',
            description: 'Filter by employee code',
          },
          buckets: {
            type: 'array',
            items: { type: 'number' },
            description: 'Aging buckets in days (default: [0, 30, 60, 90])',
          },
        },
        required: ['as_of_date'],
      },
      handler: async (args: any) => {
        const buckets = args.buckets || [0, 30, 60, 90];
        const asOfDate = new Date(args.as_of_date);

        // Build domain
        let domain: any[] = [
          ['move_type', '=', 'in_invoice'],
          ['state', '=', 'posted'],
          ['payment_state', 'in', ['not_paid', 'partial']],
        ];

        // Apply employee filter
        if (args.employee_code) {
          const employee = await employeeResolver.resolve(args.employee_code);
          domain.push(['create_uid', '=', employee.user_id]);
        }

        // Query invoices
        const invoices = await odoo.search_read<any>(
          'account.move',
          domain,
          ['partner_id', 'invoice_date_due', 'amount_residual'],
          1000
        );

        // Compute aging
        const aging = new Map<number, any>();

        for (const invoice of invoices) {
          const partnerId = invoice.partner_id[0];
          const dueDate = new Date(invoice.invoice_date_due);
          const daysOverdue = Math.floor(
            (asOfDate.getTime() - dueDate.getTime()) / (1000 * 60 * 60 * 24)
          );

          if (!aging.has(partnerId)) {
            aging.set(partnerId, {
              partner_name: invoice.partner_id[1],
              buckets: Array(buckets.length + 1).fill(0),
            });
          }

          const partnerAging = aging.get(partnerId)!;
          const bucketIndex = buckets.findIndex((b) => daysOverdue < b);
          if (bucketIndex === -1) {
            partnerAging.buckets[buckets.length] += invoice.amount_residual;
          } else {
            partnerAging.buckets[bucketIndex] += invoice.amount_residual;
          }
        }

        // Format as markdown table
        const headers = ['Vendor', ...buckets.map((b) => `${b}+ days`), 'Total'];
        const rows = Array.from(aging.values()).map((a) => [
          a.partner_name,
          ...a.buckets.map((amt: number) => amt.toFixed(2)),
          a.buckets.reduce((sum: number, amt: number) => sum + amt, 0).toFixed(2),
        ]);

        const table = [
          `| ${headers.join(' | ')} |`,
          `| ${headers.map(() => '---').join(' | ')} |`,
          ...rows.map((row) => `| ${row.join(' | ')} |`),
        ].join('\n');

        return {
          content: [
            {
              type: 'text',
              text: `# AP Aging Report\n\n` +
                    `As of: ${args.as_of_date}\n` +
                    `${args.employee_code ? `Employee: ${args.employee_code}\n` : ''}\n` +
                    `${table}\n`,
            },
          ],
        };
      },
    },
  ];
}
```

### 2.2 Partner Tools

**File**: `src/tools/partner.ts`

```typescript
export function registerPartnerTools(
  odoo: OdooClient,
  employeeResolver: EmployeeResolver
) {
  return [
    {
      name: 'odoo:partner:query-vendors',
      description: 'Query vendors with optional filters',
      inputSchema: {
        type: 'object',
        properties: {
          filters: {
            type: 'object',
            properties: {
              name: { type: 'string', description: 'Fuzzy search by name' },
              tin: { type: 'string', description: 'Exact TIN match' },
              employee_code: { type: 'string' },
            },
          },
          fields: {
            type: 'array',
            items: { type: 'string' },
            description: 'Fields to return (default: name, tin, email, phone)',
          },
          limit: { type: 'number', default: 100 },
        },
      },
      handler: async (args: any) => {
        // Build domain
        let domain: any[] = [['supplier_rank', '>', 0]];

        if (args.filters?.name) {
          domain.push(['name', 'ilike', args.filters.name]);
        }
        if (args.filters?.tin) {
          domain.push(['vat', '=', args.filters.tin]);
        }
        if (args.filters?.employee_code) {
          const employee = await employeeResolver.resolve(args.filters.employee_code);
          domain.push(['user_id', '=', employee.user_id]);
        }

        const fields = args.fields || ['name', 'vat', 'email', 'phone'];
        const vendors = await odoo.search_read<any>(
          'res.partner',
          domain,
          fields,
          args.limit || 100
        );

        // Format as JSON
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(vendors, null, 2),
            },
          ],
        };
      },
    },
  ];
}
```

## Phase 3: BIR Compliance Tools (Week 3-4)

**File**: `src/tools/bir.ts`

```typescript
export function registerBIRTools(
  odoo: OdooClient,
  employeeResolver: EmployeeResolver
) {
  return [
    {
      name: 'odoo:bir:generate-1601c',
      description: 'Generate BIR Form 1601-C (Monthly Withholding Tax)',
      inputSchema: {
        type: 'object',
        properties: {
          period: { type: 'string', description: 'YYYY-MM' },
          employee_code: { type: 'string', description: 'REQUIRED' },
          tin: { type: 'string', description: 'Company TIN' },
          rdo_code: { type: 'string', description: 'RDO code (e.g., 039)' },
        },
        required: ['period', 'employee_code'],
      },
      handler: async (args: any) => {
        const employee = await employeeResolver.resolve(args.employee_code);

        // Parse period
        const [year, month] = args.period.split('-');
        const periodStart = `${year}-${month}-01`;
        const periodEnd = new Date(parseInt(year), parseInt(month), 0)
          .toISOString().split('T')[0];

        // Query withholding transactions
        const transactions = await odoo.search_read<any>(
          'bir.withholding',
          [
            ['date', '>=', periodStart],
            ['date', '<=', periodEnd],
            ['create_uid', '=', employee.user_id],
          ],
          ['partner_id', 'atc_code', 'tax_base', 'tax_withheld'],
          1000
        );

        if (!transactions.length) {
          return {
            content: [
              {
                type: 'text',
                text: `⚠️ No withholding transactions found for ${args.employee_code} in ${args.period}`,
              },
            ],
          };
        }

        // Aggregate by ATC
        const schedule2 = new Map<string, any>();
        let totalTaxBase = 0;
        let totalTaxWithheld = 0;

        for (const txn of transactions) {
          const atc = txn.atc_code;
          if (!schedule2.has(atc)) {
            schedule2.set(atc, {
              atcCode: atc,
              taxBase: 0,
              taxWithheld: 0,
            });
          }
          const summary = schedule2.get(atc)!;
          summary.taxBase += txn.tax_base;
          summary.taxWithheld += txn.tax_withheld;
          totalTaxBase += txn.tax_base;
          totalTaxWithheld += txn.tax_withheld;
        }

        // Generate eBIRForms JSON
        const ebir = {
          header: {
            formType: '1601C',
            tin: args.tin,
            rdoCode: args.rdo_code,
            taxableMonth: month,
            taxableYear: year,
          },
          schedules: {
            schedule1: {
              employees: transactions.map((txn: any) => ({
                tin: txn.partner_id.vat,
                employeeName: txn.partner_id.name,
                atcCode: txn.atc_code,
                taxBase: txn.tax_base,
                taxWithheld: txn.tax_withheld,
              })),
            },
            schedule2: {
              summary: Array.from(schedule2.values()),
              grandTotal: totalTaxWithheld,
            },
          },
        };

        // Create Odoo document
        const returnId = await odoo.create('bir.tax_return', {
          form_type: '1601-C',
          employee_code: args.employee_code,
          period_start: periodStart,
          period_end: periodEnd,
          total_tax_due: totalTaxWithheld,
          status: 'draft',
        });

        return {
          content: [
            {
              type: 'text',
              text: `✅ BIR Form 1601-C generated\n\n` +
                    `Employee: ${args.employee_code}\n` +
                    `Period: ${args.period}\n` +
                    `Transactions: ${transactions.length}\n` +
                    `Total tax withheld: PHP ${totalTaxWithheld.toFixed(2)}\n\n` +
                    `📎 eBIRForms JSON:\n\`\`\`json\n${JSON.stringify(ebir, null, 2)}\n\`\`\`\n\n` +
                    `View in Odoo: /web#id=${returnId}&model=bir.tax_return`,
            },
          ],
        };
      },
    },
    {
      name: 'odoo:bir:query-deadlines',
      description: 'Query upcoming BIR filing deadlines',
      inputSchema: {
        type: 'object',
        properties: {
          days_ahead: { type: 'number', default: 7 },
          form_types: { type: 'array', items: { type: 'string' } },
          employee_code: { type: 'string' },
        },
      },
      handler: async (args: any) => {
        const daysAhead = args.days_ahead || 7;
        const today = new Date().toISOString().split('T')[0];
        const futureDate = new Date(Date.now() + daysAhead * 24 * 60 * 60 * 1000)
          .toISOString().split('T')[0];

        let domain: any[] = [
          ['filing_deadline', '>=', today],
          ['filing_deadline', '<=', futureDate],
          ['status', 'in', ['not_started', 'in_progress']],
        ];

        if (args.form_types) {
          domain.push(['form_type', 'in', args.form_types]);
        }

        if (args.employee_code) {
          const employee = await employeeResolver.resolve(args.employee_code);
          domain.push(['create_uid', '=', employee.user_id]);
        }

        const deadlines = await odoo.search_read<any>(
          'bir.filing_deadline',
          domain,
          ['form_type', 'filing_deadline', 'status', 'responsible_person'],
          100
        );

        // Format as markdown table
        const table = [
          '| Form | Deadline | Employee | Status |',
          '| ---- | -------- | -------- | ------ |',
          ...deadlines.map((d: any) =>
            `| ${d.form_type} | ${d.filing_deadline} | ${d.responsible_person} | ${d.status} |`
          ),
        ].join('\n');

        return {
          content: [
            {
              type: 'text',
              text: `# Upcoming BIR Deadlines (next ${daysAhead} days)\n\n${table}\n`,
            },
          ],
        };
      },
    },
  ];
}
```

## Phase 4: Testing & Deployment (Week 5-6)

### 4.1 Integration Tests

**File**: `tests/integration/account.test.ts`

```typescript
import { describe, it, expect, beforeAll } from '@jest/globals';
import { OdooClient } from '../../src/odoo-client';
import { EmployeeResolver } from '../../src/utils/employee-resolver';

describe('Account Tools', () => {
  let odoo: OdooClient;
  let employeeResolver: EmployeeResolver;

  beforeAll(async () => {
    odoo = new OdooClient({
      url: process.env.ODOO_URL!,
      db: 'test_db',
      username: 'admin',
      password: 'admin',
    });
    employeeResolver = new EmployeeResolver(odoo);
  });

  it('should create journal entry', async () => {
    const moveId = await odoo.create('account.move', {
      date: '2025-11-30',
      journal_id: 1,
      ref: 'Test JE',
      line_ids: [
        [0, 0, { account_id: 100, name: 'Test Debit', debit: 1000, credit: 0 }],
        [0, 0, { account_id: 200, name: 'Test Credit', debit: 0, credit: 1000 }],
      ],
    });

    expect(moveId).toBeGreaterThan(0);
  });

  it('should query AP aging', async () => {
    const aging = await odoo.search_read(
      'account.move',
      [['move_type', '=', 'in_invoice']],
      ['partner_id', 'amount_residual'],
      10
    );

    expect(Array.isArray(aging)).toBe(true);
  });
});
```

### 4.2 Deployment Configuration

**File**: `mcp/servers/odoo-erp-server/.env.example`

```bash
# Odoo connection
ODOO_URL=http://odoo-erp-prod:8069
ODOO_DB=production
ODOO_USERNAME=<from vault>
ODOO_PASSWORD=<from vault>

# MCP coordinator (remote deployment)
MCP_COORDINATOR_URL=https://mcp.insightpulseai.net

# Redis cache (optional)
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=info
```

**File**: `mcp/servers/odoo-erp-server/infra/do/odoo-erp-server.yaml`

```yaml
name: odoo-erp-server
region: sgp
services:
  - name: mcp-server
    image:
      registry_type: DOCKER_HUB
      repository: node
      tag: "20-alpine"
    github:
      repo: jgtolentino/odoo-ce
      branch: main
      deploy_on_push: true
    envs:
      - key: ODOO_URL
        value: ${ODOO_URL}
      - key: ODOO_DB
        value: ${ODOO_DB}
      - key: ODOO_USERNAME
        scope: RUN_TIME
        type: SECRET
        value: ${ODOO_USERNAME}
      - key: ODOO_PASSWORD
        scope: RUN_TIME
        type: SECRET
        value: ${ODOO_PASSWORD}
    http_port: 8080
    instance_count: 2
    instance_size_slug: basic-xxs
    run_command: "cd mcp/servers/odoo-erp-server && npm start"
```

### 4.3 CI/CD Pipeline

**File**: `.github/workflows/mcp-server-deploy.yml`

```yaml
name: Deploy Odoo MCP Server

on:
  push:
    paths:
      - 'mcp/servers/odoo-erp-server/**'
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: cd mcp/servers/odoo-erp-server && npm ci
      - run: cd mcp/servers/odoo-erp-server && npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DO_ACCESS_TOKEN }}
      - run: doctl apps update <APP_ID> --spec mcp/servers/odoo-erp-server/infra/do/odoo-erp-server.yaml
      - run: doctl apps create-deployment <APP_ID> --force-rebuild
```

## Phase 5: Integration (Week 7-8)

### 5.1 Claude Code MCP Configuration

**File**: `~/.claude/mcp-servers.json`

```json
{
  "mcpServers": {
    "odoo-erp": {
      "command": "node",
      "args": ["/Users/tbwa/Documents/GitHub/odoo-ce/mcp/servers/odoo-erp-server/dist/index.js"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "production",
        "ODOO_USERNAME": "${ODOO_USERNAME}",
        "ODOO_PASSWORD": "${ODOO_PASSWORD}"
      }
    }
  }
}
```

### 5.2 BIR Compliance Skill Integration

**File**: `~/.claude/superclaude/skills/finance/bir-compliance-automation/.skillrc`

```yaml
mcp_dependencies:
  - odoo-erp  # Required MCP server

odoo_models:
  - bir.tax_return
  - bir.withholding
  - bir.filing_deadline
  - ipai.employee_code

auto_activation:
  keywords:
    - "bir"
    - "1601-c"
    - "2550q"
    - "withholding"
    - "tax return"
  file_patterns:
    - "*.bir.json"
    - "*_ebirforms.json"
```

## Success Criteria

✅ All 50+ tools implemented and tested
✅ Employee code resolution working with 5-min cache
✅ BIR form generation validated against eBIRForms schema
✅ Integration tests covering CRUD operations
✅ CI/CD pipeline deploying to DigitalOcean
✅ Documentation complete (README, API docs, examples)
✅ Performance targets met (<2s queries, <5s mutations)
✅ Zero direct database access (100% via Odoo API)
