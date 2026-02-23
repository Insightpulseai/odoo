# Quick Start: Native REST API

**Module:** `ipai_rest_controllers` v19.0.1.0.0
**Status:** ✅ Ready for installation
**Commits:** 790c35fa8, 9f71c83a1

---

## 1. Install Module (2 minutes)

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/sandbox/dev

# Install ipai_rest_controllers
scripts/odoo/install_modules_chunked.sh odoo ipai_rest_controllers 1
```

**Expected:** Module installs without errors, REST endpoints become available.

---

## 2. Test Endpoints (2 minutes)

### Health Check (No Auth)

```bash
curl -X POST http://localhost:8069/api/v1/health \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{},"id":1}'
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "ipai-rest-controllers",
  "version": "19.0.1.0.0",
  "odoo_version": "19.0"
}
```

### Echo Test (Requires API Key)

```bash
curl -X POST http://localhost:8069/api/v1/echo \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"message":"Hello World"},"id":1}'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "echo": "Hello World",
    "user": "Administrator",
    "timestamp": "..."
  }
}
```

### Partner Search (Requires API Key)

```bash
curl -X POST http://localhost:8069/api/v1/partners/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"name":"Azure","limit":5},"id":1}'
```

---

## 3. Add Custom Endpoints (as needed)

Edit `addons/ipai_rest_controllers/controllers/main.py`:

```python
@http.route('/api/v1/your-endpoint', type='json', auth='user', methods=['POST'], csrf=False)
@validate_api_key
def your_endpoint(self, **kwargs):
    """Your endpoint documentation"""
    try:
        # Your business logic here
        data = kwargs.get('data', {})

        return {
            'jsonrpc': '2.0',
            'result': {
                'status': 'success',
                'data': data
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

**Then:** Restart Odoo to pick up changes.

---

## 4. Monitor Upstream Migration (weekly)

```bash
# Check if OCA base_rest is ready for Odoo 19.0
./scripts/oca/check_rest_framework_19.sh
```

**When ready:**
- Script will exit with code 0
- Follow migration instructions in `docs/architecture/rest_migration_plan.md`

---

## Documentation

**Complete Guide:** `addons/ipai_rest_controllers/README.md`
**Migration Plan:** `docs/architecture/rest_migration_plan.md`
**Evidence:** `docs/evidence/20260216-0215/rest-implementation/IMPLEMENTATION_SUMMARY.md`

---

## Troubleshooting

### Endpoint returns 404
```bash
# Restart Odoo
docker restart odoo-dev-1

# Check module installed
docker exec odoo-dev-1 odoo --list-db
```

### Authentication errors
```bash
# Check API key header present
curl -v -X POST http://localhost:8069/api/v1/echo \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"message":"test"},"id":1}'
```

### JSON-RPC format errors

Ensure proper format:
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {...},
  "id": 1
}
```

---

## Migration Timeline

**Now:** Native REST controllers (ipai_rest_controllers)
**Weekly:** Monitor OCA upstream with `check_rest_framework_19.sh`
**Future:** Migrate to base_rest when OCA completes 19.0 migration

**Current Upstream Status:**
- ❌ component module (OCA/connector:19.0) - not migrated
- ❌ base_rest version - still 18.0.x
- ❌ base_rest installable - still False

---

**Questions?** See complete documentation in `addons/ipai_rest_controllers/README.md`
