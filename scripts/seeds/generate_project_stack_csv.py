#!/usr/bin/env python3
"""
Generate Odoo-importable CSV files from Project Stack seed YAML files.

Usage:
    python scripts/seeds/generate_project_stack_csv.py [--output-dir OUTPUT_DIR]

This script reads the YAML seed files from seeds/workstreams/project_stack/
and generates CSV files that can be directly imported into Odoo.

Import order in Odoo:
    1. partners_customers.csv      (res.partner)
    2. analytic_accounts.csv       (account.analytic.account)
    3. products_services.csv       (product.product)
    4. projects.csv                (project.project)
    5. task_tags.csv               (project.tags)
    6. task_stages.csv             (project.task.type)
    7. tasks.csv                   (project.task)
    8. timesheets.csv              (account.analytic.line)
"""

import argparse
import csv
import os
import sys
from pathlib import Path

import yaml


def load_yaml(filepath: Path) -> dict:
    """Load a YAML file and return its contents."""
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_partners_csv(data: dict, output_path: Path) -> None:
    """Generate res.partner CSV from partners YAML."""
    partners = data.get("partners", [])

    fieldnames = [
        "External ID",
        "Name",
        "Company Type",
        "Is a Company",
        "Parent Company",
        "Email",
        "Phone",
        "Street",
        "City",
        "Zip",
        "Country",
        "Is a Customer",
        "Is a Vendor",
        "Internal Reference",
        "Job Position",
        "Notes",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for p in partners:
            row = {
                "External ID": p["id"],
                "Name": p["name"],
                "Company Type": p.get("company_type", "company"),
                "Is a Company": "TRUE" if p.get("is_company", True) else "FALSE",
                "Parent Company": p.get("parent_id", ""),
                "Email": p.get("email", ""),
                "Phone": p.get("phone", ""),
                "Street": p.get("street", ""),
                "City": p.get("city", ""),
                "Zip": p.get("zip", ""),
                "Country": p.get("country", ""),
                "Is a Customer": p.get("customer_rank", 0),
                "Is a Vendor": p.get("supplier_rank", 0),
                "Internal Reference": p.get("ref", ""),
                "Job Position": p.get("function", ""),
                "Notes": p.get("comment", ""),
            }
            writer.writerow(row)

    print(f"  Generated: {output_path.name} ({len(partners)} records)")


def generate_analytic_accounts_csv(data: dict, output_path: Path) -> None:
    """Generate account.analytic.account CSV from analytic YAML."""
    accounts = data.get("analytic_accounts", [])

    fieldnames = ["External ID", "Name", "Code", "Partner", "Active"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for a in accounts:
            row = {
                "External ID": a["id"],
                "Name": a["name"],
                "Code": a.get("code", ""),
                "Partner": a.get("partner_id", ""),
                "Active": "TRUE" if a.get("active", True) else "FALSE",
            }
            writer.writerow(row)

    print(f"  Generated: {output_path.name} ({len(accounts)} records)")


def generate_products_csv(data: dict, output_path: Path) -> None:
    """Generate product.product CSV from products YAML."""
    products = data.get("products", [])

    fieldnames = [
        "External ID",
        "Name",
        "Internal Reference",
        "Product Type",
        "Sales Price",
        "Cost",
        "Unit of Measure",
        "Invoicing Policy",
        "Track Service",
        "Active",
        "Can be Sold",
        "Sales Description",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for p in products:
            row = {
                "External ID": p["id"],
                "Name": p["name"],
                "Internal Reference": p.get("default_code", ""),
                "Product Type": p.get("type", "service"),
                "Sales Price": p.get("list_price", 0),
                "Cost": p.get("standard_price", 0),
                "Unit of Measure": p.get("uom_id", "Unit"),
                "Invoicing Policy": p.get("invoice_policy", "delivery"),
                "Track Service": p.get("service_type", "manual"),
                "Active": "TRUE" if p.get("active", True) else "FALSE",
                "Can be Sold": "TRUE" if p.get("sale_ok", True) else "FALSE",
                "Sales Description": p.get("description_sale", ""),
            }
            writer.writerow(row)

    print(f"  Generated: {output_path.name} ({len(products)} records)")


def generate_projects_csv(data: dict, output_path: Path) -> None:
    """Generate project.project CSV from projects YAML."""
    projects = data.get("projects", [])

    fieldnames = [
        "External ID",
        "Name",
        "Customer",
        "Analytic Account",
        "Allow Timesheets",
        "Billable",
        "Timesheet Product",
        "Privacy",
        "Active",
        "Description",
        "Start Date",
        "End Date",
        "Color",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for p in projects:
            row = {
                "External ID": p["id"],
                "Name": p["name"],
                "Customer": p.get("partner_id", ""),
                "Analytic Account": p.get("analytic_account_id", ""),
                "Allow Timesheets": (
                    "TRUE" if p.get("allow_timesheets", True) else "FALSE"
                ),
                "Billable": "TRUE" if p.get("allow_billable", False) else "FALSE",
                "Timesheet Product": p.get("timesheet_product_id", ""),
                "Privacy": p.get("privacy_visibility", "followers"),
                "Active": "TRUE" if p.get("active", True) else "FALSE",
                "Description": (p.get("description", "") or "")
                .replace("\n", " ")
                .strip(),
                "Start Date": p.get("date_start", ""),
                "End Date": p.get("date", ""),
                "Color": p.get("color", 0),
            }
            writer.writerow(row)

    print(f"  Generated: {output_path.name} ({len(projects)} records)")


def generate_tags_csv(data: dict, output_path: Path) -> None:
    """Generate project.tags CSV from tags YAML."""
    tags = data.get("tags", [])

    fieldnames = ["External ID", "Name", "Color"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for t in tags:
            row = {
                "External ID": t["id"],
                "Name": t["name"],
                "Color": t.get("color", 0),
            }
            writer.writerow(row)

    print(f"  Generated: {output_path.name} ({len(tags)} records)")


def generate_stages_csv(data: dict, output_path: Path) -> None:
    """Generate project.task.type CSV from stages YAML."""
    stages = data.get("stages", [])

    fieldnames = ["External ID", "Name", "Sequence", "Folded", "Description"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for s in stages:
            row = {
                "External ID": s["id"],
                "Name": s["name"],
                "Sequence": s.get("sequence", 10),
                "Folded": "TRUE" if s.get("fold", False) else "FALSE",
                "Description": s.get("description", ""),
            }
            writer.writerow(row)

    print(f"  Generated: {output_path.name} ({len(stages)} records)")


def generate_tasks_csv(data: dict, output_path: Path) -> None:
    """Generate project.task CSV from tasks YAML."""
    tasks = data.get("tasks", [])

    fieldnames = [
        "External ID",
        "Name",
        "Project",
        "Customer",
        "Stage",
        "Tags",
        "Parent Task",
        "Depends on",
        "Description",
        "Planned Hours",
        "Deadline",
        "Start Date",
        "Priority",
        "Sequence",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for t in tasks:
            # Convert tag list to comma-separated string
            tags = t.get("tag_ids", [])
            tags_str = ",".join(tags) if isinstance(tags, list) else tags

            # Convert depends_on list to comma-separated string
            deps = t.get("depends_on", [])
            deps_str = ",".join(deps) if isinstance(deps, list) else deps

            row = {
                "External ID": t["id"],
                "Name": t["name"],
                "Project": t.get("project_id", ""),
                "Customer": t.get("partner_id", ""),
                "Stage": t.get("stage_id", ""),
                "Tags": tags_str,
                "Parent Task": t.get("parent_id", ""),
                "Depends on": deps_str,
                "Description": (t.get("description", "") or "")
                .replace("\n", " ")
                .strip(),
                "Planned Hours": t.get("planned_hours", ""),
                "Deadline": t.get("date_deadline", ""),
                "Start Date": t.get("date_start", ""),
                "Priority": t.get("priority", "0"),
                "Sequence": t.get("sequence", 10),
            }
            writer.writerow(row)

    print(f"  Generated: {output_path.name} ({len(tasks)} records)")


def generate_timesheets_csv(data: dict, output_path: Path) -> None:
    """Generate account.analytic.line CSV from timesheets YAML."""
    timesheets = data.get("timesheets", [])

    fieldnames = [
        "External ID",
        "Date",
        "Employee",
        "Project",
        "Task",
        "Description",
        "Hours",
        "Analytic Account",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for ts in timesheets:
            row = {
                "External ID": ts["id"],
                "Date": ts["date"],
                "Employee": ts.get("employee_id", ""),
                "Project": ts.get("project_id", ""),
                "Task": ts.get("task_id", ""),
                "Description": ts["name"],
                "Hours": ts["unit_amount"],
                "Analytic Account": ts.get("account_id", ""),
            }
            writer.writerow(row)

    print(f"  Generated: {output_path.name} ({len(timesheets)} records)")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Odoo-importable CSV files from Project Stack seed YAML"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="seeds/workstreams/project_stack/csv",
        help="Output directory for CSV files (default: seeds/workstreams/project_stack/csv)",
    )
    args = parser.parse_args()

    # Get project root
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent.parent

    # Seed directory
    seed_dir = project_root / "seeds" / "workstreams" / "project_stack"
    if not seed_dir.exists():
        print(f"Error: Seed directory not found: {seed_dir}")
        sys.exit(1)

    # Output directory
    output_dir = project_root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Project Stack CSV Generator")
    print(f"=" * 50)
    print(f"Seed directory: {seed_dir}")
    print(f"Output directory: {output_dir}")
    print()

    # Process each YAML file
    generators = [
        ("10_partners.yaml", "partners_customers.csv", generate_partners_csv),
        (
            "20_analytic_accounts.yaml",
            "analytic_accounts.csv",
            generate_analytic_accounts_csv,
        ),
        ("30_products.yaml", "products_services.csv", generate_products_csv),
        ("40_projects.yaml", "projects.csv", generate_projects_csv),
        ("50_tags.yaml", "task_tags.csv", generate_tags_csv),
        ("60_stages.yaml", "task_stages.csv", generate_stages_csv),
        ("70_tasks.yaml", "tasks.csv", generate_tasks_csv),
        ("80_timesheets.yaml", "timesheets.csv", generate_timesheets_csv),
    ]

    print("Generating CSV files:")
    for yaml_file, csv_file, generator_func in generators:
        yaml_path = seed_dir / yaml_file
        csv_path = output_dir / csv_file

        if yaml_path.exists():
            data = load_yaml(yaml_path)
            generator_func(data, csv_path)
        else:
            print(f"  Skipped: {yaml_file} (not found)")

    print()
    print("Import order in Odoo:")
    print("-" * 50)
    print("1. partners_customers.csv      (res.partner)")
    print("2. analytic_accounts.csv       (account.analytic.account)")
    print("3. products_services.csv       (product.product)")
    print("4. projects.csv                (project.project)")
    print("5. task_tags.csv               (project.tags)")
    print("6. task_stages.csv             (project.task.type)")
    print("7. tasks.csv                   (project.task)")
    print("8. timesheets.csv              (account.analytic.line)")
    print()
    print(f"CSV files ready in: {output_dir}")


if __name__ == "__main__":
    main()
