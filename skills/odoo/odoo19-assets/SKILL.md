---
name: odoo19-assets
description: Odoo 19 asset management — bundles, loading order, operations (append/prepend/before/after/include/remove/replace), lazy loading, ir.asset model
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/frontend/assets.rst"
  extracted: "2026-02-17"
---

# Odoo 19 Assets

## Overview

Odoo's asset management system handles **JavaScript**, **CSS/SCSS**, and **XML templates** for the web client, website, point of sale, and mobile app. Assets are grouped into **bundles** -- named collections of files declared in module manifests.

Key characteristics:
- Assets are processed (transpiled, compiled SCSS, minified) and concatenated
- Results are saved as file attachments with checksum-based cache URLs
- Different bundles serve different parts of the application
- Lazy loading is supported for on-demand assets

---

## Asset Types

### Code (JavaScript)

Odoo supports three kinds of JavaScript files. All are:
1. Processed (native JS modules transformed into Odoo modules)
2. Minified (unless `debug=assets` mode is active)
3. Concatenated into a single file attachment
4. Loaded via `<script>` tag in `<head>`

### Style (CSS/SCSS)

Both CSS and SCSS files are:
1. Processed (SCSS compiled to CSS)
2. Minified (unless `debug=assets` mode)
3. Concatenated into a single file attachment
4. Loaded via `<link>` tag in `<head>`

### Template (XML)

Static XML template files are:
1. Read from the filesystem on demand
2. Concatenated (not compiled/minified)
3. Fetched by the browser via the `/web/webclient/qweb/` controller

---

## Bundles

### Definition

Bundles are defined in each module's `__manifest__.py` under the `assets` key. The key maps bundle names to lists of file paths (supporting glob patterns):

```python
# In __manifest__.py
{
    'name': 'My Module',
    # ...
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/xml/**/*',
        ],
        'web.assets_common': [
            'my_module/static/lib/bootstrap/**/*',
            'my_module/static/src/js/boot.js',
            'my_module/static/src/js/webclient.js',
            'my_module/static/src/xml/webclient.xml',
        ],
        'web.assets_unit_tests': [
            'my_module/static/src/js/webclient.test.js',
        ],
    },
}
```

File paths support `glob` syntax -- a single line can declare multiple files.

### Standard Bundles

| Bundle | Description |
|--------|-------------|
| `web.assets_common` | Shared across web client, website, and POS. Contains lower-level framework building blocks including `boot.js` (the Odoo module system) |
| `web.assets_backend` | Web client specific code: action manager, views, static XML templates |
| `web.assets_frontend` | Public website specific: ecommerce, portal, forum, blog |
| `web.assets_unit_tests` | JavaScript unit testing: tests, helpers, mocks |

### Caching

Each asset bundle generates a checksum injected into the page source. This checksum is appended to the URL, enabling aggressive browser cache headers. The browser only re-fetches when the checksum changes.

---

## Bundle Operations

Operations control how files are added to or modified within a bundle. Most of the time, simple appending suffices. For precise control, use the tuple-based directive syntax.

### append (Default)

Add files at the end of the bundle. The most common operation -- just use the file path:

```python
'web.assets_common': [
    'my_addon/static/src/js/**/*',
],
```

A simple string in the list appends matching files. Glob patterns expand to multiple files. A single file path works too.

### prepend

Add files at the **beginning** of the bundle. Useful for CSS files that must load first:

```python
'web.assets_common': [
    ('prepend', 'my_addon/static/src/css/bootstrap_overridden.scss'),
],
```

### before

Add files **before** a specific target file:

```python
'web.assets_common': [
    ('before', 'web/static/src/css/bootstrap_overridden.scss',
               'my_addon/static/src/css/bootstrap_overridden.scss'),
],
```

Syntax: `('before', <target_file>, <file_to_add>)`

### after

Add files **after** a specific target file:

```python
'web.assets_common': [
    ('after', 'web/static/src/css/list_view.scss',
              'my_addon/static/src/css/list_view.scss'),
],
```

Syntax: `('after', <target_file>, <file_to_add>)`

### include

Include an entire sub-bundle inside another bundle. Odoo uses sub-bundles (conventionally prefixed with `_`) to share files across multiple bundles:

