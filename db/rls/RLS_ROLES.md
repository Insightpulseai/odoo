# RLS Roles and Permissions

**Version:** 1.0.0
**Last Updated:** 2025-12-07

---

## 1. Overview

This document defines the role hierarchy and permissions for InsightPulseAI's Row-Level Security (RLS) implementation.

---

## 2. Role Hierarchy

```
platform_admin
    └── tenant_admin
            ├── finance_director
            │       ├── teq_admin
            │       │       ├── teq_approver
            │       │       └── teq_employee
            │       └── ppm_admin
            ├── retail_admin
            │       ├── scout_analyst
            │       └── sari_store_owner
            └── engine_admin
                    └── engine_user
                            └── readonly
```

---

## 3. Platform Roles

### 3.1 `platform_admin`

**Scope:** Global (all tenants)

| Permission | Description |
|------------|-------------|
| `*` | Full access to everything |
| `tenants:create` | Create new tenants |
| `tenants:delete` | Delete tenants |
| `tenants:manage` | Manage tenant settings |

**Use Cases:**
- InsightPulseAI operations team
- Emergency access for support

---

### 3.2 `tenant_admin`

**Scope:** Single tenant

| Permission | Description |
|------------|-------------|
| `tenant:*` | Full access within tenant |
| `users:manage` | Manage users and roles |
| `settings:manage` | Manage tenant configuration |
| `audit:read` | View audit logs |

**Use Cases:**
- Client IT administrators
- Account managers

---

## 4. Finance Domain Roles

### 4.1 `finance_director`

**Scope:** Tenant / Finance domain

| Schema | Read | Write | Delete | Special |
|--------|------|-------|--------|---------|
| `expense.*` | ✅ | ✅ | ❌ | Override approvals |
| `teq.*` | ✅ | ✅ | ❌ | View all reports |
| `projects.*` | ✅ | ✅ | ❌ | Budget override |
| `rates.*` | ✅ | ✅ | ❌ | Rate approval |
| `finance.*` | ✅ | ✅ | ✅ | Full access |

**Special Permissions:**
- `expense:override_approval` — Override expense approvals
- `rates:approve` — Approve rate cards
- `budget:override` — Override budget limits

---

### 4.2 `teq_admin`

**Scope:** Tenant / TE-Cheq engine

| Schema | Read | Write | Delete | Special |
|--------|------|-------|--------|---------|
| `expense.*` | ✅ | ✅ | ❌ | - |
| `teq.*` | ✅ | ✅ | ❌ | - |
| `ref.expense_policies` | ✅ | ✅ | ❌ | Manage policies |
| `doc.*` | ✅ | ❌ | ❌ | View receipts |

**Special Permissions:**
- `policies:manage` — Create/edit expense policies
- `expense:view_all` — View all tenant expenses

---

### 4.3 `teq_approver`

**Scope:** Tenant / Assigned cost centers

| Schema | Read | Write | Delete | Special |
|--------|------|-------|--------|---------|
| `expense.expense_reports` | ✅* | ✅* | ❌ | Approval only |
| `expense.expenses` | ✅* | ❌ | ❌ | - |
| `expense.cash_advances` | ✅* | ✅* | ❌ | Approval only |

*Limited to assigned cost centers or direct reports

**Special Permissions:**
- `expense:approve` — Approve expense reports
- `expense:reject` — Reject expense reports
- `expense:request_info` — Request additional information

---

### 4.4 `teq_employee`

**Scope:** Tenant / Own records only

| Schema | Read | Write | Delete | Special |
|--------|------|-------|--------|---------|
| `expense.expense_reports` | ✅* | ✅* | ❌ | Own only |
| `expense.expenses` | ✅* | ✅* | ❌ | Own only |
| `expense.cash_advances` | ✅* | ✅* | ❌ | Own only |
| `ref.expense_policies` | ✅ | ❌ | ❌ | - |
| `ref.expense_categories` | ✅ | ❌ | ❌ | - |

*Only own records (filtered by `employee_id`)

**Special Permissions:**
- `expense:submit` — Submit expense reports
- `expense:upload_receipt` — Upload receipts

---

### 4.5 `ppm_admin`

**Scope:** Tenant / Projects domain

| Schema | Read | Write | Delete | Special |
|--------|------|-------|--------|---------|
| `projects.*` | ✅ | ✅ | ✅ | - |
| `finance.*` | ✅ | ✅ | ❌ | - |

---

## 5. Retail Domain Roles

### 5.1 `retail_admin`

**Scope:** Tenant / Retail domain

| Schema | Read | Write | Delete | Special |
|--------|------|-------|--------|---------|
| `analytics.*` | ✅ | ✅ | ❌ | - |
| `scout_*.*` | ✅ | ✅ | ❌ | - |
| `dim.*` | ✅ | ✅ | ❌ | - |
| `intel.*` | ✅ | ✅ | ❌ | - |
| `saricoach.*` | ✅ | ✅ | ❌ | - |

---

### 5.2 `scout_analyst`

**Scope:** Tenant / Analytics read + limited write

