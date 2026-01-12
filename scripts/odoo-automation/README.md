# Odoo Project + Mailgun + Portal Automation

Automated setup for email-to-task workflows with TBWA portal users.

## Overview

This automation creates:
- Odoo project with portal visibility
- Email alias for task creation
- Portal access for external users

When TBWA sends email to e.g. `sample@insightpulseai.net`:
1. Mailgun receives email
2. Mailgun POSTs to Odoo `/mailgate/mailgun`
3. Odoo matches alias and creates task in project
4. Portal TBWA users can view/interact with tasks

## Quick Start

```bash
# Set environment variables
export ODOO_URL="https://erp.insightpulseai.net/odoo"
export ODOO_DB="odoo"
export ODOO_USER="admin@insightpulseai.net"
export ODOO_PASSWORD="your-password"
export ALIAS_DOMAIN="insightpulseai.net"

# Create project with alias
python create_project_alias.py \
  --project "SAMPLE" \
  --alias "sample" \
  --company "TBWA\\SMP" \
  --visibility portal \
  --portal-users "producer@tbwa.com" "finance@tbwa.com"
```

## Mailgun Route Configuration

After running the script, configure Mailgun:

### Route Settings

| Field | Value |
|-------|-------|
| **Expression** | `match_recipient("sample@insightpulseai.net")` |
| **Action 1** | `forward("https://erp.insightpulseai.net/mailgate/mailgun")` |
| **Action 2** | `stop()` |
| **Priority** | `10` |

### Mailgun API Route Creation

```bash
curl -s --user 'api:YOUR_MAILGUN_API_KEY' \
  https://api.mailgun.net/v3/routes \
  -F priority='10' \
  -F description='SAMPLE project tasks' \
  -F expression='match_recipient("sample@insightpulseai.net")' \
  -F action='forward("https://erp.insightpulseai.net/mailgate/mailgun")' \
  -F action='stop()'
```

## Visibility Modes

| Setting | Value | Description |
|---------|-------|-------------|
| Portal + Internal | `portal` | Invited portal users and all internal users |
| Internal only | `internal` | Only internal users |
| Public | `public` | Anyone with the link |

**Recommended:** `portal` for TBWA workflows.

## End-to-End Workflow

```
TBWA Producer
    |
    v
sample@insightpulseai.net
    |
    v
Mailgun (receives email)
    |
    v
POST /mailgate/mailgun
    |
    v
Odoo (matches alias, creates task)
    |
    v
Task in SAMPLE project
    |
    v
TBWA views via portal
    |
    v
Reply → Mailgun → Odoo (threaded comment)
```

## Portal User Access

Portal users can:
- View tasks assigned to them
- Add comments via email reply
- Attach files
- View project timeline

Portal users cannot:
- Create new tasks directly
- Modify task stages
- Access internal notes

## Script Options

```
create_project_alias.py [-h] --project PROJECT --alias ALIAS
                        [--company COMPANY] [--visibility {portal,internal,public}]
                        [--portal-users [PORTAL_USERS ...]]

Options:
  --project, -p       Project name (required)
  --alias, -a         Email alias prefix (required)
  --company, -c       Company name (default: TBWA\SMP)
  --visibility, -v    Privacy visibility (default: portal)
  --portal-users      Portal user emails to grant access
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ODOO_URL` | `https://erp.insightpulseai.net/odoo` | Odoo instance URL |
| `ODOO_DB` | `odoo` | Database name |
| `ODOO_USER` | (required) | Admin email |
| `ODOO_PASSWORD` | (required) | Admin password |
| `ALIAS_DOMAIN` | `insightpulseai.net` | Email domain |

## Troubleshooting

### Email not creating task

1. Check Mailgun route is active
2. Verify alias exists in Odoo (Settings > Email > Aliases)
3. Check Odoo logs for mailgate errors
4. Ensure Mailgun webhook URL is reachable

### Portal user cannot see project

1. Verify user has portal access (not just contact)
2. Check project visibility is `portal`
3. Add user as follower via script or UI

### Authentication failed

1. Check ODOO_USER and ODOO_PASSWORD
2. Verify user has admin privileges
3. Check API is enabled (XML-RPC)

## Related Files

- `create_project_alias.py` - Main automation script
- `docs/runbooks/mailgun-odoo-integration.md` - Detailed integration guide
