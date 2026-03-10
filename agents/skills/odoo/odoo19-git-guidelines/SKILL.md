---
name: odoo19-git-guidelines
description: Odoo 19 git commit guidelines covering message structure, commit tags, format rules, module naming, and WHY vs WHAT in descriptions
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/contributing/development/git_guidelines.rst"
  extracted: "2026-02-17"
---

# Odoo 19 Git Guidelines

Complete reference for writing Odoo-style git commit messages. Covers commit structure, all official tags, format rules, module naming in commits, and the emphasis on WHY over WHAT in descriptions.

---

## 1. Git Configuration

Before contributing, configure your git identity:

```bash
git config --global user.name "Your Full Name"
git config --global user.email "your.email@example.com"
```

Also add your full name to your GitHub profile.

---

## 2. Commit Message Structure

Every commit message has four parts:

```
[TAG] module: short description (ideally < 50 chars)

Long version of the change description, including the rationale
for the change, or a summary of the feature being introduced.

Please spend a lot more time describing WHY the change is being
done rather than WHAT is being changed. This is usually easy to
grasp by actually reading the diff. WHAT should be explained
only if there are technical choices or decisions involved. In
that case explain WHY this decision was taken.

End the message with references, such as task or bug numbers,
PR numbers, and OPW tickets, following the suggested format:
task-123 (related to task)
Fixes #123  (close related issue on Github)
Closes #123  (close related PR on Github)
opw-123 (related to ticket)
```

### The Four Parts

| Part | Description | Required |
|---|---|---|
| **Tag** | Action type in brackets: `[FIX]`, `[IMP]`, etc. | Yes |
| **Module** | Technical module name | Yes |
| **Short description** | Imperative sentence, < 50 chars | Yes |
| **Long description** | WHY the change is needed | Recommended |

---

## 3. Commit Header Rules

### Format

```
[TAG] module: describe your change in a short sentence
```

### Rules

1. **Length**: Keep the header under ~50 characters for readability
2. **Sentence form**: Must make a valid sentence when concatenated with "if applied, this commit will `<header>`"
3. **Imperative mood**: "prevent", "add", "fix", "remove" -- not "prevents", "added", "fixing"
4. **No generic words**: Never use "bugfix", "improvements", "changes" alone
5. **Module name**: Use the **technical name** (not functional name, which may change)
6. **Multiple modules**: List them, or use `various` for cross-module changes

### Examples of Good Headers

```
[IMP] base: prevent to archive users linked to active partners
[FIX] account: remove frenglish
[ADD] sale_subscription: add recurring invoice module
[REF] models: use parent_path to implement parent_store
```

### Validation Test

"If applied, this commit will..."
- "...prevent to archive users linked to active partners" -- valid
- "...bugfix" -- invalid (not a sentence)
- "...improvements" -- invalid (not descriptive)

---

## 4. All Commit Tags

### [FIX] -- Bug Fix

For fixing bugs. Used primarily in stable versions but also valid for recent bugs in development.

```
[FIX] account: remove frenglish

The button label used "Créer" mixed with English text.
Changed to consistent English labeling.

Closes #22793
Fixes #22769
```

```
[FIX] website: remove unused alert div, fixes look of input-group-btn

Bootstrap's CSS depends on the input-group-btn
element being the first/last child of its parent.
This was not the case because of the invisible
and useless alert.
```

```
[FIX] sale: correct tax computation on discount lines

When a discount line was added to a sale order, the tax
was computed on the original price instead of the discounted
price. This caused incorrect invoice amounts.

Fixes #45678
```

### [IMP] -- Improvement

For incremental improvements. Most changes in the development version use this tag.

```
[IMP] base: prevent archiving users linked to active partners

Users linked to active partners should not be archived
to avoid orphaned partner records and broken email
routing.

task-12345
```

```
[IMP] sale: add batch confirmation for sale orders

Allow users to confirm multiple draft sale orders at once
from the list view. This reduces manual work for high-volume
sales teams processing many small orders.
```

```
[IMP] mail: improve notification grouping performance

Batch notification creation to reduce the number of SQL
queries from O(n) to O(1) when sending mass notifications.

task-67890
```

### [ADD] -- Add New Module

For adding entirely new modules.

```
[ADD] sale_subscription: add recurring invoice module

Introduces the sale_subscription module that handles
recurring billing, subscription management, and automated
invoice generation on configurable schedules.

task-11111
```

```
[ADD] ipai_finance_ppm: add project portfolio management module

Custom module for InsightPulse AI project portfolio
management, including project tracking, resource allocation,
and financial reporting dashboards.
```

### [REM] -- Remove Resources

For removing dead code, views, modules, or other resources.

```
[REM] sale: remove deprecated discount wizard

The discount wizard has been replaced by inline discount
fields on sale order lines since v17. Remove the now
unused wizard model, views, and security rules.
```

