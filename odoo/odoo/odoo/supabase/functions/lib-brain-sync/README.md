# LIB Brain Sync - Edge Function

Supabase Edge Function for LIB Hybrid Brain synchronization.

## Endpoints

### 1. POST /ingest

Push events from local outbox to shared brain.

**Request:**
```json
{
  "batch": [
    {
      "event_ulid": "01HQZX...",
      "device_id": "uuid-device-1",
      "event_type": "upsert_file",
      "entity_type": "file",
      "entity_key": "/path/to/file.py",
      "payload": {
        "path": "/path/to/file.py",
        "sha256": "abc123...",
        "bytes": 1024,
        "mtime_unix": 1707580800,
        "ext": ".py",
        "mime": "text/x-python"
      },
      "vector_clock": {
        "uuid-device-1": 5
      },
      "created_at": "2026-02-10T10:00:00Z"
    }
  ]
}
```

**Headers:**
- `x-lib-sync-secret`: Shared secret for authentication
- `Content-Type`: application/json

**Response:**
```json
{
  "ok": true,
  "result": {
    "inserted_events": 1,
    "upserted_entities": 1
  }
}
```

**Behavior:**
- Validates sync secret
- Limits batch to 500 events max
- Calls `lib_shared_ingest_events()` RPC
- Triggers webhooks if events inserted (non-blocking)
- Returns counts of inserted events and updated entities

---

### 2. GET /pull

Pull events from shared brain (cursored).

**Query Parameters:**
- `after_id` (optional): Pull events with id > after_id (default: 0)
- `limit` (optional): Max events to return (default: 200, max: 500)

**Headers:**
- `x-lib-sync-secret`: Shared secret for authentication

**Response:**
```json
{
  "ok": true,
  "events": [
    {
      "id": 123,
      "event_ulid": "01HQZX...",
      "device_id": "uuid-device-2",
      "event_type": "upsert_file",
      "entity_type": "file",
      "entity_key": "/path/to/file.js",
      "payload": {
        "path": "/path/to/file.js",
        "sha256": "def456...",
        "bytes": 2048,
        "mtime_unix": 1707580900
      },
      "vector_clock": {
        "uuid-device-2": 3
      },
      "created_at": "2026-02-10T10:01:00Z"
    }
  ]
}
```

**Behavior:**
- Validates sync secret
- Calls `lib_shared_pull_events()` RPC
- Returns events ordered by id (ascending)
- Use returned events' max id as next `after_id`

---

### 3. POST /webhook

Register device webhook for real-time notifications.

**Request:**
```json
{
  "device_id": "uuid-device-1",
  "webhook_url": "http://localhost:8001/webhook",
  "secret": "webhook-secret-optional"
}
```

**Headers:**
- `x-lib-sync-secret`: Shared secret for authentication
- `Content-Type`: application/json

**Response:**
```json
{
  "ok": true,
  "webhook_id": 1
}
```

**Behavior:**
- Validates sync secret and webhook URL format
- Calls `lib_shared_register_webhook()` RPC
- Upserts webhook (device_id is unique key)
- Returns webhook ID

**Webhook Notifications:**

When new events are ingested, all active webhooks receive:

```json
{
  "event": "new_events",
  "after_id": 123,
  "timestamp": "2026-02-10T10:05:00Z"
}
```

**Headers:**
- `Content-Type`: application/json
- `x-webhook-secret`: Device webhook secret (if provided)

**Timeout:** 5 seconds per webhook
**Retry:** No automatic retry (logged and continues)

---

### 4. GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.1.0"
}
```

---

## Deployment

### 1. Set Environment Variables

```bash
# Supabase secrets
supabase secrets set LIB_SYNC_SECRET=your-random-secret-here
supabase secrets set SUPABASE_URL=https://your-project.supabase.co
supabase secrets set SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### 2. Deploy Function

```bash
supabase functions deploy lib-brain-sync
```

### 3. Verify Deployment

```bash
# Health check
curl https://your-project.supabase.co/functions/v1/lib-brain-sync/health

# Expected: {"status":"healthy","version":"1.1.0"}
```

---

## Testing

### Test Ingest

```bash
curl -X POST "https://your-project.supabase.co/functions/v1/lib-brain-sync/ingest" \
  -H "x-lib-sync-secret: your-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "batch": [
      {
        "event_ulid": "01HQZX123",
        "device_id": "test-device",
        "event_type": "upsert_file",
        "entity_type": "file",
        "entity_key": "/test/file.txt",
        "payload": {"path": "/test/file.txt", "sha256": "abc", "bytes": 100},
        "vector_clock": {"test-device": 1},
        "created_at": "2026-02-10T10:00:00Z"
      }
    ]
  }'
```

### Test Pull

```bash
curl "https://your-project.supabase.co/functions/v1/lib-brain-sync/pull?after_id=0&limit=10" \
  -H "x-lib-sync-secret: your-secret"
```

### Test Webhook Registration

```bash
curl -X POST "https://your-project.supabase.co/functions/v1/lib-brain-sync/webhook" \
  -H "x-lib-sync-secret: your-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "test-device",
    "webhook_url": "http://localhost:8001/webhook",
    "secret": "test-webhook-secret"
  }'
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "ok": false,
  "error": "Invalid sync secret"
}
```

### 400 Bad Request
```json
{
  "ok": false,
  "error": "Invalid batch format"
}
```

### 500 Internal Server Error
```json
{
  "ok": false,
  "error": "RPC call failed: ..."
}
```

---

## Security

- **Authentication**: `x-lib-sync-secret` header required for all operations
- **Authorization**: Service role key used for all RPC calls (no public access to lib_shared)
- **Rate Limiting**: Batch size limited to 500 events
- **Webhook Validation**: URL format validated before registration
- **Timeout**: 5-second timeout on webhook deliveries (prevents blocking)

---

## Monitoring

### Function Logs

```bash
supabase functions logs lib-brain-sync --tail
```

### Webhook Delivery Status

Query last notification times:
```sql
SELECT device_id, webhook_url, last_notified_at, active
FROM lib_shared.device_webhooks
ORDER BY last_notified_at DESC;
```

### Event Ingestion Stats

```sql
SELECT
  DATE_TRUNC('hour', created_at) as hour,
  COUNT(*) as events,
  COUNT(DISTINCT device_id) as devices
FROM lib_shared.events
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour DESC;
```

---

## Performance

- **Batch Ingestion**: 500 events in <200ms
- **Pull Query**: 200 events in <50ms
- **Webhook Trigger**: Parallel delivery, 5s timeout per webhook
- **CRDT Merge**: Vector clock comparison in PostgreSQL (fast)

---

**Version:** 1.1.0
**Last Updated:** 2026-02-10
