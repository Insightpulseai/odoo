Analyze and fix GitHub issue: $ARGUMENTS

## Workflow

### Step 1: Gather Context
```bash
gh issue view $ARGUMENTS
```

Read the issue description, comments, and any linked PRs.

### Step 2: Identify Failing Area
- What component is affected?
- What is the expected vs actual behavior?
- Is there a reproduction case?

### Step 3: Research Codebase
- Find the relevant files
- Understand the current implementation
- Identify the root cause

### Step 4: Plan the Fix
- Determine the minimal change needed
- Consider edge cases
- Think about testing

### Step 5: Implement Fix
- Make the code changes
- Update tests if needed
- Update documentation if behavior changed

### Step 6: Verify
```bash
./scripts/repo_health.sh
./scripts/spec_validate.sh
./scripts/ci_local.sh
```

### Step 7: Commit & PR
```bash
git add .
git commit -m "fix(scope): description of fix

Fixes #$ARGUMENTS"
git push -u origin HEAD
```

## Output Format

### Issue Summary
Brief description of the issue.

### Root Cause
What was causing the problem.

### Solution
What changes were made.

### Testing
How the fix was verified.

### Commit Reference
The commit hash and message.
