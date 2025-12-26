#!/usr/bin/env python3
"""
Generate canonical Odoo XML seed data from Excel RACI + milestone spreadsheet.

Source: config/finance/Month-end Closing Task and Tax Filing (7).xlsx
Output: addons/ipai_finance_ppm_umbrella/data/*.xml

Usage:
    python3 addons/ipai_finance_ppm_umbrella/scripts/generate_seed_from_excel.py
"""
import pandas as pd
from pathlib import Path
from lxml import etree
from datetime import datetime

# Paths
# Script location: /Users/tbwa/Downloads/addons/ipai_finance_ppm_umbrella/scripts/generate_seed_from_excel.py
# Project root: /Users/tbwa/Downloads
BASE_DIR = Path(__file__).resolve().parents[3]  # Go up: scripts/ → ipai_finance_ppm_umbrella/ → addons/ → Downloads/
EXCEL_PATH = BASE_DIR / "config/finance/Month-end Closing Task and Tax Filing (7).xlsx"
DATA_DIR = BASE_DIR / "addons/ipai_finance_ppm_umbrella/data"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names: lowercase, snake_case, remove special chars."""
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^0-9a-zA-Z_]", "", regex=True)
    )
    return df


def make_root():
    """Create XML root with <odoo><data noupdate="1">."""
    root = etree.Element("odoo")
    data = etree.SubElement(root, "data", noupdate="1")
    return root, data


def write_xml(root: etree._Element, out_path: Path):
    """Write XML tree to file with proper formatting."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tree = etree.ElementTree(root)
    tree.write(
        str(out_path),
        encoding="utf-8",
        xml_declaration=True,
        pretty_print=True,
    )
    print(f"✅ Generated: {out_path.relative_to(BASE_DIR)}")


def generate_employees(closing_df: pd.DataFrame):
    """
    Generate 01_employees.xml from unique employee codes in Closing Task sheet.

    Creates res.users records for: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB
    """
    employees = sorted(
        set(e for e in closing_df["employee_code"].dropna().unique() if str(e).strip())
    )

    root, data = make_root()

    # Add XML comment
    comment = etree.Comment(" 8 Employees for TBWA Finance SSC ")
    data.append(comment)

    for code in employees:
        code_clean = str(code).strip()
        if not code_clean:
            continue

        rec = etree.SubElement(
            data,
            "record",
            id=f"user_{code_clean.lower()}",
            model="res.users",
        )
        etree.SubElement(rec, "field", name="name").text = code_clean
        etree.SubElement(rec, "field", name="login").text = code_clean.lower()
        # Optional: add default groups
        # etree.SubElement(rec, "field", name="groups_id", eval="[(4, ref('base.group_user'))]")

    write_xml(root, DATA_DIR / "01_employees.xml")
    return employees


