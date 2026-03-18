# Checklist — odoo-backup-recovery

- [ ] Azure PG backup is enabled
- [ ] Retention period meets policy minimum (7+ days)
- [ ] Geo-redundant backup is configured
- [ ] Latest backup timestamp is within last 24 hours
- [ ] Point-in-time restore window is available and current
- [ ] Backup encryption at rest confirmed (AES-256)
- [ ] Backup failure alerting is configured
- [ ] Test restore to disposable database succeeds (if drill)
- [ ] No credentials exposed in verification output
- [ ] Evidence captured in `docs/evidence/{stamp}/odoo-delivery/odoo-backup-recovery/`
