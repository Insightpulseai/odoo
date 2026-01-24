## Summary
<!-- What changed and why? Keep it brief. -->

## Status Context
<!-- Optional: If you're in a Launching window, indicate priority -->

<!-- Uncomment if applicable:
**Current:** Launching — merge → deploy → validate
Priority review requested. CI is green.
-->

## Spec Kit Compliance
<!-- Required for significant features. Check all that apply. -->

- [ ] Spec bundle exists under `spec/<slug>/` (constitution.md, prd.md, plan.md, tasks.md)
- [ ] Plan includes verification & rollback steps
- [ ] Tasks reflect current PR scope
- [ ] N/A - This is a minor change (bug fix, docs, config)

## Design Contract (if UI changes)
<!-- Required when PR touches UI components or tokens -->

- [ ] Figma contract exists (`ops/design/figma_contract.json`)
- [ ] Token diff is acceptable (no unexpected changes)
- [ ] Design owners approved
- [ ] N/A - No UI changes

## Odoo / Supabase / Ops Impact
<!-- Check all that apply -->

- [ ] DB migrations included (if schema changed)
- [ ] Seed strategy included (if ref data changed)
- [ ] RLS policies updated (if access control changed)
- [ ] Observability updated (alerts/runbooks/metrics as needed)
- [ ] N/A - No ops impact

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
