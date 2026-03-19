---
name: search
description: Search, filter, group, compare, and save favorite searches across all Odoo views.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# search — Odoo 19.0 Skill Reference

## Overview

Odoo provides a universal search, filter, and group-by system available at the top of every view. Users can type values to search fields, apply preconfigured or custom filters, group records by dimensions, compare time periods, and save complex searches as favorites for reuse. The search bar supports AND/OR logic, nested filter rules, and developer-mode domain editing. This functionality is used across all applications by all user roles.

## Key Concepts

- **Search bar**: Text input at the top of every view. Typing a value shows matching field suggestions.
- **Preconfigured filters**: Predefined filter options in the Filters drop-down. Filters within the same group use OR logic; filters across groups use AND logic.
- **Custom filter**: User-defined filter with field, operator, and value. Supports match-all (AND) or match-any (OR) logic, nested rule branches, and domain code editing (developer mode).
- **Group By**: Clusters displayed records by a field dimension. Multiple groups create nested hierarchies. Custom groups use any field on the model.
- **Comparison**: Available on certain reporting views; compares a selected time period to the Previous Period or Previous Year.
- **Favorites**: Saved searches that persist for reuse. Can be set as the default filter for a view, and shared with other users.
- **Domain**: The underlying technical filter expression (developer mode). Format: list of tuples, e.g., `[('stage_id', '=', 'Won')]`.

## Core Workflows

### 1. Search for a specific value

1. Click the search bar and start typing (e.g., a salesperson name).
2. Select the desired field and value from the dropdown suggestions.
3. The filter is applied immediately; multiple search terms stack.

### 2. Apply preconfigured filters

1. Click the dropdown icon in the search bar.
2. Under **Filters**, select one or more predefined options.
3. Same-group filters: records match **any** selected filter (OR).
4. Cross-group filters: records must match **all** groups (AND).

### 3. Create a custom filter

1. Click dropdown > Filters > **Add Custom Filter**.
2. Set matching: **Match all** (AND) or **Match any** (OR) of the following rules.
3. Define rules: Field > Operator > Value.
4. Add more rules with **New Rule**, or add nested branches with the node icon.
5. Optionally toggle **Include archived**.
6. Click **Add**.

### 4. Group records

1. Click dropdown > **Group By** > select a predefined group.
2. Or click **Add Custom Group** > select a field.
3. Multiple groups can be applied; order determines nesting hierarchy.

### 5. Compare time periods

1. Select a time period in Filters (e.g., Order Date > Q2).
2. In the **Comparison** section, select **Previous Period** or **Previous Year**.
3. View displays side-by-side comparison data.

### 6. Save a favorite search

1. Configure desired filters, groups, and search values.
2. Click dropdown > **Save current search**.
3. Enter a **Filter name**.
4. Optionally tick **Default filter** to make it the view's default.
5. Click **Save**.
6. To share: edit the favorite > set **Shared with** to specific users.

### 7. Edit or delete a favorite

1. Click dropdown > **Favorites** > hover over the saved search > click the pencil icon.
2. Modify name, sharing, default, or domain.
3. To archive or delete: click the Actions cog > Archive or Delete.

## Technical Reference

### Filter Rule Structure

```
[Field Name] [Operator] [Value]
```

- **Field Name**: Any field on the model (nested sub-fields accessible via submenu arrows).
- **Operator**: Depends on field type (e.g., `=`, `!=`, `contains`, `is in`, `>`, `<`, `is set`, `is not set`).
- **Value**: Text, number, date, boolean, or selection depending on field and operator.

### Matching Logic

| Mode | Behavior |
|------|----------|
| Match all | AND — all rules must be true |
| Match any | OR — at least one rule must be true |
| Nested branch | Sub-group with its own all/any logic |

### Developer Mode Enhancements

- Reveals technical field names and data types in the custom filter.
- Shows **# Code editor** text area for direct domain editing.
- Favorites editing reveals **Context** and **Sort** fields for group/sort customization.
- All favorites viewable at: Settings > Technical > User-defined Filters.

### Model

| Model | Purpose |
|-------|---------|
| `ir.filters` | Saved searches (favorites) |

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18 vs 19 breaking changes listed in RST source -->

## Common Pitfalls

- **Same-group OR vs. cross-group AND**: Misunderstanding filter combination logic leads to unexpected results. Filters separated by a horizontal line in the menu belong to different groups (AND).
- **Comparison requires time filter**: The Comparison section only appears when a time-period filter is already active.
- **Partial search matches**: Typing a value and selecting the field directly (without picking a specific record) applies a "contains" filter, which may return more results than expected.
- **Default filter overrides**: Setting a favorite as the default replaces the view's built-in default filters for the user.
- **Shared favorites scope**: A favorite shared with specific users appears under a separate "shared" section in their Favorites menu, below personal favorites.
