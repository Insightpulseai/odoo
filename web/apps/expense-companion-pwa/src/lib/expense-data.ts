import { getOdooClient } from '@/lib/odoo-client';

export interface ExpenseRecord {
  id: string;
  title: string;
  merchant: string;
  category: string;
  amount: number;
  date: string;
  status: 'Draft' | 'Submitted' | 'Manager Review' | 'Approved' | 'Paid';
  paymentMode: 'Employee' | 'Company';
  reportName: string;
  policyNote: string;
}

interface AlertItem {
  title: string;
  detail: string;
  severity: 'watch' | 'urgent' | 'clear';
}

export interface ExpenseDashboardSnapshot {
  source: 'demo' | 'odoo';
  sessionLabel: string;
  expenses: ExpenseRecord[];
  alerts: AlertItem[];
}

const demoExpenses: ExpenseRecord[] = [
  {
    id: 'demo-1',
    title: 'Client dinner in Makati',
    merchant: 'Blackbird',
    category: 'Meals',
    amount: 4820,
    date: 'Apr 27',
    status: 'Manager Review',
    paymentMode: 'Employee',
    reportName: 'APR WK4 FIELD',
    policyNote: 'Attach attendee list before accounting can release reimbursement.',
  },
  {
    id: 'demo-2',
    title: 'Airport transfer',
    merchant: 'Grab',
    category: 'Ground transport',
    amount: 1260,
    date: 'Apr 27',
    status: 'Submitted',
    paymentMode: 'Employee',
    reportName: 'APR WK4 FIELD',
    policyNote: 'Policy-compliant. Waiting for manager decision.',
  },
  {
    id: 'demo-3',
    title: 'Project site fuel',
    merchant: 'Shell NLEX',
    category: 'Mileage',
    amount: 3380,
    date: 'Apr 26',
    status: 'Approved',
    paymentMode: 'Company',
    reportName: 'Q2 CLIENT VISITS',
    policyNote: 'Approved and batched for month-end clearing.',
  },
  {
    id: 'demo-4',
    title: 'Hotel wifi add-on',
    merchant: 'Seda BGC',
    category: 'Lodging',
    amount: 780,
    date: 'Apr 24',
    status: 'Paid',
    paymentMode: 'Employee',
    reportName: 'Q2 CLIENT VISITS',
    policyNote: 'Paid to payroll reimbursement on Apr 25.',
  },
];

export async function loadExpenseDashboard(): Promise<ExpenseDashboardSnapshot> {
  const client = getOdooClient();

  try {
    const session = await client.getSessionInfo();
    if (!session) {
      return demoSnapshot();
    }

    const expenses = await client.searchRead('hr.expense', [], [
      'name',
      'date',
      'total_amount',
      'payment_mode',
      'state',
      'employee_id',
      'product_id',
    ], {
      limit: 8,
      order: 'date desc, id desc',
    });

    const normalized = expenses.map((expense: Record<string, unknown>, index: number) => {
      const productName = readMany2OneLabel(expense.product_id) || 'Expense item';
      const employeeName = readMany2OneLabel(expense.employee_id) || 'Odoo employee';

      return {
        id: String(expense.id ?? `odoo-${index}`),
        title: String(expense.name ?? productName),
        merchant: employeeName,
        category: productName,
        amount: Number(expense.total_amount ?? 0),
        date: formatDate(expense.date),
        status: mapOdooState(String(expense.state ?? 'draft')),
        paymentMode: mapPaymentMode(String(expense.payment_mode ?? 'own_account')),
        reportName: 'ODOO LIVE',
        policyNote: 'Live Odoo session detected. Extend this feed with employee-specific domains next.',
      } satisfies ExpenseRecord;
    });

    return {
      source: 'odoo',
      sessionLabel: session.username,
      expenses: normalized.length > 0 ? normalized : demoExpenses,
      alerts: buildAlerts(normalized.length > 0 ? normalized : demoExpenses),
    };
  } catch {
    return demoSnapshot();
  }
}

export function summarizeStatusBreakdown(expenses: ExpenseRecord[]) {
  const statusOrder: ExpenseRecord['status'][] = ['Draft', 'Submitted', 'Manager Review', 'Approved'];

  return statusOrder.map((status) => {
    const matching = expenses.filter((expense) => expense.status === status);

    return {
      status,
      count: matching.length,
      total: matching.reduce((sum, expense) => sum + expense.amount, 0),
    };
  });
}

function demoSnapshot(): ExpenseDashboardSnapshot {
  return {
    source: 'demo',
    sessionLabel: 'Demo mode',
    expenses: demoExpenses,
    alerts: buildAlerts(demoExpenses),
  };
}

function buildAlerts(expenses: ExpenseRecord[]): AlertItem[] {
  const hasEmployeeReceipts = expenses.some((expense) => expense.paymentMode === 'Employee' && expense.status !== 'Paid');
  const managerReviewCount = expenses.filter((expense) => expense.status === 'Manager Review').length;
  const draftCount = expenses.filter((expense) => expense.status === 'Draft').length;

  return [
    {
      title: 'Unreimbursed employee spend',
      detail: hasEmployeeReceipts
        ? 'Employee-paid receipts are still open. Keep the queue tight to avoid payroll spillover.'
        : 'No employee-funded expenses are currently waiting for reimbursement.',
      severity: hasEmployeeReceipts ? 'urgent' : 'clear',
    },
    {
      title: 'Manager bottleneck',
      detail:
        managerReviewCount > 0
          ? `${managerReviewCount} expense item(s) are waiting on manager review.`
          : 'No manager-review backlog is visible in the current snapshot.',
      severity: managerReviewCount > 0 ? 'watch' : 'clear',
    },
    {
      title: 'Draft cleanup',
      detail:
        draftCount > 0
          ? `${draftCount} draft item(s) still need final detail and receipt attachment.`
          : 'Draft queue is clear.',
      severity: draftCount > 0 ? 'watch' : 'clear',
    },
  ];
}

function mapOdooState(state: string): ExpenseRecord['status'] {
  switch (state) {
    case 'submit':
      return 'Submitted';
    case 'reported':
      return 'Manager Review';
    case 'approved':
      return 'Approved';
    case 'done':
      return 'Paid';
    default:
      return 'Draft';
  }
}

function mapPaymentMode(paymentMode: string): ExpenseRecord['paymentMode'] {
  return paymentMode === 'company_account' ? 'Company' : 'Employee';
}

function readMany2OneLabel(value: unknown): string | null {
  if (Array.isArray(value) && typeof value[1] === 'string') {
    return value[1];
  }

  return null;
}

function formatDate(value: unknown): string {
  if (typeof value !== 'string') {
    return 'Recent';
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
}
