# Migration and Cutover Protocol — Pulser for Odoo

This protocol defines the technical standards for migrating tenant data into the Pulser Hub and executing a verified production cutover.

---

## 1. Migration Inventory (BOM 13)

The following data sets constitute the mandatory migration scope for a production-ready tenant.

### Master Data (The Foundation)
- **Partner Registry**: Customers, Vendors, and Employees (aligned with HR records).
- **Chart of Accounts (COA)**: Unified Pulser/Tenant account mapping.
- **Product/Service Catalog**: Including tax-mapping and category definitions.
- **Project WBS**: WBS structures (Portfolio -> Project -> Workstream -> Task).

### Transactional Data (Open Items)
- **Open AR/AP**: Individual outstanding Invoices and Bills (reconstituted to maintain sub-ledger granularity).
- **Pending Expenses**: Expenses in "Submitted" or "Approved" state not yet posted.
- **Opening Balances**: Trial Balance balances as of the cutover date.
- **Bank History**: Opening bank balances per statement.

### Historical Data (Audit Trail)
- **Trial Balance Snapshots**: At least 24 months of monthly TB snapshots (account-level balances).
- **Previous Years**: Optional high-level P&L and Balance Sheet summaries.

## 2. The Conversion Lifecycle

1. **Extraction**: Automated/Manual extraction from Legacy ERP/Spreadsheets.
2. **Transformation**: Mapping legacy tags/centers to Odoo 18 **Analytic Accounts** and **Tags**.
3. **Loading**:
    - **Initial Load**: Master and Historical data (Staging stamp).
    - **Delta Load**: Open transactions (during Cutover Window).
4. **Validation**: Execute the **Data Reconciliation Routine (FACT-DG-01)**.

## 3. Cutover Validation Routine

The cutover is only verified when the following checks return **Zero Variance**:

| Level | Component | Check Type |
|-------|-----------|------------|
| GL | Trial Balance | Total Debits == Total Credits; TB vs Legacy Match. |
| Sub-ledger | Accounts Receivable | Total Open AR per Odoo == Total Open AR per Legacy. |
| Sub-ledger | Accounts Payable | Total Open AP per Odoo == Total Open AP per Legacy. |
| Cash | Bank Balance | Odoo Bank Journal Balance == Bank Statement Balance. |

---

*Last updated: 2026-04-11*
