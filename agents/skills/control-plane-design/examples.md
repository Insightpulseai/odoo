# Examples: Control Plane Design

## Example 1: Tenant Catalog Schema

**Scenario**: Control plane for Odoo CE multi-tenant platform.

**Catalog schema**:
```sql
CREATE TABLE tenant_catalog (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            VARCHAR(63) UNIQUE NOT NULL,
    display_name    VARCHAR(255) NOT NULL,
    tier            VARCHAR(20) NOT NULL CHECK (tier IN ('free', 'standard', 'enterprise')),
    state           VARCHAR(20) NOT NULL DEFAULT 'provisioning'
                    CHECK (state IN ('provisioning', 'active', 'suspended', 'deleting', 'deleted')),
    stamp_id        VARCHAR(63) NOT NULL,
    database_name   VARCHAR(63) NOT NULL,
    admin_email     VARCHAR(255) NOT NULL,
    config_version  INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ
);

CREATE TABLE tenant_config (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL REFERENCES tenant_catalog(id),
    version         INTEGER NOT NULL,
    config          JSONB NOT NULL,
    applied_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, version)
);

CREATE TABLE tenant_audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID REFERENCES tenant_catalog(id),
    actor           VARCHAR(255) NOT NULL,
    action          VARCHAR(100) NOT NULL,
    details         JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## Example 2: Control Plane API (OpenAPI Skeleton)

**Scenario**: RESTful API for tenant management.

**Endpoints**:
```yaml
paths:
  /api/v1/tenants:
    get:
      summary: List tenants
      parameters: [state, tier, stamp_id, page, per_page]
      responses: { 200: TenantListResponse }
    post:
      summary: Create tenant (trigger provisioning)
      requestBody: CreateTenantRequest
      responses: { 202: TenantResponse }

  /api/v1/tenants/{tenant_id}:
    get:
      summary: Get tenant details
      responses: { 200: TenantDetailResponse }
    patch:
      summary: Update tenant metadata
      responses: { 200: TenantResponse }

  /api/v1/tenants/{tenant_id}/config:
    get:
      summary: Get current configuration
      responses: { 200: TenantConfigResponse }
    put:
      summary: Apply new configuration version
      responses: { 200: TenantConfigResponse }

  /api/v1/tenants/{tenant_id}/suspend:
    post:
      summary: Suspend tenant
      responses: { 200: TenantResponse }

  /api/v1/tenants/{tenant_id}/resume:
    post:
      summary: Resume suspended tenant
      responses: { 200: TenantResponse }

  /api/v1/tenants/{tenant_id}/health:
    get:
      summary: Get tenant health status
      responses: { 200: TenantHealthResponse }
```

---

## Example 3: Health Aggregation Architecture

**Scenario**: Platform health dashboard showing tenant and stamp status.

**Health check flow**:
```
Per-Stamp Health Probe (every 60s)
  → Check PostgreSQL connectivity
  → Check Container App responsiveness (HTTP 200)
  → Check Redis connectivity
  → Report stamp health to control plane

Per-Tenant Health Probe (every 300s)
  → Check Odoo database accessible
  → Check Odoo web responds for tenant URL
  → Report tenant health to control plane

Control Plane Aggregation
  → Platform health = all stamps healthy
  → Stamp health = all probes pass
  → Tenant health = database + web responding
  → Dashboard: green/yellow/red per tenant
  → Alert: tenant unhealthy for >3 consecutive checks
```
