# Odoo 19 Module Structure

## Manifest (`__manifest__.py`)

The manifest declares a Python package as an Odoo module. It is a dictionary in `__manifest__.py`.

```python
{
    'name': "My Module",
    'version': '1.0',
    'depends': ['base', 'sale'],
    'author': "Author Name",
    'category': 'Uncategorized',
    'description': """
    Long description of module via ReST.
    """,
    # Data files to load (order matters!)
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/data.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
```

## Directory Structure

```
my_module/
├── __init__.py          # Imports models, controllers
├── __manifest__.py      # Metadata
├── models/              # Python models
│   ├── __init__.py
│   └── my_model.py
├── controllers/         # HTTP controllers
│   ├── __init__.py
│   └── main.py
├── views/               # XML views
│   └── views.xml
├── security/            # ACLs and Rules
│   └── ir.model.access.csv
├── data/                # Data records
│   └── data.xml
└── static/              # Web assets
    ├── src/
    │   └── components/
    └── description/     # Module icon
        └── icon.png
```

## Hooks (`__init__.py`)

Hooks allow executing code at specific lifecycle moments. They are defined in `__init__.py` and referenced in the manifest.

**Manifest:**

```python
{
    ...
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
```

**`__init__.py`:**

```python
def pre_init_hook(env):
    """Called before installation."""
    pass

def post_init_hook(env):
    """Called after installation."""
    pass

def uninstall_hook(env):
    """Called after uninstallation."""
    pass
```

## Common Mistakes

- **Order in `data`:** ACLs must be loaded _before_ views that use the model. Dependencies format is `['security/ir.model.access.csv', 'views/views.xml']`.
- **Missing `__init__.py`:** Folder is not a Python package without it.
- **Assets Paths:** Assets are referenced relative to the module root, e.g., `'my_module/static/src/file.js'`.
- **`auto_install` Nuance:** `True` means "install if _all_ dependencies are installed". Use carefully to avoid unexpected installations.

## Source Links

- [Module Manifests](https://www.odoo.com/documentation/19.0/developer/reference/backend/module.html)
