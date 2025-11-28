#!/usr/bin/env python3
"""
Task Deduplication Script for Monthly Closing Tasks
Purpose: Import CSV tasks into Odoo with intelligent deduplication
Author: Claude Code with SuperClaude Framework
Date: 2025-11-21
"""

import csv
import hashlib
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor


class TaskDeduplicator:
    """Deduplicate and import monthly closing tasks into Odoo."""

    def __init__(self, db_config: Dict[str, str]):
        """Initialize with database configuration."""
        self.conn = psycopg2.connect(**db_config)
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

        # Deduplication strategy: hash on name + cluster + owner
        self.fingerprint_fields = ['name', 'cluster', 'owner_code']

    def calculate_fingerprint(self, task: Dict) -> str:
        """Calculate unique fingerprint for task deduplication."""
        fingerprint_data = '|'.join([
            str(task.get(field, '')).strip().lower()
            for field in self.fingerprint_fields
        ])
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]

    def load_csv_tasks(self, csv_path: str) -> List[Dict]:
        """Load tasks from CSV file."""
        tasks = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                task = {
                    'name': row['Name'].strip(),
                    'owner_code': row['Owner Code'].strip(),
                    'owner_name': row['Owner Name'].strip(),
                    'owner_email': row['Owner Email'].strip(),
                    'cluster': row['Cluster'].strip(),
                    'cluster_label': row['Cluster Label'].strip(),
                    'relative_due': row['Relative Due'].strip(),
                    'due_date': row['Due Date'].strip() if row['Due Date'] else None,
                    'month_end': row['Month End'].strip() if row['Month End'] else None,
                    'status': row['Status'].strip(),
                    'notes': row.get('Notes', '').strip(),
                    'reviewer_code': row.get('Reviewer Code', '').strip(),
                    'reviewer_name': row.get('Reviewer Name', '').strip(),
                    'reviewer_email': row.get('Reviewer Email', '').strip(),
                    'approver_code': row.get('Approver Code', '').strip(),
                    'approver_name': row.get('Approver Name', '').strip(),
                    'approver_email': row.get('Approver Email', '').strip(),
                }
                task['fingerprint'] = self.calculate_fingerprint(task)
                tasks.append(task)

        print(f"✅ Loaded {len(tasks)} tasks from CSV")
        return tasks

    def get_existing_tasks(self, project_id: int) -> Dict[str, Dict]:
        """Get existing tasks from Odoo project.task table."""
        self.cursor.execute("""
            SELECT
                id,
                name,
                cluster,
                date_deadline,
                stage_id,
                reviewer_id,
                approver_id,
                description
            FROM project_task
            WHERE project_id = %s
            AND active = true
        """, (project_id,))

        existing_tasks = {}
        for row in self.cursor.fetchall():
            # Extract owner code from description or use name matching
            owner_code = self._extract_owner_code(row)

            fingerprint_data = '|'.join([
                str(row['name']).strip().lower(),
                str(row['cluster'] or '').strip().lower(),
                str(owner_code).strip().lower()
            ])
            fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]

            existing_tasks[fingerprint] = dict(row)

        print(f"✅ Found {len(existing_tasks)} existing tasks in Odoo")
        return existing_tasks

    def _extract_owner_code(self, task_row: Dict) -> str:
        """Extract owner code from task description or name."""
        description = task_row.get('description') or ''
        # Look for pattern: Owner: CODE
        if 'Owner:' in description:
            parts = description.split('Owner:')
            if len(parts) > 1:
                return parts[1].split()[0].strip()
        return ''

    def get_or_create_user(self, owner_code: str, owner_name: str, owner_email: str) -> Optional[int]:
        """Get or create Odoo user by owner code."""
        # First try to find by email (login)
        if owner_email:
            self.cursor.execute("""
                SELECT id FROM res_users WHERE login = %s LIMIT 1
            """, (owner_email,))
            result = self.cursor.fetchone()
            if result:
                return result['id']

        # Try by partner name
        if owner_name:
            self.cursor.execute("""
                SELECT u.id
                FROM res_users u
                JOIN res_partner p ON u.partner_id = p.id
                WHERE p.name ILIKE %s
                LIMIT 1
            """, (f"%{owner_name}%",))
            result = self.cursor.fetchone()
            if result:
                return result['id']

        # Default to admin user (id=2 typically)
        print(f"⚠️  User not found: {owner_code} ({owner_name}), skipping user assignment")
        return None

    def get_stage_id(self, status: str) -> int:
        """Map CSV status to Odoo stage_id."""
        status_mapping = {
            'Not started': 1,  # Default stage
            'In Progress': 2,
            'Blocked': 3,
            'Ready to Post': 4,
            'Done': 5,
            'Posted': 5
        }

        # Query actual stages (name is JSONB, extract en_US)
        self.cursor.execute("""
            SELECT id, name->>'en_US' as name_en
            FROM project_task_type
            ORDER BY sequence LIMIT 10
        """)

        stages = {row['name_en']: row['id'] for row in self.cursor.fetchall()}

        # Try exact match
        if status in stages:
            return stages[status]

        # Try mapping
        if status in status_mapping:
            return status_mapping[status]

        # Default to first stage
        return 1

    def deduplicate_tasks(
        self,
        csv_tasks: List[Dict],
        existing_tasks: Dict[str, Dict]
    ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Deduplicate tasks: separate into new, updated, and unchanged."""
        new_tasks = []
        updated_tasks = []
        unchanged_tasks = []

        for task in csv_tasks:
            fingerprint = task['fingerprint']

            if fingerprint in existing_tasks:
                existing = existing_tasks[fingerprint]

                # Check if task needs update (status or due date changed)
                needs_update = (
                    str(task['due_date']) != str(existing.get('date_deadline')) or
                    task['status'] != self._get_status_name(existing.get('stage_id'))
                )

                if needs_update:
                    task['odoo_id'] = existing['id']
                    updated_tasks.append(task)
                else:
                    unchanged_tasks.append(task)
            else:
                new_tasks.append(task)

        print(f"\n📊 Deduplication Results:")
        print(f"  - New tasks: {len(new_tasks)}")
        print(f"  - Tasks to update: {len(updated_tasks)}")
        print(f"  - Unchanged tasks: {len(unchanged_tasks)}")

        return new_tasks, updated_tasks, unchanged_tasks

    def _get_status_name(self, stage_id: int) -> str:
        """Get stage name by ID."""
        if not stage_id:
            return 'Not started'

        self.cursor.execute("""
            SELECT name->>'en_US' as name_en FROM project_task_type WHERE id = %s
        """, (stage_id,))

        result = self.cursor.fetchone()
        return result['name_en'] if result else 'Not started'

    def import_tasks(
        self,
        new_tasks: List[Dict],
        updated_tasks: List[Dict],
        project_id: int,
        dry_run: bool = False
    ) -> Dict:
        """Import new tasks and update existing ones."""
        results = {
            'created': 0,
            'updated': 0,
            'errors': []
        }

        # Insert new tasks
        for task in new_tasks:
            try:
                # Get stage ID first
                stage_id = self.get_stage_id(task['status'])

                # Build description
                description = self._build_description(task)

                # Try to resolve user IDs (may return None)
                reviewer_id = None
                if task.get('reviewer_code'):
                    reviewer_id = self.get_or_create_user(
                        task['reviewer_code'],
                        task['reviewer_name'],
                        task['reviewer_email']
                    )

                approver_id = None
                if task.get('approver_code'):
                    approver_id = self.get_or_create_user(
                        task['approver_code'],
                        task['approver_name'],
                        task['approver_email']
                    )

                if not dry_run:
                    self.cursor.execute("""
                        INSERT INTO project_task (
                            name,
                            project_id,
                            reviewer_id,
                            approver_id,
                            date_deadline,
                            cluster,
                            relative_due,
                            stage_id,
                            description,
                            create_date,
                            write_date,
                            active,
                            state
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), true, '01_in_progress'
                        )
                    """, (
                        task['name'],
                        project_id,
                        reviewer_id,
                        approver_id,
                        task['due_date'],
                        task['cluster'],
                        task['relative_due'],
                        stage_id,
                        description
                    ))

                results['created'] += 1
                print(f"  ✅ Created: {task['name'][:50]}...")

            except Exception as e:
                import traceback
                error_msg = f"Failed to create task: {task['name'][:50]} - {str(e)}"
                results['errors'].append(error_msg)
                print(f"  ❌ {error_msg}")
                traceback.print_exc()

        # Update existing tasks
        for task in updated_tasks:
            try:
                stage_id = self.get_stage_id(task['status'])

                if not dry_run:
                    self.cursor.execute("""
                        UPDATE project_task
                        SET
                            date_deadline = %s,
                            stage_id = %s,
                            write_date = NOW()
                        WHERE id = %s
                    """, (
                        task['due_date'],
                        stage_id,
                        task['odoo_id']
                    ))

                results['updated'] += 1
                print(f"  ✅ Updated: {task['name'][:50]}...")

            except Exception as e:
                error_msg = f"Failed to update task: {task['name'][:50]} - {str(e)}"
                results['errors'].append(error_msg)
                print(f"  ❌ {error_msg}")

        if not dry_run:
            self.conn.commit()
            print(f"\n✅ Database changes committed")
        else:
            print(f"\n🔍 DRY RUN - No changes committed")

        return results

    def _build_description(self, task: Dict) -> str:
        """Build task description with all metadata."""
        description_parts = [
            f"**Owner:** {task['owner_code']} - {task['owner_name']}",
            f"**Cluster:** {task['cluster']} - {task['cluster_label']}",
            f"**Relative Due:** {task['relative_due']}",
            f"**Month End:** {task['month_end']}",
        ]

        if task['reviewer_code']:
            description_parts.append(
                f"**Reviewer:** {task['reviewer_code']} - {task['reviewer_name']}"
            )

        if task['approver_code']:
            description_parts.append(
                f"**Approver:** {task['approver_code']} - {task['approver_name']}"
            )

        if task['notes']:
            description_parts.append(f"\n**Notes:** {task['notes']}")

        return '\n'.join(description_parts)

    def close(self):
        """Close database connection."""
        self.cursor.close()
        self.conn.close()


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Deduplicate and import monthly closing tasks'
    )
    parser.add_argument(
        'csv_path',
        help='Path to CSV file with tasks'
    )
    parser.add_argument(
        '--project-id',
        type=int,
        required=True,
        help='Odoo project ID for monthly closing'
    )
    parser.add_argument(
        '--db-host',
        default='db',
        help='Database host (default: db)'
    )
    parser.add_argument(
        '--db-port',
        type=int,
        default=5432,
        help='Database port (default: 5432)'
    )
    parser.add_argument(
        '--db-name',
        default='odoo',
        help='Database name (default: odoo)'
    )
    parser.add_argument(
        '--db-user',
        default='odoo',
        help='Database user (default: odoo)'
    )
    parser.add_argument(
        '--db-password',
        default='odoo',
        help='Database password (default: odoo)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform dry run without committing changes'
    )

    args = parser.parse_args()

    # Database configuration
    db_config = {
        'host': args.db_host,
        'port': args.db_port,
        'dbname': args.db_name,
        'user': args.db_user,
        'password': args.db_password
    }

    print("=" * 60)
    print("Monthly Closing Task Deduplication & Import")
    print("=" * 60)
    print(f"CSV File: {args.csv_path}")
    print(f"Project ID: {args.project_id}")
    print(f"Dry Run: {args.dry_run}")
    print("=" * 60)

    try:
        # Initialize deduplicator
        deduplicator = TaskDeduplicator(db_config)

        # Load CSV tasks
        csv_tasks = deduplicator.load_csv_tasks(args.csv_path)

        # Get existing tasks from Odoo
        existing_tasks = deduplicator.get_existing_tasks(args.project_id)

        # Deduplicate
        new_tasks, updated_tasks, unchanged_tasks = deduplicator.deduplicate_tasks(
            csv_tasks,
            existing_tasks
        )

        # Import tasks
        results = deduplicator.import_tasks(
            new_tasks,
            updated_tasks,
            args.project_id,
            dry_run=args.dry_run
        )

        # Summary
        print("\n" + "=" * 60)
        print("IMPORT SUMMARY")
        print("=" * 60)
        print(f"✅ Created: {results['created']} tasks")
        print(f"✅ Updated: {results['updated']} tasks")
        print(f"ℹ️  Unchanged: {len(unchanged_tasks)} tasks")
        print(f"❌ Errors: {len(results['errors'])}")

        if results['errors']:
            print("\nErrors:")
            for error in results['errors']:
                print(f"  - {error}")

        # Close connection
        deduplicator.close()

        print("\n✅ Import completed successfully")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
