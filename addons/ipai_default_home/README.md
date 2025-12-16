# InsightPulse Default Home Page

**Purpose**: Set default landing page after login to Project view (`/odoo/project`)

## Features
- Redirects users to Project view immediately after login
- Overrides Odoo's default home page behavior
- Works for all users (can be customized per user group if needed)

## Configuration
The default home page is set via system parameter:
- **Key**: `web.base.url.redirect`
- **Value**: `/odoo/project`

## Installation
1. Install this module via Odoo Apps menu
2. Users will be redirected to Project view after login

## Technical Details
- Modifies `res.users` default home action
- Sets menu action to Project application
- Compatible with Odoo 18 CE
