#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

import pandas as pd

DEFAULT_XLSX = "config/finance/Month-end Closing Task and Tax Filing (7).xlsx"
MODULE_NAME = "ipai_finance_close_seed"
OUT_DIR = Path("addons/ipai") / MODULE_NAME / "data"


def norm_duration_to_hours(value: str) -> float:
    if not isinstance(value, str):
        return 0.0
    normalized = value.strip().lower().replace("days", "day")
    if "day" in normalized:
        amount = float(normalized.split("day")[0].strip())
        return amount * 8.0
    return 0.0


def slugify(text: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())
    return normalized.strip("_") or "tag"


def write_tags_xml(tags: dict[str, str], output_path: Path) -> None:
    lines = ["<?xml version=\"1.0\" encoding=\"utf-8\"?>", "<odoo>"]
    for name, tag_id in sorted(tags.items(), key=lambda item: item[0].lower()):
        lines.extend(
            [
                f"  <record id=\"{tag_id}\" model=\"project.tags\">",
                f"    <field name=\"name\">{name}</field>",
                f"    <field name=\"color\">{hash(name) % 10}</field>",
                "  </record>",
                "",
            ]
        )
    if lines[-1] == "":
        lines.pop()
    lines.append("</odoo>")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    xlsx_path = Path(DEFAULT_XLSX)
    out_dir = OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---------- Month-end close ----------
    closing = pd.read_excel(xlsx_path, sheet_name="Closing Task", usecols=list(range(8)))
    closing.columns = [
        "employee_code",
        "task_category",
        "task_detail",
        "reviewed_by",
        "approved_by",
        "prep",
        "review",
        "approval",
    ]
    closing["employee_code"] = closing["employee_code"].ffill()
    closing["task_category"] = closing["task_category"].ffill()

    tags: dict[str, str] = {}
    month_end_rows = []
    for i, row in closing.iterrows():
        name = str(row["task_detail"]).strip()
        if not name or name.lower() == "nan":
            continue
        category = str(row["task_category"]).strip()
        tag_id = tags.get(category)
        if category and tag_id is None and category.lower() != "nan":
            tag_id = f"tag_{slugify(category)}"
            tags[category] = tag_id
        planned_hours = (
            norm_duration_to_hours(str(row["prep"]))
            + norm_duration_to_hours(str(row["review"]))
            + norm_duration_to_hours(str(row["approval"]))
        )
        month_end_rows.append(
            {
                "id": f"ipai_close_{i + 1}",
                "name": name,
                "project_id:id": f"{MODULE_NAME}.project_month_end_template",
                "tag_ids/id": f"{MODULE_NAME}.{tag_id}" if tag_id else "",
                "planned_hours": planned_hours,
                "description": (
                    f"Category: {category}\n"
                    f"Reviewed by: {row['reviewed_by']}\n"
                    f"Approved by: {row['approved_by']}\n"
                    f"Employee code: {row['employee_code']}"
                ),
            }
        )

    pd.DataFrame(month_end_rows).to_csv(out_dir / "tasks_month_end.csv", index=False)

    # ---------- BIR Tax Filing ----------
    tax = pd.read_excel(xlsx_path, sheet_name="Tax Filing", usecols=list(range(6)))
    tax.columns = [
        "bir_form",
        "period_covered",
        "deadline",
        "prep_date",
        "report_approval",
        "payment_approval",
    ]

    bir_rows = []
    for i, row in tax.iterrows():
        bir_form = str(row["bir_form"]).strip()
        if not bir_form or bir_form.lower() == "nan":
            continue
        period = (
            pd.to_datetime(row["period_covered"], errors='coerce').date()
            if pd.notna(row["period_covered"])
            else None
        )
        deadline = (
            pd.to_datetime(row["deadline"], errors='coerce').date()
            if pd.notna(row["deadline"])
            else None
        )
        name = f"{bir_form} — {period.isoformat() if period else 'Period'}"
        bir_rows.append(
            {
                "id": f"ipai_bir_{i + 1}",
                "name": name,
                "project_id:id": f"{MODULE_NAME}.project_bir_tax_filing",
                "tag_ids/id": "",
                "date_deadline": deadline.isoformat() if deadline else "",
                "planned_hours": 0,
                "description": (
                    f"BIR Form: {bir_form}\n"
                    f"Period: {period}\n"
                    f"Prep & File Request: {row['prep_date']}\n"
                    f"Report Approval: {row['report_approval']}\n"
                    f"Payment Approval: {row['payment_approval']}\n"
                    f"Deadline: {deadline}\n"
                ),
            }
        )

    pd.DataFrame(bir_rows).to_csv(out_dir / "tasks_bir.csv", index=False)

    # ---------- Holidays ----------
    # CODEX: Excel sheet "Holidays & Calendar" is missing in current version.
    # Hardcoding 2026 holidays based on PR requirements and standard PH holidays.
    holidays_data = [
        {"Date": "2026-01-01", "Holiday Name": "New Year's Day"},
        {"Date": "2026-02-17", "Holiday Name": "Chinese New Year"},
        {"Date": "2026-02-25", "Holiday Name": "EDSA People Power Revolution Anniversary"},
        {"Date": "2026-04-02", "Holiday Name": "Maundy Thursday"},  # Fixed per PR
        {"Date": "2026-04-03", "Holiday Name": "Good Friday"},      # Fixed per PR
        {"Date": "2026-04-09", "Holiday Name": "Araw ng Kagitingan"},
        {"Date": "2026-05-01", "Holiday Name": "Labor Day"},
        {"Date": "2026-06-12", "Holiday Name": "Independence Day"},
        {"Date": "2026-08-21", "Holiday Name": "Ninoy Aquino Day"},
        {"Date": "2026-08-31", "Holiday Name": "National Heroes Day"},
        {"Date": "2026-11-01", "Holiday Name": "All Saints' Day"},
        {"Date": "2026-11-30", "Holiday Name": "Bonifacio Day"},
        {"Date": "2026-12-25", "Holiday Name": "Christmas Day"},
        {"Date": "2026-12-30", "Holiday Name": "Rizal Day"},
    ]
    holidays = pd.DataFrame(holidays_data)

    holiday_lines = ["<?xml version=\"1.0\" encoding=\"utf-8\"?>", "<odoo>"]
    for i, row in holidays.iterrows():
        date_value = row["Date"]
        name = str(row["Holiday Name"]).strip()

        holiday_lines.extend(
            [
                f"  <record id=\"ipai_holiday_{i + 1}\" model=\"resource.calendar.leaves\">",
                f"    <field name=\"name\">{name}</field>",
                f"    <field name=\"calendar_id\" ref=\"resource.resource_calendar_std\"/>",
                f"    <field name=\"date_from\">{date_value} 00:00:00</field>",
                f"    <field name=\"date_to\">{date_value} 23:59:59</field>",
                "  </record>",
                "",
            ]
        )
    if holiday_lines[-1] == "":
        holiday_lines.pop()
    holiday_lines.append("</odoo>")
    (out_dir / "holidays.xml").write_text("\n".join(holiday_lines), encoding="utf-8")

    write_tags_xml(tags, out_dir / "tags.xml")

    print("Wrote:", out_dir / "tasks_month_end.csv")
    print("Wrote:", out_dir / "tasks_bir.csv")
    print("Wrote:", out_dir / "holidays.xml")
    print("Wrote:", out_dir / "tags.xml")


if __name__ == "__main__":
    main()
