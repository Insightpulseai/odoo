#!/usr/bin/env python3
"""
Odoo Project + Email Alias + Portal Access Automation

Creates a project with email-to-task routing and portal user access.
No UI configuration required - fully automated via XML-RPC.

Usage:
    python create_project_alias.py --project "SAMPLE" --alias "sample" --company "TBWA\\SMP"

Environment Variables:
    ODOO_URL       - Odoo instance URL (default: https://erp.insightpulseai.net/odoo)
    ODOO_DB        - Database name (default: odoo)
    ODOO_USER      - Admin email
    ODOO_PASSWORD  - Admin password
    ALIAS_DOMAIN   - Email domain (default: insightpulseai.net)

Example:
    export ODOO_URL="https://erp.insightpulseai.net/odoo"
    export ODOO_DB="odoo"
    export ODOO_USER="admin@insightpulseai.net"
    export ODOO_PASSWORD="your-password"
    python create_project_alias.py --project "SAMPLE" --alias "sample"
"""

import argparse
import os
import sys
import xmlrpc.client
from typing import Optional


def get_env(key: str, default: Optional[str] = None) -> str:
    """Get environment variable or default."""
    value = os.environ.get(key, default)
    if value is None:
        raise ValueError(f"Missing required environment variable: {key}")
    return value


