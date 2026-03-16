# Focalboard Integration

## Overview

Focalboard is our Kanban-style project tracking tool, providing visual task management that syncs with Odoo projects.

**Production URL:** https://boards.insightpulseai.com

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Focalboard Integration                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Odoo CE                          ipai-ops-stack                │
│   ┌────────────────────┐           ┌──────────────────────┐     │
│   │ ipai_integrations  │           │   Focalboard Server  │     │
│   │ - Connector config │◄─────────►│   (Docker)           │     │
│   │ - Webhooks         │   API v2  │                      │     │
│   └────────────────────┘           │   PostgreSQL         │     │
│   ┌────────────────────┐           │   (shared)           │     │
│   │ ipai_focalboard_   │           └──────────────────────┘     │
│   │ connector          │                                        │
│   │ - API client       │                                        │
│   │ - Board sync       │                                        │
│   │ - Card <-> Task    │                                        │
│   └────────────────────┘                                        │
│   ┌────────────────────┐                                        │
│   │ project.task       │                                        │
│   │ (extended)         │                                        │
│   │ - fb_card_id       │                                        │
│   │ - fb_sync_enabled  │                                        │
│   └────────────────────┘                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Odoo Modules

### ipai_focalboard_connector

Focalboard-specific functionality:
- API v2 client (`FocalboardClient`)
- Board synchronization
- Card synchronization
- Bidirectional sync with `project.task`

## Configuration

### 1. System Parameters

Set these in Odoo (Settings > Technical > Parameters > System Parameters):

| Key | Description |
|-----|-------------|
| `ipai_integrations.focalboard_url` | Base URL (default: https://boards.insightpulseai.com) |
| `ipai_focalboard.token_{connector_id}` | Personal access token |

### 2. Create Connector

1. Go to **Integrations > Configuration > Connectors**
2. Create new connector:
   - Name: Focalboard (InsightPulse AI)
   - Type: Focalboard
   - Base URL: https://boards.insightpulseai.com
   - Auth Type: Personal Access Token
3. Click **Test Connection**
4. If successful, click **Activate**

### 3. Sync Boards

1. Go to **Integrations > Focalboard > Boards**
2. Click **Sync Boards** to import boards from Focalboard
3. For each board you want to sync:
   - Link to an Odoo Project
   - Enable sync
   - Choose sync direction

### 4. Link Projects

1. Edit a Focalboard board in Odoo
2. Set **Linked Project** to your Odoo project
3. Enable **Sync Enabled**
4. Choose sync direction:
   - Focalboard → Odoo: Cards create/update Odoo tasks
   - Odoo → Focalboard: Tasks create/update cards
   - Bidirectional: Two-way sync

## Sync Behavior

### Card → Task Mapping

| Focalboard | Odoo |
|------------|------|
| Card title | Task name |
| Card properties | (stored as JSON) |
| Card ID | `fb_card_id` field |

### Task → Card Mapping

| Odoo | Focalboard |
|------|------------|
| Task name | Card title |
| Task stage | Card property (if mapped) |

## API Usage

### Sync Boards

```python
connector = self.env["ipai.integration.connector"].search([
    ("connector_type", "=", "focalboard"),
    ("state", "=", "active"),
], limit=1)

if connector:
    connector.fb_sync_boards()
```

### Sync Cards for a Board

```python
board = self.env["ipai.focalboard.board"].browse(board_id)
board.action_sync_cards()
```

### Create Task from Card

```python
card = self.env["ipai.focalboard.card"].browse(card_id)
card.action_create_odoo_task()
```

### Sync Task to Focalboard

```python
task = self.env["project.task"].browse(task_id)
task.action_sync_to_focalboard()
```

## Data Model

### ipai.focalboard.board

| Field | Type | Description |
|-------|------|-------------|
| `fb_board_id` | Char | Focalboard board ID |
| `title` | Char | Board title |
| `project_id` | Many2one | Linked Odoo project |
| `sync_enabled` | Boolean | Enable sync |
| `sync_direction` | Selection | Sync direction |

### ipai.focalboard.card

| Field | Type | Description |
|-------|------|-------------|
| `fb_card_id` | Char | Focalboard card ID |
| `title` | Char | Card title |
| `task_id` | Many2one | Linked Odoo task |
| `sync_status` | Selection | synced/pending/conflict/error |

### project.task (extended)

| Field | Type | Description |
|-------|------|-------------|
| `fb_card_id` | Char | Linked Focalboard card ID |
| `fb_sync_enabled` | Boolean | Enable sync to Focalboard |

## Troubleshooting

### Connection Failed

1. Verify Focalboard is running: `curl https://boards.insightpulseai.com/api/v2/ping`
2. Check token is valid
3. Review audit logs

### Sync Conflicts

When the same item is modified in both systems:
1. Card/task will be marked with `sync_status = 'conflict'`
2. Manually resolve by choosing which version to keep
3. Re-sync

### Cards Not Appearing

1. Check board is synced
2. Verify workspace ID is correct
3. Run sync manually

## External Resources

- **Runtime Deployment:** `ipai-ops-stack` repository
- **Focalboard Docs:** https://www.focalboard.com/docs/
- **Channel:** #project-management on chat.insightpulseai.com
