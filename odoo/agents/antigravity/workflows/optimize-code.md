---
description: Refactor and optimize code with performance benchmarks and proof
---

# Refactor & Optimize

## Goal

Improve performance and maintainability with measurable proof (benchmarks, tests, diffs).

## Steps

### 1. Identify Hotspots

Analyze code for performance and maintainability issues:

**Performance**:

- Nested loops (O(n²) or worse)
- Repeated database calls (N+1 queries)
- Unnecessary serialization/deserialization
- Large memory allocations
- Inefficient algorithms

**Maintainability**:

- Code duplication (DRY violations)
- Long functions (>50 lines)
- Deep nesting (>3 levels)
- Unclear naming
- Missing abstractions

### 2. Propose Plan (Before Changing Code)

Create a plan artifact with:

- What will be refactored
- Why (performance gain or maintainability improvement)
- Approach (algorithm change, caching, batching, etc.)
- Expected impact (2x faster, 50% less code, etc.)
- Risks (behavior changes, edge cases)

### 3. Apply Minimal Safe Refactor

Make the smallest change that achieves the goal:

- Extract functions/methods
- Replace algorithms
- Add caching
- Batch operations
- Optimize queries

**Preserve behavior** - refactoring should not change functionality.

### 4. Add/Adjust Tests

- Lock in existing behavior with tests
- Add performance regression tests if applicable
- Ensure edge cases are covered

### 5. Provide Evidence

#### Diff Summary

```bash
git diff --stat
# 3 files changed, 45 insertions(+), 87 deletions(-)
```

#### Benchmark (if relevant)

```bash
# Before
time python script.py
# real    0m12.456s

# After
time python script.py
# real    0m2.134s

# Improvement: 5.8x faster
```

#### Test Output

```bash
pytest -v
# 47 passed, 0 failed

# Performance test
pytest tests/test_performance.py
# test_bulk_insert: 2.1s (was 12.4s)
```

## Output Format

### Plan Artifact

```markdown
## Refactoring Plan: Optimize User Query

### Current Issue

`get_active_users()` makes N+1 queries (1 for users + N for profiles).
For 1000 users, this results in 1001 database queries.

### Proposed Change

Use `prefetch_related('profile')` to fetch all profiles in 2 queries.

### Expected Impact

- Queries: 1001 → 2 (99.8% reduction)
- Response time: ~12s → ~2s (6x faster)

### Risks

- None - Django ORM handles prefetching safely
- Behavior unchanged (same data returned)

### Implementation

1. Add `prefetch_related('profile')` to queryset
2. Add performance regression test
3. Benchmark before/after
```

### Patch

```diff
diff --git a/users/views.py b/users/views.py
index 1234567..abcdefg 100644
--- a/users/views.py
+++ b/users/views.py
@@ -10,7 +10,8 @@ class UserListView(ListView):
     model = User

     def get_queryset(self):
-        return User.objects.filter(is_active=True)
+        return User.objects.filter(is_active=True) \
+                           .prefetch_related('profile')
```

### Verification Commands

```bash
# Run tests
pytest tests/test_users.py -v

# Benchmark
python -m pytest tests/test_performance.py::test_user_query_performance -v

# Check query count (should be 2)
python manage.py shell
>>> from django.test.utils import override_settings
>>> from django.db import connection
>>> from users.views import UserListView
>>> with override_settings(DEBUG=True):
...     view = UserListView()
...     users = list(view.get_queryset())
...     print(f"Queries: {len(connection.queries)}")
# Queries: 2
```

### Results

```
✅ All tests passing (47/47)
✅ Performance test: 2.1s (was 12.4s) - 5.8x improvement
✅ Query count: 2 (was 1001) - 99.8% reduction
✅ Behavior unchanged (same data returned)
```

## Verification

- [ ] Plan created before making changes
- [ ] Minimal, focused refactoring
- [ ] Tests added/updated
- [ ] Benchmark shows improvement
- [ ] No behavior changes (tests prove it)
