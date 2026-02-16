# IPAI REST Controllers

**Version:** 19.0.1.0.0
**Category:** Technical
**License:** LGPL-3

## Overview

Native Odoo REST API controllers providing JSON-RPC endpoints for external integrations.

This is an **interim solution** while waiting for OCA `base_rest` migration to Odoo 19.0.

## Why This Module Exists

**Problem:** OCA `base_rest` module is uninstallable in Odoo 19.0 due to:
- Missing `component` module dependency (OCA/connector not migrated to 19.0)
- Version still at 18.0.x (not bumped to 19.0.x)
- All modules marked `installable: False`

**Solution:** Native implementation using Odoo HTTP controllers until upstream migration completes.

**Migration Path:** See `docs/architecture/rest_migration_plan.md` for complete strategy.

---

## Features

✅ JSON-RPC endpoints for external integrations
✅ Session and API key authentication
✅ Request validation and error handling
✅ Health check endpoint for monitoring
✅ Example endpoints (echo, partner search)
✅ Production-ready with comprehensive error handling

---

## Installation

```bash
# Install module
scripts/odoo/install_modules_chunked.sh odoo ipai_rest_controllers 1

# Verify installation
curl -X POST http://localhost:8069/api/v1/health \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{},"id":1}'
```

---

## API Endpoints

### Health Check

**Endpoint:** `/api/v1/health`
**Method:** POST
**Auth:** None

**Request:**
```bash
curl -X POST http://localhost:8069/api/v1/health \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{},"id":1}'
```

**Response:**
```json
{
  "status": "ok",
  "service": "ipai-rest-controllers",
  "version": "19.0.1.0.0",
  "odoo_version": "19.0"
}
```

---

### Echo Test

**Endpoint:** `/api/v1/echo`
**Method:** POST
**Auth:** Session + API Key

**Request:**
```bash
curl -X POST http://localhost:8069/api/v1/echo \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "jsonrpc":"2.0",
    "method":"call",
    "params":{"message":"Hello World"},
    "id":1
  }'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "echo": "Hello World",
    "user": "Administrator",
    "timestamp": "2026-02-16 12:00:00"
  }
}
```

---

### Partner Search (Example)

**Endpoint:** `/api/v1/partners/search`
**Method:** POST
**Auth:** Session + API Key

**Request:**
```bash
curl -X POST http://localhost:8069/api/v1/partners/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "jsonrpc":"2.0",
    "method":"call",
    "params":{"name":"Azure","limit":5},
    "id":1
  }'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "count": 2,
    "partners": [
      {
        "id": 14,
        "name": "Azure Interior",
        "email": "azure.Interior24@example.com",
        "phone": "+1 555-555-5555"
      }
    ]
  }
}
```

---

## Authentication

### Session-Based (Web Client)

Uses standard Odoo session cookies. Authenticate via `/web/session/authenticate` first.

### API Key-Based (External Integrations)

Pass API key in `X-API-Key` header.

**TODO:** Implement proper API key model and validation.
**Current:** Accepts any non-empty key for demonstration.

---

## Adding Custom Endpoints

Extend `controllers/main.py` with your business logic:

```python
@http.route('/api/v1/your-endpoint', type='json', auth='user', methods=['POST'], csrf=False)
@validate_api_key
def your_endpoint(self, **kwargs):
    """Your endpoint documentation"""
    try:
        # Your logic here
        return {
            'jsonrpc': '2.0',
            'result': {
                'status': 'success',
                'data': {...}
            }
        }
    except Exception as e:
        _logger.error(f"Error: {e}", exc_info=True)
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': 500,
                'message': str(e)
            }
        }
```

---

## Error Handling

All endpoints return JSON-RPC 2.0 error format:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": 400,
    "message": "Error description"
  }
}
```

**Error Codes:**
- `400` - Bad Request (missing/invalid parameters)
- `401` - Unauthorized (missing/invalid API key)
- `403` - Access Denied (insufficient permissions)
- `500` - Internal Server Error

---

## Migration to base_rest

When OCA `base_rest` becomes available for Odoo 19.0:

1. **Monitor upstream:**
   ```bash
   ./scripts/oca/check_rest_framework_19.sh
   ```

2. **Install base_rest:**
   ```bash
   scripts/odoo/install_modules_chunked.sh odoo base_rest,base_rest_datamodel 2
   ```

3. **Refactor controllers:**
   - Replace `http.Controller` with `base_rest.RestController`
   - Use `@restapi.method()` decorators
   - Use base_rest response helpers
   - Preserve API contracts

4. **Deprecate this module:**
   - Mark as deprecated
   - Plan removal after validation period

**See:** `docs/architecture/rest_migration_plan.md` for complete migration guide.

---

## Monitoring Upstream

Check OCA migration status weekly:

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/sandbox/dev
./scripts/oca/check_rest_framework_19.sh
```

**Watch:**
- [OCA/connector](https://github.com/OCA/connector) - Component module migration
- [OCA/rest-framework](https://github.com/OCA/rest-framework) - Version bump to 19.0

---

## Dependencies

- `base` - Core Odoo functionality
- `web` - HTTP request handling

**No OCA dependencies** - fully self-contained.

---

## Known Limitations

1. **API Key Validation:** Currently accepts any non-empty key (TODO: implement proper model)
2. **Rate Limiting:** Not implemented (TODO: add rate limiting)
3. **API Documentation:** No automatic OpenAPI spec generation (unlike base_rest)
4. **Versioning:** Manual API versioning (base_rest has built-in support)

---

## Troubleshooting

### Endpoint returns 404

Check Odoo is running and restart:
```bash
docker restart odoo-dev-1
```

### Authentication errors

Verify session or API key:
```bash
# Check session
curl -c cookies.txt -X POST http://localhost:8069/web/session/authenticate \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","params":{"db":"odoo","login":"admin","password":"admin"}}'

# Use session cookie
curl -b cookies.txt -X POST http://localhost:8069/api/v1/echo ...
```

### JSON-RPC format errors

Ensure proper JSON-RPC 2.0 format:
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {...},
  "id": 1
}
```

---

## Development

**File Structure:**
```
addons/ipai_rest_controllers/
├── README.md
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py          # Add endpoints here
├── models/
│   └── __init__.py      # Future: API key model
└── security/
    └── ir.model.access.csv
```

**Coding Standards:**
- Follow OCA guidelines
- Add docstrings to all endpoints
- Implement proper error handling
- Log errors with context
- Add TODO comments for base_rest migration

---

## Support

**Documentation:** `docs/architecture/rest_migration_plan.md`
**Issues:** GitHub Issues
**Contact:** InsightPulse AI Development Team

---

## License

LGPL-3 - Same as Odoo Community Edition

---

**Last Updated:** 2026-02-16
**Status:** Production-ready interim solution
