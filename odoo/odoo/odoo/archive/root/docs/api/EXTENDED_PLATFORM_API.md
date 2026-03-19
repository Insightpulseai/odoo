# Extended Platform API Documentation

REST API endpoints for Odoo 18 CE Extended Platform using OCA `base_rest`.

## Table of Contents

- [Authentication](#authentication)
- [AI Endpoints](#ai-endpoints)
- [Command Center](#command-center)
- [Queue Jobs](#queue-jobs)
- [KPI Dashboard](#kpi-dashboard)
- [Date Ranges](#date-ranges)
- [Documents](#documents)
- [Error Handling](#error-handling)

---

## Base Configuration

### Base URL
```
https://erp.example.com/api/v1
```

### Content Type
```
Content-Type: application/json
```

### Authentication Methods

#### Session Cookie (Web UI)
```bash
# Login to get session cookie
curl -X POST https://erp.example.com/web/session/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "db": "odoo_core",
      "login": "admin",
      "password": "admin"
    },
    "id": 1
  }' \
  -c cookies.txt
```

#### API Key (Recommended for integrations)
```bash
curl -X GET https://erp.example.com/api/v1/health \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## AI Endpoints

### Ask AI

Execute an AI query with context.

**Endpoint:** `POST /api/v1/ai/ask`

**Request:**
```json
{
  "prompt": "What are the top 5 overdue invoices?",
  "context": {
    "model": "account.move",
    "domain": [["payment_state", "=", "not_paid"]],
    "limit": 5
  },
  "options": {
    "stream": false,
    "model": "gpt-4"
  }
}
```

**Response:**
```json
{
  "id": 123,
  "status": "success",
  "response": "Based on the data, here are the top 5 overdue invoices:\n\n1. INV/2026/0001 - $5,000 (30 days overdue)\n...",
  "metadata": {
    "model": "gpt-4",
    "tokens_input": 150,
    "tokens_output": 200,
    "latency_ms": 1500
  }
}
```

### AI Health Check

**Endpoint:** `GET /api/v1/ai/health`

**Response:**
```json
{
  "status": "healthy",
  "provider": "openai",
  "model": "gpt-4",
  "last_check": "2026-01-06T12:00:00Z",
  "response_time_ms": 250
}
```

---

## Command Center

### List Runs

Get paginated list of command center runs.

**Endpoint:** `GET /api/v1/command-center/runs`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `state` | string | Filter by state (pending, running, done, failed) |
| `run_type` | string | Filter by type (ai_query, batch_job, report) |
| `limit` | int | Page size (default: 20, max: 100) |
| `offset` | int | Pagination offset |
| `date_from` | date | Filter by start date |
| `date_to` | date | Filter by end date |

**Response:**
```json
{
  "count": 150,
  "offset": 0,
  "limit": 20,
  "runs": [
    {
      "id": 1,
      "name": "Monthly Close - January 2026",
      "run_type": "batch_job",
      "state": "done",
      "date_start": "2026-01-31T18:00:00Z",
      "date_end": "2026-01-31T18:05:32Z",
      "duration": 332.5,
      "user_id": 2,
      "user_name": "Admin"
    }
  ]
}
```

### Get Run Details

**Endpoint:** `GET /api/v1/command-center/runs/{id}`

**Response:**
```json
{
  "id": 1,
  "name": "Monthly Close - January 2026",
  "run_type": "batch_job",
  "state": "done",
  "date_start": "2026-01-31T18:00:00Z",
  "date_end": "2026-01-31T18:05:32Z",
  "duration": 332.5,
  "result": {
    "steps_completed": 12,
    "records_processed": 1500,
    "warnings": []
  },
  "error_message": null,
  "job_id": 456,
  "user_id": 2,
  "user_name": "Admin"
}
```

### Create Run

**Endpoint:** `POST /api/v1/command-center/runs`

**Request:**
```json
{
  "name": "Custom Report Generation",
  "run_type": "report",
  "params": {
    "report_id": 10,
    "date_range_id": 5
  }
}
```

**Response:**
```json
{
  "id": 157,
  "state": "pending",
  "job_id": 789
}
```

### Get Dashboard Metrics

**Endpoint:** `GET /api/v1/command-center/metrics`

**Response:**
```json
{
  "runs_today": 45,
  "runs_pending": 3,
  "runs_failed_24h": 1,
  "avg_duration_ms": 5230,
  "by_type": {
    "ai_query": 30,
    "batch_job": 10,
    "report": 5
  },
  "by_state": {
    "done": 42,
    "pending": 3,
    "failed": 0
  }
}
```

---

## Queue Jobs

### List Jobs

**Endpoint:** `GET /api/v1/queue/jobs`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `state` | string | pending, enqueued, started, done, failed |
| `channel` | string | Channel name filter |
| `limit` | int | Page size |
| `offset` | int | Offset |

**Response:**
```json
{
  "count": 500,
  "jobs": [
    {
      "id": 1,
      "uuid": "abc-123-def-456",
      "name": "Process Invoice #1234",
      "func_string": "account.move.action_post",
      "channel": "root.medium",
      "state": "done",
      "priority": 10,
      "date_created": "2026-01-06T10:00:00Z",
      "date_done": "2026-01-06T10:00:05Z",
      "retry": 0,
      "max_retries": 5
    }
  ]
}
```

### Get Job Details

**Endpoint:** `GET /api/v1/queue/jobs/{uuid}`

**Response:**
```json
{
  "id": 1,
  "uuid": "abc-123-def-456",
  "name": "Process Invoice #1234",
  "func_string": "account.move.action_post",
  "channel": "root.medium",
  "state": "done",
  "priority": 10,
  "date_created": "2026-01-06T10:00:00Z",
  "date_enqueued": "2026-01-06T10:00:01Z",
  "date_started": "2026-01-06T10:00:02Z",
  "date_done": "2026-01-06T10:00:05Z",
  "eta": null,
  "retry": 0,
  "max_retries": 5,
  "result": {"status": "posted", "id": 1234},
  "exc_info": null,
  "model_name": "account.move",
  "record_ids": [1234]
}
```

### Retry Failed Job

**Endpoint:** `POST /api/v1/queue/jobs/{uuid}/retry`

**Response:**
```json
{
  "uuid": "abc-123-def-456",
  "state": "pending",
  "retry": 1
}
```

### Cancel Job

**Endpoint:** `POST /api/v1/queue/jobs/{uuid}/cancel`

**Response:**
```json
{
  "uuid": "abc-123-def-456",
  "state": "failed",
  "cancelled": true
}
```

---

## KPI Dashboard

### List Dashboards

**Endpoint:** `GET /api/v1/kpi/dashboards`

**Response:**
```json
{
  "dashboards": [
    {
      "id": 1,
      "name": "Finance KPIs",
      "number_of_columns": 4,
      "tile_count": 8
    }
  ]
}
```

### Get Dashboard Data

**Endpoint:** `GET /api/v1/kpi/dashboards/{id}`

**Response:**
```json
{
  "id": 1,
  "name": "Finance KPIs",
  "tiles": [
    {
      "id": 1,
      "name": "Revenue MTD",
      "widget": "number",
      "value": 125000.00,
      "formatted_value": "$125,000",
      "trend": "+15%",
      "trend_direction": "up",
      "color": "#30B636",
      "icon": "fa-dollar"
    },
    {
      "id": 2,
      "name": "Open Invoices",
      "widget": "count",
      "value": 45,
      "goal_value": 30,
      "progress": 66.7,
      "color": "#FA9807"
    }
  ]
}
```

### Refresh Dashboard

**Endpoint:** `POST /api/v1/kpi/dashboards/{id}/refresh`

**Response:**
```json
{
  "id": 1,
  "refreshed_at": "2026-01-06T12:00:00Z",
  "tiles_updated": 8
}
```

---

## Date Ranges

### List Date Range Types

**Endpoint:** `GET /api/v1/date-ranges/types`

**Response:**
```json
{
  "types": [
    {
      "id": 1,
      "name": "Fiscal Year",
      "allow_overlap": false,
      "range_count": 3
    },
    {
      "id": 2,
      "name": "Quarter",
      "allow_overlap": false,
      "range_count": 12
    },
    {
      "id": 3,
      "name": "Month",
      "allow_overlap": false,
      "range_count": 36
    }
  ]
}
```

### List Date Ranges

**Endpoint:** `GET /api/v1/date-ranges`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `type_id` | int | Filter by type |
| `date` | date | Find range containing date |
| `year` | int | Filter by year |

**Response:**
```json
{
  "ranges": [
    {
      "id": 1,
      "name": "FY2026 Q1",
      "type_id": 2,
      "type_name": "Quarter",
      "date_start": "2026-01-01",
      "date_end": "2026-03-31"
    }
  ]
}
```

### Get Current Period

**Endpoint:** `GET /api/v1/date-ranges/current`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | string | Type name (e.g., "Quarter", "Month") |

**Response:**
```json
{
  "fiscal_year": {
    "id": 1,
    "name": "FY 2026",
    "date_start": "2026-01-01",
    "date_end": "2026-12-31"
  },
  "quarter": {
    "id": 1,
    "name": "FY2026 Q1",
    "date_start": "2026-01-01",
    "date_end": "2026-03-31"
  },
  "month": {
    "id": 1,
    "name": "January 2026",
    "date_start": "2026-01-01",
    "date_end": "2026-01-31"
  }
}
```

---

## Documents

### DMS - List Directories

**Endpoint:** `GET /api/v1/dms/directories`

**Response:**
```json
{
  "directories": [
    {
      "id": 1,
      "name": "Company Documents",
      "complete_name": "Company Documents",
      "parent_id": null,
      "file_count": 0,
      "child_count": 5
    }
  ]
}
```

### DMS - List Files

**Endpoint:** `GET /api/v1/dms/files`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `directory_id` | int | Filter by directory |
| `category_id` | int | Filter by category |
| `search` | string | Search in name |

**Response:**
```json
{
  "files": [
    {
      "id": 1,
      "name": "Q1 Financial Report.pdf",
      "directory_id": 5,
      "mimetype": "application/pdf",
      "size": 1048576,
      "category_id": 2,
      "category_name": "Statements",
      "tags": ["2026", "Q1", "Financial"]
    }
  ]
}
```

### DMS - Upload File

**Endpoint:** `POST /api/v1/dms/files`

**Request (multipart/form-data):**
```
file: <binary>
directory_id: 5
category_id: 2
tags: ["2026", "Q1"]
```

**Response:**
```json
{
  "id": 123,
  "name": "uploaded-file.pdf",
  "size": 1048576,
  "directory_id": 5
}
```

### DMS - Download File

**Endpoint:** `GET /api/v1/dms/files/{id}/download`

**Response:** Binary file content with appropriate headers.

### Knowledge - List Pages

**Endpoint:** `GET /api/v1/knowledge/pages`

**Response:**
```json
{
  "pages": [
    {
      "id": 1,
      "name": "Company Wiki",
      "display_name": "Company Wiki",
      "type": "category",
      "child_count": 3
    }
  ]
}
```

### Knowledge - Get Page

**Endpoint:** `GET /api/v1/knowledge/pages/{id}`

**Response:**
```json
{
  "id": 5,
  "name": "Expense Policy",
  "display_name": "Company Wiki / Policies / Finance / Expense Policy",
  "content": "<h1>Expense Policy</h1><p>...</p>",
  "type": "content",
  "history_count": 5,
  "last_modified": "2026-01-05T14:30:00Z",
  "last_modified_by": "Admin"
}
```

### Knowledge - Update Page

**Endpoint:** `PUT /api/v1/knowledge/pages/{id}`

**Request:**
```json
{
  "content": "<h1>Updated Expense Policy</h1><p>New content...</p>",
  "summary": "Updated reimbursement limits"
}
```

**Response:**
```json
{
  "id": 5,
  "history_id": 6,
  "updated_at": "2026-01-06T12:00:00Z"
}
```

---

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid date range",
    "details": {
      "field": "date_start",
      "constraint": "date_start must be before date_end"
    }
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `CONFLICT` | 409 | Resource conflict |
| `RATE_LIMITED` | 429 | Too many requests |
| `SERVER_ERROR` | 500 | Internal server error |

### Rate Limiting

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1704556800
```

---

## OpenAPI Specification

The full OpenAPI 3.0 specification is available at:

```
GET /api/v1/openapi.json
```

Or browse the interactive Swagger UI:

```
GET /api/v1/docs
```

---

*Generated: 2026-01-06 | Odoo 18 CE Extended Platform*
