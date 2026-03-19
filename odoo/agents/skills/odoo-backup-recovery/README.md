# odoo-backup-recovery

Validates backup posture and recovery capabilities on Azure managed PostgreSQL. Ensures incremental backups, geo-redundancy, and point-in-time restore.

## When to use
- Pre-deployment backup verification
- Periodic backup posture audit
- Disaster recovery drill
- Post-incident recovery execution

## Key rule
Never reduce backup retention. Never disable geo-redundancy. Test restores go to disposable databases only. Never expose credentials in output.

## Cross-references
- `agents/knowledge/benchmarks/odoo-sh-persona-model.md`
- `agents/personas/odoo-platform-admin.md`
- `.claude/rules/infrastructure.md`
