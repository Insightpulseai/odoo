---
name: code-review
description: Use when the user asks for a code review, PR review, review comments, or pre-merge verification. Produces structured findings with severity, evidence, and concrete patches + verification commands.
---

# Code Review Skill

## Goal

Perform a high-signal code review that prioritizes correctness, security, performance, maintainability, and testability. Output should be actionable: findings + fixes + commands to verify.

## When to activate

Activate for:

- "review this PR / diff / branch"
- "do a code review"
- "pre-merge check"
- "find bugs / edge cases in this code"
- "review for security/perf/regressions"
- "check this module/component"

Do NOT activate for:

- pure copywriting/docs-only requests (unless user asks to review docs quality)
- brainstorming without code
- general questions about code structure

## Inputs you should request (only if missing and truly blocking)

- Diff/PR link OR changed files list
- Test/lint commands used by the repo (if not obvious)

If not provided, infer from repo files (package.json, pyproject.toml, **manifest**.py, etc.) and proceed.

## Review process (always follow)

### 1. Scope the change

- What files changed? What behaviors are affected?
- Identify risk areas: auth, payments, migrations, data integrity, concurrency, perf hot paths.
- For Odoo: check model changes, security rules, views, workflows, data migrations.

### 2. Correctness & edge cases

- Validate input boundaries, null/None, empty lists, timezones, off-by-one, retry semantics.
- Look for undefined behavior or hidden assumptions.
- **Odoo-specific**: Check domain filters, search/read/write patterns, recordset operations, `sudo()` usage.

### 3. Security

- AuthZ/AuthN checks, injection risk, secret handling, SSRF, insecure defaults.
- Ensure least privilege and safe error messages.
- **Odoo-specific**: Verify `ir.rule` (record rules), field-level access, `sudo()` justification, SQL injection in raw queries.

### 4. Reliability

- Idempotency, retries, timeouts, backoff, partial failures.
- Logging/metrics: enough to debug? no sensitive leakage?
- **Odoo-specific**: Transaction handling, `@api.model` vs `@api.multi`, proper use of `ensure_one()`.

### 5. Performance

- O(n^2) loops, repeated DB calls, unnecessary serialization, large payloads.
- Cache correctness (staleness, invalidation), pagination.
- **Odoo-specific**: N+1 queries, missing `prefetch`, inefficient `search()` + loop patterns, computed field dependencies.

### 6. Maintainability

- DRY violations, naming, cohesion, single-responsibility, dead code.
- API boundaries: avoid leaking internals; keep interfaces small.
- **Odoo-specific**: Follow OCA conventions, proper module dependencies, no core modifications.

### 7. Tests

- Are tests present for happy path + edge cases?
- Any missing regression tests? Add them.
- **Odoo-specific**: Test with different user roles, test record rules, test workflows end-to-end.

## Severity scale (use these labels)

- **BLOCKER**: likely bug/data loss/security flaw; must fix before merge
- **MAJOR**: correctness/perf/reliability risk; fix strongly recommended
- **MINOR**: maintainability/clarity; fix when convenient
- **NIT**: style/consistency; optional

## Output format (strict)

### Summary

- 1–3 bullets: what changed + overall risk

### Findings

For each finding:

- **[SEVERITY] Title**
- Evidence: file:path + line(s) or code snippet
- Impact: what can go wrong
- Fix: exact patch suggestion (or a minimal diff)
- Verify: exact commands to run

### Patchset (optional)

If multiple edits are required, propose an ordered patchset with filenames and changes.

### Verification commands

Provide copy-paste blocks:

1. apply (if edits are produced)
2. test/lint
3. run minimal repro
4. production/sandbox validation steps (logs/health endpoints)

## Review depth options

### Quick review (default)

- Focus on BLOCKER and MAJOR issues
- 3–6 findings max
- Prioritize correctness and security

### Deep security review

- Exhaustive security analysis
- Check all auth/authz paths
- Review all user inputs and outputs
- Verify secret handling and encryption
- Check for OWASP Top 10 vulnerabilities

### Performance review

- Profile hot paths
- Identify N+1 queries
- Check caching strategies
- Review database indexes
- Analyze memory usage patterns

### OCA compliance review

- Verify OCA coding standards
- Check module structure and dependencies
- Review documentation completeness
- Validate translation support
- Ensure no Enterprise dependencies

## Odoo-specific checklist

### Model changes

- [ ] Proper field types and constraints
- [ ] Computed fields have correct dependencies
- [ ] `store=True` is justified
- [ ] Proper use of `related` vs `compute`
- [ ] No SQL injection in `_where` clauses

### Security

- [ ] Record rules (`ir.rule`) are defined
- [ ] Field-level access controls are set
- [ ] `sudo()` usage is justified and documented
- [ ] No sensitive data in logs

### Views

- [ ] Proper view inheritance (no `replace` without justification)
- [ ] Correct use of `groups` attribute
- [ ] No hardcoded IDs (use `ref()`)
- [ ] Responsive design considerations

### Performance

- [ ] No N+1 queries (use `prefetch` or `read_group`)
- [ ] Batch operations where possible
- [ ] Proper indexing on frequently searched fields
- [ ] Avoid `search()` + loop (use `search_read` or `read_group`)

### Data migrations

- [ ] Idempotent (can run multiple times)
- [ ] Handles missing data gracefully
- [ ] Tested on realistic dataset
- [ ] Rollback plan documented

## Examples (few-shot)

**Example request:** "Review this function for edge cases."

**Example response:**

````
### Summary
- Function `calculate_discount` modified to handle bulk orders
- Risk: MAJOR - potential division by zero and missing null checks

### Findings

**[BLOCKER] Division by zero in discount calculation**
- Evidence: `models/sale_order.py:45`
  ```python
  discount = total_amount / order_count
````

- Impact: Crashes when `order_count` is 0
- Fix:
  ```python
  if not order_count:
      return 0.0
  discount = total_amount / order_count
  ```
- Verify: `python -m pytest tests/test_sale_order.py::test_empty_order_discount`

**[MAJOR] Missing null check for partner**

- Evidence: `models/sale_order.py:52`
- Impact: AttributeError when partner is not set
- Fix: Add `if not self.partner_id: return False`
- Verify: Add test case with missing partner

### Verification commands

```bash
# Run tests
python -m pytest tests/test_sale_order.py -v

# Check for similar patterns
ruff check addons/sale_custom/models/

# Manual verification
# 1. Create order with 0 items
# 2. Create order without partner
# 3. Verify no crashes
```

````

## Scripts available

You can invoke the verification script:
```bash
.agent/skills/code-review/scripts/review_verify.sh
````

This runs repo-detected linters and tests automatically.

## Notes

- Always provide concrete, actionable feedback
- Include line numbers and file paths
- Suggest fixes, don't just point out problems
- Prioritize by severity
- Keep findings concise but complete
- Test suggestions should be copy-pasteable
