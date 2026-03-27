# B-2: Credential Sanitization Manifest

**Date**: 2026-03-27
**Blocker**: B-2 (12 credentials exposed in `archive/`)
**Status**: IN PROGRESS -- repo sanitized, runtime rotation still required

---

## Summary

All plaintext credentials in `archive/` have been replaced with `REDACTED_BY_AUDIT_20260327`. No files were deleted. Original credential values no longer appear anywhere in the archive tree.

---

## Credentials Sanitized

### 1. PG Pooler Connection String (password: `SHWYXDMFAwXI1drT`)

Supabase PostgreSQL pooler password embedded in connection URIs. Found in 16 files across inventory snapshots and documentation.

| # | File | Credential Type |
|---|------|-----------------|
| 1 | `archive/inventory/runs/20251231T015431Z/apps.list.json` | PG pooler password in SQLALCHEMY_DATABASE_URI |
| 2 | `archive/inventory/runs/20251231T015708Z/apps.list.json` | PG pooler password in SQLALCHEMY_DATABASE_URI |
| 3 | `archive/inventory/runs/20251231T015728Z/apps.list.json` | PG pooler password in SQLALCHEMY_DATABASE_URI |
| 4 | `archive/inventory/runs/20251231T015728Z/apps.73af11cb-...json` | PG pooler password in SQLALCHEMY_DATABASE_URI |
| 5 | `archive/inventory/runs/20251231T015829Z/apps.list.json` | PG pooler password in SQLALCHEMY_DATABASE_URI |
| 6 | `archive/inventory/runs/20251231T015829Z/apps.73af11cb-...json` | PG pooler password in SQLALCHEMY_DATABASE_URI |
| 7 | `archive/inventory/runs/20251231T015909Z/apps.list.json` | PG pooler password in SQLALCHEMY_DATABASE_URI |
| 8 | `archive/inventory/runs/20251231T015909Z/apps.73af11cb-...json` | PG pooler password in SQLALCHEMY_DATABASE_URI |
| 9 | `archive/inventory/runs/20251231T020517Z/apps.list.json` | PG pooler password in SQLALCHEMY_DATABASE_URI |
| 10 | `archive/inventory/runs/20251231T020517Z/apps.73af11cb-...json` | PG pooler password in SQLALCHEMY_DATABASE_URI |
| 11 | `archive/root/docs/deployment/DEPLOYMENT_SUMMARY.md` | PG pooler password in POSTGRES_URL |
| 12 | `archive/root/docs/guides/QUICK_START.md` | PG pooler password in POSTGRES_URL |
| 13 | `archive/root/docs/architecture/TENANT_ARCHITECTURE.md` | PG pooler password (pooled + direct) |
| 14 | `archive/root/docs/infra/SUPERSET_INTEGRATION.md` | PG pooler password in POSTGRES_URL |
| 15 | `archive/templates/saas-landing/DEPLOY.md` | PG pooler password in DB_URL |
| 16 | `archive/templates/saas-landing/scripts/test-local.sh` | PG pooler password in DB_URL |

### 2. Superset Secret Key (plaintext)

Found in 10 files (6 `apps.list.json` + 4 `apps.73af11cb-...json`). Key: `SUPERSET_SECRET_KEY`.

### 3. Supabase ANON_KEY (JWT)

Full JWT token for anon role. Found in 3 files:

| # | File |
|---|------|
| 1 | `archive/root/docs/guides/QUICK_START.md` |
| 2 | `archive/root/docs/architecture/TENANT_ARCHITECTURE.md` |
| 3 | `archive/root/docs/infra/SUPERSET_INTEGRATION.md` |

### 4. Supabase SERVICE_ROLE_KEY (JWT)

Full JWT token for service_role. Found in 3 files:

| # | File |
|---|------|
| 1 | `archive/root/docs/guides/QUICK_START.md` |
| 2 | `archive/root/docs/architecture/TENANT_ARCHITECTURE.md` |
| 3 | `archive/root/docs/infra/SUPERSET_INTEGRATION.md` |

### 5. User Passwords (3 users)

Plaintext passwords in Odoo user data XML.

| # | File | Users |
|---|------|-------|
| 1 | `archive/addons/tbwa_spectra_integration/data/users_data.xml` | finance.head, cfo, finance.manager |

### 6. n8n API Key (JWT)

Full JWT token for n8n public API access.

| # | File |
|---|------|
| 1 | `archive/root/docs/evidence/20260127-0630/platform-kit-merge/N8N_INTEGRATION.md` |

---

## Not Sanitized (Encrypted / Already Safe)

The following items were found in the archive but are DigitalOcean encrypted environment variable blobs (`EV[1:...]`). These are platform-encrypted and cannot be decoded from the archived JSON alone:

- `ODOO_ADMIN_PASSWORD` -- `EV[1:H99vfV2eEXed...]` (5 locations across inventory runs)
- `ODOO_PASSWORD` -- `EV[1:+1R4pQV3ngNs...]` (4 locations across inventory runs)
- `SUPABASE_SERVICE_ROLE_KEY` -- `EV[1:nGtwo+78ClFE...]` and variants (multiple locations)
- `SUPABASE_ANON_KEY` -- `EV[1:GH1PbFKTrPI+...]` (multiple locations)
- Various Redis, Superset admin password blobs

These encrypted blobs remain in the archive as they are not directly exploitable. However, all underlying credentials should still be rotated at runtime.

---

## Verification

Post-sanitization grep confirms zero remaining plaintext credential matches:

- `SHWYXDMFAwXI1drT`: 0 matches
- `1eRsQ4+93UP6OIP2xPLoOKfFCs89kLJMcJ`: 0 matches
- `finance@tbwa2025|cfo@tbwa2025|finance.mgr@tbwa2025`: 0 matches
- Supabase JWT tokens (full-length): 0 matches
- n8n API key JWT: 0 matches

---

## Remaining Work (Runtime)

1. **Rotate Supabase PG password** -- the `SHWYXDMFAwXI1drT` password must be changed at the Supabase project level (deprecated service, may be moot)
2. **Rotate Superset secret key** -- generate new key for any active Superset deployment
3. **Rotate n8n API key** -- n8n decommissioned 2026-03-25, confirmed moot
4. **Confirm DigitalOcean encrypted values are non-functional** -- DO apps deleted, credentials should be inert
5. **Add pre-commit hook** -- `.pre-commit-config.yaml` should include `detect-secrets` or equivalent scanner

---

*Generated: 2026-03-27*
