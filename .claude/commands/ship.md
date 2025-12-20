You are the ORCHESTRATOR agent. Execute a full shipping workflow.

Input: $ARGUMENTS

## Shipping Workflow

### Phase 1: Plan
Invoke the PLANNER role:
- Read specs and understand requirements
- Create a detailed change plan
- Identify risks and verification steps

### Phase 2: Implement
Invoke the IMPLEMENTER role:
- Execute the plan step by step
- Make minimal, focused changes
- Update documentation if needed
- Prepare change summary

### Phase 3: Verify
Invoke the VERIFIER role:
- Run all verification checks
- Fix any failures
- Re-verify until green

### Phase 4: Commit & PR
Prepare a PR-ready summary:

```markdown
## Intent
What problem does this solve?

## Approach
How was it solved?

## Verification Evidence
- [ ] repo_health.sh passes
- [ ] spec_validate.sh passes
- [ ] Python syntax valid
- [ ] Formatting clean
- [ ] Tests pass (if applicable)

## Risks & Rollback
How to revert if issues arise.

## Checklist
- [ ] Code changes complete
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] Commit message follows convention
```

## Commit Convention
```
<type>(<scope>): <description>

<body>
```

Types: feat, fix, refactor, docs, test, chore, style

## Rules
- Each phase must complete before the next
- If verification fails, fix and re-verify
- Do not skip any phase
- Produce a clean, reviewable commit
