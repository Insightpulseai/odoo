# Examples: Tenant Context Mapping

## Example 1: Subdomain-Based Mapping

**Request flow**:
```
https://acme.app.insightpulseai.com/api/orders
        ^^^^
        tenant subdomain

1. Front Door receives request
2. Routing rule extracts subdomain: "acme"
3. Tenant resolver looks up "acme" -> tenant-id: "uuid-123"
4. X-Tenant-Id header injected: "uuid-123"
5. Container App receives request with tenant context
6. Middleware validates X-Tenant-Id header
7. Database connection sets: SET app.current_tenant_id = 'uuid-123'
8. Query returns only acme's orders
```

**DNS**: Wildcard `*.app.insightpulseai.com` CNAME to Front Door.

---

## Example 2: Token Claim-Based Mapping

**JWT token**:
```json
{
  "sub": "user-456",
  "tid": "tenant-uuid-789",
  "roles": ["member"],
  "aud": "api://ipai-platform"
}
```

**Middleware**:
```python
def extract_tenant_context(request):
    token = validate_jwt(request.headers['Authorization'])
    tenant_id = token.claims.get('tid')
    if not tenant_id:
        raise HTTPException(403, "Missing tenant context in token")
    request.state.tenant_id = tenant_id
    return tenant_id
```

---

## Example 3: Async Message Envelope

**Queue message schema**:
```json
{
  "metadata": {
    "tenant_id": "tenant-uuid-789",
    "correlation_id": "corr-abc-123",
    "timestamp": "2026-03-17T10:00:00Z",
    "source": "order-service"
  },
  "payload": {
    "event": "order.created",
    "order_id": "order-456"
  }
}
```

**Consumer validation**:
```python
def process_message(message):
    tenant_id = message.metadata.get('tenant_id')
    if not tenant_id:
        dead_letter(message, reason="missing tenant_id")
        return
    with tenant_context(tenant_id):
        handle_event(message.payload)
```

---

## Example 4: Observability Integration

**Structured log entry**:
```json
{
  "timestamp": "2026-03-17T10:00:00Z",
  "level": "info",
  "message": "Order created",
  "tenant_id": "tenant-uuid-789",
  "user_id": "user-456",
  "trace_id": "trace-xyz",
  "span_id": "span-abc"
}
```

**OpenTelemetry span attribute**:
```python
span.set_attribute("tenant.id", tenant_id)
span.set_attribute("tenant.tier", "enterprise")
```
