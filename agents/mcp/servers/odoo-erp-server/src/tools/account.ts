/**
 * Accounting Tools
 *
 * Journal entries, AP/AR aging, bank reconciliation, trial balance queries
 */

import type { OdooClient } from '../odoo-client.js';
import type { EmployeeResolver } from '../utils/employee-resolver.js';

interface JournalEntryLine {
  account_id: number;
  name: string;
  debit: number;
  credit: number;
  partner_id?: number;
  tax_ids?: number[];
}

interface JournalEntryArgs {
  date: string;
  journal_id: number;
  ref: string;
  line_ids: JournalEntryLine[];
  employee_code?: string;
}

export function registerAccountTools(
  odoo: OdooClient,
  employeeResolver: EmployeeResolver
) {
  return [
    {
      name: 'odoo:account:create-journal-entry',
      description: 'Create a journal entry (account.move) in Odoo',
      inputSchema: {
        type: 'object',
        properties: {
          date: {
            type: 'string',
            description: 'Entry date (YYYY-MM-DD)',
          },
          journal_id: {
            type: 'number',
            description: 'Journal ID (use odoo:account:list-journals to find)',
          },
          ref: {
            type: 'string',
            description: 'Reference/memo for this entry',
          },
          line_ids: {
            type: 'array',
            description: 'Journal entry lines (must balance)',
            items: {
              type: 'object',
              properties: {
                account_id: { type: 'number', description: 'Account code or ID' },
                name: { type: 'string', description: 'Line description' },
                debit: { type: 'number', description: 'Debit amount' },
                credit: { type: 'number', description: 'Credit amount' },
                partner_id: { type: 'number', description: 'Partner ID (optional)' },
              },
              required: ['account_id', 'name', 'debit', 'credit'],
            },
          },
          employee_code: {
            type: 'string',
            description: 'Employee code (RIM, CKVC, etc.) - sets context for operation',
          },
        },
        required: ['date', 'journal_id', 'ref', 'line_ids'],
      },
      handler: async (args: JournalEntryArgs) => {
        try {
          // Build context
          let context: any = {};
          if (args.employee_code) {
            const employee = await employeeResolver.resolve(args.employee_code);
            context = { uid: employee.user_id };
          }

          // Validate debit/credit balance
          const totalDebit = args.line_ids.reduce((sum, line) => sum + (line.debit || 0), 0);
          const totalCredit = args.line_ids.reduce((sum, line) => sum + (line.credit || 0), 0);

          if (Math.abs(totalDebit - totalCredit) > 0.01) {
            return {
              content: [
                {
                  type: 'text',
                  text: `❌ Journal entry unbalanced:\n` +
                        `Total Debit: ${totalDebit.toFixed(2)}\n` +
                        `Total Credit: ${totalCredit.toFixed(2)}\n` +
                        `Difference: ${(totalDebit - totalCredit).toFixed(2)}`,
                },
              ],
            };
          }

          // Create journal entry
          const moveId = await odoo.create(
            'account.move',
            {
              date: args.date,
              journal_id: args.journal_id,
              ref: args.ref,
              line_ids: args.line_ids.map(line => [0, 0, {
                account_id: line.account_id,
                name: line.name,
                debit: line.debit || 0,
                credit: line.credit || 0,
                partner_id: line.partner_id || false,
                tax_ids: line.tax_ids ? [[6, 0, line.tax_ids]] : false,
              }]),
            },
            context
          );

          return {
            content: [
              {
                type: 'text',
                text: `✅ Journal entry created successfully\n\n` +
                      `**Details:**\n` +
                      `- Move ID: ${moveId}\n` +
                      `- Date: ${args.date}\n` +
                      `- Reference: ${args.ref}\n` +
                      `- Total Debit: PHP ${totalDebit.toFixed(2)}\n` +
                      `- Total Credit: PHP ${totalCredit.toFixed(2)}\n` +
                      `- Lines: ${args.line_ids.length}\n\n` +
                      `View in Odoo: /web#id=${moveId}&model=account.move`,
              },
            ],
          };
        } catch (error: any) {
          return {
            content: [
              {
                type: 'text',
                text: `❌ Failed to create journal entry:\n${error.message}`,
              },
            ],
          };
        }
      },
    },

    {
      name: 'odoo:account:query-ap-aging',
      description: 'Get accounts payable aging report (vendor payables by aging bucket)',
      inputSchema: {
        type: 'object',
        properties: {
          as_of_date: {
            type: 'string',
            description: 'As of date (YYYY-MM-DD) - defaults to today',
          },
          employee_code: {
            type: 'string',
            description: 'Filter by employee code (only show assigned vendors)',
          },
          buckets: {
            type: 'array',
            items: { type: 'number' },
            description: 'Aging buckets in days (default: [0, 30, 60, 90])',
          },
          include_details: {
            type: 'boolean',
            description: 'Include invoice-level details',
          },
        },
      },
      handler: async (args: any) => {
        try {
          const buckets = args.buckets || [0, 30, 60, 90];
          const asOfDate = new Date(args.as_of_date || new Date());

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
          const invoices = await odoo.search_read('account.move', {
            domain,
            fields: ['partner_id', 'invoice_date_due', 'amount_residual', 'name'],
            limit: 1000,
          });

          if (!invoices.length) {
            return {
              content: [
                {
                  type: 'text',
                  text: `ℹ️ No unpaid vendor invoices found${args.employee_code ? ` for employee ${args.employee_code}` : ''}`,
                },
              ],
            };
          }

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
                details: [],
              });
            }

            const partnerAging = aging.get(partnerId)!;

            // Find bucket
            const bucketIndex = buckets.findIndex(b => daysOverdue < b);
            if (bucketIndex === -1) {
              partnerAging.buckets[buckets.length] += invoice.amount_residual;
            } else {
              partnerAging.buckets[bucketIndex] += invoice.amount_residual;
            }

            if (args.include_details) {
              partnerAging.details.push({
                invoice: invoice.name,
                due_date: invoice.invoice_date_due,
                days_overdue: daysOverdue,
                amount: invoice.amount_residual,
              });
            }
          }

          // Format as markdown table
          const headers = ['Vendor', ...buckets.map(b => `${b}+ days`), `${buckets[buckets.length - 1]}+`, 'Total'];
          const rows = Array.from(aging.values()).map(a => {
            const total = a.buckets.reduce((sum: number, amt: number) => sum + amt, 0);
            return [
              a.partner_name,
              ...a.buckets.map((amt: number) => `PHP ${amt.toFixed(2)}`),
              `PHP ${total.toFixed(2)}`,
            ];
          });

          const table = [
            `| ${headers.join(' | ')} |`,
            `| ${headers.map(() => '---').join(' | ')} |`,
            ...rows.map(row => `| ${row.join(' | ')} |`),
          ].join('\n');

          let detailsText = '';
          if (args.include_details) {
            detailsText = '\n\n**Invoice Details:**\n';
            for (const [partnerId, data] of aging.entries()) {
              detailsText += `\n**${data.partner_name}:**\n`;
              for (const detail of data.details) {
                detailsText += `- ${detail.invoice}: PHP ${detail.amount.toFixed(2)} (${detail.days_overdue} days overdue)\n`;
              }
            }
          }

          const grandTotal = Array.from(aging.values())
            .reduce((sum, a) => sum + a.buckets.reduce((s: number, amt: number) => s + amt, 0), 0);

          return {
            content: [
              {
                type: 'text',
                text: `# Accounts Payable Aging Report\n\n` +
                      `**As of:** ${asOfDate.toISOString().split('T')[0]}\n` +
                      `${args.employee_code ? `**Employee:** ${args.employee_code}\n` : ''}` +
                      `**Vendors:** ${aging.size}\n` +
                      `**Total AP:** PHP ${grandTotal.toFixed(2)}\n\n` +
                      `${table}${detailsText}`,
              },
            ],
          };
        } catch (error: any) {
          return {
            content: [
              {
                type: 'text',
                text: `❌ Failed to query AP aging:\n${error.message}`,
              },
            ],
          };
        }
      },
    },

    {
      name: 'odoo:account:list-journals',
      description: 'List available journals (for use in journal entries)',
      inputSchema: {
        type: 'object',
        properties: {
          type: {
            type: 'string',
            enum: ['sale', 'purchase', 'cash', 'bank', 'general'],
            description: 'Filter by journal type',
          },
        },
      },
      handler: async (args: any) => {
        try {
          const domain: any[] = [];
          if (args.type) {
            domain.push(['type', '=', args.type]);
          }

          const journals = await odoo.search_read('account.journal', {
            domain,
            fields: ['id', 'name', 'code', 'type'],
            limit: 100,
          });

          const table = [
            '| ID | Code | Name | Type |',
            '| --- | --- | --- | --- |',
            ...journals.map((j: any) => `| ${j.id} | ${j.code} | ${j.name} | ${j.type} |`),
          ].join('\n');

          return {
            content: [
              {
                type: 'text',
                text: `# Available Journals\n\n${table}\n\nUse the **ID** column when creating journal entries.`,
              },
            ],
          };
        } catch (error: any) {
          return {
            content: [
              {
                type: 'text',
                text: `❌ Failed to list journals:\n${error.message}`,
              },
            ],
          };
        }
      },
    },
  ];
}