```python
'web.assets_common': [
    ('include', 'web._primary_variables'),
],
```

Syntax: `('include', <bundle_name>)`

### remove

Remove files from a bundle:

```python
'web.assets_common': [
    ('remove', 'web/static/src/js/boot.js'),
],
```

Syntax: `('remove', <target_file>)`

### replace

Replace a file with one or more replacement files at the **same position**:

```python
'web.assets_common': [
    ('replace', 'web/static/src/js/boot.js',
                'my_addon/static/src/js/boot.js'),
],
```

Syntax: `('replace', <target_file>, <replacement_file>)`

### Operation Summary Table

| Operation | Syntax | Description |
|-----------|--------|-------------|
| `append` | `'path/to/file'` | Add at end (default) |
| `prepend` | `('prepend', 'path')` | Add at beginning |
| `before` | `('before', 'target', 'path')` | Add before target |
| `after` | `('after', 'target', 'path')` | Add after target |
| `include` | `('include', 'bundle_name')` | Include sub-bundle |
| `remove` | `('remove', 'target')` | Remove target file |
| `replace` | `('replace', 'target', 'path')` | Replace target with new file |

**Important**: `before`, `after`, `replace`, and `remove` require the target file to be already declared -- either in manifests of modules higher in the dependency chain or in `ir.asset` records with lower sequence.

---

## Loading Order

The asset loading order is deterministic and follows this process:

1. **Bundle requested** (e.g., `t-call-assets="web.assets_common"`) -- an empty asset list is created.

2. **`ir.asset` records with sequence < 16** are fetched, sorted by sequence, and applied first.

3. **Module manifest declarations** are processed in **module dependency order** (e.g., `web` before `website`). If a file already exists in the list, the duplicate is ignored (first occurrence wins).

4. **Remaining `ir.asset` records (sequence >= 16)** are processed and applied.

### Controlling Order Within a Manifest

Since file path uniqueness is guaranteed, you can mention a specific file before a glob that includes it. That file will appear in the list before all others matched by the glob:

```python
'web.assets_common': [
    # jquery.js loads first, then all other jquery files
    'my_addon/static/lib/jquery/jquery.js',
    'my_addon/static/lib/jquery/**/*',
],
```

### Dependency Requirement

A module removing or replacing assets declared by another module **must depend on** that module. Operating on undeclared assets causes an error:

```python
# In __manifest__.py of my_addon (which depends on 'web')
{
    'depends': ['web'],
    'assets': {
        'web.assets_common': [
            ('replace', 'web/static/src/js/boot.js',
                        'my_addon/static/src/js/boot.js'),
        ],
    },
}
```

---

## Lazy Loading

Sometimes assets should only load when needed (e.g., a heavy library used by one feature). Odoo provides helper functions in `@web/core/assets`.

### loadAssets Function

```javascript
import { loadAssets } from "@web/core/assets";

await loadAssets({
    jsLibs: ["/web/static/lib/stacktracejs/stacktrace.js"],
    cssLibs: ["/web/static/lib/some_lib/style.css"],
});
```

**Parameters**:

| Key | Type | Description |
|-----|------|-------------|
| `jsLibs` | `string[]` | URLs of JavaScript files to load |
| `cssLibs` | `string[]` | URLs of CSS files to load |

Returns a `Promise<void>` that resolves when all assets are loaded.

### useAssets Hook

For components that need to load assets during `onWillStart`:

```javascript
import { useAssets } from "@web/core/assets";

class MyComponent extends Component {
    setup() {
        useAssets({
            jsLibs: ["/web/static/lib/chart/chart.js"],
        });
    }
}
```

Internally calls `loadAssets`. The component will wait for assets to load before rendering.

### Lazy Loading Example

```javascript
import { Component } from "@odoo/owl";
import { useAssets } from "@web/core/assets";

class ChartWidget extends Component {
    static template = "myaddon.ChartWidget";

    setup() {
        // Chart.js will be loaded before the component mounts
        useAssets({
            jsLibs: ["/web/static/lib/Chart/Chart.js"],
            cssLibs: ["/web/static/lib/Chart/Chart.css"],
        });
    }

    mounted() {
        // Chart.js is guaranteed to be available here
        const ctx = this.el.querySelector('canvas').getContext('2d');
        new Chart(ctx, this.getChartConfig());
    }
}
```

