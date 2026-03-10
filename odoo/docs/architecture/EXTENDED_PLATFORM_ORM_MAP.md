# Extended Platform ORM Mapping

Odoo 18 CE + OCA Extended Platform - Complete ORM Field Reference

## Table of Contents

- [Queue Job (Background Processing)](#queue-job-background-processing)
- [Date Ranges](#date-ranges)
- [MIS Builder (Reporting)](#mis-builder-reporting)
- [KPI Dashboard](#kpi-dashboard)
- [Spreadsheet OCA](#spreadsheet-oca)
- [Knowledge (Document Page)](#knowledge-document-page)
- [DMS (Document Management)](#dms-document-management)
- [Audit Log](#audit-log)
- [Account Financial Tools](#account-financial-tools)
- [IPAI Platform](#ipai-platform)

---

## Queue Job (Background Processing)

### `queue.job`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `uuid` | Char(36) | Yes | Unique job identifier (auto-generated) |
| `name` | Char | No | Human-readable job description |
| `func_string` | Text | Yes | Python function path (e.g., `module.model.method`) |
| `channel` | Char | Yes | Job channel (`root`, `high`, `medium`, `low`) |
| `state` | Selection | Yes | `pending`, `enqueued`, `started`, `done`, `failed` |
| `priority` | Integer | No | Priority (0-100, lower = higher priority) |
| `date_created` | Datetime | Yes | Creation timestamp |
| `date_enqueued` | Datetime | No | When job was queued |
| `date_started` | Datetime | No | Execution start time |
| `date_done` | Datetime | No | Completion time |
| `eta` | Datetime | No | Earliest execution time (delay jobs) |
| `max_retries` | Integer | No | Maximum retry attempts (default: 5) |
| `retry` | Integer | No | Current retry count |
| `result` | Text | No | JSON execution result |
| `exc_info` | Text | No | Exception traceback if failed |
| `model_name` | Char | No | Related Odoo model |
| `record_ids` | Text | No | JSON array of record IDs |
| `company_id` | Many2one | No | → `res.company` |
| `user_id` | Many2one | No | → `res.users` |

**Key Methods:**
```python
# Create a delayed job
record.with_delay(priority=10, eta=eta_datetime).method_name(args)

# Create with specific channel
record.with_delay(channel='root.high').method_name(args)

# Retry configuration
record.with_delay(max_retries=10).method_name(args)
```

### `queue.job.channel`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | Channel name (e.g., `root.high`) |
| `parent_id` | Many2one | No | → `queue.job.channel` (parent channel) |
| `complete_name` | Char | No | Full channel path (computed) |
| `capacity` | Integer | Yes | Max concurrent jobs (default: 1) |

---

## Date Ranges

### `date.range.type`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | Type name (e.g., "Fiscal Year", "Quarter") |
| `allow_overlap` | Boolean | No | Allow overlapping ranges (default: False) |
| `active` | Boolean | No | Active flag (default: True) |
| `company_id` | Many2one | No | → `res.company` |

### `date.range`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | Period name (e.g., "FY2026-Q1") |
| `type_id` | Many2one | Yes | → `date.range.type` |
| `date_start` | Date | Yes | Period start date |
| `date_end` | Date | Yes | Period end date |
| `active` | Boolean | No | Active flag |
| `company_id` | Many2one | No | → `res.company` |

**Usage in Wizards:**
```python
# Find date range for a date
date_range = self.env['date.range'].search([
    ('type_id', '=', type_id),
    ('date_start', '<=', target_date),
    ('date_end', '>=', target_date),
], limit=1)
```

---

## MIS Builder (Reporting)

### `mis.report`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | Report name |
| `description` | Text | No | Report description |
| `style_id` | Many2one | No | → `mis.report.style` (default style) |
| `move_lines_source` | Char | No | Source for accounting data |
| `account_model` | Char | No | Account model (default: `account.account`) |
| `kpi_ids` | One2many | No | → `mis.report.kpi` |

### `mis.report.kpi`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `report_id` | Many2one | Yes | → `mis.report` |
| `name` | Char | Yes | Technical name (e.g., `revenue`) |
| `description` | Char | No | Display name (e.g., "Total Revenue") |
| `expression` | Text | Yes | Python expression or AEP formula |
| `type` | Selection | No | `num` (number), `pct` (percentage), `str` (string) |
| `compare_method` | Selection | No | `pct`, `diff`, `none` |
| `sequence` | Integer | No | Display order |
| `divider` | Selection | No | `1`, `1000`, `1000000` |
| `dp` | Integer | No | Decimal places (default: 0) |
| `prefix` | Char | No | Value prefix |
| `suffix` | Char | No | Value suffix |
| `style_id` | Many2one | No | → `mis.report.style` |

**Expression Examples:**
```python
# Simple account balance
balp[('account_id.code', '=like', '4%')]

# Revenue minus expenses
revenue - expenses

# Python expression
sum(line.debit for line in move_lines if line.account_id.code.startswith('4'))
```

### `mis.report.instance`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | Instance name |
| `report_id` | Many2one | Yes | → `mis.report` |
| `company_id` | Many2one | No | → `res.company` |
| `target_move` | Selection | No | `posted` or `all` |
| `period_ids` | One2many | No | → `mis.report.instance.period` |

### `mis.report.instance.period`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `report_instance_id` | Many2one | Yes | → `mis.report.instance` |
| `name` | Char | Yes | Period name |
| `sequence` | Integer | No | Display order |
| `mode` | Selection | No | `fix`, `relative`, `relative_date_range` |
| `date_from` | Date | No | Fixed start date |
| `date_to` | Date | No | Fixed end date |
| `date_range_type_id` | Many2one | No | → `date.range.type` |
| `date_range_id` | Many2one | No | → `date.range` |
| `offset` | Integer | No | Offset periods (for relative mode) |
| `duration` | Integer | No | Duration in periods |

---

## KPI Dashboard

### `kpi.dashboard`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | Dashboard name |
| `active` | Boolean | No | Active flag |
| `number_of_columns` | Integer | No | Grid columns (default: 4) |
| `group_ids` | Many2many | No | → `res.groups` (access control) |
| `company_id` | Many2one | No | → `res.company` |
| `tile_ids` | One2many | No | → `kpi.dashboard.tile` |

### `kpi.dashboard.tile`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dashboard_id` | Many2one | Yes | → `kpi.dashboard` |
| `name` | Char | Yes | Tile name |
| `sequence` | Integer | No | Display order |
| `widget` | Selection | No | `number`, `graph`, `count` |
| `model_id` | Many2one | No | → `ir.model` (data source) |
| `domain` | Char | No | JSON domain filter |
| `measure_field_id` | Many2one | No | → `ir.model.fields` |
| `color` | Char | No | CSS color |
| `icon` | Char | No | FontAwesome icon class |
| `compare_method` | Selection | No | Comparison method |
| `goal_value` | Float | No | Target value |

---

## Spreadsheet OCA

### `spreadsheet.spreadsheet`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | Spreadsheet name |
| `data` | Binary (JSON) | No | Full spreadsheet data |
| `thumbnail` | Binary | No | PNG preview thumbnail |
| `active` | Boolean | No | Active flag |
| `group_ids` | Many2many | No | → `res.groups` |
| `company_id` | Many2one | No | → `res.company` |

### `spreadsheet.dashboard`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | Dashboard name |
| `spreadsheet_id` | Many2one | No | → `spreadsheet.spreadsheet` |
| `active` | Boolean | No | Active flag |
| `publish_dashboard` | Boolean | No | Publish to users |
| `group_ids` | Many2many | No | → `res.groups` |

---

## Knowledge (Document Page)

### `document.page`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | Page title |
| `parent_id` | Many2one | No | → `document.page` (parent page) |
| `content` | Html | No | Page content (HTML) |
| `display_name` | Char | No | Full path (computed) |
| `sequence` | Integer | No | Display order |
| `type` | Selection | No | `content`, `category` |
| `active` | Boolean | No | Active flag |
| `group_ids` | Many2many | No | → `res.groups` |
| `company_id` | Many2one | No | → `res.company` |
| `child_ids` | One2many | No | → `document.page` (children) |
| `history_ids` | One2many | No | → `document.page.history` |

### `document.page.history`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `page_id` | Many2one | Yes | → `document.page` |
| `content` | Text | No | Historical content snapshot |
| `summary` | Char | No | Change summary |
| `create_date` | Datetime | No | Revision timestamp |
| `create_uid` | Many2one | No | → `res.users` |

---

## DMS (Document Management)

### `dms.storage`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | Storage name |
| `save_type` | Selection | Yes | `database`, `attachment`, `file` |
| `external_root` | Char | No | Base path for file storage |
| `is_hidden` | Boolean | No | Hide from UI |
| `company_id` | Many2one | No | → `res.company` |

### `dms.directory`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | Directory name |
| `parent_id` | Many2one | No | → `dms.directory` |
| `complete_name` | Char | No | Full path (computed) |
| `storage_id` | Many2one | No | → `dms.storage` |
| `group_ids` | Many2many | No | → `res.groups` |
| `company_id` | Many2one | No | → `res.company` |
| `file_ids` | One2many | No | → `dms.file` |
| `child_directory_ids` | One2many | No | → `dms.directory` |

### `dms.file`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | File name |
| `directory_id` | Many2one | Yes | → `dms.directory` |
| `content` | Binary | No | File content |
| `mimetype` | Char | No | MIME type |
| `extension` | Char | No | File extension |
| `size` | Integer | No | File size (bytes) |
| `category_id` | Many2one | No | → `dms.category` |
| `tag_ids` | Many2many | No | → `dms.tag` |
| `locked_by` | Many2one | No | → `res.users` |

### `dms.category`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | Category name |
| `parent_id` | Many2one | No | → `dms.category` |
| `complete_name` | Char | No | Full path |

### `dms.tag`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | Tag name |
| `color` | Integer | No | Odoo color index (0-11) |
| `category_id` | Many2one | No | → `dms.category` |

---

## Audit Log

### `auditlog.rule`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | Rule name |
| `model_id` | Many2one | Yes | → `ir.model` (model to audit) |
| `log_read` | Boolean | No | Log read operations |
| `log_create` | Boolean | No | Log create operations |
| `log_write` | Boolean | No | Log update operations |
| `log_unlink` | Boolean | No | Log delete operations |
| `state` | Selection | No | `draft`, `subscribed` |

### `auditlog.log`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model_id` | Many2one | Yes | → `ir.model` |
| `res_id` | Integer | Yes | Record ID |
| `method` | Char | Yes | `create`, `write`, `unlink`, `read` |
| `user_id` | Many2one | No | → `res.users` |
| `http_session_id` | Integer | No | HTTP session reference |
| `http_request_id` | Integer | No | HTTP request reference |
| `create_date` | Datetime | No | Log timestamp |
| `line_ids` | One2many | No | → `auditlog.log.line` |

### `auditlog.log.line`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `log_id` | Many2one | Yes | → `auditlog.log` |
| `field_id` | Many2one | Yes | → `ir.model.fields` |
| `old_value` | Text | No | Previous value (raw) |
| `old_value_text` | Text | No | Previous value (display) |
| `new_value` | Text | No | New value (raw) |
| `new_value_text` | Text | No | New value (display) |

---

## Account Financial Tools

### `account.fiscal.year`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | Fiscal year name |
| `date_from` | Date | Yes | Start date |
| `date_to` | Date | Yes | End date |
| `company_id` | Many2one | No | → `res.company` |

---

## IPAI Platform

### `ipai.command.center.run`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Char | Yes | Run name/description |
| `run_type` | Selection | No | `ai_query`, `batch_job`, `integration`, `report` |
| `state` | Selection | No | `pending`, `running`, `done`, `failed` |
| `date_start` | Datetime | No | Execution start |
| `date_end` | Datetime | No | Execution end |
| `duration` | Float | No | Duration in seconds |
| `job_id` | Many2one | No | → `queue.job` |
| `result` | Text (JSON) | No | Execution result |
| `error_message` | Text | No | Error details |
| `user_id` | Many2one | No | → `res.users` |
| `company_id` | Many2one | No | → `res.company` |

### `ipai.ai.request`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | Text | Yes | User prompt |
| `response` | Text | No | AI response |
| `model` | Char | No | AI model identifier |
| `tokens_input` | Integer | No | Input token count |
| `tokens_output` | Integer | No | Output token count |
| `latency_ms` | Integer | No | Response latency |
| `context_model` | Char | No | Source Odoo model |
| `context_res_id` | Integer | No | Source record ID |
| `user_id` | Many2one | No | → `res.users` |
| `create_date` | Datetime | No | Request timestamp |

---

## Common ORM Patterns

### Delayed Job Creation
```python
# Basic delayed job
self.with_delay().process_records()

# With priority and ETA
from datetime import timedelta
eta = fields.Datetime.now() + timedelta(hours=1)
self.with_delay(priority=5, eta=eta).process_records()

# With retry configuration
self.with_delay(max_retries=10, channel='root.high').sync_external()
```

### Date Range Queries
```python
# Get current fiscal period
fiscal_type = self.env['date.range.type'].search([('name', '=', 'Fiscal Year')])
current_period = self.env['date.range'].search([
    ('type_id', '=', fiscal_type.id),
    ('date_start', '<=', fields.Date.today()),
    ('date_end', '>=', fields.Date.today()),
], limit=1)
```

### MIS Report Generation
```python
# Generate report data
instance = self.env['mis.report.instance'].browse(instance_id)
data = instance.compute()

# Export to XLSX
instance.action_export_xlsx()
```

### Audit Log Query
```python
# Get changes for a record
logs = self.env['auditlog.log'].search([
    ('model_id.model', '=', 'sale.order'),
    ('res_id', '=', order_id),
])
for log in logs:
    for line in log.line_ids:
        print(f"{line.field_id.name}: {line.old_value} → {line.new_value}")
```

---

*Generated: 2026-01-06 | Odoo 18 CE Extended Platform*
