---
description: Draft a professional Pull Request description based on recent changes
---

# PR Description Generator

## Goal

Draft a professional Pull Request description based on recent changes, ready for GitHub/GitLab.

## Steps

### 1. Analyze Changes

Run `git diff --stat` and `git diff` against the target branch (default: main).

```bash
git diff --stat origin/main
git diff origin/main
```

### 2. Infer Intent

From code, comments, and commit messages, determine:

- What changed (files, functions, features)
- Why (problem being solved, feature being added)
- Impact (breaking changes, migrations, performance)

### 3. Draft PR Description

Produce output in Markdown with these sections:

#### What Changed

- Bullet list of changes
- Group by component/module
- Include file counts

#### Why

- Problem statement or feature rationale
- Business value or technical debt addressed
- Links to issues/tickets if applicable

#### Testing

- Exact commands run
- Test results (pass/fail counts)
- Manual testing steps performed

#### Risk Notes (if applicable)

- Database migrations
- Auth/security changes
- Performance implications
- Breaking changes
- Deployment requirements

### 4. Include Metadata

- Related issues: `Fixes #123`, `Closes #456`
- Reviewers: `@username`
- Labels: `bug`, `feature`, `breaking-change`

## Output Format

````markdown
## What Changed

- Added user profile editing feature
- Refactored authentication middleware
- Updated 12 files across 3 modules

## Why

Addresses user feedback requesting profile customization. Previous implementation
was tightly coupled to the registration flow, making it difficult to extend.

Fixes #789

## Testing

```bash
npm test
# All 47 tests passing

npm run e2e
# 12/12 scenarios passing
```
````

Manual testing:

1. Login as test user
2. Navigate to /profile/edit
3. Update name, email, avatar
4. Verify changes persist after logout/login

## Risk Notes

- **Breaking change**: Profile API now requires authentication token
- **Migration**: Run `npm run migrate:profiles` before deploying
- **Performance**: Added database index on `users.email` (may take 2-3 minutes on large DBs)

## Reviewers

@backend-team @security-team

```

## Verification
- [ ] PR description is complete and accurate
- [ ] All test commands are copy-pasteable
- [ ] Risk notes highlight breaking changes
- [ ] Related issues are linked
```
