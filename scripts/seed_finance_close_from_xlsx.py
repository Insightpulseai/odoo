#!/usr/bin/env python3
"""
Seed Finance Close from XLSX

Regenerates seed data files for ipai_finance_close_seed module from the
Month-end Closing Task and Tax Filing Excel file.

Usage:
    python scripts/seed_finance_close_from_xlsx.py [path_to_xlsx]

    If no path provided, uses: config/finance/Month-end Closing Task and Tax Filing (7).xlsx
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is required. Install with: pip install pandas openpyxl")
    sys.exit(1)

# Module output directory
OUT_DIR = (
    Path(__file__).parent.parent
    / "addons"
    / "ipai"
    / "ipai_finance_close_seed"
    / "data"
)

# Tag mapping from category name to XML ID
TAG_MAP = {
    "Payroll & Personnel": "tag_payroll_personnel",
    "Tax & Provisions": "tag_tax_provisions",
    "Rent & Leases": "tag_rent_leases",
    "Accruals & Expenses": "tag_accruals_expenses",
    "Prior Period Review": "tag_prior_period_review",
    "Amortization & Corporate": "tag_amortization_corporate",
    "Corporate Accruals": "tag_corporate_accruals",
    "Insurance": "tag_insurance",
    "Treasury & Other": "tag_treasury_other",
    "Regional Reporting": "tag_regional_reporting",
    "Client Billings": "tag_client_billings",
    "WIP/OOP Management": "tag_wip_oop_management",
    "AR Aging - WC": "tag_ar_aging_wc",
    "CA Liquidations": "tag_ca_liquidations",
    "AP Aging - WC": "tag_ap_aging_wc",
    "OOP": "tag_oop",
    "Asset & Lease Entries": "tag_asset_lease_entries",
    "Reclassifications": "tag_reclassifications",
    "VAT & Taxes": "tag_vat_taxes",
    "Accruals & Assets": "tag_accruals_assets",
    "AP Aging": "tag_ap_aging",
    "Expense Reclassification": "tag_expense_reclassification",
    "VAT Reporting": "tag_vat_reporting",
    "Job Transfers": "tag_job_transfers",
    "Accruals": "tag_accruals",
    "WIP": "tag_wip",
}

# Task code prefix mapping from category to short code
# Aligns with Supabase Logframe CSV and Odoo Import sheets
TASK_CODE_MAP = {
    "Payroll & Personnel": "PAYROLL",
    "Tax & Provisions": "TAX_PROV",
    "Rent & Leases": "RENT",
    "Accruals & Expenses": "ACCRUAL",
    "Prior Period Review": "PRIOR",
    "Amortization & Corporate": "AMORT",
    "Corporate Accruals": "CORP_ACC",
    "Insurance": "INSURE",
    "Treasury & Other": "TREASURY",
    "Regional Reporting": "REGIONAL",
    "Client Billings": "BILLING",
    "WIP/OOP Management": "WIP_OOP",
    "AR Aging - WC": "AR_WC",
    "CA Liquidations": "CA_LIQ",
    "AP Aging - WC": "AP_WC",
    "OOP": "OOP",
    "Asset & Lease Entries": "ASSET",
    "Reclassifications": "RECLASS",
    "VAT & Taxes": "VAT",
    "Accruals & Assets": "ACC_ASSET",
    "AP Aging": "AP",
    "Expense Reclassification": "EXP_REC",
    "VAT Reporting": "VAT_RPT",
    "Job Transfers": "JOB_XFER",
    "Accruals": "ACCRUALS",
    "WIP": "WIP",
}

# OCA-compatible stage mapping (external IDs)
# Aligns with OCA Stage Config sheet in workbook
STAGE_MAP = {
    "todo": "ipai_stage_todo",
    "preparation": "ipai_stage_preparation",
    "review": "ipai_stage_review",
    "approval": "ipai_stage_approval",
    "done": "ipai_stage_done",
    "cancelled": "ipai_stage_cancelled",
}

# Category counters for generating unique task codes
_category_counters: dict[str, int] = {}


def duration_to_hours(s) -> float:
    """Convert duration like '1 Day' or '0.5 Day' to hours."""
    if pd.isna(s):
        return 0.0
    s = str(s).strip().lower().replace("days", "day")
    if "day" in s:
        try:
            n = float(s.split("day")[0].strip())
            return n * 8.0
        except ValueError:
            return 0.0
    return 0.0


def xml_escape(s) -> str:
    """Escape XML special characters."""
    if not s or pd.isna(s):
        return ""
    s = str(s)
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    return s


def make_id(s: str) -> str:
    """Convert string to valid XML ID component."""
    s = str(s).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")[:50]


def parse_date(val):
    """Parse date from various formats."""
    if pd.isna(val):
        return None
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.date()
    s = str(val).strip()
    try:
        dt = pd.to_datetime(val)
        return dt.date()
    except Exception:
        pass
    # Try extracting date from strings like "Oct 12 (Oct 10 is Sat)"
    match = re.match(r"(\w+)\s+(\d+)", s)
    if match:
        month_str, day_str = match.groups()
        try:
            dt = pd.to_datetime(f"{month_str} {day_str} 2026")
            return dt.date()
        except Exception:
            pass
    return None


def parse_period(val) -> str:
    """Parse period covered from various formats."""
    if pd.isna(val):
        return ""
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.strftime("%b %Y")
    return str(val).strip()


def generate_task_code(category: str, seq: int) -> str:
    """Generate a unique task code from category and sequence."""
    prefix = TASK_CODE_MAP.get(category, "CLOSE")
    return f"{prefix}_{seq:03d}"


def generate_month_end_tasks(xlsx_path: Path) -> tuple[int, list[dict]]:
    """Generate month-end tasks XML from Excel.

    Returns tuple of (count, task_list) where task_list contains task metadata
    for CSV export alignment.
    """
    closing = pd.read_excel(xlsx_path, sheet_name="Closing Task")

    # Clean and forward-fill
    closing["Employee Code"] = closing["Employee Code"].ffill()
    closing["Task Category"] = closing["Task Category"].ffill()

    # Reset category counters for task code generation
    category_counters: dict[str, int] = {}

    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        "<odoo>",
        '    <data noupdate="1">',
    ]
    count = 0
    task_list = []

    for i, row in closing.iterrows():
        name = str(row["Detailed Monthly Tasks"]).strip()
        if not name or name.lower() == "nan":
            continue

        category = (
            str(row["Task Category"]).strip()
            if not pd.isna(row["Task Category"])
            else ""
        )
        employee_code = (
            str(row["Employee Code"]).strip()
            if not pd.isna(row["Employee Code"])
            else ""
        )
        reviewed_by = (
            str(row["Reviewed by"]).strip() if not pd.isna(row["Reviewed by"]) else ""
        )
        approved_by = (
            str(row["Approved by"]).strip() if not pd.isna(row["Approved by"]) else ""
        )

        prep_hours = duration_to_hours(row["Preparation"])
        review_hours = duration_to_hours(row["Review"])
        approval_hours = duration_to_hours(row["Approval"])
        total_hours = prep_hours + review_hours + approval_hours

        # Generate unique task code
        category_counters[category] = category_counters.get(category, 0) + 1
        task_code = generate_task_code(category, category_counters[category])

        tag_ref = TAG_MAP.get(category, "")
        task_id = f"task_close_{count + 1:02d}_{make_id(name[:30])}"

        # Enhanced description with task_code for cross-sheet alignment
        desc = f"Task Code: {task_code}\\nCategory: {category}\\nEmployee Code: {employee_code}\\nReviewed by: {reviewed_by}\\nApproved by: {approved_by}"

        lines.append(f'        <record id="{task_id}" model="project.task">')
        lines.append(f'            <field name="name">{xml_escape(name)}</field>')
        lines.append(
            '            <field name="project_id" ref="project_month_end_template"/>'
        )
        # Default stage: preparation (matches workbook OCA Stage Config)
        lines.append(
            f'            <field name="stage_id" ref="{STAGE_MAP["preparation"]}"/>'
        )
        if tag_ref:
            lines.append(
                f'            <field name="tag_ids" eval="[(6, 0, [ref(\'{tag_ref}\')])]"/>'
            )
        lines.append(f'            <field name="planned_hours">{total_hours}</field>')
        lines.append(
            f'            <field name="description">{xml_escape(desc)}</field>'
        )
        lines.append("        </record>")

        # Store task metadata for CSV export
        task_list.append({
            "task_code": task_code,
            "task_id": task_id,
            "name": name,
            "category": category,
            "employee_code": employee_code,
            "reviewed_by": reviewed_by,
            "approved_by": approved_by,
            "planned_hours": total_hours,
        })
        count += 1

    lines.append("    </data>")
    lines.append("</odoo>")

    output_path = OUT_DIR / "tasks_month_end.xml"
    output_path.write_text("\n".join(lines), encoding="utf-8")

    # Also generate CSV for Supabase/BI alignment
    csv_path = OUT_DIR / "tasks_month_end.csv"
    if task_list:
        import csv
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=task_list[0].keys())
            writer.writeheader()
            writer.writerows(task_list)

    return count, task_list


def generate_bir_tasks(xlsx_path: Path) -> tuple[int, list[dict]]:
    """Generate BIR tasks XML from Excel.

    Returns tuple of (count, task_list) where task_list contains task metadata
    for CSV export alignment.
    """
    tax = pd.read_excel(xlsx_path, sheet_name="Tax Filing")

    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        "<odoo>",
        '    <data noupdate="1">',
    ]
    count = 0
    task_list = []

    for i, row in tax.iterrows():
        bir_form = str(row["BIR Form"]).strip() if not pd.isna(row["BIR Form"]) else ""
        if not bir_form or bir_form.lower() == "nan":
            continue

        period = parse_period(row["Period Covered"])
        deadline = parse_date(row["BIR Filing & Payment Deadline (2026)"])

        name = f"{bir_form} - {period}"
        # Generate task code for BIR forms (e.g., TAX_1601C_001)
        task_code = f"TAX_{make_id(bir_form).upper()}_{count + 1:03d}"
        task_id = f"task_bir_{count + 1:02d}_{make_id(bir_form)}_{make_id(period)}"

        prep_date = parse_date(row["1. Prep & File Request (Finance Supervisor)"])
        review_date = parse_date(row["2. Report Approval (Senior Finance Manager)"])
        approval_date = parse_date(row["3. Payment Approval (Finance Director)"])

        desc_parts = [f"Task Code: {task_code}", f"BIR Form: {bir_form}", f"Period: {period}"]
        if deadline:
            desc_parts.append(f"Deadline: {deadline.isoformat()}")
        if prep_date:
            desc_parts.append(f"Prep Date: {prep_date.isoformat()}")
        if review_date:
            desc_parts.append(f"Review Date: {review_date.isoformat()}")
        if approval_date:
            desc_parts.append(f"Approval Date: {approval_date.isoformat()}")
        desc = "\\n".join(desc_parts)

        lines.append(f'        <record id="{task_id}" model="project.task">')
        lines.append(f'            <field name="name">{xml_escape(name)}</field>')
        lines.append(
            '            <field name="project_id" ref="project_bir_tax_filing"/>'
        )
        # Default stage: preparation
        lines.append(
            f'            <field name="stage_id" ref="{STAGE_MAP["preparation"]}"/>'
        )
        if deadline:
            lines.append(
                f'            <field name="date_deadline">{deadline.isoformat()}</field>'
            )
        lines.append(
            f'            <field name="description">{xml_escape(desc)}</field>'
        )
        lines.append("        </record>")

        # Store task metadata for CSV export
        task_list.append({
            "task_code": task_code,
            "task_id": task_id,
            "bir_form": bir_form,
            "period": period,
            "deadline": deadline.isoformat() if deadline else "",
            "prep_date": prep_date.isoformat() if prep_date else "",
            "review_date": review_date.isoformat() if review_date else "",
            "approval_date": approval_date.isoformat() if approval_date else "",
        })
        count += 1

    lines.append("    </data>")
    lines.append("</odoo>")

    output_path = OUT_DIR / "tasks_bir.xml"
    output_path.write_text("\n".join(lines), encoding="utf-8")

    # Also generate CSV for Supabase/BI alignment
    csv_path = OUT_DIR / "tasks_bir.csv"
    if task_list:
        import csv
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=task_list[0].keys())
            writer.writeheader()
            writer.writerows(task_list)

    return count, task_list


def main():
    parser = argparse.ArgumentParser(description="Generate seed data from Excel")
    parser.add_argument(
        "xlsx_path",
        nargs="?",
        default="config/finance/Month-end Closing Task and Tax Filing (7).xlsx",
        help="Path to the Excel file",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run validation checks (mirrors Excel Data Validation sheet)",
    )
    args = parser.parse_args()

    xlsx_path = Path(args.xlsx_path)
    if not xlsx_path.exists():
        print(f"Error: File not found: {xlsx_path}")
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    month_end_count, month_end_tasks = generate_month_end_tasks(xlsx_path)
    print(
        f"Generated {month_end_count} month-end tasks -> {OUT_DIR / 'tasks_month_end.xml'}"
    )
    print(f"  CSV export -> {OUT_DIR / 'tasks_month_end.csv'}")

    bir_count, bir_tasks = generate_bir_tasks(xlsx_path)
    print(f"Generated {bir_count} BIR tasks -> {OUT_DIR / 'tasks_bir.xml'}")
    print(f"  CSV export -> {OUT_DIR / 'tasks_bir.csv'}")

    print(f"\nTotal: {month_end_count + bir_count} tasks")

    if args.validate:
        print("\n=== Validation Checks ===")
        validate_seed_data(month_end_tasks, bir_tasks)

    print("\nTo install/update the seed module:")
    print("  ./odoo-bin -d <db> -u ipai_finance_close_seed --stop-after-init")


def validate_seed_data(month_end_tasks: list[dict], bir_tasks: list[dict]) -> bool:
    """Validate seed data (mirrors Excel Data Validation sheet checks)."""
    errors = []
    warnings = []

    # Check 1: All task codes unique
    all_codes = [t["task_code"] for t in month_end_tasks] + [t["task_code"] for t in bir_tasks]
    if len(all_codes) != len(set(all_codes)):
        duplicates = [c for c in all_codes if all_codes.count(c) > 1]
        errors.append(f"Duplicate task codes found: {set(duplicates)}")
    else:
        print("  [PASS] All task codes unique")

    # Check 2: All task IDs unique
    all_ids = [t["task_id"] for t in month_end_tasks] + [t["task_id"] for t in bir_tasks]
    if len(all_ids) != len(set(all_ids)):
        duplicates = [i for i in all_ids if all_ids.count(i) > 1]
        errors.append(f"Duplicate task IDs found: {set(duplicates)}")
    else:
        print("  [PASS] All task IDs unique")

    # Check 3: BIR deadlines present
    missing_deadlines = [t for t in bir_tasks if not t.get("deadline")]
    if missing_deadlines:
        warnings.append(f"BIR tasks missing deadlines: {len(missing_deadlines)}")
    else:
        print("  [PASS] All BIR deadlines present")

    # Check 4: Employee codes valid (known codes from workbook)
    known_codes = {"RIM", "BOM", "JPAL", "LAS", "JLI", "RMQB", "JAP", "JRMO", "CKVC"}
    for t in month_end_tasks:
        code = t.get("employee_code", "")
        if code and code not in known_codes:
            warnings.append(f"Unknown employee code: {code} in task {t['task_code']}")

    # Check 5: Year mismatch validation for BIR tasks
    # Critical: Tax Filing approval dates must match or be after Period Covered year
    for t in bir_tasks:
        period_covered = t.get("period_covered", "")
        deadline = t.get("deadline")

        if period_covered and deadline:
            try:
                # Extract year from period_covered (e.g., "2026-12" -> 2026)
                period_year = int(period_covered.split("-")[0])
                # Extract year from deadline datetime
                deadline_year = datetime.fromisoformat(deadline.replace("Z", "+00:00")).year

                if deadline_year < period_year:
                    errors.append(
                        f"CRITICAL: Year mismatch in task {t['task_code']}: "
                        f"Period Covered {period_covered} (year {period_year}) but "
                        f"deadline in {deadline_year}. Approval date must be >= period year."
                    )
            except (ValueError, AttributeError, IndexError) as e:
                warnings.append(f"Could not validate year for task {t['task_code']}: {e}")

    if warnings:
        print(f"  [WARN] {len(warnings)} warnings found")
        for w in warnings[:5]:
            print(f"    - {w}")

    if errors:
        print(f"  [FAIL] {len(errors)} errors found")
        for e in errors:
            print(f"    - {e}")
        return False

    print("  [PASS] Validation complete - ready for import")
    return True


if __name__ == "__main__":
    main()
