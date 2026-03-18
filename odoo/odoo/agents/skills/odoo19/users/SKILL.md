---
name: users
description: Manage internal/portal/public users, access rights, groups, passwords, 2FA, and multi-company access.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# users — Odoo 19.0 Skill Reference

## Overview

The Users module controls who can access an Odoo database and what they can see and do. It covers user creation, invitation workflows, access rights assignment per application, group-based permission management, password policies, two-factor authentication (2FA), device tracking, multi-company access, portal users, and LDAP/OAuth integration (Google, Azure, Facebook). Database administrators use this module to enforce security policies and manage organizational access.

## Key Concepts

- **Internal user**: Full database user with configurable access rights per application.
- **Portal user**: External user with restricted, pre-set access to the database portal (views records, no admin access rights).
- **Public user**: Anonymous visitor accessing the website frontend.
- **Access rights**: Per-application permission levels assigned on the user form's Access Rights tab (e.g., Blank/None, User: Own Documents, User: All Documents, Administrator).
- **Groups**: Named sets of permissions (model access + record rules) that can be assigned to users. Managed under Settings > Users & Companies > Groups (developer mode).
- **Record rules**: Domain-based filters that refine access rights at the record level (read/write/create/delete).
- **Superuser mode**: Bypasses all record rules and access rights. Activated via developer mode debug menu > "Become Superuser". Requires Administration: Settings.
- **Two-factor authentication (2FA)**: TOTP-based second factor using an authenticator app. Can be enforced database-wide.
- **User devices**: Kanban list of devices a user has logged in from, including IP address tracking and revocation.

## Core Workflows

### 1. Add a new internal user

1. Navigate to Settings > Users > Manage Users > New.
2. Fill in name, email, and access rights per application.
3. Save. An invitation email is sent automatically.
4. User clicks the link to accept and create their login.

### 2. Configure access rights

1. Open user profile > Access Rights tab.
2. For each application, select permission level from drop-down.
3. Administration field: choose Settings or Access Rights.
4. Save.

### 3. Manage groups and specific permissions (developer mode)

1. Enable developer mode.
2. Settings > Users & Companies > Groups.
3. Select or create a group. Configure: Users, Inherited groups, Menus, Views, Access Rights (model CRUD), Record Rules.
4. On a user's Technical Access Rights tab, add/remove Selected Groups.

### 4. Enable and enforce two-factor authentication

1. User: Profile avatar > My Profile > Account Security tab > toggle 2FA on.
2. Enter password to confirm, scan QR code with authenticator app, enter verification code, click Activate.
3. Admin enforcement: Settings > Permissions > tick "Enforce two-factor authentication" > Employees only or All users > Save.

### 5. Reset a user's password

- **From login page**: User clicks "Reset Password" (if enabled in Settings > Permissions > Password Reset).
- **Admin-initiated**: Settings > Users > select user > "Send Password Reset Instructions".
- **Direct change**: Settings > Users > select user > Actions > Change Password.

### 6. Deactivate (archive) a user

1. Settings > Users > Manage Users.
2. Select user(s) via checkbox.
3. Actions > Archive > confirm.

## Technical Reference

### Models

| Model | Purpose |
|-------|---------|
| `res.users` | User records |
| `res.groups` | Permission groups |
| `ir.model.access` | Model-level CRUD access rights |
| `ir.rule` | Record rules (domain-based) |
| `res.users.device` | User device tracking |

### Key Fields on `res.users`

| Field | Purpose |
|-------|---------|
| `login` | Email / username for login |
| `groups_id` | Many2many to `res.groups` |
| `company_ids` | Allowed companies |
| `company_id` | Default company |
| `totp_enabled` | Whether 2FA is active |

### Menu Paths

- `Settings > Users > Manage Users`
- `Settings > Users & Companies > Users`
- `Settings > Users & Companies > Groups` (developer mode)
- `Settings > Permissions` (Password Reset, Minimum Password Length, Enforce 2FA)

### Important Settings

| Setting | Location | Default |
|---------|----------|---------|
| Minimum Password Length | Settings > Permissions | 8 |
| Password Reset | Settings > Permissions | Enabled |
| Enforce 2FA | Settings > Permissions | Disabled |

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18 vs 19 breaking changes listed in RST source -->

## Common Pitfalls

- **Never deactivate the admin user**: Disabling or modifying the main administrator can cause "impotent admin" — no user can change access rights. Contact Odoo support if this happens.
- **Superuser mode lock-out**: Changes made in superuser mode can lock the user out. Always test access changes on non-admin users first.
- **Multi-company misconfiguration**: Incorrect Allowed Companies / Default Company settings cause inconsistent cross-company behavior. Only experienced users should modify these.
- **Subscription upsell on user add**: Adding users on yearly/multi-year plans triggers an upsell quotation (30-day window). Monthly plans auto-adjust.
- **2FA lost authenticator**: If a user loses access to their authenticator, an administrator must manually deactivate 2FA on their account before they can log in again.