```
[REM] base: remove dead code in partner merge

The _merge_notify method was never called after the
refactoring in commit abc123. Remove it to reduce
code complexity.
```

### [REV] -- Revert Commit

For reverting commits that caused issues or are no longer wanted.

```
[REV] sale: revert batch confirmation feature

Reverts commit abc1234. The batch confirmation caused
race conditions when multiple users confirmed overlapping
order sets simultaneously.

This reverts commit abc1234567890.
```

### [MOV] -- Move Files

For moving files. Use `git mv` and do **not** change the content of moved files (Git may lose track of history).

```
[MOV] sale: move discount logic from wizard to model

Move the discount computation from the transient model
wizard/sale_discount.py to models/sale_order.py to make
it reusable across different entry points.
```

```
[MOV] web: reorganize static assets directory structure

Move JavaScript components from static/src/js/widgets/
to static/src/js/components/ to align with the new
OWL component architecture.
```

### [REF] -- Refactoring

For heavy rewrites of existing features.

```
[REF] models: use parent_path to implement parent_store

This replaces the former modified preorder tree traversal
(MPTT) with the fields parent_left/parent_right. The new
parent_path approach is simpler, more maintainable, and
performs better on large hierarchies.
```

```
[REF] account: rewrite bank statement reconciliation

Complete rewrite of the bank reconciliation widget using
OWL components. The previous jQuery-based implementation
had performance issues with large statement batches and
was difficult to extend.

task-22222
```

### [REL] -- Release

For new major or minor stable version releases.

```
[REL] all: release 19.0
```

```
[REL] sale: bump version to 19.0.2.0
```

### [MERGE] -- Merge Commit

For merge commits, used in forward ports of bug fixes and as the main commit for features involving several separated commits.

```
[MERGE] sale: forward port fixes from 18.0 to 19.0

Forward port of bug fixes for sale order tax computation
and discount handling from the 18.0 stable branch.
```

```
[MERGE] account: merge invoice refactoring branch

Merges the multi-commit invoice refactoring that includes
new payment matching logic, improved reconciliation UI,
and updated report templates.
```

### [CLA] -- Contributor License Agreement

For signing the Odoo Individual Contributor License.

```
[CLA] sign the Odoo Individual Contributor License Agreement
```

### [I18N] -- Internationalization

For changes in translation files.

```
[I18N] sale: update French translations

Update fr.po with translations for new fields added
in the batch confirmation feature.
```

```
[I18N] account: add Spanish (Argentina) translations

Initial translation of the account module to es_AR.
```

### [PERF] -- Performance

For performance patches.

```
[PERF] stock: optimize quant reservation query

Replace the sequential Python loop with a single SQL
query for quant reservation. This reduces the average
confirmation time for large sale orders from 12s to 0.8s.

task-33333
```

```
[PERF] mail: batch notification queries

Group notification insertions into batches of 1000
instead of individual inserts. Reduces mail sending
time by 85% for mass mailings.
```

### [CLN] -- Code Cleanup

For general code cleanup that doesn't change behavior.

```
[CLN] sale: remove unused imports and variables

Clean up sale_order.py by removing unused imports
(datetime, json) and dead variables identified by
the linter.
```

```
[CLN] base: standardize docstrings in res_partner

Add missing docstrings and standardize existing ones
to follow the Odoo documentation conventions.
```

### [LINT] -- Linting

For linting passes (formatting, style fixes).

```
[LINT] account: fix PEP8 violations in account_move

Fix line length, whitespace, and import ordering
issues flagged by flake8.
```

```
[LINT] web: fix ESLint warnings in form_view.js

Address unused variable warnings and missing semicolons
in the form view JavaScript module.
```

---

## 5. Tag Quick Reference

| Tag | When to Use | Typical Branch |
|---|---|---|
| `[FIX]` | Bug fix | Stable + development |
| `[IMP]` | Improvement / enhancement | Development |
| `[ADD]` | New module | Development |
| `[REM]` | Remove code/views/modules | Both |
| `[REV]` | Revert a previous commit | Both |
| `[MOV]` | Move files (use git mv) | Both |
| `[REF]` | Heavy rewrite / refactoring | Development |
| `[REL]` | Version release | Stable |
| `[MERGE]` | Merge / forward port | Both |
| `[CLA]` | Sign contributor license | N/A |
| `[I18N]` | Translation changes | Both |
| `[PERF]` | Performance optimization | Both |
| `[CLN]` | Code cleanup (no behavior change) | Development |
| `[LINT]` | Linting / formatting fixes | Development |

---

## 6. Module Naming in Commits

- Always use the **technical** module name (e.g., `sale`, `account_payment`, `website_forum`)
- If modifying **multiple modules**, list them: `sale, purchase: ...`
- If truly cross-module, use `various`: `[IMP] various: update deprecated API calls`
- **Avoid cross-module commits** when possible -- split into separate commits per module

