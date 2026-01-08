# WHAT_SHIPPED - Release [TAG]

## Release Information

| Field | Value |
|-------|-------|
| Release Tag | `[TAG]` |
| Deploy Date | `[YYYY-MM-DD HH:MM UTC]` |
| Git SHA | `[FULL_SHA]` |
| Ship Bundle Version | `1.1.0` |
| Environment | `production` |
| Deployed By | `[USERNAME]` |

---

## Modules Deployed

### IPAI Ship Bundle

| Module | Version | State |
|--------|---------|-------|
| `ipai_theme_aiux` | 18.0.0.1.0 | [installed/upgraded] |
| `ipai_aiux_chat` | 18.0.0.1.0 | [installed/upgraded] |
| `ipai_ask_ai` | 18.0.1.0.0 | [installed/upgraded] |
| `ipai_document_ai` | 18.0.1.0.0 | [installed/upgraded] |
| `ipai_expense_ocr` | 18.0.1.0.0 | [installed/upgraded] |

### Additional Modules (if any)

| Module | Version | State |
|--------|---------|-------|
| [module_name] | [version] | [state] |

---

## Verification Proofs

### Health Checks

| Check | Result | Timestamp |
|-------|--------|-----------|
| `/web/login` | [200/303] | [TIMESTAMP] |
| `/web/health` | [200] | [TIMESTAMP] |
| `/longpolling/poll` | [200/400] | [TIMESTAMP] |
| DB Connectivity | [OK] | [TIMESTAMP] |
| Container Uptime | [Xm stable] | [TIMESTAMP] |

### Asset Verification

| Check | Result |
|-------|--------|
| Backend JS | [200] |
| Backend CSS | [200] |
| QWeb Templates | [200] |
| No SCSS Errors | [PASS] |

### Integration Tests

| Integration | Test | Result |
|-------------|------|--------|
| Email (Mailgun) | SMTP Connect | [PASS/SKIP] |
| SMS (Sinch) | API Connect | [PASS/SKIP] |
| OCR Service | Health Check | [PASS/SKIP] |

---

## Changes Included

### Features
- [Feature 1 description]
- [Feature 2 description]

### Bug Fixes
- [Fix 1 description]
- [Fix 2 description]

### Infrastructure
- [Infra change description]

---

## Configuration Changes

### Environment Variables

| Variable | Change |
|----------|--------|
| [VAR_NAME] | [Added/Modified/Removed] |

### System Parameters

| Parameter | Old Value | New Value |
|-----------|-----------|-----------|
| [param.key] | [old] | [new] |

---

## Rollback Information

### Previous Release
- Tag: `[PREVIOUS_TAG]`
- SHA: `[PREVIOUS_SHA]`

### Rollback Command
```bash
# Update to previous tag
# Edit .env: APP_IMAGE_VERSION=[PREVIOUS_TAG]

# Deploy
docker compose -f deploy/docker-compose.prod.yml pull
docker compose -f deploy/docker-compose.prod.yml up -d

# Verify
./scripts/deploy/verify_prod.sh
```

### DB Backup
- Backup File: `[backup_YYYYMMDD_HHMMSS.sql]`
- Backup Location: `[path or object storage URL]`

---

## Known Issues

| Issue | Severity | Workaround |
|-------|----------|------------|
| [Issue description] | [Low/Medium/High] | [Workaround if any] |

---

## Post-Deploy Checklist

- [ ] All health checks passing
- [ ] No error spikes in logs
- [ ] Key workflows tested (expense OCR, AI chat)
- [ ] Stakeholders notified
- [ ] Change freeze in effect (24-48h)

---

## Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Deployer | [NAME] | [✓] | [DATE] |
| Verifier | [NAME] | [✓] | [DATE] |
| Owner | [NAME] | [✓] | [DATE] |

---

## Proof Artifacts

Attached artifacts:
- `proofs/deploy-[TIMESTAMP].json` - Verification proof JSON
- `proofs/module_install.log` - Module installation log
- `proofs/healthcheck.log` - Health check outputs

---

*Generated: [TIMESTAMP]*
*Template Version: 1.0*