| Schema | Read | Write | Delete | Special |
|--------|------|-------|--------|---------|
| `analytics.*` | ✅ | ❌ | ❌ | - |
| `scout_gold.*` | ✅ | ❌ | ❌ | - |
| `scout_silver.*` | ✅ | ❌ | ❌ | - |
| `dim.*` | ✅ | ❌ | ❌ | - |
| `intel.*` | ✅ | ❌ | ❌ | - |

---

### 5.3 `sari_store_owner`

**Scope:** Tenant / Own store only

| Schema | Read | Write | Delete | Special |
|--------|------|-------|--------|---------|
| `saricoach.stores` | ✅* | ✅* | ❌ | Own store |
| `saricoach.store_metrics_daily` | ✅* | ❌ | ❌ | Own store |
| `saricoach.recommendations` | ✅* | ✅* | ❌ | Accept/reject |
| `analytics.sales_daily` | ✅* | ❌ | ❌ | Own store |

*Filtered by `store_id` ownership

---

### 5.4 `brand_sponsor`

**Scope:** Tenant / Sponsored brand aggregates only

| Schema | Read | Write | Delete | Special |
|--------|------|-------|--------|---------|
| `analytics.sales_daily` | ✅* | ❌ | ❌ | Brand aggregates |
| `dim.brands` | ✅* | ❌ | ❌ | Sponsored brands |
| `scout_gold.*` | ✅* | ❌ | ❌ | Brand aggregates |

*Filtered by `brand_id` sponsorship

---

## 6. Document Processing Roles

### 6.1 `doc_ocr_admin`

**Scope:** Tenant / Document processing

| Schema | Read | Write | Delete | Special |
|--------|------|-------|--------|---------|
| `doc.*` | ✅ | ✅ | ✅ | - |

**Special Permissions:**
- `doc:manage_models` — Configure OCR models
- `doc:retrain` — Trigger model retraining

---

### 6.2 `engine_consumer`

**Scope:** Tenant / Upload and view own documents

| Schema | Read | Write | Delete | Special |
|--------|------|-------|--------|---------|
| `doc.raw_documents` | ✅* | ✅* | ❌ | Own uploads |
| `doc.parsed_documents` | ✅* | ❌ | ❌ | Own documents |
| `doc.user_corrections` | ✅* | ✅* | ❌ | Submit corrections |

---

## 7. Generic Roles

### 7.1 `engine_admin`

**Scope:** Tenant / Specific engine

Generic admin role for any engine. Specific permissions depend on engine configuration.

| Permission | Description |
|------------|-------------|
| `engine:*` | Full engine access |
| `engine:config` | Configure engine settings |
| `engine:users` | Manage engine users |

---

### 7.2 `engine_user`

**Scope:** Tenant / Specific engine

Standard user role for any engine.

| Permission | Description |
|------------|-------------|
| `engine:read` | Read engine data |
| `engine:write` | Write engine data |

---

### 7.3 `readonly`

**Scope:** Tenant / Read-only

| Permission | Description |
|------------|-------------|
| `tenant:read` | Read all tenant data |

---

## 8. RLS Policy Implementation

### 8.1 Standard Tenant Isolation

```sql
CREATE POLICY tenant_isolation ON schema.table_name
    FOR ALL
    USING (tenant_id = core.current_tenant_id());
```

### 8.2 Role-Based Access

```sql
CREATE POLICY role_based_read ON schema.table_name
    FOR SELECT
    USING (
        tenant_id = core.current_tenant_id()
        AND core.has_any_role(ARRAY['teq_admin', 'finance_director'])
    );
```

### 8.3 Owner-Based Access

```sql
CREATE POLICY owner_access ON expense.expense_reports
    FOR ALL
    USING (
        tenant_id = core.current_tenant_id()
        AND (
            employee_id = core.current_user_id()
            OR core.has_role('teq_admin')
            OR core.has_role('finance_director')
        )
    );
```

### 8.4 Hierarchical Access

```sql
CREATE POLICY manager_access ON expense.expense_reports
    FOR SELECT
    USING (
        tenant_id = core.current_tenant_id()
        AND (
            employee_id = core.current_user_id()
            OR employee_id IN (
                SELECT id FROM core.get_subordinates(core.current_user_id())
            )
            OR core.has_role('teq_admin')
        )
    );
```

---

## 9. Role Assignment

### 9.1 Assigning Roles

```sql
-- Assign a role to a user
INSERT INTO core.user_roles (tenant_id, user_id, role_id, granted_by)
SELECT
    'tenant-uuid',
    'user-uuid',
    r.id,
    'admin-uuid'
FROM core.roles r
WHERE r.name = 'teq_employee';
```

### 9.2 Revoking Roles

```sql
-- Revoke a role (soft delete with expiry)
UPDATE core.user_roles
SET expires_at = now()
WHERE user_id = 'user-uuid'
AND role_id = (SELECT id FROM core.roles WHERE name = 'teq_approver');
```

---

## 10. Related Documents

- [RLS_BASE_TEMPLATE.sql](RLS_BASE_TEMPLATE.sql) — SQL templates for RLS
- [DB_TARGET_ARCHITECTURE.md](../DB_TARGET_ARCHITECTURE.md) — Schema definitions
- [INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md](../../docs/architecture/INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md) — Full architecture

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-07 | Initial release |
