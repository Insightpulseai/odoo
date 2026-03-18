#!/usr/bin/env python3
"""
Validate SSOT Excel files against canonical Finance PPM seed data.

Compares Excel source files to expected canonical state:
- 8 employees (BOM, JAP, JLI, JPAL, JRMO, LAS, RIM, RMQB)
- 12 logframe entries
- 144 BIR schedule records
- 36 closing tasks

Expected sheets: "Closing Task" and "Tax Filing"
"""

import pandas as pd
import sys
from pathlib import Path

# Canonical expected counts from FINANCE_PPM_CANONICAL.md
EXPECTED_EMPLOYEES = 8
EXPECTED_LOGFRAME = 12
EXPECTED_BIR = 144
EXPECTED_TASKS = 36

# Excel file paths
SSOT_DIR_FILE = Path("/Users/tbwa/Documents/GitHub/Insightpulseai/ssot/Month-end Closing Task Tax Filing .xlsx")
CONFIG_DIR_FILE = Path("/Users/tbwa/Documents/GitHub/Insightpulseai/odoo/config/finance/Month-end Closing Task and Tax Filing (7).xlsx")

def analyze_excel_file(filepath):
    """Analyze an Excel file and return its structure and counts."""
    print(f"\n{'='*80}")
    print(f"📊 Analyzing: {filepath.name}")
    print(f"   Size: {filepath.stat().st_size / 1024:.1f} KB")
    print(f"{'='*80}\n")

    try:
        # Read Excel file to get sheet names
        xl_file = pd.ExcelFile(filepath)
        print(f"📑 Sheets found: {xl_file.sheet_names}\n")

        results = {
            'filepath': filepath,
            'sheets': xl_file.sheet_names,
            'valid': False,
            'closing_task_count': 0,
            'tax_filing_count': 0,
            'unique_employees': []
        }

        # Check for expected sheets
        has_closing = "Closing Task" in xl_file.sheet_names
        has_tax = "Tax Filing" in xl_file.sheet_names

        if not has_closing:
            print("❌ Missing 'Closing Task' sheet")
        if not has_tax:
            print("❌ Missing 'Tax Filing' sheet")

        if not (has_closing and has_tax):
            print("\n⚠️  File does not have expected sheet structure\n")
            return results

        # Read Closing Task sheet
        print("📋 Reading 'Closing Task' sheet...")
        closing_df = pd.read_excel(filepath, sheet_name="Closing Task")
        results['closing_task_count'] = len(closing_df)
        print(f"   Rows: {len(closing_df)}")
        print(f"   Columns: {list(closing_df.columns)[:5]}... ({len(closing_df.columns)} total)\n")

        # Extract unique employees from closing tasks
        employee_cols = [col for col in closing_df.columns if 'employee' in col.lower() or 'code' in col.lower()]
        if employee_cols:
            # Try common employee column names
            for col in ['employee_code', 'Employee Code', 'code', 'Code']:
                if col in closing_df.columns:
                    unique_employees = closing_df[col].dropna().unique().tolist()
                    results['unique_employees'] = sorted(unique_employees)
                    print(f"👥 Unique employees from '{col}': {results['unique_employees']}")
                    print(f"   Count: {len(results['unique_employees'])}\n")
                    break

        # Read Tax Filing sheet
        print("📋 Reading 'Tax Filing' sheet...")
        tax_df = pd.read_excel(filepath, sheet_name="Tax Filing")
        results['tax_filing_count'] = len(tax_df)
        print(f"   Rows: {len(tax_df)}")
        print(f"   Columns: {list(tax_df.columns)[:5]}... ({len(tax_df.columns)} total)\n")

        # Validation against canonical state
        print("✅ VALIDATION AGAINST CANONICAL STATE:")
        print(f"   Closing Tasks: {results['closing_task_count']} (expected: {EXPECTED_TASKS})")
        print(f"   Tax Filing Records: {results['tax_filing_count']} (expected: {EXPECTED_BIR})")
        print(f"   Unique Employees: {len(results['unique_employees'])} (expected: {EXPECTED_EMPLOYEES})")

        # Calculate validation score
        tasks_match = results['closing_task_count'] == EXPECTED_TASKS
        bir_match = results['tax_filing_count'] == EXPECTED_BIR
        employees_match = len(results['unique_employees']) == EXPECTED_EMPLOYEES

        results['valid'] = tasks_match and bir_match and employees_match

        print(f"\n   Tasks Match: {'✅' if tasks_match else '❌'}")
        print(f"   BIR Match: {'✅' if bir_match else '❌'}")
        print(f"   Employees Match: {'✅' if employees_match else '❌'}")
        print(f"\n   Overall: {'✅ VALID' if results['valid'] else '⚠️ DISCREPANCIES FOUND'}\n")

        return results

    except Exception as e:
        print(f"❌ Error reading file: {e}\n")
        return {'filepath': filepath, 'error': str(e), 'valid': False}

def main():
    """Main validation routine."""
    print("\n" + "="*80)
    print("🔍 FINANCE PPM SSOT VALIDATION")
    print("="*80)
    print(f"\nCanonical State (from FINANCE_PPM_CANONICAL.md):")
    print(f"  - Employees: {EXPECTED_EMPLOYEES}")
    print(f"  - Logframe: {EXPECTED_LOGFRAME}")
    print(f"  - BIR Schedule: {EXPECTED_BIR}")
    print(f"  - Closing Tasks: {EXPECTED_TASKS}")

    # Check if files exist
    files_to_check = []

    if SSOT_DIR_FILE.exists():
        files_to_check.append(SSOT_DIR_FILE)
    else:
        print(f"\n⚠️  File not found: {SSOT_DIR_FILE}")

    if CONFIG_DIR_FILE.exists():
        files_to_check.append(CONFIG_DIR_FILE)
    else:
        print(f"\n⚠️  File not found: {CONFIG_DIR_FILE}")

    if not files_to_check:
        print("\n❌ No Excel files found to validate!")
        sys.exit(1)

    # Analyze each file
    results = []
    for filepath in files_to_check:
        result = analyze_excel_file(filepath)
        results.append(result)

    # Final recommendation
    print("\n" + "="*80)
    print("📌 RECOMMENDATION")
    print("="*80 + "\n")

    valid_files = [r for r in results if r.get('valid', False)]

    if len(valid_files) == 1:
        ssot_file = valid_files[0]['filepath']
        print(f"✅ Single Source of Truth (SSOT): {ssot_file.name}")
        print(f"   Location: {ssot_file}")
        print(f"\n   This file matches the canonical state and should be used for seed generation.")
    elif len(valid_files) > 1:
        print(f"⚠️  Multiple files match canonical state:")
        for r in valid_files:
            print(f"   - {r['filepath'].name}")
        print(f"\n   Recommend: Use the file referenced in generate_seed_from_excel.py")
    else:
        print(f"❌ No files match canonical state!")
        print(f"\n   Both files have discrepancies with expected counts.")
        print(f"   Manual review required to determine correct SSOT.")

    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