def create_project_with_alias(
    project_name: str,
    alias_name: str,
    company_name: str = "TBWA\\SMP",
    visibility: str = "portal",
    portal_emails: Optional[list] = None,
) -> dict:
    """
    Create an Odoo project with email alias for task creation.

    Args:
        project_name: Name of the project
        alias_name: Email alias prefix (e.g., "sample" for sample@domain.com)
        company_name: Company to assign project to
        visibility: Privacy visibility ("portal", "internal", "public")
        portal_emails: List of portal user emails to grant access

    Returns:
        dict with project_id, alias_id, and status
    """
    # Configuration from environment
    url = get_env("ODOO_URL", "https://erp.insightpulseai.net/odoo")
    db = get_env("ODOO_DB", "odoo")
    user = get_env("ODOO_USER")
    password = get_env("ODOO_PASSWORD")
    domain_name = get_env("ALIAS_DOMAIN", "insightpulseai.net")

    print(f"Connecting to {url}...")

    # Authenticate
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, user, password, {})

    if not uid:
        raise RuntimeError("Authentication failed. Check credentials.")

    print(f"Authenticated as UID: {uid}")

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    # Step 1: Ensure alias domain exists
    print(f"Checking alias domain: {domain_name}...")
    dom_ids = models.execute_kw(
        db, uid, password, "mail.alias.domain", "search", [[["name", "=", domain_name]]]
    )

    if dom_ids:
        alias_domain_id = dom_ids[0]
        print(f"  Using existing domain ID: {alias_domain_id}")
    else:
        alias_domain_id = models.execute_kw(
            db,
            uid,
            password,
            "mail.alias.domain",
            "create",
            [{"name": domain_name, "catchall_domain": True}],
        )
        print(f"  Created new domain ID: {alias_domain_id}")

    # Step 2: Find company
    print(f"Finding company: {company_name}...")
    company_ids = models.execute_kw(
        db, uid, password, "res.company", "search", [[["name", "=", company_name]]]
    )

    if not company_ids:
        raise RuntimeError(f"Company not found: {company_name}")

    company_id = company_ids[0]
    print(f"  Found company ID: {company_id}")

    # Step 3: Check if project already exists
    print(f"Checking for existing project: {project_name}...")
    existing_projects = models.execute_kw(
        db,
        uid,
        password,
        "project.project",
        "search",
        [[["name", "=", project_name], ["company_id", "=", company_id]]],
    )

    if existing_projects:
        project_id = existing_projects[0]
        print(f"  Project already exists, ID: {project_id}")
    else:
        # Create project
        print(f"Creating project: {project_name}...")
        project_id = models.execute_kw(
            db,
            uid,
            password,
            "project.project",
            "create",
            [
                {
                    "name": project_name,
                    "company_id": company_id,
                    "privacy_visibility": visibility,
                    "allow_task_dependencies": True,
                }
            ],
        )
        print(f"  Created project ID: {project_id}")

    # Step 4: Get model IDs for alias
    task_model_id = models.execute_kw(
        db, uid, password, "ir.model", "search", [[["model", "=", "project.task"]]]
    )[0]

    project_model_id = models.execute_kw(
        db, uid, password, "ir.model", "search", [[["model", "=", "project.project"]]]
    )[0]

    # Step 5: Check if alias already exists
    print(f"Setting up email alias: {alias_name}@{domain_name}...")
    existing_aliases = models.execute_kw(
        db,
        uid,
        password,
        "mail.alias",
        "search",
        [[["alias_name", "=", alias_name], ["alias_domain_id", "=", alias_domain_id]]],
    )

    if existing_aliases:
        alias_id = existing_aliases[0]
        # Update existing alias to point to this project
        models.execute_kw(
            db,
            uid,
            password,
            "mail.alias",
            "write",
            [
                [alias_id],
                {
                    "alias_model_id": task_model_id,
                    "alias_force_thread_id": project_id,
                    "alias_parent_model_id": project_model_id,
                    "alias_parent_thread_id": project_id,
                },
            ],
        )
        print(f"  Updated existing alias ID: {alias_id}")
    else:
        # Create new alias
        alias_id = models.execute_kw(
            db,
            uid,
            password,
            "mail.alias",
            "create",
            [
                {
                    "alias_name": alias_name,
                    "alias_domain_id": alias_domain_id,
                    "alias_model_id": task_model_id,
                    "alias_force_thread_id": project_id,
                    "alias_parent_model_id": project_model_id,
                    "alias_parent_thread_id": project_id,
                }
            ],
        )
        print(f"  Created alias ID: {alias_id}")

    # Step 6: Grant portal access to specified users
    if portal_emails:
        print(f"Granting portal access to: {portal_emails}...")
        partner_ids = models.execute_kw(
            db,
            uid,
            password,
            "res.partner",
            "search",
            [[["email", "in", portal_emails]]],
        )

        if partner_ids:
            # Add portal access via message_partner_ids (followers)
            models.execute_kw(
                db,
                uid,
                password,
                "project.project",
                "write",
                [
                    [project_id],
                    {"message_partner_ids": [(4, pid) for pid in partner_ids]},
                ],
            )
            print(f"  Granted access to {len(partner_ids)} partners")
        else:
            print("  No matching partners found for portal access")

    # Summary
    email_address = f"{alias_name}@{domain_name}"
    print("\n" + "=" * 60)
    print("SUCCESS: Project + Email Alias Created")
    print("=" * 60)
    print(f"  Project ID:    {project_id}")
    print(f"  Project Name:  {project_name}")
    print(f"  Company:       {company_name}")
    print(f"  Visibility:    {visibility}")
    print(f"  Email Alias:   {email_address}")
    print(f"  Alias ID:      {alias_id}")
    print("=" * 60)
    print("\nNext Steps:")
    print(f"  1. Configure Mailgun route to forward {email_address}")
    print(f'     Expression: match_recipient("{email_address}")')
    print(f"     Action:     forward(\"{url.replace('/odoo', '')}/mailgate/mailgun\")")
    print("  2. Test by sending an email to the alias")
    print("=" * 60)

    return {
        "project_id": project_id,
        "project_name": project_name,
        "alias_id": alias_id,
        "email_address": email_address,
        "company_id": company_id,
        "visibility": visibility,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Create Odoo project with email-to-task alias",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--project", "-p", required=True, help="Project name")
    parser.add_argument(
        "--alias",
        "-a",
        required=True,
        help="Email alias prefix (e.g., 'sample' for sample@domain.com)",
    )
    parser.add_argument(
        "--company", "-c", default="TBWA\\SMP", help="Company name (default: TBWA\\SMP)"
    )
    parser.add_argument(
        "--visibility",
        "-v",
        choices=["portal", "internal", "public"],
        default="portal",
        help="Privacy visibility (default: portal)",
    )
    parser.add_argument(
        "--portal-users", nargs="*", help="Portal user emails to grant access"
    )

    args = parser.parse_args()

    try:
        result = create_project_with_alias(
            project_name=args.project,
            alias_name=args.alias,
            company_name=args.company,
            visibility=args.visibility,
            portal_emails=args.portal_users,
        )
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
