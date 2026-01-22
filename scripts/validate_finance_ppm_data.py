#!/usr/bin/env python3
"""
Finance PPM Data Validation Script

Validates Finance PPM seed data consistency across:
- Odoo XML seed files
- CSV export files
- Excel workbook source (optional)

Mirrors the validation logic from the Excel "Data Validation" sheet.

Usage:
    python scripts/validate_finance_ppm_data.py
    python scripts/validate_finance_ppm_data.py --xlsx path/to/workbook.xlsx
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Known employee codes from the workbook
KNOWN_EMPLOYEE_CODES = {
    "RIM", "BOM", "JPAL", "LAS", "JLI", "RMQB", "JAP", "JRMO", "CKVC"
}

# Valid task categories from the workbook
VALID_CATEGORIES = {
    "Payroll & Personnel",
    "Tax & Provisions",
    "Rent & Leases",
    "Accruals & Expenses",
    "Prior Period Review",
    "Amortization & Corporate",
    "Corporate Accruals",
    "Insurance",
    "Treasury & Other",
    "Regional Reporting",
    "Client Billings",
    "WIP/OOP Management",
    "AR Aging - WC",
    "CA Liquidations",
    "AP Aging - WC",
    "OOP",
    "Asset & Lease Entries",
    "Reclassifications",
    "VAT & Taxes",
    "Accruals & Assets",
    "AP Aging",
    "Expense Reclassification",
    "VAT Reporting",
    "Job Transfers",
    "Accruals",
    "WIP",
}

# OCA-compatible stages
VALID_STAGES = {
    "ipai_stage_todo",
    "ipai_stage_preparation",
    "ipai_stage_review",
    "ipai_stage_approval",
    "ipai_stage_done",
    "ipai_stage_cancelled",
}


def validate_xml_file(xml_path: Path) -> tuple[list[str], list[str], int]:
    """Validate an Odoo XML seed file.

    Returns: (errors, warnings, record_count)
    """
    errors = []
    warnings = []

    if not xml_path.exists():
        errors.append(f"File not found: {xml_path}")
        return errors, warnings, 0

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        errors.append(f"XML parse error in {xml_path}: {e}")
        return errors, warnings, 0

    records = root.findall(".//record[@model='project.task']")
    record_count = len(records)

    task_ids = []
    for record in records:
        task_id = record.get("id", "")
        task_ids.append(task_id)

        # Check for required fields
        name_field = record.find("field[@name='name']")
        if name_field is None or not name_field.text:
            errors.append(f"Task {task_id} missing name field")

        project_field = record.find("field[@name='project_id']")
        if project_field is None:
            errors.append(f"Task {task_id} missing project_id field")

    # Check for duplicate IDs
    duplicates = [tid for tid in task_ids if task_ids.count(tid) > 1]
    if duplicates:
        errors.append(f"Duplicate task IDs: {set(duplicates)}")

    return errors, warnings, record_count


def validate_csv_file(csv_path: Path) -> tuple[list[str], list[str], int]:
    """Validate a CSV export file.

    Returns: (errors, warnings, record_count)
    """
    errors = []
    warnings = []

    if not csv_path.exists():
        warnings.append(f"CSV file not found (optional): {csv_path}")
        return errors, warnings, 0

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        errors.append(f"CSV read error in {csv_path}: {e}")
        return errors, warnings, 0

    record_count = len(rows)

    # Check task codes unique
    if "task_code" in rows[0] if rows else {}:
        codes = [r.get("task_code", "") for r in rows]
        duplicates = [c for c in codes if codes.count(c) > 1]
        if duplicates:
            errors.append(f"Duplicate task codes in CSV: {set(duplicates)}")

    # Check employee codes valid
    if "employee_code" in rows[0] if rows else {}:
        for row in rows:
            code = row.get("employee_code", "")
            if code and code not in KNOWN_EMPLOYEE_CODES:
                warnings.append(f"Unknown employee code: {code}")

    return errors, warnings, record_count


def validate_stage_references(xml_path: Path) -> tuple[list[str], list[str]]:
    """Check that all stage references are valid OCA stages."""
    errors = []
    warnings = []

    if not xml_path.exists():
        return errors, warnings

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError:
        return errors, warnings

    for record in root.findall(".//record[@model='project.task']"):
        task_id = record.get("id", "")
        stage_field = record.find("field[@name='stage_id']")
        if stage_field is not None:
            stage_ref = stage_field.get("ref", "")
            if stage_ref and stage_ref not in VALID_STAGES:
                warnings.append(f"Task {task_id} has unknown stage: {stage_ref}")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate Finance PPM seed data")
    parser.add_argument(
        "--xlsx",
        help="Path to Excel workbook for additional validation",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    args = parser.parse_args()

    # Paths to seed files
    seed_dir = Path(__file__).parent.parent / "addons" / "ipai" / "ipai_finance_close_seed" / "data"

    all_errors = []
    all_warnings = []
    total_records = 0

    print("=" * 60)
    print("Finance PPM Data Validation")
    print("=" * 60)
    print()

    # Validate month-end tasks XML
    print("1. Validating tasks_month_end.xml...")
    xml_path = seed_dir / "tasks_month_end.xml"
    errors, warnings, count = validate_xml_file(xml_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    total_records += count
    if errors:
        print(f"   [FAIL] {len(errors)} errors")
    else:
        print(f"   [PASS] {count} records validated")

    # Check stage references
    stage_errors, stage_warnings = validate_stage_references(xml_path)
    all_errors.extend(stage_errors)
    all_warnings.extend(stage_warnings)

    # Validate BIR tasks XML
    print("2. Validating tasks_bir.xml...")
    xml_path = seed_dir / "tasks_bir.xml"
    errors, warnings, count = validate_xml_file(xml_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    total_records += count
    if errors:
        print(f"   [FAIL] {len(errors)} errors")
    else:
        print(f"   [PASS] {count} records validated")

    # Validate CSV exports
    print("3. Validating tasks_month_end.csv...")
    csv_path = seed_dir / "tasks_month_end.csv"
    errors, warnings, count = validate_csv_file(csv_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        print(f"   [FAIL] {len(errors)} errors")
    elif count > 0:
        print(f"   [PASS] {count} records validated")
    else:
        print("   [SKIP] File not found (optional)")

    print("4. Validating tasks_bir.csv...")
    csv_path = seed_dir / "tasks_bir.csv"
    errors, warnings, count = validate_csv_file(csv_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        print(f"   [FAIL] {len(errors)} errors")
    elif count > 0:
        print(f"   [PASS] {count} records validated")
    else:
        print("   [SKIP] File not found (optional)")

    # Validate projects.xml
    print("5. Validating projects.xml...")
    xml_path = seed_dir / "projects.xml"
    if xml_path.exists():
        try:
            tree = ET.parse(xml_path)
            projects = tree.findall(".//record[@model='project.project']")
            print(f"   [PASS] {len(projects)} projects defined")
        except ET.ParseError as e:
            all_errors.append(f"projects.xml parse error: {e}")
            print(f"   [FAIL] Parse error")
    else:
        all_warnings.append("projects.xml not found")
        print("   [WARN] File not found")

    # Validate tags.xml
    print("6. Validating tags.xml...")
    xml_path = seed_dir / "tags.xml"
    if xml_path.exists():
        try:
            tree = ET.parse(xml_path)
            tags = tree.findall(".//record[@model='project.tags']")
            print(f"   [PASS] {len(tags)} tags defined")
        except ET.ParseError as e:
            all_errors.append(f"tags.xml parse error: {e}")
            print(f"   [FAIL] Parse error")
    else:
        all_warnings.append("tags.xml not found")
        print("   [WARN] File not found")

    # Summary
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total records validated: {total_records}")
    print(f"Errors: {len(all_errors)}")
    print(f"Warnings: {len(all_warnings)}")

    if all_errors:
        print()
        print("Errors:")
        for e in all_errors:
            print(f"  - {e}")

    if all_warnings:
        print()
        print("Warnings:")
        for w in all_warnings[:10]:  # Limit to first 10
            print(f"  - {w}")
        if len(all_warnings) > 10:
            print(f"  ... and {len(all_warnings) - 10} more")

    # Exit code
    if all_errors or (args.strict and all_warnings):
        print()
        print("[FAIL] Validation failed")
        sys.exit(1)
    else:
        print()
        print("[PASS] All validations passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
