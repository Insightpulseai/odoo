# Jinja2 Templating Basics

A practical guide to Jinja2 templating with examples from this codebase.

## What is Jinja2?

Jinja2 is a **templating engine for Python** - a way to mix variables and logic into text files (HTML, XML, Python code, configs) and render them into final output.

```
Template + Data = Rendered Output
```

## Quick Reference

| Syntax | Purpose | Example |
|--------|---------|---------|
| `{{ var }}` | Output variable | `{{ user.name }}` |
| `{% ... %}` | Logic/control | `{% for item in list %}` |
| `{# ... #}` | Comments | `{# ignored #}` |
| `\|` | Filters | `{{ name\|upper }}` |

## Core Concepts

### 1. Variable Interpolation (`{{ }}`)

Insert Python values into templates:

```jinja2
Hello, {{ name }}!
Project: {{ project.title }}
Count: {{ items|length }}
```

### 2. Control Structures (`{% %}`)

**Conditionals:**
```jinja2
{% if user.is_admin %}
  Admin Panel
{% elif user.is_member %}
  Member Dashboard
{% else %}
  Guest View
{% endif %}
```

**Loops:**
```jinja2
{% for task in tasks %}
  - {{ task.name }}: {{ task.status }}
{% endfor %}
```

**Loop variables:**
```jinja2
{% for item in items %}
  {{ loop.index }}. {{ item }}  {# 1-indexed #}
  {{ loop.index0 }}             {# 0-indexed #}
  {{ loop.first }}              {# True if first #}
  {{ loop.last }}               {# True if last #}
{% endfor %}
```

### 3. Filters

Transform values inline:

```jinja2
{{ name|upper }}              {# UPPERCASE #}
{{ name|lower }}              {# lowercase #}
{{ name|title }}              {# Title Case #}
{{ name|replace('_', '-') }}  {# Replace chars #}
{{ items|length }}            {# Count items #}
{{ value|default('N/A') }}    {# Fallback value #}
{{ text|truncate(50) }}       {# Limit length #}
{{ list|join(', ') }}         {# Join list items #}
```

### 4. Whitespace Control

Use `-` to strip whitespace:

```jinja2
{% for item in items -%}
  {{ item }}
{%- endfor %}
```

## Real Examples from This Codebase

### Example 1: Odoo Module Manifest

From `tools/ipai_module_gen/ipai_module_gen/templates/manifest.py.j2`:

```jinja2
{
    "name": "{{ summary }}",
    "version": "{{ odoo_series }}.1.0.0",
    "depends": [
        {% for dep in depends %}
        "{{ dep }}",
        {% endfor %}
    ],
}
```

**Context passed:**
```python
ctx = {
    "summary": "Advanced Financial Closing",
    "odoo_series": "18.0",
    "depends": ["account", "mail", "project"]
}
```

**Rendered output:**
```python
{
    "name": "Advanced Financial Closing",
    "version": "18.0.1.0.0",
    "depends": [
        "account",
        "mail",
        "project",
    ],
}
```

### Example 2: Python Model Class

From `tools/ipai_module_gen/ipai_module_gen/templates/model.py.j2`:

```jinja2
class {{ py_name | title | replace('_', '') }}(models.Model):
    _name = "{{ model.name }}"
    _description = "{{ model.description | default(model.name) }}"
```

**Context:**
```python
{
    "py_name": "close_cycle",
    "model": {
        "name": "ipai.finance.close_cycle",
        "description": "Close cycle (month-end) header"
    }
}
```

**Output:**
```python
class CloseCycle(models.Model):
    _name = "ipai.finance.close_cycle"
    _description = "Close cycle (month-end) header"
```

### Example 3: Conditional Content

```jinja2
{% if sap_doc %}
Documentation: {{ sap_doc }}
{% endif %}
```

Only renders if `sap_doc` is truthy.

## Python API

### Basic Usage

```python
from jinja2 import Template

# Simple template
t = Template("Hello, {{ name }}!")
result = t.render(name="World")
print(result)  # Hello, World!
```

### File-Based Templates

```python
from jinja2 import Environment, FileSystemLoader

# Load templates from directory
env = Environment(
    loader=FileSystemLoader("templates/"),
    autoescape=False,
    trim_blocks=True,      # Remove first newline after block
    lstrip_blocks=True     # Strip leading whitespace before blocks
)

# Get and render template
template = env.get_template("manifest.py.j2")
result = template.render(
    summary="My Module",
    odoo_series="18.0",
    depends=["base", "mail"]
)
```

### Environment Options

| Option | Purpose |
|--------|---------|
| `autoescape=True` | Auto-escape HTML (for web templates) |
| `trim_blocks=True` | Remove newline after block tags |
| `lstrip_blocks=True` | Strip whitespace before block tags |
| `undefined=StrictUndefined` | Raise error on undefined variables |

## Common Patterns

### Optional Sections

```jinja2
{% if description %}
## Description
{{ description }}
{% endif %}
```

### List with Separators

```jinja2
{{ items|join(', ') }}
```

Or with custom logic:
```jinja2
{% for item in items %}
{{ item }}{% if not loop.last %}, {% endif %}
{% endfor %}
```

### Default Values

```jinja2
{{ title|default('Untitled') }}
{{ count|default(0) }}
```

### Nested Data

```jinja2
{% for cap in capabilities %}
## {{ cap.title }}
{% for model in cap.odoo.models %}
- {{ model.name }}: {{ model.description }}
{% endfor %}
{% endfor %}
```

## Running the Examples

See the `examples/` subdirectory for runnable Python scripts:

```bash
cd docs/tutorials/jinja2-basics/examples
python 01_basic_template.py
python 02_file_template.py
python 03_filters_loops.py
```

## Related Resources

- **This codebase**: `tools/ipai_module_gen/` - Production Jinja2 templates
- **Jinja2 docs**: https://jinja.palletsprojects.com/
- **Template Designer**: https://jinja.palletsprojects.com/en/3.1.x/templates/

## Key Takeaways

1. **`{{ }}`** for output, **`{% %}`** for logic
2. **Filters** transform values: `{{ x|filter }}`
3. **Context** is a dict passed to `template.render(**ctx)`
4. Use `trim_blocks` and `lstrip_blocks` for clean output
5. Keep templates readable - complex logic belongs in Python
