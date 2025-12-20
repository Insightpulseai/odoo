# /ship Command

You are preparing a PR-ready package. Your role is to validate the spec-kit, generate PR artifacts, and ensure everything is ready to merge.

## Rules

1. **Spec-kit required**: Block if `spec/<slug>/` is incomplete
2. **Verification required**: Block if `/verify` hasn't passed
3. **Evidence required**: Include what was tested and what passed
4. **Traceability**: Link PR to spec and tasks

## Pre-Ship Checklist

Before generating PR artifacts, verify:

- [ ] All files in `spec/<slug>/` exist (constitution, prd, plan, tasks)
- [ ] No placeholder text (TODO, TBD, etc.) in spec files
- [ ] All tasks in `tasks.md` are marked complete
- [ ] Verification has passed (or user has approved exceptions)
- [ ] No uncommitted changes outside the plan scope

## Workflow

1. Run `python scripts/spec-kit-enforce.py spec/<slug>/`
2. Check task completion status
3. Generate PR description
4. Prepare commit message
5. Output shipping checklist

## Output Format

```markdown
## Ship Checklist

### Spec-Kit Validation
- [x] `constitution.md` - 450 words, no placeholders
- [x] `prd.md` - 1200 words, no placeholders
- [x] `plan.md` - 380 words, no placeholders
- [x] `tasks.md` - 12/12 tasks complete

### Files Changed
- `supabase/functions/expense-policy-check/index.ts`
- `config/expense-policies.yaml`
- `docs/expense-policies.md`
- `spec/expense-per-diem/tasks.md`

---

## PR Description (copy below)

### Summary
Add per diem expense limit validation to the expense policy engine, enabling automatic enforcement of daily spending limits based on travel destination.

### Spec Reference
`spec/expense-per-diem/`

### Changes
- Added `per_diem` rule type to expense policy engine
- Added per diem rate configuration by region
- Updated expense policy documentation

### Verification Evidence
- [x] Unit tests: 42 passed, 0 failed
- [x] Lint: flake8 passed
- [x] Type check: mypy passed
- [x] Pre-commit: all hooks passed

### Tasks Completed
- [x] Add per_diem rule type to policy engine
- [x] Add per diem rates to config
- [x] Write unit tests for per diem validation
- [x] Update documentation

---

## Commit Message (copy below)

```
feat(expense): Add per diem expense limit validation

- Add per_diem rule type to expense policy engine
- Add per diem rate configuration by region
- Include unit tests and documentation

Spec: expense-per-diem
```

---

## Next Steps

1. Stage changes: `git add -A`
2. Commit: `git commit -m "..."`
3. Push: `git push -u origin feature/expense-per-diem`
4. Create PR with the description above
```

## Blocking Conditions

If spec-kit validation fails, output:

```markdown
## Ship Blocked

### Reason
Spec-kit validation failed:
- Missing: `spec/expense-per-diem/constitution.md`
- Placeholder found: `plan.md:45` - "TODO: add rollback strategy"

### Required Actions
1. Create missing spec files
2. Remove placeholder text
3. Run `/ship` again

Use `--allow-missing-spec` to override (not recommended)
```

## CI Classification Note

Based on the files changed, add this note if applicable:

```markdown
### CI Note
This PR only changes docs/spec/infra files. Odoo CI should be skipped via `paths-ignore`.

If Odoo CI runs anyway, update `.github/workflows/*.yml` with:
```yaml
paths-ignore:
  - 'spec/**'
  - 'docs/**'
  - '.continue/**'
```
```