```
# GOOD -- single module
[FIX] sale: correct discount calculation

# GOOD -- two related modules
[FIX] sale, sale_stock: fix delivery date propagation

# OK -- truly cross-module
[REF] various: replace deprecated partner_shipping_id usage

# BAD -- vague
[FIX] fix stuff
```

---

## 7. WHY vs WHAT in Descriptions

The commit body should focus on **WHY** the change is made, not **WHAT** was changed (the diff shows that).

### Good: Explains WHY

```
[FIX] sale: prevent negative quantities on order lines

Users were able to enter negative quantities on sale order
lines, which caused incorrect stock reservations and
accounting entries. The warehouse team reported this as
blocking their daily operations.

Fixes #12345
```

### Bad: Explains WHAT (redundant with diff)

```
[FIX] sale: prevent negative quantities on order lines

Added a constraint on the quantity field to check if it
is greater than zero. Modified the _check_quantity method
to raise a ValidationError.
```

### When to Explain WHAT

Only explain WHAT when there are non-obvious **technical choices**:

```
[REF] account: switch reconciliation from Python to SQL

The Python-based reconciliation was processing records
one by one, causing timeouts on databases with more than
10,000 unreconciled entries.

Switched to a single SQL query using window functions
instead of the ORM loop. This approach was chosen over
batched ORM calls because the reconciliation logic requires
comparing all candidates simultaneously for optimal matching.

task-44444
```

---

## 8. References in Commit Messages

End commit messages with relevant references:

```
task-123     # Related task number
Fixes #123   # Closes related GitHub issue
Closes #123  # Closes related GitHub PR
opw-123      # Related OPW (Odoo Partner Works) ticket
```

Multiple references are fine:

```
[FIX] sale: correct tax rounding on multi-currency orders

Fix the tax rounding issue that occurred when converting
between currencies with different decimal precisions.

task-55555
Fixes #67890
opw-11111
```

---

## 9. Commit Best Practices

### One Logical Change Per Commit

Each commit should represent a single logical change. Do not mix:
- Bug fixes with refactoring
- Multiple unrelated features
- Code changes with formatting fixes

### Separate Modules, Separate Commits

```
# GOOD -- separate commits
[IMP] sale: add batch confirmation button
[IMP] purchase: add batch confirmation button

# BAD -- mixing modules
[IMP] sale, purchase: add batch confirmation button everywhere
```

Exception: when changes are tightly coupled across modules and splitting would break functionality.

### Write for the Future Reader

Someone will read your commit message in 4 decades (or 3 days). Include:
- The purpose of the change
- The business context
- Why this approach was chosen
- References to specifications or tasks

### Spend Time on Messages

You spent hours/days/weeks on the feature. Take 5-10 minutes to write a clear commit message. People will judge your work by these few sentences.

---

## 10. Complete Commit Examples

### Feature Addition

```
[IMP] sale: add order line discount presets

Sales managers frequently need to apply standard discount
percentages (5%, 10%, 15%) to order lines. Currently this
requires manual entry on each line, which is error-prone
and slow for large orders.

Add a discount preset dropdown on sale order lines that
populates the discount field with predefined values. The
presets are configurable in Sales > Configuration > Discount
Presets.

task-77777
```

### Bug Fix with Technical Detail

```
[FIX] stock: resolve deadlock in quant reservation

Under high concurrency (>50 simultaneous confirmations),
the quant reservation process could deadlock because two
transactions would attempt to lock the same quants in
different orders.

The fix orders the quant candidates by ID before locking,
ensuring a consistent lock acquisition order across all
concurrent transactions. The NOWAIT approach was considered
but rejected because it would require retry logic that
complicates the calling code.

Fixes #89012
opw-22222
```

### Refactoring

```
[REF] mail: rewrite composer as OWL component

The mail composer widget was one of the last major jQuery
widgets in the mail module. It was difficult to maintain
and extend due to complex state management spread across
multiple event handlers.

Rewrite as an OWL component with centralized state
management. The component API remains backwards-compatible
to avoid breaking existing extensions.

task-99999
```

### Cleanup

```
[CLN] account: remove compatibility code for v16 migration

The v16-to-v17 migration helpers in account_move.py have
been in place for two major versions and are no longer
needed. All databases have been migrated past v17.
Removing them reduces the module's code surface by ~200
lines.
```

### Revert

```
[REV] website: revert lazy loading of page images

Reverts commit def4567890. The lazy loading implementation
caused a layout shift that degraded the Largest Contentful
Paint (LCP) score on product pages, negatively impacting
SEO rankings.

A new implementation with proper placeholder sizing will
be submitted separately.

This reverts commit def4567890123.
task-11112
```
