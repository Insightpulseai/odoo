# InsightPulse Default Home Page

**Purpose**: Set default landing page after login to Apps Dashboard (`/odoo`)

## Features
- Shows Apps Dashboard with icon grid (like official Odoo)
- Displays: Discuss, Dashboards, Invoicing, Employees, Expenses, Apps, Settings
- Works for all users
- Matches official Odoo behavior

## Configuration
The default home page is set via system parameter:
- **Key**: `web.base.url.redirect`
- **Value**: `/odoo`

## Installation
1. Install this module via Odoo Apps menu
2. Users will see the Apps Dashboard icon grid after login

## Technical Details
- Sets `res.users` default home action to `False` (shows Apps Dashboard)
- Redirects to `/odoo` base URL
- Compatible with Odoo 18 CE
