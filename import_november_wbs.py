#!/usr/bin/env python3
import psycopg2
import csv
import sys

def import_november_wbs():
    print("📋 Importing November 2025 Close WBS...")

    try:
        # Database connection - connect to Docker container
        conn = psycopg2.connect(
            host="db",
            database="odoo",
            user="odoo",
            password="odoo"
        )
        cursor = conn.cursor()

        print("✅ Connected to Odoo database")

        # Read CSV file
        with open('/tmp/finance_wbs_deadlines.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            tasks = list(reader)

        print(f"📊 Found {len(tasks)} tasks to import")

        # Create project
        project_name = "Finance Month-End (Nov 2025)"
        cursor.execute("""
            INSERT INTO project_project (
                name, alias_id, privacy_visibility, rating_status, rating_status_period, last_update_status,
                create_date, write_date
            )
            VALUES (%s, 1, 'followers', 'stage', 'weekly', 'none', NOW(), NOW())
            RETURNING id
        """, (f'{{"en_US": "{project_name}"}}',))
        project_id = cursor.fetchone()[0]
        print(f"✅ Created project: {project_name} (ID: {project_id})")

        # Create task mapping
        task_map = {}

        for task in tasks:
            task_id = task['ID']
            task_name = task['Task Name']
            parent_task = task['Parent Task']
            assigned_email = task['Assigned To (Email)']
            deadline = task['Deadline']
            description = task['Description / SOP']

            # Get user ID from email
            cursor.execute("SELECT id FROM res_users WHERE login = %s", (assigned_email,))
            user_result = cursor.fetchone()
            user_id = user_result[0] if user_result else None

            # Get parent task ID
            parent_id = None
            if parent_task:
                parent_id = task_map.get(parent_task)

            # Insert task
            cursor.execute("""
                INSERT INTO project_task
                (name, state, project_id, parent_id, create_uid, date_deadline, description, create_date, write_date)
                VALUES (%s, '01_in_progress', %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id
            """, (task_name, project_id, parent_id, user_id, deadline, description))

            task_id_new = cursor.fetchone()[0]
            task_map[task_name] = task_id_new

            print(f"✅ Created task: {task_name}")

        # Commit changes
        conn.commit()
        print("\n🎉 November 2025 Close WBS imported successfully!")
        print(f"📊 Summary:")
        print(f"   • Project: {project_name}")
        print(f"   • Total tasks: {len(tasks)}")
        print(f"   • Deadline range: Nov 26 - Dec 10, 2025")
        print(f"   • Team members: RIM, JPAL, BOM, LAS")

    except Exception as e:
        print(f"❌ Error during import: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import_november_wbs()
