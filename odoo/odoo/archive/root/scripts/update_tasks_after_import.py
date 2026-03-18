#!/usr/bin/env python3
"""
update_tasks_after_import.py - Bulk update tasks after CSV import

Updates tasks in Odoo after minimal CSV import:
- Creates phase/category tags if missing
- Assigns phase tags based on task name patterns ([I., [II., [III., [IV.)
- Assigns users to tasks based on email mapping CSV
- Sets stages for tasks

Usage:
    export ODOO_URL="https://erp.insightpulseai.com"
    export ODOO_DB="odoo"
    export ODOO_LOGIN="admin@example.com"
    export ODOO_PASSWORD="your_password"

    # Update phase tags only
    python3 scripts/update_tasks_after_import.py

    # With user assignments from CSV
    python3 scripts/update_tasks_after_import.py --user-mapping data/user_assignments.csv

    # Filter by project
    python3 scripts/update_tasks_after_import.py --project "Month-End Close"
"""

import argparse
import csv
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    print("Error: requests is required. Install with: pip install requests")
    sys.exit(1)


# Color codes for output
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
NC = "\033[0m"  # No Color


def log_info(message: str):
    print(f"{BLUE}[INFO]{NC} {message}")


def log_success(message: str):
    print(f"{GREEN}[SUCCESS]{NC} {message}")


def log_warning(message: str):
    print(f"{YELLOW}[WARNING]{NC} {message}")


def log_error(message: str):
    print(f"{RED}[ERROR]{NC} {message}")


def log_step(step: int, total: int, message: str):
    print(f"{CYAN}[{step}/{total}]{NC} {message}")


# Default phase tags configuration
PHASE_TAGS = {
    "Phase I: Initial & Compliance": {
        "pattern": r"^\[I\.",
        "color": 1,  # Red
        "description": "Initial compliance and setup tasks",
    },
    "Phase II: Accruals & Amortization": {
        "pattern": r"^\[II\.",
        "color": 2,  # Orange
        "description": "Accrual and amortization processing",
    },
    "Phase III: WIP": {
        "pattern": r"^\[III\.",
        "color": 3,  # Yellow
        "description": "Work in progress reconciliation",
    },
    "Phase IV: Final Adjustments": {
        "pattern": r"^\[IV\.",
        "color": 4,  # Light Blue
        "description": "Final adjustments and closing entries",
    },
}

# Category tags (created but not auto-assigned)
CATEGORY_TAGS = [
    {"name": "Payroll & Personnel", "color": 5},
    {"name": "Tax & Provisions", "color": 6},
    {"name": "VAT & Taxes", "color": 7},
    {"name": "CA Liquidations", "color": 8},
    {"name": "Accruals & Expenses", "color": 9},
    {"name": "Corporate Accruals", "color": 10},
    {"name": "Client Billings", "color": 1},
    {"name": "WIP/OOP Management", "color": 2},
    {"name": "Prior Period Review", "color": 3},
    {"name": "Reclassifications", "color": 4},
]


