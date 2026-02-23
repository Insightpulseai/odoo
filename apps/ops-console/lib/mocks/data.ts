// apps/ops-console/lib/mock-data.ts

export const BUILDS = [
  { id: 1, branch: "main", stage: "production", sha: "a3f9c21", msg: "fix(account): BIR 2307 tax computation", author: "jgtolentino", status: "success", modules: ["ipai_bir_tax", "ipai_accounting"], ts: "2026-02-23T08:12:00Z", dur: 47 },
  { id: 2, branch: "staging/expense-ocr", stage: "staging", sha: "d7b4e08", msg: "feat(expense): PaddleOCR receipt parsing", author: "jgtolentino", status: "warning", modules: ["ipai_expense_ocr"], ts: "2026-02-23T06:30:00Z", dur: 123 },
  { id: 3, branch: "staging/approval-flow", stage: "staging", sha: "1ec83fa", msg: "feat(purchase): 3-tier approval workflow", author: "jgtolentino", status: "success", modules: ["ipai_purchase_approval"], ts: "2026-02-22T14:20:00Z", dur: 65 },
  { id: 4, branch: "dev/payroll-13th", stage: "development", sha: "8f2a1b3", msg: "wip: 13th month pay computation", author: "jgtolentino", status: "building", modules: ["ipai_payroll_ph"], ts: "2026-02-23T09:45:00Z", dur: null },
  { id: 5, branch: "main", stage: "production", sha: "c91d5e7", msg: "fix(reports): aged receivable date filter", author: "jgtolentino", status: "success", modules: ["account_financial_report"], ts: "2026-02-21T11:00:00Z", dur: 38 },
  { id: 6, branch: "dev/vendor-portal", stage: "development", sha: "4a7f2c9", msg: "feat: vendor self-service portal", author: "jgtolentino", status: "failed", modules: ["ipai_vendor_portal"], ts: "2026-02-22T09:15:00Z", dur: 89 },
];

export const SYNC_STATUS = [
  { model: "account.move", last: "2026-02-23T09:50:00Z", records: 1247, status: "synced", delta: 3 },
  { model: "account.payment", last: "2026-02-23T09:48:00Z", records: 893, status: "synced", delta: 1 },
  { model: "res.partner", last: "2026-02-23T09:45:00Z", records: 2341, status: "synced", delta: 12 },
  { model: "product.product", last: "2026-02-23T08:00:00Z", records: 456, status: "stale", delta: 0 },
  { model: "hr.expense", last: "2026-02-23T09:30:00Z", records: 178, status: "synced", delta: 5 },
  { model: "purchase.order", last: "2026-02-23T07:00:00Z", records: 312, status: "error", delta: 0, error: "RPC timeout after 30s" },
];

export const DLQ_ITEMS = [
  { id: 1, model: "purchase.order", odoo_id: 1847, error: "RPC timeout: connection refused", attempts: 3, created: "2026-02-23T07:01:00Z" },
  { id: 2, model: "account.move", odoo_id: 5923, error: "Checksum mismatch on amount_total", attempts: 1, created: "2026-02-23T09:12:00Z" },
  { id: 3, model: "res.partner", odoo_id: 441, error: "Duplicate external_id conflict", attempts: 5, created: "2026-02-22T16:00:00Z" },
];

export const MODULES = [
  { name: "ipai_bir_tax", version: "19.0.2.1.0", stage: "production", oca: false },
  { name: "ipai_accounting", version: "19.0.1.4.2", stage: "production", oca: false },
  { name: "account_financial_report", version: "19.0.1.0.1", stage: "production", oca: true },
  { name: "account_payment_order", version: "19.0.1.0.0", stage: "production", oca: true },
  { name: "ipai_expense_ocr", version: "19.0.0.3.0", stage: "staging", oca: false },
  { name: "ipai_purchase_approval", version: "19.0.1.0.0", stage: "staging", oca: false },
  { name: "server_tools", version: "19.0.1.0.0", stage: "production", oca: true },
  { name: "ipai_payroll_ph", version: "19.0.0.1.0", stage: "development", oca: false },
];

export const TEAM = [
  { code: "JGT", name: "Jake Tolentino", role: "admin", email: "jake.tolentino@insightpulseai.com", active: true },
  { code: "CKVC", name: "Finance Director", role: "manager", email: "ckvc@tbwasmp.com", active: true },
  { code: "RIM", name: "Sr. Finance Manager", role: "manager", email: "rim@tbwasmp.com", active: true },
  { code: "BOM", name: "Finance Supervisor", role: "supervisor", email: "bom@tbwasmp.com", active: true },
  { code: "LAS", name: "Accountant", role: "viewer", email: "las@tbwasmp.com", active: true },
  { code: "JAP", name: "Accountant", role: "viewer", email: "jap@tbwasmp.com", active: false },
];

export const QUERIES = [
  "SELECT count(*) FROM odoo_replica.account_move WHERE state = 'posted' AND date >= '2026-01-01'",
  "SELECT partner_name, sum(amount_residual) FROM odoo_replica.account_move_line GROUP BY partner_name ORDER BY 2 DESC LIMIT 10",
  "SELECT * FROM ops.runs WHERE status = 'failed' ORDER BY started_at DESC LIMIT 5",
];

// ─── End of Data ─────────────────────────────────────────────────