def generate_logframe(closing_df: pd.DataFrame):
    """
    Generate 02_logframe_complete.xml from task categories.

    Creates 12 logframe entries (Goal → Activities) based on unique task categories.
    """
    root, data = make_root()

    # Get unique task categories (filter NaN and empty strings)
    categories = [
        cat for cat in closing_df["task_category"].dropna().astype(str).unique()
        if cat.strip() and cat.lower() != "nan"
    ][:12]  # Limit to 12 entries

    comment = etree.Comment(" 12 Logframe Entries: Goal → Outcome → IM1/IM2 → Outputs → Activities ")
    data.append(comment)

    # Predefined logframe hierarchy
    logframe_entries = [
        {
            "code": "GOAL-001",
            "level": "goal",
            "name": "100% Compliant and Timely Month-End Closing and Tax Filing",
            "indicators": "% of deadlines met; # of penalties; total penalty amount",
            "verification": "BIR receipts; audit reports; bank statements",
            "assumptions": "Government systems operational; reviewers responsive",
        },
        {
            "code": "OUTCOME-001",
            "level": "outcome",
            "name": "Zero-Penalty Compliance with Timely Financial Reporting",
            "indicators": "Zero BIR penalties; 100% on-time month-end close",
            "verification": "BIR confirmation receipts; monthly close reports",
            "assumptions": "Adequate resources; stable systems",
        },
        {
            "code": "IM1",
            "level": "im1",
            "name": "Month-End Closing Processes",
            "indicators": "Books closed within 5 business days; Zero material misstatements",
            "verification": "Trial balance; account reconciliations",
            "assumptions": "All departments submit data on time",
        },
        {
            "code": "IM2",
            "level": "im2",
            "name": "Tax Filing Compliance",
            "indicators": "% of filings before deadline; # of late filings; penalty amount",
            "verification": "BIR filing tracker; bank debit advices",
            "assumptions": "BIR portals operational; approvers available",
        },
    ]

    # Add outputs from task categories (max 4)
    for idx, cat in enumerate(categories[:4], start=1):
        logframe_entries.append({
            "code": f"OUT-{idx:02d}",
            "level": "output",
            "name": f"{cat} Completed",
            "indicators": f"# of {cat.lower()} tasks completed; Accuracy rate",
            "verification": f"{cat} task checklist; approval signatures",
            "assumptions": "Data available; systems accessible",
        })

    # Add activities from task categories (max 4)
    for idx, cat in enumerate(categories[:4], start=1):
        logframe_entries.append({
            "code": f"ACT-IM{(idx % 2) + 1}-{idx:02d}",
            "level": f"activity_im{(idx % 2) + 1}",
            "name": f"Execute {cat} Tasks",
            "indicators": f"Task completion rate; Time to complete",
            "verification": f"Task logs; timesheet records",
            "assumptions": "Required documents available",
        })

    for idx, entry in enumerate(logframe_entries, start=1):
        rec = etree.SubElement(
            data,
            "record",
            id=f"logframe_{idx:03d}_{entry['code'].lower().replace('-', '_')}",
            model="ipai.finance.logframe",
        )
        etree.SubElement(rec, "field", name="level").text = entry["level"]
        etree.SubElement(rec, "field", name="code").text = entry["code"]
        etree.SubElement(rec, "field", name="name").text = entry["name"]
        etree.SubElement(rec, "field", name="indicators").text = entry["indicators"]
        etree.SubElement(rec, "field", name="means_of_verification").text = entry["verification"]
        etree.SubElement(rec, "field", name="assumptions").text = entry["assumptions"]
        etree.SubElement(rec, "field", name="sequence").text = str(idx * 10)

    write_xml(root, DATA_DIR / "02_logframe_complete.xml")
    return categories


