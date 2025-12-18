
# ipai_finance_project_hybrid

Odoo 18 addon that:

- Seeds Finance Directory (code → person), BIR Schedule, and Month-End task templates from a bundled JSON file.
- Generates two child IM projects under a root project:
  - **IM1**: Month-End Close
  - **IM2**: Tax & BIR Compliance
- Generates tasks automatically (idempotent) and adds finance-centric task analytics (pivot + graph).

## Usage

1. Install the addon.
2. Go to **Project → Finance Ops → Configuration → Seed Finance Framework** (optional; auto-seeded on install if empty).
3. Open a root project and click **Generate IM Projects**.

## Notes

- Assignment is via `Owner Code` (directory). If a matching user exists with `login=email`, the user is assigned automatically.
- Dashboards are in **Project → Finance Ops → Finance Task Analytics**.
