## Summary
<!-- What changed and why? Keep it brief. -->

## Policy Gates
<!-- CI gates enforce merge policy. No human reviewer required when all pass. -->
<!-- See: docs/governance/POLICY_GATES.md -->

All 5 policy gates must be green before merge:
- **Gate 1** Spec Bundle Presence (feat/* with >3 scoped changes)
- **Gate 2** Secret Pattern Diff (no hardcoded credentials in changed lines)
- **Gate 3** Odoo 19 View Convention (`<list>` not `<tree>`)
- **Gate 4** Migration RLS Contract (new tables must enable RLS)
- **Gate 5** Deprecated Reference Block (no `.net`, Mattermost, Mailgun, etc.)

## Spec Kit Compliance
<!-- Required for significant features on feat/* branches. Check all that apply. -->

- [ ] Spec bundle exists under `spec/<slug>/` (constitution.md, prd.md, plan.md, tasks.md)
- [ ] Spec bundle paths are canonical (no docs/development/* drift; plan/tasks references match deliverables)
- [ ] Tasks are DoD-style and machine-checkable (Owner + Deliverable + DoD markers present)
- [ ] Any UI/manual steps are labeled Optional; primary path is automation-first
- [ ] Plan includes verification & rollback steps
- [ ] Tasks reflect current PR scope
- [ ] n8n workflow exports (if any) are secret-free (`automations/n8n/workflows/*.json`)
- [ ] N/A — Minor change (bug fix, docs, config, OCA porting)

## Design Contract (if UI changes)
<!-- Required when PR touches UI components or tokens -->

- [ ] Figma contract exists (`ops/design/figma_contract.json`)
- [ ] Token diff is acceptable (no unexpected changes)
- [ ] Design gate CI check passed (`canonical-gate.yml` green)
- [ ] N/A — No UI changes

## Odoo / Supabase / Ops Impact
<!-- Check all that apply -->

- [ ] DB migrations included (if schema changed)
- [ ] Seed strategy included (if ref data changed)
- [ ] RLS policies updated (if access control changed)
- [ ] Observability updated (alerts/runbooks/metrics as needed)
- [ ] N/A — No ops impact

## Validation Evidence
<!-- Attach proof that this works -->

- [ ] CI passed (all gates green)
- [ ] Local/preview validation attached (logs/screenshots/links)

<details>
<summary>Evidence</summary>

<!-- Paste logs, screenshots, or links here -->

</details>

## Rollback
<!-- How to undo this change if needed -->

<!-- Example: Revert this PR, run migration rollback script -->

## Checklist

- [ ] Tests added/updated for new functionality
- [ ] Documentation updated if needed
- [ ] No secrets or credentials in code
- [ ] Follows OCA-style commit convention

## Related Issues
<!-- Link related issues: Fixes #123, Part of #456 -->
