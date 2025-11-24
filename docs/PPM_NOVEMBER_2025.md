# Notion / Clarity-Style PPM — November 2025 Close (Kickoff: 24 Nov)

This playbook instantiates the Finance PPM spine for the **November 2025 close** using the existing assets and Odoo project boards as status trackers. It avoids any new Odoo module work and focuses on activating the already-delivered framework (Logical Framework, unified workbook directory, BIR tax calendar 2025–2026, and monthly task matrix).

## 1) Scope and prerequisites
- **Projects in Odoo**: `Month-End Closing` and `BIR Tax Filing 2025–2026` already exist. Use them only as Kanban/status boards.
- **Logical framework anchors**: Goal → Outcomes → IM1 (Month-End Closing) and IM2 (Tax Filing Compliance).
- **People directory**: Use the code/email directory (CKVC, RIM, BOM, JPAL, LAS, JI, JO, JM, RMQB, JAP, JRMO…) for assignment fields.
- **Monthly task matrix**: Source of categories, detailed tasks, reviewer/approver, and SLA (1d prep, 0.5d review, 0.5d approval) for November.
- **BIR calendar 2025–2026**: Use the legal deadlines and apply the internal −4/−2/−1 business-day offsets.

## 2) Kickoff actions for 24 Nov
1. **Freeze project boards**
   - In **Month-End Closing**: duplicate last month’s stages/tasks (if not already), filter to **Nov 2025**, and reset status to `To Do`.
   - In **BIR Tax Filing 2025–2026**: confirm forms tied to **November data** (e.g., 1601-C for Nov payroll, VAT monthly if applicable, Q4 VAT).
2. **Apply owner/reviewer/approver**
   - Map every task card to **Owner**, **Reviewer**, **Approver** using the code directory.
   - Enforce SLA-backed target dates (prep = +1d, review = +0.5d, approval = +0.5d from the prep start).
3. **Attach evidence**
   - Link Superset/Excel/Odoo exports to each card as it moves `To Do → In Progress → For Review → For Approval → Approved`.

## 3) Execution timeline (IM1: Month-End)
- **24 Nov** – Kickoff and board freeze (steps above).
- **25–27 Nov** – Pre-close execution per task matrix (accruals, WIP, tax & provisions, leases, FX reval, CA liquidations, AP aging, etc.).
- **28–29 Nov** – Review cycle: reviewers move cards `For Review → For Approval`; log adjustments as sub-tasks.
- **1–2 Dec** – Approvals: CKVC approves critical categories (Payroll, VAT & Taxes, Treasury, Regional Reporting) and locks numbers.
- **3–4 Dec** – Final close packaging: create a "**November Close – Summary**" card linking TB/flash, reconciliation packs, and accruals/WIP summary.

## 4) BIR workflow alignment (IM2: Tax Filing)
Use the BIR calendar (2025–2026) with **−4/−2/−1 business-day** offsets for prep/review/approval. Track these in **BIR Tax Filing 2025–2026** with fields: period covered, BIR deadline, prep owner (Finance Supervisor), reviewer (BOM or RIM), approver (CKVC), and linked evidence.

| Form | Period | BIR deadline | Prep (−4 BD) | Review (−2 BD) | Approval (−1 BD) | Board |
| --- | --- | --- | --- | --- | --- | --- |
| 1601-C | Nov 2025 payroll | **2025-12-15** | 2025-12-09 | 2025-12-11 | 2025-12-12 | BIR Tax Filing 2025–2026 |
| 2550Q | Q4 2025 VAT (Nov data included) | **2026-01-25** | 2026-01-20 | 2026-01-22 | 2026-01-23 | BIR Tax Filing 2025–2026 |

> Adjust prep/review/approval one business day earlier if the legal deadline falls on a non-working day and shifts forward.

## 5) Minimal “ship” checklist (today)
- [ ] Both boards filtered to **Nov 2025** with tasks reset to `To Do`.
- [ ] Every card populated with **Owner, Reviewer, Approver, Target date** (per SLA).
- [ ] Evidence placeholders added (links to sheets/exports).
- [ ] Critical-path approvals assigned to **CKVC** and visible in the board.
- [ ] "**November Close – Summary**" card created and linked from Month-End Closing.

Once the checklist is complete, you have shipped **“TBWA Finance PPM – November 2025 Close & BIR Readiness”** using the existing Notion/Clarity-style framework with live Odoo status boards.
