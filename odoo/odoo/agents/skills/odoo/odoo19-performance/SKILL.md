---
name: odoo19-performance
description: Odoo 19 performance profiling, collectors, batch operations, prefetch, indexes, and optimization patterns
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/backend/performance.rst"
  extracted: "2026-02-17"
---

# Odoo 19 Performance

## Overview

Odoo provides integrated profiling tools and established best practices for writing
performant code. This document covers the profiler, collectors, and critical
optimization patterns every Odoo developer should follow.

---

## Profiling

### `odoo.tools.profiler.Profiler`

The profiler records executed queries and stack traces during execution. Results
can be viewed with the integrated speedscope flamegraph viewer or exported to JSON.

### Enable from Python Code

Use the `Profiler` as a context manager to profile specific code sections:

```python
from odoo.tools.profiler import Profiler

with Profiler():
    do_stuff()
```

With specific collectors:

```python
from odoo.tools.profiler import Profiler, PeriodicCollector

with Profiler(collectors=['sql', PeriodicCollector(interval=0.1)]):
    do_stuff()
```

In test classes, use the `self.profile()` shortcut:

```python
with self.profile():
    with self.assertQueryCount(__system__=1211):
        do_stuff()
```

**Important**: Call `self.profile()` **outside** of `assertQueryCount` to catch
queries made when exiting the context manager (e.g., flush).

### Profiler Constructor

```python
Profiler(
    collectors=None,    # List of collector keys or instances
    db=None,            # Database name (defaults to current)
    profile_session=None,  # Session identifier
    description=None,   # Description for the profile record
    disable_gc=False,   # Disable garbage collector during profiling
)
```

### Enable from the UI

1. Enable developer mode
2. Open developer mode tools, toggle "Enable profiling" -- a wizard suggests expiry times
3. Go to Settings > General Settings > Performance to set "Enable profiling until"
4. After enabling globally, toggle profiling for the current session in developer tools
5. Default options: "Record sql" and "Record traces" (recommended)

When enabled, all requests are profiled and saved into `ir.profile` records grouped
by profiling session.

**Note**: Odoo Online databases cannot be profiled.

### ExecutionContext

Use `ExecutionContext` as a context manager to break down results into multiple
frames when a method is called multiple times:

```python
from odoo.tools.profiler import ExecutionContext

for index in range(max_index):
    with ExecutionContext(current_index=index):
        do_stuff()
```

This helps identify each iteration separately in speedscope results.

---

## Collectors

Collectors determine **what** data is collected during profiling. Each collector
can be enabled individually.

### Available Collectors

| Name | Python Key | Python Class | UI Toggle | Thread |
|------|------------|--------------|-----------|--------|
| SQL | `sql` | `SQLCollector` | Record sql | Same |
| Periodic | `traces_async` | `PeriodicCollector` | Record traces | Separate |
| QWeb | `qweb` | `QwebCollector` | Record qweb | Same |
| Sync | `traces_sync` | `SyncCollector` | No | Same |

**Default**: SQL and Periodic collectors are enabled by default.

### SQL Collector (`SQLCollector`)

- Saves all SQL queries made to the database in the current thread
- Records stack traces for each query
- Overhead is added per query, so many small queries may impact execution time
- Useful for debugging query counts
- Key: `'sql'`

```python
with Profiler(collectors=['sql']):
    # All SQL queries in this block are recorded
    records = self.env['res.partner'].search([])
```

### Periodic Collector (`PeriodicCollector`)

- Runs in a **separate thread**
- Saves stack traces of the analyzed thread at regular intervals
- Default interval: 10 ms
- Very low impact on execution time (best for performance analysis)
- Key: `'traces_async'`

```python
from odoo.tools.profiler import Profiler, PeriodicCollector

# Custom interval of 5ms
with Profiler(collectors=[PeriodicCollector(interval=0.005)]):
    do_stuff()
```

**Warning**: Very low intervals on long requests generate memory issues.
Very high intervals lose information on short function executions.

### QWeb Collector (`QwebCollector`)

- Saves Python execution time and queries for all QWeb directives
- Overhead can be significant with many small directives
- Results viewable via custom widget in `ir.profile` form view
- Mainly useful for optimizing views
- Key: `'qweb'`

```python
with Profiler(collectors=['qweb']):
    # Profile QWeb template rendering
    result = self.env['ir.qweb']._render('my_module.my_template', values)
```