def generate_bir_schedule(tax_df: pd.DataFrame, employees: list):
    """
    Generate 03_bir_schedule.xml from Tax Filing sheet.

    Creates BIR schedule records with:
    - Form type (1601-C, 2550Q, 1601-EQ, 1702-RT, 1702Q)
    - Period covered
    - Deadlines (filing, prep, review, approval)
    - RACI assignments (supervisor, reviewer, approver)
    """
    root, data = make_root()

    comment = etree.Comment(" BIR Filing Schedule 2026 with RACI Matrix ")
    data.append(comment)

    # Filter valid rows (remove explanation rows at bottom)
    tax_df_clean = tax_df[tax_df["bir_form"].notna() & (tax_df["bir_form"] != "Step")].copy()

    record_count = 0
    for idx, row in tax_df_clean.iterrows():
        bir_form = str(row.get("bir_form", "")).strip()
        if not bir_form or bir_form.lower() in ["nan", "step"]:
            continue

        period_covered = str(row.get("period_covered", "")).strip()
        # Column names have double underscores after cleaning special chars
        filing_deadline = row.get("bir_filing__payment_deadline_2026")
        prep_deadline = row.get("1_prep__file_request_finance_supervisor")
        review_deadline = row.get("2_report_approval_senior_finance_manager")
        approval_deadline = row.get("3_payment_approval_finance_director")

        # Parse dates
        def parse_date(val):
            if pd.isna(val):
                return None
            if isinstance(val, datetime):
                return val.strftime("%Y-%m-%d")
            # Handle string dates
            val_str = str(val).strip()
            # Handle special cases like "Apr 27 (Apr 25 is Sat)"
            if "(" in val_str:
                val_str = val_str.split("(")[0].strip()
            try:
                return pd.to_datetime(val_str).strftime("%Y-%m-%d")
            except:
                return None

        filing_date = parse_date(filing_deadline)
        prep_date = parse_date(prep_deadline)
        review_date = parse_date(review_deadline)
        approval_date = parse_date(approval_deadline)

        if not filing_date:
            continue  # Skip if no filing deadline

        # Determine if per-employee or shared
        # Monthly forms (1601-C, 0619-E) are per-employee
        # Quarterly forms (2550Q, 1601-EQ, 1702Q) are per-employee
        # Annual forms (1702-RT) are per-employee

        is_per_employee = True  # All forms are per-employee based on Excel structure

        if is_per_employee:
            for emp_code in employees:
                record_count += 1
                xml_id = f"bir_{bir_form.lower().replace('/', '_').replace(' ', '_')}_{period_covered.replace(' ', '_').lower()}_{emp_code.lower()}"

                rec = etree.SubElement(
                    data,
                    "record",
                    id=xml_id,
                    model="ipai.finance.bir_schedule",
                )
                etree.SubElement(rec, "field", name="name").text = f"{bir_form} – {period_covered} ({emp_code})"
                etree.SubElement(rec, "field", name="period_covered").text = period_covered

                # Deadlines
                if filing_date:
                    etree.SubElement(rec, "field", name="filing_deadline").text = filing_date
                if prep_date:
                    etree.SubElement(rec, "field", name="prep_deadline").text = prep_date
                if review_date:
                    etree.SubElement(rec, "field", name="review_deadline").text = review_date
                if approval_date:
                    etree.SubElement(rec, "field", name="approval_deadline").text = approval_date

                # RACI assignments (default mapping from Excel)
                # Supervisor: BOM, Reviewer: RIM (SFM), Approver: CKVC (FD)
                etree.SubElement(rec, "field", name="supervisor_id", ref="user_bom")
                etree.SubElement(rec, "field", name="reviewer_id", ref="user_rim")
                etree.SubElement(rec, "field", name="approver_id", ref="user_ckvc")

                # Link to IM2 logframe (Tax Filing Compliance)
                etree.SubElement(rec, "field", name="logframe_id", ref="logframe_004_im2")

                # Status
                etree.SubElement(rec, "field", name="status").text = "not_started"
                etree.SubElement(rec, "field", name="completion_pct").text = "0.0"

    write_xml(root, DATA_DIR / "03_bir_schedule.xml")
    print(f"   📊 Generated {record_count} BIR schedule records")