---

## The ir.asset Model (Database-Driven Assets)

For cases requiring more flexibility than manifest declarations, `ir.asset` records provide dynamic, database-driven asset management.

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | String | | Identifier name for the record |
| `bundle` | String | | Target bundle name |
| `directive` | Selection | `"append"` | Operation type |
| `path` | String | | File path, glob pattern, URL, or bundle name |
| `target` | String | | Target file (for `replace`, `before`, `after`) |
| `active` | Boolean | `True` | Whether the record is active |
| `sequence` | Integer | `16` | Loading order (ascending). Sequence < 16 processes before manifest assets |

### Available Directives

| Directive | Required Fields | Description |
|-----------|----------------|-------------|
| `append` | `path` | Add file(s) at end of bundle |
| `prepend` | `path` | Add file(s) at start of bundle |
| `before` | `target`, `path` | Add before target |
| `after` | `target`, `path` | Add after target |
| `include` | `path` (= bundle name) | Include another bundle |
| `remove` | `path` (= target to remove) | Remove a file |
| `replace` | `target`, `path` | Replace target with path |

### XML Record Definition

Standard `<record>` syntax:

```xml
<record id="my_asset_record" model="ir.asset">
    <field name="name">My Custom Asset</field>
    <field name="bundle">web.assets_backend</field>
    <field name="directive">append</field>
    <field name="path">my_addon/static/src/js/custom.js</field>
</record>
```

### Asset Tag Syntax (Preferred for Website)

For website-related applications with conditional assets, use the `<asset>` tag:

```xml
<asset id="my_conditional_asset">
    <field name="name">Conditional Style</field>
    <field name="bundle">web.assets_frontend</field>
    <field name="directive">append</field>
    <field name="path">my_addon/static/src/css/custom_theme.scss</field>
    <field name="active" eval="False"/>
</asset>
```

The `<asset>` syntax is preferred over `<record>` for website use cases because it properly handles the `active` field for conditional activation (e.g., when a theme option is enabled).

### Sequence Control

- **sequence < 16**: Processed BEFORE module manifest assets
- **sequence >= 16** (default): Processed AFTER module manifest assets

```xml
<!-- Load this asset before everything in the manifest -->
<record id="my_early_asset" model="ir.asset">
    <field name="name">Early Bootstrap Override</field>
    <field name="bundle">web.assets_common</field>
    <field name="directive">prepend</field>
    <field name="path">my_addon/static/src/css/early_override.scss</field>
    <field name="sequence">5</field>
</record>
```

---

## Complete Manifest Examples

### Basic Module with Backend Assets

```python
{
    'name': 'My Backend Module',
    'depends': ['web'],
    'assets': {
        'web.assets_backend': [
            # JavaScript
            'my_module/static/src/js/**/*.js',
            # Styles
            'my_module/static/src/css/**/*.scss',
            # Templates
            'my_module/static/src/xml/**/*.xml',
        ],
    },
}
```

### Module with Multiple Bundle Targets

```python
{
    'name': 'My Full Module',
    'depends': ['web', 'website'],
    'assets': {
        # Backend assets
        'web.assets_backend': [
            'my_module/static/src/backend/**/*',
        ],
        # Frontend/website assets
        'web.assets_frontend': [
            'my_module/static/src/frontend/**/*',
        ],
        # Shared/common assets
        'web.assets_common': [
            'my_module/static/src/common/**/*',
        ],
        # Test assets
        'web.assets_unit_tests': [
            'my_module/static/tests/**/*',
        ],
    },
}
```

### Module with Advanced Operations