### Sync Collector (`SyncCollector`)

- Saves stack for every function call and return
- Runs on the **same thread** -- greatly impacts performance
- Useful for debugging complex flows and understanding execution order
- **Not recommended** for performance analysis due to high overhead
- Key: `'traces_sync'`

```python
with Profiler(collectors=['traces_sync']):
    # Every function call/return is recorded -- very detailed but slow
    complex_workflow()
```

---

## Analysing Results

Profiling results are stored in `ir.profile` records. Access them via developer
mode tools button or Settings > Technical > Profiling.

### Speedscope Views

| View | Description |
|------|-------------|
| Combined | SQL queries and traces merged together |
| Combined no context | Same but ignores execution context |
| sql (no gap) | SQL queries as if executed sequentially (no Python) |
| sql (density) | SQL queries with gaps; spots SQL vs Python bottlenecks |
| frames | Only periodic collector results |

---

## Profiling Pitfalls

- **Randomness**: Multiple executions may produce different results (e.g., garbage collector triggering)
- **Blocking calls**: External `c_call` may hold GIL, causing unexpected long frames with Periodic collector
- **Cache**: Profiling before view/assets are cached gives different results
- **Profiler overhead**: SQL collector overhead is significant with many small queries; disable profiler to measure real impact of code changes
- **Memory**: Long requests or install profiling may exhaust memory. Increase memory limit:

```bash
--limit-memory-hard $((8*1024**3))
```

---

## Good Practices: Batch Operations

### Replace search_count in Loops with _read_group

**Bad** -- one SQL query per record:

```python
def _compute_count(self):
    for record in self:
        domain = [('related_id', '=', record.id)]
        record.count = other_model.search_count(domain)
```

**Good** -- one SQL query for the entire batch:

```python
def _compute_count(self):
    domain = [('related_id', 'in', self.ids)]
    counts_data = other_model._read_group(domain, ['related_id'], ['__count'])
    mapped_data = dict(counts_data)
    for record in self:
        record.count = mapped_data.get(record, 0)
```

### Batch Create Instead of Loop Create

**Bad** -- multiple INSERT statements:

```python
for name in ['foo', 'bar']:
    model.create({'name': name})
```

**Good** -- single batched create:

```python
create_values = []
for name in ['foo', 'bar']:
    create_values.append({'name': name})
records = model.create(create_values)
```

Batched `create()` allows the framework to optimize field computation across
all records at once.

### Browse Entire Recordset for Prefetch

**Bad** -- browsing one record at a time breaks prefetch:

```python
for record_id in record_ids:
    record = model.browse(record_id)
    record.foo  # One query per record
```

**Good** -- browse all at once to enable batch prefetch:

```python
records = model.browse(record_ids)
for record in records:
    record.foo  # One query for the entire recordset
```

You can verify prefetching with the `prefetch_ids` attribute which includes
all record IDs in the batch.

### Custom Prefetch Control with `with_prefetch`

If browsing all records together is impractical, use `with_prefetch` to
control prefetch behavior:

```python
for values in values_list:
    message = self.browse(values['id']).with_prefetch(self.ids)
```

---

## Good Practices: Algorithmic Complexity

### Use Dictionaries to Reduce O(n^2) to O(n)

**Bad** -- nested loops O(n^2):

```python
for record in self:
    for result in results:
        if result['id'] == record.id:
            record.foo = result['foo']
            break
```

**Good** -- dictionary lookup O(n):

```python
mapped_result = {result['id']: result['foo'] for result in results}
for record in self:
    record.foo = mapped_result.get(record.id)
```

### Use Sets for Membership Tests

**Bad** -- `in` on a list is O(n):

```python
invalid_ids = self.search(domain).ids
for record in self:
    if record.id in invalid_ids:  # O(n) per check if ids is a list
        ...
```

**Good** -- `in` on a set is O(1):

```python
invalid_ids = set(self.search(domain).ids)
for record in self:
    if record.id in invalid_ids:  # O(1) per check
        ...
```

**Also good** -- use recordset operations:

```python
invalid_records = self.search(domain)
for record in self - invalid_records:
    ...
```

---

## Good Practices: Database Indexes

Add indexes to fields that are frequently used in search operations:

```python
name = fields.Char(string="Name", index=True)
```

