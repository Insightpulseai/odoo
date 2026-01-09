#!/usr/bin/env python3
"""Promote OAuth users from Portal to Internal Users"""

# List of OAuth user emails to promote
emails = ['jgtolentino.rn@gmail.com']  # Add more emails here as needed

# Get the internal and portal groups
internal = env.ref('base.group_user')
portal = env.ref('base.group_portal')

print(f"Internal User group: {internal.name} (ID: {internal.id})")
print(f"Portal group: {portal.name} (ID: {portal.id})")
print()

for email in emails:
    u = env['res.users'].sudo().search([('login', '=', email)], limit=1)
    if not u:
        print(f'❌ NOT FOUND: {email}')
        continue

    # Check current groups
    is_portal = portal in u.groups_id
    is_internal = internal in u.groups_id

    print(f'Found user: {u.name} ({u.login})')
    print(f'  Current state: Portal={is_portal}, Internal={is_internal}')

    # Promote to internal user
    u.write({'groups_id': [(4, internal.id), (3, portal.id)]})

    # Reload to verify the change
    u = env['res.users'].sudo().browse(u.id)
    is_portal_after = portal in u.groups_id
    is_internal_after = internal in u.groups_id

    print(f'  After update: Portal={is_portal_after}, Internal={is_internal_after}')
    print(f'✅ PROMOTED: {u.login}')
    print()

print("Done!")