```python
{
    'name': 'My Advanced Module',
    'depends': ['web', 'sale'],
    'assets': {
        'web.assets_backend': [
            # Standard append
            'my_module/static/src/js/main.js',
            'my_module/static/src/xml/templates.xml',

            # Load a specific file first, then the rest via glob
            'my_module/static/src/js/core/init.js',
            'my_module/static/src/js/core/**/*.js',

            # Add SCSS before a specific file
            ('before', 'web/static/src/scss/primary_variables.scss',
                       'my_module/static/src/scss/variables.scss'),

            # Add JS after a specific file
            ('after', 'web/static/src/js/core/registry.js',
                      'my_module/static/src/js/registry_extensions.js'),

            # Replace a file entirely
            ('replace', 'sale/static/src/js/sale_order.js',
                        'my_module/static/src/js/sale_order_custom.js'),

            # Remove an unwanted file
            ('remove', 'sale/static/src/js/deprecated_feature.js'),

            # Include a sub-bundle
            ('include', 'my_module._shared_components'),
        ],

        # Define a sub-bundle (convention: underscore prefix)
        'my_module._shared_components': [
            'my_module/static/src/js/shared/**/*',
            'my_module/static/src/xml/shared/**/*',
        ],

        # Prepend critical CSS
        'web.assets_common': [
            ('prepend', 'my_module/static/src/scss/critical.scss'),
        ],
    },
}
```

### Website Module with Conditional Assets

```python
{
    'name': 'My Website Theme',
    'depends': ['website'],
    'assets': {
        'web.assets_frontend': [
            'my_theme/static/src/scss/theme.scss',
            'my_theme/static/src/js/animations.js',
        ],
    },
}
```

With conditional `ir.asset` in XML data:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Always active -->
    <record id="asset_theme_base" model="ir.asset">
        <field name="name">Theme Base Styles</field>
        <field name="bundle">web.assets_frontend</field>
        <field name="path">my_theme/static/src/scss/base.scss</field>
    </record>

    <!-- Conditionally active (e.g., toggled by website option) -->
    <asset id="asset_dark_mode">
        <field name="name">Dark Mode Styles</field>
        <field name="bundle">web.assets_frontend</field>
        <field name="path">my_theme/static/src/scss/dark_mode.scss</field>
        <field name="active" eval="False"/>
    </asset>

    <!-- Replace default styles when active -->
    <asset id="asset_custom_header">
        <field name="name">Custom Header</field>
        <field name="bundle">web.assets_frontend</field>
        <field name="directive">replace</field>
        <field name="target">website/static/src/scss/header.scss</field>
        <field name="path">my_theme/static/src/scss/header.scss</field>
        <field name="active" eval="False"/>
    </asset>
</odoo>
```

---

## Troubleshooting Asset Loading

If a file is not loading or updating:

1. **Verify the file is saved** to disk.
2. **Check the browser console** (F12) for errors.
3. **Add a `console.log()`** at the top of your file to confirm it loads.
4. **Verify the asset bundle** -- ensure the file is in the correct bundle in `__manifest__.py`.
5. **Force asset regeneration**:
   - Restart the server (forces recheck on next request)
   - In debug mode: use the debug menu (bug icon in navbar) to force regeneration
   - Start server with `--dev=xml` to auto-check assets on every request (development only)
6. **Refresh the browser page** -- Odoo has no hot module reloading.

### Debug Modes for Assets

- **`debug=assets`**: Un-minified JS/CSS, source maps generated. Activate via URL parameter or debug menu.
- **`--dev=xml` server flag**: Forces asset bundle freshness check on every request. Use during development.

---

## Quick Reference

### Manifest Asset Declaration

```python
'assets': {
    'bundle.name': [
        'path/to/file.js',                              # append
        'path/to/files/**/*.js',                         # append with glob
        ('prepend', 'path/to/file.css'),                 # prepend
        ('before', 'target/file.js', 'my/file.js'),     # before
        ('after', 'target/file.js', 'my/file.js'),      # after
        ('include', 'other.bundle'),                     # include bundle
        ('remove', 'target/file.js'),                    # remove
        ('replace', 'target/file.js', 'my/file.js'),    # replace
    ],
},
```

### Lazy Loading in Components

```javascript
import { useAssets } from "@web/core/assets";
import { loadAssets } from "@web/core/assets";

// In component setup
useAssets({ jsLibs: ["/path/to/lib.js"] });

// Anywhere async
await loadAssets({ jsLibs: ["/path/to/lib.js"], cssLibs: ["/path/to/lib.css"] });
```

### Bundle Loading in Templates

```xml
<!-- Load a bundle in a QWeb template (typically in base templates) -->
<t t-call-assets="web.assets_common"/>
<t t-call-assets="web.assets_backend"/>
```