def generate_closing_tasks(closing_df: pd.DataFrame, categories: list):
    """
    Generate 04_closing_tasks.xml from Closing Task sheet.

    Creates month-end closing task records with:
    - Task category and details
    - Employee assignments
    - RACI matrix (prep, review, approve)
    - Task durations
    - Logframe linkage
    """
    root, data = make_root()

    comment = etree.Comment(" 36 Month-End Closing Tasks with RACI Matrix ")
    data.append(comment)

    def parse_days(val):
        """Convert '1 Day' or '0.5 Day' to float."""
        if pd.isna(val):
            return 0.0
        s = str(val).lower().replace("day", "").replace("days", "").strip()
        try:
            return float(s)
        except ValueError:
            return 0.0

    def logframe_ref_for_category(cat: str, categories: list) -> str:
        """Map task category to logframe reference."""
        try:
            idx = categories.index(cat)
            # Map to output logframe entries (005-008)
            lf_idx = 5 + (idx % 4)
            return f"logframe_{lf_idx:03d}_out_{(idx % 4) + 1:02d}"
        except (ValueError, IndexError):
            return "logframe_003_im1"  # Default to IM1

    record_count = 0
    current_employee = None

    for idx, row in closing_df.iterrows():
        emp_code = row.get("employee_code")
        if pd.notna(emp_code):
            current_employee = str(emp_code).strip()

        task_name = str(row.get("detailed_monthly_tasks", "")).strip()
        if not task_name or task_name.lower() == "nan":
            continue

        cat = str(row.get("task_category", "General")).strip()
        if cat.lower() == "nan":
            cat = "General"

        reviewed_by = str(row.get("reviewed_by", "")).strip()
        approved_by = str(row.get("approved_by", "")).strip()

        prep_days = parse_days(row.get("preparation"))
        review_days = parse_days(row.get("review"))
        approval_days = parse_days(row.get("approval"))

        record_count += 1
        xml_id = f"closing_task_{record_count:03d}"

        rec = etree.SubElement(
            data,
            "record",
            id=xml_id,
            model="project.task",  # Using standard Odoo project.task
        )
        etree.SubElement(rec, "field", name="name").text = task_name
        etree.SubElement(rec, "field", name="description").text = f"Category: {cat}\nEmployee: {current_employee or 'N/A'}"

        # Link to Finance PPM project
        etree.SubElement(rec, "field", name="project_id", ref="ipai_finance_ppm.project_month_end_closing")

        # Employee assignment (prep user)
        if current_employee:
            etree.SubElement(rec, "field", name="user_ids", eval=f"[(4, ref('user_{current_employee.lower()}'))]")

        # Link to logframe
        lf_ref = logframe_ref_for_category(cat, categories)
        etree.SubElement(rec, "field", name="finance_logframe_id", ref=lf_ref)

        # Task metadata (stored in description or custom fields if model extended)
        # For now, store RACI in description
        raci_note = f"\n\nRACI Matrix:\n- Preparation: {current_employee} ({prep_days} days)\n- Review: {reviewed_by} ({review_days} days)\n- Approval: {approved_by} ({approval_days} days)"
        if etree.SubElement(rec, "field", name="description").text:
            etree.SubElement(rec, "field", name="description").text += raci_note

    write_xml(root, DATA_DIR / "04_closing_tasks.xml")
    print(f"   📋 Generated {record_count} closing task records")


def main():
    """Main execution flow."""
    print("\n🚀 Generating Canonical Seed Data from Excel\n")
    print(f"📂 Source: {EXCEL_PATH.relative_to(BASE_DIR)}")
    print(f"📂 Output: {DATA_DIR.relative_to(BASE_DIR)}\n")

    if not EXCEL_PATH.exists():
        raise SystemExit(f"❌ Excel file not found: {EXCEL_PATH}")

    # Read Excel sheets
    print("📖 Reading Excel sheets...")
    closing_df = pd.read_excel(EXCEL_PATH, sheet_name="Closing Task")
    tax_df = pd.read_excel(EXCEL_PATH, sheet_name="Tax Filing")

    # Clean column names
    closing_df = clean_columns(closing_df)
    tax_df = clean_columns(tax_df)

    print(f"   ✓ Closing Task: {len(closing_df)} rows")
    print(f"   ✓ Tax Filing: {len(tax_df)} rows\n")

    # Generate seed data files
    print("🔨 Generating XML seed data files...\n")

    employees = generate_employees(closing_df)
    print(f"   👥 {len(employees)} employees: {', '.join(employees)}\n")

    categories = generate_logframe(closing_df)
    print(f"   📊 {len(categories)} task categories found\n")

    generate_bir_schedule(tax_df, employees)
    print()

    generate_closing_tasks(closing_df, categories)
    print()

    print("✅ Seed data generation complete!\n")
    print("📦 Next steps:")
    print("   1. Install base module: odoo -d production -i ipai_finance_ppm")
    print("   2. Install umbrella: odoo -d production -i ipai_finance_ppm_umbrella")
    print("   3. Verify seed data loaded correctly\n")


if __name__ == "__main__":
    main()
