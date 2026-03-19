# Seed Dedup Remediation — Tasks

## Status Legend
- [ ] Not started
- [x] Done

## Workstream 4: Mirror Cleanup (lowest risk)
- [ ] Diff-verify ops-platform/supabase/ copies are identical
- [ ] Grep for references to ops-platform/supabase/ paths
- [ ] Delete ops-platform/supabase/seeds/ and seed/ mirrors
- [ ] Diff-verify nested odoo/ copies are stale
- [ ] Grep for references to odoo/ nested paths
- [ ] Delete nested odoo/ stale seed copies

## Workstream 3: BIR Consolidation
- [ ] Compare tasks_bir.xml (27) vs 07_tasks_bir_tax.xml (33)
- [ ] Identify tasks in 27 not in 33 (if any)
- [ ] Remove tasks_bir.xml from __manifest__.py data list
- [ ] Delete tasks_bir.xml
- [ ] Test install: odoo -d test_bir -i ipai_finance_close_seed --stop-after-init

## Workstream 2: Mail Server Canonicalization
- [ ] Check production install state of ipai_mailgun_smtp
- [ ] Uninstall ipai_mailgun_smtp if installed
- [ ] Delete ipai_mailgun_smtp module directory
- [ ] Remove mail_server.xml record from ipai_enterprise_bridge data
- [ ] Evaluate ipai_system_config hook vs ipai_zoho_mail canonical path
- [ ] Verify exactly one ir.mail_server at sequence=1
- [ ] Test install: odoo -d test_mail -i ipai_zoho_mail --stop-after-init

## Workstream 1: Finance Task Canonicalization
- [ ] Query production ir_model_data for ipai_finance_close_seed references
- [ ] Plan XML ID migration if needed
- [ ] Remove stage/project/task seed files from ipai_finance_close_seed
- [ ] Update ipai_finance_close_seed __manifest__.py
- [ ] Test install: odoo -d test_finance -i ipai_finance_workflow --stop-after-init
- [ ] Verify no duplicate project.task records

## Final Verification
- [ ] python3 scripts/ci/validate_platform_strategy.py passes
- [ ] No CI workflows reference deleted paths
- [ ] Evidence committed to docs/evidence/
