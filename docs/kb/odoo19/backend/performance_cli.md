# Odoo 19 Performance & CLI

## Command Line Interface (CLI)

The `odoo-bin` executable is the entry point for running and managing Odoo.

### Common Commands

- **Run Server:** `odoo-bin -c odoo.conf`
- **Install Module:** `odoo-bin -d <db_name> -i <module_name>`
- **Update Module:** `odoo-bin -d <db_name> -u <module_name>`
- **Scaffold Module:** `odoo-bin scaffold <module_name> <destination_path>`
- **Shell:** `odoo-bin shell -d <db_name>` (Interactive Python shell)
- **Populate:** `odoo-bin populate -d <db_name> --models res.partner,sale.order` (Generate test data)

### Database Management

- **Init:** `odoo-bin db init -d <db_name>`
- **Dump:** `odoo-bin db dump -d <db_name> > dump.zip`
- **Load:** `odoo-bin db load -d <db_name> dump.zip`
- **Neutralize:** `odoo-bin neutralize -d <db_name>` (Disable crons/emails for testing)

### Key Options

- `--dev=all`: Enable all developer features (auto-reload python/xml, debugger).
- `--test-enable`: Run tests after module installation/update.
- `--stop-after-init`: Stop server after loading modules (useful for CI/Tests).

## Performance Guidelines

### Profiling

- **UI:** Enable via the "Bug" icon in the navbar > "Enable Profiling".
- **Python:**
  ```python
  from odoo.tools.profiler import Profiler
  with Profiler(collectors=['sql', 'periodic']):
      self.do_something()
  ```
  Or for tests: `self.profile(collectors=['sql'])`

### Best Practices

1. **Batch Operations:** ALWAYS use batch methods (`create`, `write`, `unlink`) instead of looping.
   - **Bad:** `for r in records: r.write({'a': 1})`
   - **Good:** `records.write({'a': 1})`

2. **Read Group:** Use `read_group` or `_read_group` for aggregations (counts, sums) instead of `search` + `len()`.

3. **Prefetching:** Odoo automatically prefetches fields.
   - Break prefetching if necessary: `records.with_prefetch().name`

4. **Algorithmic Complexity:**
   - Use `set()` for membership tests (`id in set(ids)` is O(1)).
   - Use mapped dictionaries for lookups (`{r.id: r.val for r in records}`).

5. **SQL:**
   - Avoid `browse` inside loops.
   - Use `flush()` judiously; Odoo manages the cache.

## Source Links

- [CLI Reference](https://www.odoo.com/documentation/19.0/developer/reference/cli.html)
- [Performance](https://www.odoo.com/documentation/19.0/developer/reference/backend/performance.html)
