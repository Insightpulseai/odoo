# -*- coding: utf-8 -*-
{
    "name": "IPAI OAuth Internal User",
    "version": "18.0.1.0.0",
    "category": "Technical",
    "summary": "Makes OAuth users Internal Users instead of Portal users",
    "description": """
IPAI OAuth Internal User
========================

This module modifies the default OAuth authentication behavior to create
users as Internal Users (with backend access) instead of Portal users
(limited to portal pages like /my/home).

By default, Odoo's auth_oauth module creates new OAuth users with the
Portal group (base.group_portal), which only allows access to portal
pages like invoices, quotes, and account settings.

This module overrides that behavior to:

1. Assign the Internal User group (base.group_user) to new OAuth users
2. Remove the Portal group if it was assigned
3. Allow OAuth users full access to the Odoo backend (/web)

Use Case
--------
This is useful when you want employees to log in via Google OAuth
and have access to the full ERP system, not just the portal.

Security Note
-------------
Only enable this module if ALL OAuth users should be internal users.
If you need to distinguish between portal and internal OAuth users,
consider using a more sophisticated approach based on email domain
or OAuth provider attributes.
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "AGPL-3",
    "depends": [
        "auth_oauth",
    ],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}
