# Expense Companion PWA

Mobile-first Odoo expense companion app for receipt capture, approvals, and reimbursement tracking.

This app is aligned to:

- `spec/reverse-sap-concur`
- `spec/expense-parity-odoo`
- `spec/sap-joule-concur-odoo-azure`

## Runtime contract

- Uses the Odoo web session through Next.js rewrites under `/api/odoo/*`
- Falls back to seeded demo data when no active Odoo session is available
- Ships as an installable PWA with offline fallback and camera-first receipt capture

## Environment

- `NEXT_PUBLIC_ODOO_URL`
- `NEXT_PUBLIC_ODOO_DB`
