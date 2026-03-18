#!/usr/bin/env python3
"""
Seed Odoo projects (Month-End Closing, BIR Tax Filing) from Excel workbook.
Reads from sheets: "Closing Task", "Tax Filing"
Creates projects, stages, tasks with idempotent upsert logic.

Usage:
  export ODOO_URL=https://erp.insightpulseai.com
  export ODOO_DB=odoo
  export ODOO_USER=admin@Insightpulseai
  export ODOO_PASS=your_password
  ./scripts/seed_projects_from_xlsx.py --xlsx "data/month_end_and_bir.xlsx"
"""

import os
import sys
import argparse
import xmlrpc.client
from datetime import datetime
from typing import Optional

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas not installed. Run: pip install pandas openpyxl", file=sys.stderr)
    sys.exit(1)


class OdooSeeder:
    def __init__(self, url: str, db: str, user: str, password: str):
        self.url = url
        self.db = db
        self.user = user
        self.password = password

        # Authenticate
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        self.uid = common.authenticate(db, user, password, {})
        if not self.uid:
            raise RuntimeError("Authentication failed")

        self.models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
        print(f"✅ Authenticated as {user} (uid={self.uid})")

    def execute_kw(self, model: str, method: str, args: list, kwargs: dict = None):
        """Execute XML-RPC call"""
        kwargs = kwargs or {}
        return self.models.execute_kw(
            self.db, self.uid, self.password, model, method, args, kwargs
        )

    def search(self, model: str, domain: list, limit: Optional[int] = None):
        """Search records"""
        kwargs = {}
        if limit is not None:
            kwargs["limit"] = limit
        return self.execute_kw(model, "search", [domain], kwargs)

    def search_read(self, model: str, domain: list, fields: list, limit: Optional[int] = None):
        """Search and read records"""
        kwargs = {"fields": fields}
        if limit is not None:
            kwargs["limit"] = limit
        return self.execute_kw(model, "search_read", [domain], kwargs)

    def read(self, model: str, ids: list, fields: list):
        """Read records"""
        return self.execute_kw(model, "read", [ids], {"fields": fields})

    def create(self, model: str, vals: dict):
        """Create record"""
        return self.execute_kw(model, "create", [vals])

    def write(self, model: str, ids: list, vals: dict):
        """Update records"""
        return self.execute_kw(model, "write", [ids, vals])

    def ensure_tag(self, name: str) -> int:
        """Ensure tag exists, return ID"""
        domain = [["name", "=", name]]
        ids = self.search("project.tags", domain, limit=1)
        if ids:
            return ids[0]
        return self.create("project.tags", {"name": name})

    def ensure_project(self, name: str) -> int:
        """Ensure project exists, return ID"""
        domain = [["name", "=", name]]
        ids = self.search("project.project", domain, limit=1)
        if ids:
            print(f"  Project '{name}' already exists (id={ids[0]})")
            return ids[0]
        pid = self.create("project.project", {"name": name})
        print(f"  ✅ Created project '{name}' (id={pid})")
        return pid

    def ensure_stage(self, project_id: int, name: str, sequence: int, fold: bool = False) -> int:
        """Ensure stage exists and is linked to project"""
        # Check if stage exists for this project
        domain = [["name", "=", name], ["project_ids", "in", [project_id]]]
        ids = self.search("project.task.type", domain, limit=1)

        if ids:
            sid = ids[0]
            # Update sequence/fold if needed
            self.write("project.task.type", [sid], {"sequence": sequence, "fold": fold})
            return sid

        # Check if stage exists globally
        domain_global = [["name", "=", name]]
        global_ids = self.search("project.task.type", domain_global, limit=1)

        if global_ids:
            sid = global_ids[0]
            # Link to project
            self.write("project.task.type", [sid], {
                "project_ids": [(4, project_id)],
                "sequence": sequence,
                "fold": fold
            })
            print(f"    Linked stage '{name}' to project (id={sid})")
            return sid

        # Create new stage
        sid = self.create("project.task.type", {
            "name": name,
            "sequence": sequence,
            "fold": fold,
            "project_ids": [(4, project_id)]
        })
        print(f"    ✅ Created stage '{name}' (id={sid})")
        return sid

    def upsert_task(
        self,
        project_id: int,
        stage_id: int,
        name: str,
        description: str,
        deadline_iso: Optional[str],
        tag_ids: list[int]
    ) -> tuple[int, str]:
        """Create or update task"""
        domain = [["project_id", "=", project_id], ["name", "=", name]]
        recs = self.search_read("project.task", domain, ["id", "name"], limit=1)

        vals = {
            "project_id": project_id,
            "stage_id": stage_id,
            "name": name,
            "description": description or "",
            "tag_ids": [(6, 0, tag_ids)]
        }
        if deadline_iso:
            vals["date_deadline"] = deadline_iso

        if recs:
            tid = recs[0]["id"]
            self.write("project.task", [tid], vals)
            return tid, "updated"

        tid = self.create("project.task", vals)
        return tid, "created"

    def seed_month_end(self, xlsx_path: str):
        """Seed Month-End Closing project from Excel 'Closing Task' sheet"""
        print("\n📋 Seeding Month-End Closing Project...")

        # Read Excel
        df = pd.read_excel(xlsx_path, sheet_name="Closing Task")

        # Create project
        project_id = self.ensure_project("Month-End Closing")

        # Create stages
        stages = [
            ("Preparation", 10, False),
            ("Review", 20, False),
            ("Approval", 30, False),
            ("Done", 40, True)
        ]
        stage_map = {}
        for stage_name, seq, fold in stages:
            sid = self.ensure_stage(project_id, stage_name, seq, fold)
            stage_map[stage_name] = sid

        # Create tag
        tag_id = self.ensure_tag("MONTH_END_CLOSING")

        # Create tasks
        created = updated = 0
        for idx, row in df.iterrows():
            task_name = row.get("Task Name") or row.get("task_name")
            task_desc = row.get("Description") or row.get("description") or ""
            stage_name = row.get("Stage") or row.get("stage") or "Preparation"
            deadline = row.get("Deadline") or row.get("deadline")

            if pd.isna(task_name):
                continue

            # Convert deadline to ISO format
            deadline_iso = None
            if deadline and not pd.isna(deadline):
                if isinstance(deadline, datetime):
                    deadline_iso = deadline.strftime("%Y-%m-%d")
                else:
                    try:
                        deadline_iso = pd.to_datetime(deadline).strftime("%Y-%m-%d")
                    except:
                        pass

            stage_id = stage_map.get(stage_name, stage_map["Preparation"])

            tid, action = self.upsert_task(
                project_id=project_id,
                stage_id=stage_id,
                name=task_name,
                description=task_desc,
                deadline_iso=deadline_iso,
                tag_ids=[tag_id]
            )

            if action == "created":
                created += 1
            else:
                updated += 1

        print(f"  ✅ Month-End: {created} tasks created, {updated} tasks updated")
        return project_id

    def seed_bir(self, xlsx_path: str):
        """Seed BIR Tax Filing project from Excel 'Tax Filing' sheet"""
        print("\n📋 Seeding BIR Tax Filing Project...")

        # Read Excel
        df = pd.read_excel(xlsx_path, sheet_name="Tax Filing")

        # Create project
        project_id = self.ensure_project("BIR Tax Filing")

        # Create stages
        stages = [
            ("Preparation", 10, False),
            ("Report Approval", 20, False),
            ("Payment Approval", 30, False),
            ("Filing & Payment", 40, False),
            ("Done", 50, True)
        ]
        stage_map = {}
        for stage_name, seq, fold in stages:
            sid = self.ensure_stage(project_id, stage_name, seq, fold)
            stage_map[stage_name] = sid

        # Create tag
        tag_id = self.ensure_tag("BIR_TAX_FILING")

        # Create tasks
        created = updated = 0
        for idx, row in df.iterrows():
            task_name = row.get("Task Name") or row.get("task_name")
            task_desc = row.get("Description") or row.get("description") or ""
            stage_name = row.get("Stage") or row.get("stage") or "Preparation"
            deadline = row.get("Deadline") or row.get("deadline")

            if pd.isna(task_name):
                continue

            # Convert deadline to ISO format
            deadline_iso = None
            if deadline and not pd.isna(deadline):
                if isinstance(deadline, datetime):
                    deadline_iso = deadline.strftime("%Y-%m-%d")
                else:
                    try:
                        deadline_iso = pd.to_datetime(deadline).strftime("%Y-%m-%d")
                    except:
                        pass

            stage_id = stage_map.get(stage_name, stage_map["Preparation"])

            tid, action = self.upsert_task(
                project_id=project_id,
                stage_id=stage_id,
                name=task_name,
                description=task_desc,
                deadline_iso=deadline_iso,
                tag_ids=[tag_id]
            )

            if action == "created":
                created += 1
            else:
                updated += 1

        print(f"  ✅ BIR Tax Filing: {created} tasks created, {updated} tasks updated")
        return project_id


def main():
    parser = argparse.ArgumentParser(description="Seed Odoo projects from Excel")
    parser.add_argument("--xlsx", required=True, help="Path to Excel workbook")
    args = parser.parse_args()

    # Get environment variables
    ODOO_URL = os.environ.get("ODOO_URL")
    ODOO_DB = os.environ.get("ODOO_DB")
    ODOO_USER = os.environ.get("ODOO_USER")
    ODOO_PASS = os.environ.get("ODOO_PASS")

    if not all([ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASS]):
        print("ERROR: Missing environment variables", file=sys.stderr)
        print("Required: ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASS", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.xlsx):
        print(f"ERROR: Excel file not found: {args.xlsx}", file=sys.stderr)
        sys.exit(1)

    print(f"📁 Reading Excel: {args.xlsx}")

    try:
        seeder = OdooSeeder(ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASS)
        seeder.seed_month_end(args.xlsx)
        seeder.seed_bir(args.xlsx)
        print("\n✅ Seeding completed successfully")
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
