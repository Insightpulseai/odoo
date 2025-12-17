# InsightPulse Custom Routes

**Purpose**: Clean URL routes for Odoo apps matching official Odoo behavior

## Features

- **Apps Dashboard as Default Home**: Shows icon grid after login (like official Odoo)
- **Clean URLs**: `/odoo/discuss`, `/odoo/calendar`, `/odoo/project`, `/odoo/expenses`
- **No Configuration Needed**: Works immediately after installation

## Available Routes

| URL | Destination | Description |
|-----|-------------|-------------|
| `/odoo` | Apps Dashboard | Default home page (icon grid) |
| `/odoo/discuss` | Discuss app | Messages, channels, chats |
| `/odoo/calendar` | Calendar app | Events, meetings |
| `/odoo/project` | Project app | Projects, tasks |
| `/odoo/expenses` | Expenses app | Expense reports |

## Installation

1. Go to Apps menu
2. Update Apps List
3. Search "InsightPulse Custom Routes"
4. Click Install
5. Logout and login again

## After Installation

- Default home page: Apps Dashboard at `/odoo`
- All users see icon grid after login
- Clean URLs work like official Odoo

## Technical Details

- **Module Name**: `ipai_custom_routes`
- **Version**: 18.0.1.0.0
- **Dependencies**: base, web, mail, calendar, project, hr_expense
- **Controller**: Custom HTTP routes in `controllers/main.py`
- **Data**: System parameters and user defaults in `data/default_home_data.xml`

## Compatibility

- Odoo 18 CE
- All InsightPulse AI modules
