# IPAI AI Sources (Odoo Export)

Exports Odoo data to Supabase KB for AI retrieval (RAG).

## Features

- Scheduled export of project tasks to KB
- Export of knowledge articles (if OCA document_page installed)
- Incremental sync (only exports recent changes)
- Tenant-scoped data (per company)
- Upsert logic to prevent duplicates
- Export run tracking for monitoring

## Installation

1. Install the module in Odoo
2. Configure Supabase environment variables
3. The cron job runs automatically every 15 minutes

## Configuration

### Environment Variables

```bash
# Required: Supabase connection
IPAI_SUPABASE_URL=https://<project>.supabase.co
IPAI_SUPABASE_SERVICE_ROLE_KEY=<key>

# Optional: Configuration
IPAI_KB_EXPORT_LOOKBACK_HOURS=24  # Export changes from last N hours
IPAI_PUBLIC_BASE_URL=https://your-odoo.com  # For generating deep links
```

## Data Sources

### project.task

Exports:
- Task name
- Project name
- Stage
- Assignees
- Description (HTML stripped, max 2000 chars)

Chunk format:
```
Task: Task Name
Project: Project Name
Stage: In Progress
Assigned to: John, Jane

Description:
Task description text...
```

### document.page (Optional)

Requires OCA `document_page` module.

Exports:
- Page title
- Page content (HTML stripped, max 4000 chars)

## Supabase Schema

The exporter pushes data to the `kb.chunks` table:

```sql
CREATE TABLE kb.chunks (
  tenant_ref TEXT NOT NULL,      -- 'odoo_company:1'
  source_type TEXT NOT NULL,     -- 'odoo_task', 'odoo_kb'
  source_ref TEXT NOT NULL,      -- 'project.task:123'
  title TEXT,
  url TEXT,
  content TEXT NOT NULL,
  embedding vector(1536),
  updated_at TIMESTAMPTZ,
  UNIQUE(tenant_ref, source_type, source_ref)
);
```

## Monitoring

View export runs in: **AI → KB Export Runs**

Each run shows:
- Start/end time
- Number of chunks exported
- Duration
- Success/failure status
- Error messages (if failed)

## Manual Trigger

To trigger an export manually:

```python
# In Odoo shell
env['ipai.kb.exporter'].cron_export_recent()
```

Or via Docker:

```bash
docker exec -it odoo-erp-prod odoo shell -d odoo <<< "env['ipai.kb.exporter'].cron_export_recent()"
```

## Cron Schedule

Default: Every 15 minutes

To modify, go to: **Settings → Technical → Scheduled Actions → IPAI KB Export**

## Dependencies

- `project` - Odoo project module (for tasks)
- `document_page` - OCA knowledge module (optional, for KB articles)

## License

LGPL-3