class OdooClient:
    """JSON-RPC client for Odoo."""

    def __init__(self, url: str, db: str, login: str, password: str, timeout: int = 60):
        self.url = url.rstrip("/")
        self.db = db
        self.login = login
        self.password = password
        self.timeout = timeout
        self.s = requests.Session()
        self.uid = self._authenticate()

    def _jsonrpc(self, endpoint: str, payload: Dict[str, Any]) -> Any:
        """Execute JSON-RPC request."""
        r = self.s.post(f"{self.url}{endpoint}", json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(f"Odoo JSON-RPC error: {data['error']}")
        return data.get("result")

    def _authenticate(self) -> int:
        """Authenticate and return user ID."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "common",
                "method": "authenticate",
                "args": [self.db, self.login, self.password, {}],
            },
            "id": 1,
        }
        uid = self._jsonrpc("/jsonrpc", payload)
        if not uid:
            raise RuntimeError(
                "Authentication failed (check ODOO_DB/ODOO_LOGIN/ODOO_PASSWORD)."
            )
        return uid

    def call_kw(self, model: str, method: str, args=None, kwargs=None) -> Any:
        """Call model method via JSON-RPC."""
        args = args or []
        kwargs = kwargs or {}
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": model,
                "method": method,
                "args": args,
                "kwargs": kwargs,
            },
            "id": 1,
        }
        return self._jsonrpc(f"/web/dataset/call_kw/{model}/{method}", payload)

    def search(self, model: str, domain: List, limit: int = None) -> List[int]:
        """Search for records."""
        kwargs = {}
        if limit:
            kwargs["limit"] = limit
        return self.call_kw(model, "search", [domain], kwargs)

    def search_read(
        self, model: str, domain: List, fields: List[str], limit: int = None
    ) -> List[Dict]:
        """Search and read records."""
        kwargs = {"fields": fields}
        if limit:
            kwargs["limit"] = limit
        return self.call_kw(model, "search_read", [domain], kwargs)

    def read(self, model: str, ids: List[int], fields: List[str]) -> List[Dict]:
        """Read records by IDs."""
        return self.call_kw(model, "read", [ids, fields], {})

    def create(self, model: str, vals: Dict) -> int:
        """Create a record."""
        return self.call_kw(model, "create", [vals], {})

    def write(self, model: str, ids: List[int], vals: Dict) -> bool:
        """Update records."""
        return self.call_kw(model, "write", [ids, vals], {})


def ensure_tags_exist(odoo: OdooClient, dry_run: bool = False) -> Dict[str, int]:
    """
    Ensure all phase and category tags exist.

    Returns:
        Dict mapping tag name to tag ID
    """
    tag_ids = {}

    # Phase tags
    for tag_name, config in PHASE_TAGS.items():
        existing = odoo.search("project.tags", [["name", "=", tag_name]], limit=1)
        if existing:
            tag_ids[tag_name] = existing[0]
            log_info(f"Tag exists: {tag_name} (ID: {existing[0]})")
        else:
            if dry_run:
                log_info(f"Would create tag: {tag_name}")
                tag_ids[tag_name] = -1
            else:
                tid = odoo.create(
                    "project.tags", {"name": tag_name, "color": config["color"]}
                )
                tag_ids[tag_name] = tid
                log_success(f"Created tag: {tag_name} (ID: {tid})")

    # Category tags
    for tag_config in CATEGORY_TAGS:
        tag_name = tag_config["name"]
        existing = odoo.search("project.tags", [["name", "=", tag_name]], limit=1)
        if existing:
            tag_ids[tag_name] = existing[0]
            log_info(f"Tag exists: {tag_name} (ID: {existing[0]})")
        else:
            if dry_run:
                log_info(f"Would create tag: {tag_name}")
                tag_ids[tag_name] = -1
            else:
                tid = odoo.create(
                    "project.tags", {"name": tag_name, "color": tag_config["color"]}
                )
                tag_ids[tag_name] = tid
                log_success(f"Created tag: {tag_name} (ID: {tid})")

    return tag_ids


def get_phase_tag_for_task(task_name: str) -> Optional[str]:
    """
    Determine which phase tag applies to a task based on name pattern.

    Args:
        task_name: The task name

    Returns:
        Phase tag name or None
    """
    for tag_name, config in PHASE_TAGS.items():
        if re.match(config["pattern"], task_name):
            return tag_name
    return None


def assign_phase_tags(
    odoo: OdooClient,
    tag_ids: Dict[str, int],
    project_filter: Optional[str] = None,
    dry_run: bool = False,
) -> Tuple[int, int]:
    """
    Assign phase tags to tasks based on name patterns.

    Args:
        odoo: Odoo client
        tag_ids: Mapping of tag names to IDs
        project_filter: Optional project name to filter tasks
        dry_run: If True, don't make changes

    Returns:
        Tuple of (updated_count, skipped_count)
    """
    # Build domain
    domain = []
    if project_filter:
        project_ids = odoo.search(
            "project.project", [["name", "=", project_filter]], limit=1
        )
        if not project_ids:
            log_error(f"Project not found: {project_filter}")
            return 0, 0
        domain.append(["project_id", "=", project_ids[0]])

    # Fetch all tasks
    tasks = odoo.search_read("project.task", domain, ["id", "name", "tag_ids"])
    log_info(f"Found {len(tasks)} tasks to process")

    updated = 0
    skipped = 0

    for task in tasks:
        task_id = task["id"]
        task_name = task["name"]
        current_tags = task.get("tag_ids", [])

        # Determine phase tag
        phase_tag_name = get_phase_tag_for_task(task_name)
        if not phase_tag_name:
            skipped += 1
            continue

        phase_tag_id = tag_ids.get(phase_tag_name)
        if not phase_tag_id or phase_tag_id < 0:
            skipped += 1
            continue

        # Check if tag already assigned
        if phase_tag_id in current_tags:
            log_info(f"Tag already assigned: {task_name}")
            skipped += 1
            continue

        # Add tag
        new_tags = current_tags + [phase_tag_id]
        if dry_run:
            log_info(f"Would assign '{phase_tag_name}' to: {task_name}")
        else:
            odoo.write("project.task", [task_id], {"tag_ids": [(6, 0, new_tags)]})
            log_success(f"Assigned '{phase_tag_name}' to: {task_name}")

        updated += 1

    return updated, skipped


def load_user_mapping(csv_path: str) -> Dict[str, List[str]]:
    """
    Load user assignment mapping from CSV.

    Expected CSV format:
        Task Name,Assignee Emails
        "[I.1] Prepare payroll file","user1@example.com,user2@example.com"

    Args:
        csv_path: Path to CSV file

    Returns:
        Dict mapping task name to list of email addresses
    """
    mapping = {}
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                task_name = row.get("Task Name", "").strip()
                emails = row.get("Assignee Emails", "").strip()
                if task_name and emails:
                    mapping[task_name] = [
                        e.strip() for e in emails.split(",") if e.strip()
                    ]
        log_success(f"Loaded {len(mapping)} user mappings from CSV")
    except FileNotFoundError:
        log_error(f"User mapping file not found: {csv_path}")
    except Exception as e:
        log_error(f"Error reading user mapping: {e}")

    return mapping


def resolve_user_ids(odoo: OdooClient, emails: List[str]) -> List[int]:
    """
    Resolve email addresses to user IDs.

    Args:
        odoo: Odoo client
        emails: List of email addresses

    Returns:
        List of user IDs
    """
    user_ids = []
    for email in emails:
        # Try login first, then email field
        ids = odoo.search("res.users", [["login", "=", email]], limit=1)
        if not ids:
            ids = odoo.search("res.users", [["email", "=", email]], limit=1)
        if ids:
            user_ids.append(ids[0])
        else:
            log_warning(f"User not found: {email}")
    return user_ids


def assign_users_from_mapping(
    odoo: OdooClient,
    user_mapping: Dict[str, List[str]],
    project_filter: Optional[str] = None,
    dry_run: bool = False,
) -> Tuple[int, int]:
    """
    Assign users to tasks based on mapping.

    Args:
        odoo: Odoo client
        user_mapping: Dict mapping task name to emails
        project_filter: Optional project name to filter
        dry_run: If True, don't make changes

    Returns:
        Tuple of (updated_count, skipped_count)
    """
    # Build domain
    domain = []
    if project_filter:
        project_ids = odoo.search(
            "project.project", [["name", "=", project_filter]], limit=1
        )
        if not project_ids:
            log_error(f"Project not found: {project_filter}")
            return 0, 0
        domain.append(["project_id", "=", project_ids[0]])

    # Fetch tasks
    tasks = odoo.search_read("project.task", domain, ["id", "name", "user_ids"])

    updated = 0
    skipped = 0

    for task in tasks:
        task_id = task["id"]
        task_name = task["name"]

        if task_name not in user_mapping:
            skipped += 1
            continue

        emails = user_mapping[task_name]
        user_ids = resolve_user_ids(odoo, emails)

        if not user_ids:
            log_warning(f"No valid users for: {task_name}")
            skipped += 1
            continue

        if dry_run:
            log_info(f"Would assign {emails} to: {task_name}")
        else:
            odoo.write("project.task", [task_id], {"user_ids": [(6, 0, user_ids)]})
            log_success(f"Assigned {len(user_ids)} user(s) to: {task_name}")

        updated += 1

    return updated, skipped


def set_task_stages(
    odoo: OdooClient,
    stage_name: str,
    project_filter: Optional[str] = None,
    dry_run: bool = False,
) -> Tuple[int, int]:
    """
    Set all matching tasks to a specific stage.

    Args:
        odoo: Odoo client
        stage_name: Target stage name
        project_filter: Optional project to filter
        dry_run: If True, don't make changes

    Returns:
        Tuple of (updated_count, skipped_count)
    """
    # Find stage
    stage_ids = odoo.search("project.task.type", [["name", "=", stage_name]], limit=1)
    if not stage_ids:
        log_error(f"Stage not found: {stage_name}")
        return 0, 0

    stage_id = stage_ids[0]

    # Build domain
    domain = [["stage_id", "!=", stage_id]]
    if project_filter:
        project_ids = odoo.search(
            "project.project", [["name", "=", project_filter]], limit=1
        )
        if not project_ids:
            log_error(f"Project not found: {project_filter}")
            return 0, 0
        domain.append(["project_id", "=", project_ids[0]])

    # Fetch tasks not in target stage
    tasks = odoo.search_read("project.task", domain, ["id", "name"])

    if not tasks:
        log_info("All tasks already in target stage")
        return 0, 0

    if dry_run:
        log_info(f"Would update {len(tasks)} tasks to stage: {stage_name}")
        return len(tasks), 0

    # Bulk update
    task_ids = [t["id"] for t in tasks]
    odoo.write("project.task", task_ids, {"stage_id": stage_id})
    log_success(f"Updated {len(task_ids)} tasks to stage: {stage_name}")

    return len(task_ids), 0


def print_summary(odoo: OdooClient, project_filter: Optional[str] = None):
    """Print summary of tasks and tags."""
    print(f"\n{CYAN}=== SUMMARY ==={NC}")

    # List projects and task counts
    domain = []
    if project_filter:
        domain.append(["name", "=", project_filter])

    projects = odoo.search_read("project.project", domain, ["id", "name"])

    for project in projects:
        task_count = len(
            odoo.search("project.task", [["project_id", "=", project["id"]]])
        )
        print(f"Project: {project['name']} - {task_count} tasks")

        # Count by phase tag
        for tag_name in PHASE_TAGS.keys():
            tag_ids = odoo.search("project.tags", [["name", "=", tag_name]], limit=1)
            if tag_ids:
                count = len(
                    odoo.search(
                        "project.task",
                        [
                            ["project_id", "=", project["id"]],
                            ["tag_ids", "in", tag_ids],
                        ],
                    )
                )
                if count > 0:
                    print(f"  - {tag_name}: {count} tasks")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Update Odoo tasks after CSV import")
    parser.add_argument(
        "--url",
        default=os.getenv("ODOO_URL", "https://erp.insightpulseai.com"),
        help="Odoo URL",
    )
    parser.add_argument(
        "--db", default=os.getenv("ODOO_DB", "odoo"), help="Odoo database name"
    )
    parser.add_argument(
        "--login",
        default=os.getenv("ODOO_LOGIN", ""),
        help="Odoo login (or ODOO_LOGIN env var)",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("ODOO_PASSWORD", ""),
        help="Odoo password (or ODOO_PASSWORD env var)",
    )
    parser.add_argument(
        "--project", help="Filter by project name (e.g., 'Month-End Close')"
    )
    parser.add_argument("--user-mapping", help="Path to CSV file with user assignments")
    parser.add_argument(
        "--set-stage", help="Set all tasks to this stage (e.g., 'Preparation')"
    )
    parser.add_argument(
        "--skip-tags", action="store_true", help="Skip tag creation and assignment"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    if not args.login or not args.password:
        log_error(
            "Missing ODOO_LOGIN or ODOO_PASSWORD (use env vars or --login/--password)"
        )
        sys.exit(1)

    log_info("=" * 80)
    log_info("Odoo Task Update - Post Import")
    log_info(f"URL: {args.url}")
    log_info(f"Database: {args.db}")
    log_info(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE UPDATE'}")
    if args.project:
        log_info(f"Project filter: {args.project}")
    log_info("=" * 80)
    print()

    # Connect to Odoo
    log_step(1, 4, "Connecting to Odoo...")
    try:
        odoo = OdooClient(args.url, args.db, args.login, args.password)
        log_success(f"Connected as user ID: {odoo.uid}")
    except Exception as e:
        log_error(f"Failed to connect: {e}")
        sys.exit(1)
    print()

    # Step 2: Ensure tags exist
    if not args.skip_tags:
        log_step(2, 4, "Ensuring tags exist...")
        tag_ids = ensure_tags_exist(odoo, args.dry_run)
        print()

        # Step 3: Assign phase tags
        log_step(3, 4, "Assigning phase tags to tasks...")
        updated, skipped = assign_phase_tags(odoo, tag_ids, args.project, args.dry_run)
        log_info(f"Phase tags: {updated} updated, {skipped} skipped")
        print()
    else:
        log_step(2, 4, "Skipping tag operations")
        log_step(3, 4, "Skipping phase tag assignment")
        tag_ids = {}
        print()

    # Step 4: Additional operations
    log_step(4, 4, "Additional operations...")

    # Assign users from mapping
    if args.user_mapping:
        log_info("Loading user mapping...")
        user_mapping = load_user_mapping(args.user_mapping)
        if user_mapping:
            updated, skipped = assign_users_from_mapping(
                odoo, user_mapping, args.project, args.dry_run
            )
            log_info(f"User assignments: {updated} updated, {skipped} skipped")

    # Set stage
    if args.set_stage:
        log_info(f"Setting tasks to stage: {args.set_stage}")
        updated, skipped = set_task_stages(
            odoo, args.set_stage, args.project, args.dry_run
        )
        log_info(f"Stage updates: {updated} updated, {skipped} skipped")

    print()

    # Print summary
    print_summary(odoo, args.project)

    print()
    if args.dry_run:
        log_warning("DRY RUN: No changes were made")
    else:
        log_success("Update completed successfully")


if __name__ == "__main__":
    main()