**Warning**: Do not index every field. Indexes:
- Consume disk space
- Slow down `INSERT`, `UPDATE`, and `DELETE` operations
- Only add indexes to fields used frequently in `WHERE` clauses, `JOIN` conditions,
  or `ORDER BY` clauses

### When to Add Indexes

| Scenario | Recommendation |
|----------|---------------|
| Field used in `search()` domains frequently | Add `index=True` |
| Foreign key field (`Many2one`) queried often | Add `index=True` |
| Field rarely queried but frequently written | Do NOT index |
| Boolean field with low cardinality | Usually not worth indexing |
| Field used in record rules (ir.rule) | Consider indexing |

---

## Good Practices: Computed Fields

### Store When Appropriate

Stored computed fields are persisted in the database and only recalculated when
dependencies change. Use them for values that are read frequently but change
infrequently:

```python
total = fields.Float(compute='_compute_total', store=True)

@api.depends('line_ids.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.line_ids.mapped('amount'))
```

### Avoid Heavy Computations in Non-Stored Fields

Non-stored computed fields are recalculated on every read. Keep them lightweight:

```python
# Good: simple computation
display_name = fields.Char(compute='_compute_display_name')

@api.depends('name', 'code')
def _compute_display_name(self):
    for record in self:
        record.display_name = f"[{record.code}] {record.name}"

# Bad: heavy computation in non-stored field
stats = fields.Text(compute='_compute_stats')

def _compute_stats(self):
    for record in self:
        # This runs a complex query every time the field is read!
        record.stats = self._calculate_complex_statistics(record)
```

---

## Good Practices: Recordset Operations

### Use `mapped()` and `filtered()` Efficiently

```python
# Get all partner emails from sale orders
emails = sale_orders.mapped('partner_id.email')

# Filter confirmed orders
confirmed = sale_orders.filtered(lambda o: o.state == 'confirmed')

# Equivalent but more readable:
confirmed = sale_orders.filtered_domain([('state', '=', 'confirmed')])
```

### Avoid Repeated Environment Switches

**Bad** -- switching sudo per record:

```python
for record in records:
    record.sudo().do_something()
```

**Good** -- switch once for the entire recordset:

```python
sudo_records = records.sudo()
for record in sudo_records:
    record.do_something()
```

### Use `with_context` on Recordset, Not Per Record

**Bad**:
```python
for record in records:
    record.with_context(key='value').action()
```

**Good**:
```python
ctx_records = records.with_context(key='value')
for record in ctx_records:
    record.action()
```

---

## Testing Performance: `@warmup` and `@users` Decorators

### `@warmup`

Runs the test method multiple times. First runs are "warmup" (to populate caches),
and only subsequent runs are measured:

```python
from odoo.tests.common import TransactionCase, warmup

class TestPerformance(TransactionCase):

    @warmup
    def test_method_performance(self):
        with self.assertQueryCount(__system__=5):
            self.env['res.partner'].search([('name', 'like', 'test')])
```

### `@users`

Runs the test method with specific users to measure performance under different
access rights:

```python
from odoo.tests.common import TransactionCase, users

class TestPerformance(TransactionCase):

    @users('__system__', 'demo')
    def test_access_performance(self):
        with self.assertQueryCount(__system__=3, demo=5):
            # More queries expected for demo due to access rights checks
            self.env['res.partner'].search([])
```

### Combining `@warmup` and `@users`

```python
@users('__system__', 'demo')
@warmup
def test_combined(self):
    with self.assertQueryCount(__system__=10, demo=15):
        self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })
```

---

## Performance Optimization Checklist

1. **Batch operations**: Use `_read_group` instead of looped `search_count`; batch `create()`
2. **Prefetch**: Browse entire recordsets, not individual IDs
3. **Algorithmic complexity**: Use dicts/sets to avoid O(n^2) patterns
4. **Indexes**: Add `index=True` to frequently searched fields
5. **Stored computed fields**: Use `store=True` for heavy computations read often
6. **Avoid N+1 queries**: Prefetch related fields, use `mapped()` on recordsets
7. **Environment switches**: Apply `sudo()`, `with_context()` once on the recordset
8. **Profile first**: Use the Profiler to identify actual bottlenecks before optimizing
9. **Cache awareness**: Consider caching behavior in views and assets
10. **Query count tests**: Use `assertQueryCount` with `@warmup` / `@users` decorators
