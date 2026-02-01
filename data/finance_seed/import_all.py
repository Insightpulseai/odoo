#!/usr/bin/env python3
"""
Complete Finance Seed Data Import via XML-RPC
Imports tags, projects, and tasks directly to Odoo without Docker.
"""

import csv
import sys
import xmlrpc.client
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================
ODOO_URL = "https://erp.insightpulseai.com"
DB_NAME = "odoo_core"

# Get credentials from command line or prompt
def get_credentials():
    if len(sys.argv) >= 3:
        return sys.argv[1], sys.argv[2]
    print("Usage: python3 import_all.py <username> <password>")
    print("Or set ODOO_USER and ODOO_PASSWORD environment variables")
    import os
    user = os.environ.get('ODOO_USER', 'admin')
    password = os.environ.get('ODOO_PASSWORD')
    if not password:
        import getpass
        password = getpass.getpass(f"Password for {user}@{ODOO_URL}: ")
    return user, password


def connect(url, db, username, password):
    """Connect to Odoo via XML-RPC"""
    print(f"Connecting to {url}...")
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)

    try:
        version = common.version()
        print(f"  Server version: {version.get('server_version', 'unknown')}")
    except Exception as e:
        print(f"  Warning: Could not get version: {e}")

    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise Exception(f"Authentication failed for {username}")

    print(f"  Authenticated as UID {uid}")
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
    return uid, models


def read_csv(filepath):
    """Read CSV file and return list of dicts"""
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def import_records(models, db, uid, password, model_name, records, id_field='id'):
    """Import records using Odoo's load() method"""
    if not records:
        print(f"  No records to import for {model_name}")
        return []

    fields = list(records[0].keys())
    data = [[row.get(f, '') for f in fields] for row in records]

    result = models.execute_kw(db, uid, password, model_name, 'load', [fields, data])

    ids = result.get('ids', [])
    messages = result.get('messages', [])

    if messages:
        for msg in messages[:5]:  # Show first 5 messages
            print(f"    {msg.get('type', 'info')}: {msg.get('message', '')[:100]}")
        if len(messages) > 5:
            print(f"    ... and {len(messages) - 5} more messages")

    return ids


def get_existing_records(models, db, uid, password, model_name, domain=None):
    """Get existing records"""
    domain = domain or []
    return models.execute_kw(db, uid, password, model_name, 'search_read',
                             [domain], {'fields': ['id', 'name']})


def main():
    script_dir = Path(__file__).parent

    username, password = get_credentials()

    try:
        uid, models = connect(ODOO_URL, DB_NAME, username, password)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("FINANCE SEED DATA IMPORT")
    print("=" * 60)

    # =========================================================================
    # STEP 1: Import Tags
    # =========================================================================
    print("\n[1/4] Importing Tags...")
    tags_file = script_dir / "01_project.tags.csv"
    if tags_file.exists():
        tags = read_csv(tags_file)
        ids = import_records(models, DB_NAME, uid, password, 'project.tags', tags)
        print(f"  Imported {len(ids)} tags")
    else:
        print(f"  SKIP: {tags_file} not found")

    # =========================================================================
    # STEP 2: Import Projects
    # =========================================================================
    print("\n[2/4] Importing Projects...")
    projects_file = script_dir / "02_project.project.csv"
    if projects_file.exists():
        projects = read_csv(projects_file)
        ids = import_records(models, DB_NAME, uid, password, 'project.project', projects)
        print(f"  Imported {len(ids)} projects")
    else:
        print(f"  SKIP: {projects_file} not found")

    # =========================================================================
    # STEP 3: Import Month-End Close Tasks
    # =========================================================================
    print("\n[3/4] Importing Month-End Close Tasks...")
    me_tasks_file = script_dir / "03_project.task.month_end.csv"
    if me_tasks_file.exists():
        tasks = read_csv(me_tasks_file)
        ids = import_records(models, DB_NAME, uid, password, 'project.task', tasks)
        print(f"  Imported {len(ids)} month-end tasks")
    else:
        print(f"  SKIP: {me_tasks_file} not found")

    # =========================================================================
    # STEP 4: Import BIR Tax Filing Tasks
    # =========================================================================
    print("\n[4/4] Importing BIR Tax Filing Tasks...")
    bir_tasks_file = script_dir / "04_project.task.bir_tax.csv"
    if bir_tasks_file.exists():
        tasks = read_csv(bir_tasks_file)
        ids = import_records(models, DB_NAME, uid, password, 'project.task', tasks)
        print(f"  Imported {len(ids)} BIR tax tasks")
    else:
        print(f"  SKIP: {bir_tasks_file} not found")

    # =========================================================================
    # VERIFICATION
    # =========================================================================
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)

    # Count tags
    tag_count = models.execute_kw(DB_NAME, uid, password, 'project.tags', 'search_count', [[]])
    print(f"\n  Total tags in system: {tag_count}")

    # List projects
    projects = get_existing_records(models, DB_NAME, uid, password, 'project.project',
                                    [('name', 'in', ['Month-End Close', 'BIR Tax Filing'])])
    print(f"\n  Finance Projects:")
    for p in projects:
        # Get task count for project
        task_count = models.execute_kw(DB_NAME, uid, password, 'project.task', 'search_count',
                                       [[('project_id', '=', p['id'])]])
        print(f"    - {p['name']}: {task_count} tasks")

    print("\n" + "=" * 60)
    print("IMPORT COMPLETE")
    print("=" * 60)
    print(f"\nView your projects at: {ODOO_URL}/odoo/projects")
    print("\nNext: Run update_tasks_after_import.py to assign users")


if __name__ == '__main__':
    main()
