# Odoo 19 Assets & Bundles

## Bundles (`__manifest__.py`)

Assets are grouped into bundles defined in the specific `assets` key of the manifest.

```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/scss/styles.scss',
        'my_module/static/src/js/component.js',
        'my_module/static/src/xml/template.xml',
    ],
    'web.assets_frontend': [
        'my_module/static/src/public/**/*',
    ],
    'web.assets_common': [
        ('include', 'web._primary_variables'),
    ],
}
```

## Operations

- **Append:** `'path/to/file'` (Default)
- **Prepend:** `('prepend', 'path/to/file')` (Start of bundle)
- **Before:** `('before', 'target/file', 'path/to/file')`
- **After:** `('after', 'target/file', 'path/to/file')`
- **Remove:** `('remove', 'target/file')`
- **Include:** `('include', 'bundle_name')` (Nest bundles)

## Key Bundles

- `web.assets_common`: Low-level basics (boot.js), shared.
- `web.assets_backend`: Cloud/Backend client.
- `web.assets_frontend`: Public website/portal.
- `web.assets_unit_tests`: JS Tests.

## `ir.asset` (Database Assets)

For dynamic/conditional assets (e.g., Website Builder themes).

- **Model:** `ir.asset`
- **Fields:** `name`, `bundle`, `path`, `directive` (append/prepend/etc.), `target`.

## Source Links

- [Assets](https://www.odoo.com/documentation/19.0/developer/reference/frontend/assets.html)
