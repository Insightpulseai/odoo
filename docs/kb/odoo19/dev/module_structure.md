# Module Structure: Manifest, Hooks, Dependencies

## What it is

An Odoo module (addon) is a directory containing a manifest and other resources, implementing specific business logic.

## Key concepts

- ****manifest**.py:** Metadata (name, version, dependencies, data files).
- ****init**.py:** Python package initialization.
- **Hooks:** functions run `pre_init`, `post_init`, or `uninstall`.
- **Dependencies:** Odoo installs modules based on the dependency graph in `depends`.

## Implementation patterns

### Manifest Structure

```python
{
    'name': 'My Module',
    'version': '1.0',
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/my_view.xml',
    ],
    'installable': True,
    'application': False,
}
```

## Gotchas

- **Data Order:** The order of files in `data` matters. Dependencies (like views using a newly defined action) must come after definitions.
- **CSV format:** `ir.model.access.csv` is strict.

## References

- [Odoo Module Structure Documentation](https://www.odoo.com/documentation/19.0/developer/reference/backend/module.html)
