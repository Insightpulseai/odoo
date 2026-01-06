#!/usr/bin/env python3
"""
Update imported tasks with full data (assignees, tags, stages, etc.)
Run AFTER importing the minimal CSVs.

Usage: python3 update_tasks_after_import.py --url http://localhost:8069 --db odoo --user admin --password admin
"""

import xmlrpc.client
import argparse

# =============================================================================
# TASK ASSIGNMENTS (from your spreadsheet)
# =============================================================================
CLOSING_TASK_ASSIGNMENTS = {
    '[I.1]': {'user': 'RIM - Rey Meran', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase I: Initial & Compliance', 'Payroll & Personnel']},
    '[I.2]': {'user': 'RIM - Rey Meran', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase I: Initial & Compliance', 'Tax & Provisions']},
    '[I.3]': {'user': 'RIM - Rey Meran', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase I: Initial & Compliance', 'Rent & Leases']},
    '[I.4]': {'user': 'RIM - Rey Meran', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase I: Initial & Compliance', 'Accruals & Expenses']},
    '[I.5]': {'user': 'RIM - Rey Meran', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase I: Initial & Compliance', 'Accruals & Expenses']},
    '[I.6]': {'user': 'RIM - Rey Meran', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase I: Initial & Compliance', 'Prior Period Review']},
    '[II.1]': {'user': 'Beng Manalo', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase II: Accruals & Amortization', 'Amortization & Corporate']},
    '[II.2]': {'user': 'Beng Manalo', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase II: Accruals & Amortization', 'Corporate Accruals']},
    '[II.3]': {'user': 'Beng Manalo', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase II: Accruals & Amortization', 'Insurance']},
    '[II.4]': {'user': 'Beng Manalo', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase II: Accruals & Amortization', 'Treasury & Other']},
    '[II.5]': {'user': 'Beng Manalo', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase II: Accruals & Amortization', 'Prior Period Review']},
    '[II.6]': {'user': 'Beng Manalo', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase II: Accruals & Amortization', 'Regional Reporting']},
    '[III.1]': {'user': 'Jinky Paladin', 'reviewer': 'Beng Manalo', 'tags': ['Phase III: WIP', 'Client Billings']},
    '[III.2]': {'user': 'Jinky Paladin', 'reviewer': 'Beng Manalo', 'tags': ['Phase III: WIP', 'WIP/OOP Management']},
    '[III.3]': {'user': 'Jinky Paladin', 'reviewer': 'Beng Manalo', 'tags': ['Phase III: WIP', 'Amortization & Corporate']},
    '[III.4]': {'user': 'Jinky Paladin', 'reviewer': 'Beng Manalo', 'tags': ['Phase III: WIP', 'Amortization & Corporate']},
    '[III.5]': {'user': 'Jinky Paladin', 'reviewer': 'Beng Manalo', 'tags': ['Phase III: WIP', 'Amortization & Corporate']},
    '[III.6]': {'user': 'Jinky Paladin', 'reviewer': 'Beng Manalo', 'tags': ['Phase III: WIP', 'Amortization & Corporate']},
    '[III.7]': {'user': 'Jinky Paladin', 'reviewer': 'Beng Manalo', 'tags': ['Phase III: WIP', 'AR Aging - WC']},
    '[III.8]': {'user': 'Amor Lasaga', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase III: WIP', 'CA Liquidations']},
    '[III.9]': {'user': 'Amor Lasaga', 'reviewer': 'Beng Manalo', 'tags': ['Phase III: WIP', 'AP Aging - WC']},
    '[III.10]': {'user': 'Amor Lasaga', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase III: WIP', 'OOP']},
    '[III.11]': {'user': 'Amor Lasaga', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase III: WIP', 'Asset & Lease Entries']},
    '[III.12]': {'user': 'Amor Lasaga', 'reviewer': 'Beng Manalo', 'tags': ['Phase III: WIP', 'Reclassifications']},
    '[IV.1]': {'user': 'Jasmin Ignacio', 'reviewer': 'Jinky Paladin', 'tags': ['Phase IV: Final Adjustments', 'VAT & Taxes']},
    '[IV.2]': {'user': 'Jasmin Ignacio', 'reviewer': 'Amor Lasaga', 'tags': ['Phase IV: Final Adjustments', 'Accruals & Assets']},
    '[IV.3]': {'user': 'Jasmin Ignacio', 'reviewer': 'Amor Lasaga', 'tags': ['Phase IV: Final Adjustments', 'Accruals & Assets']},
    '[IV.4]': {'user': 'Jasmin Ignacio', 'reviewer': 'Amor Lasaga', 'tags': ['Phase IV: Final Adjustments', 'AP Aging']},
    '[IV.5]': {'user': 'Jhoee Oliva', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase IV: Final Adjustments', 'CA Liquidations']},
    '[IV.6]': {'user': 'Jhoee Oliva', 'reviewer': 'Amor Lasaga', 'tags': ['Phase IV: Final Adjustments', 'Accruals & Assets']},
    '[IV.7]': {'user': 'Jhoee Oliva', 'reviewer': 'RIM - Rey Meran', 'tags': ['Phase IV: Final Adjustments', 'Expense Reclassification']},
    '[IV.8]': {'user': 'Jasmin Ignacio', 'reviewer': 'Jinky Paladin', 'tags': ['Phase IV: Final Adjustments', 'VAT Reporting']},
    '[IV.9]': {'user': 'Jasmin Ignacio', 'reviewer': 'Jinky Paladin', 'tags': ['Phase IV: Final Adjustments', 'Job Transfers']},
    '[IV.10]': {'user': 'Jasmin Ignacio', 'reviewer': 'Jinky Paladin', 'tags': ['Phase IV: Final Adjustments', 'Job Transfers']},
    '[IV.11]': {'user': 'Joana Maravillas', 'reviewer': 'Jinky Paladin', 'tags': ['Phase IV: Final Adjustments', 'Accruals']},
    '[IV.12]': {'user': 'Joana Maravillas', 'reviewer': 'Jinky Paladin', 'tags': ['Phase IV: Final Adjustments', 'WIP']},
}

TAX_TASK_ASSIGNMENTS = {
    # All tax tasks: Preparer=BOM, Reviewer=RIM
    'default': {'user': 'Beng Manalo', 'reviewer': 'RIM - Rey Meran'}
}


def connect(url, db, username, password):
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise Exception("Authentication failed")
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    return uid, models, db, password


def get_user_id(models, db, uid, password, name):
    users = models.execute_kw(db, uid, password, 'res.users', 'search_read',
                              [[('name', 'ilike', name)]], {'fields': ['id', 'name'], 'limit': 1})
    return users[0]['id'] if users else None


def get_tag_id(models, db, uid, password, name):
    tags = models.execute_kw(db, uid, password, 'project.tags', 'search_read',
                             [[('name', '=', name)]], {'fields': ['id'], 'limit': 1})
    return tags[0]['id'] if tags else None


def get_stage_id(models, db, uid, password, name):
    stages = models.execute_kw(db, uid, password, 'project.task.type', 'search_read',
                               [[('name', '=', name)]], {'fields': ['id'], 'limit': 1})
    return stages[0]['id'] if stages else None


def main():
    parser = argparse.ArgumentParser(description='Update tasks after import')
    parser.add_argument('--url', default='http://localhost:8069')
    parser.add_argument('--db', default='odoo')
    parser.add_argument('--user', default='admin')
    parser.add_argument('--password', default='admin')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    args = parser.parse_args()

    print(f"Connecting to {args.url}...")
    uid, models, db, password = connect(args.url, args.db, args.user, args.password)
    print(f"Connected as UID {uid}")

    if args.dry_run:
        print("\n*** DRY RUN MODE - No changes will be made ***\n")

    # Cache user IDs
    print("\n=== Caching User IDs ===")
    user_cache = {}
    for name in ['RIM - Rey Meran', 'Beng Manalo', 'Jinky Paladin', 'Amor Lasaga',
                 'Jerald Loterte', 'Jhoee Oliva', 'Jasmin Ignacio', 'Joana Maravillas']:
        user_id = get_user_id(models, db, uid, password, name)
        if user_id:
            user_cache[name] = user_id
            print(f"  {name}: {user_id}")
        else:
            print(f"  {name}: NOT FOUND")

    # Cache tag IDs (create if missing)
    print("\n=== Creating/Caching Tags ===")
    tag_cache = {}
    all_tags = set()
    for data in CLOSING_TASK_ASSIGNMENTS.values():
        all_tags.update(data['tags'])

    for tag_name in sorted(all_tags):
        tag_id = get_tag_id(models, db, uid, password, tag_name)
        if not tag_id:
            if args.dry_run:
                print(f"  Would create tag '{tag_name}'")
                tag_cache[tag_name] = -1  # Placeholder
            else:
                # Create tag
                tag_id = models.execute_kw(db, uid, password, 'project.tags', 'create',
                                           [{'name': tag_name, 'color': 1}])
                print(f"  Created tag '{tag_name}': {tag_id}")
                tag_cache[tag_name] = tag_id
        else:
            print(f"  Tag '{tag_name}' exists: {tag_id}")
            tag_cache[tag_name] = tag_id

    # Get stage ID for 'Backlog' or 'To Do'
    backlog_stage_id = get_stage_id(models, db, uid, password, 'Backlog')
    if not backlog_stage_id:
        backlog_stage_id = get_stage_id(models, db, uid, password, 'To Do')
    print(f"\n  Default stage ID: {backlog_stage_id}")

    # Update closing tasks
    print("\n=== Updating Closing Tasks ===")
    closing_tasks = models.execute_kw(db, uid, password, 'project.task', 'search_read',
                                      [[('project_id.name', 'ilike', 'Month-End Close')]],
                                      {'fields': ['id', 'name']})

    updated = 0
    for task in closing_tasks:
        # Find matching assignment by task code prefix
        task_code = None
        for code in CLOSING_TASK_ASSIGNMENTS.keys():
            if code in task['name']:
                task_code = code
                break

        if task_code:
            assignment = CLOSING_TASK_ASSIGNMENTS[task_code]
            update_vals = {}

            # Set assignee
            if assignment['user'] in user_cache:
                update_vals['user_ids'] = [(6, 0, [user_cache[assignment['user']]])]

            # Set tags
            tag_ids = [tag_cache[t] for t in assignment['tags'] if t in tag_cache and tag_cache[t] > 0]
            if tag_ids:
                update_vals['tag_ids'] = [(6, 0, tag_ids)]

            if update_vals:
                if args.dry_run:
                    print(f"  Would update: {task['name'][:60]}...")
                else:
                    models.execute_kw(db, uid, password, 'project.task', 'write',
                                      [[task['id']], update_vals])
                    print(f"  Updated: {task['name'][:60]}...")
                updated += 1

    print(f"\n  {'Would update' if args.dry_run else 'Updated'} {updated} closing tasks")

    # Update tax tasks
    print("\n=== Updating Tax Tasks ===")
    tax_tasks = models.execute_kw(db, uid, password, 'project.task', 'search_read',
                                  [[('project_id.name', 'ilike', 'BIR Tax Filing')]],
                                  {'fields': ['id', 'name']})

    default_user_id = user_cache.get('Beng Manalo')
    updated = 0
    for task in tax_tasks:
        if default_user_id:
            if args.dry_run:
                print(f"  Would assign: {task['name'][:60]}...")
            else:
                models.execute_kw(db, uid, password, 'project.task', 'write',
                                  [[task['id']], {'user_ids': [(6, 0, [default_user_id])]}])
            updated += 1

    print(f"  {'Would update' if args.dry_run else 'Updated'} {updated} tax tasks (assigned to Beng Manalo)")

    print("\n" + "=" * 60)
    print("UPDATE COMPLETE" if not args.dry_run else "DRY RUN COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
