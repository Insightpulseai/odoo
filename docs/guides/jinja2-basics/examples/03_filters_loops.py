#!/usr/bin/env python3
"""
Jinja2 filters and loop controls.

Demonstrates:
- Built-in filters
- Loop variables
- Conditional rendering
- Whitespace control
"""
from jinja2 import Template

# Built-in filters
print("=== Filters ===")
filters_template = Template("""
upper:    {{ name|upper }}
lower:    {{ name|lower }}
title:    {{ name|title }}
length:   {{ items|length }}
first:    {{ items|first }}
last:     {{ items|last }}
join:     {{ items|join(', ') }}
default:  {{ missing|default('N/A') }}
replace:  {{ name|replace('_', '-') }}
""".strip())

result = filters_template.render(
    name="hello_world",
    items=["apple", "banana", "cherry"]
)
print(result)
print()

# Loop variables
print("=== Loop Variables ===")
loop_template = Template("""
{% for item in items %}
{{ loop.index }}. {{ item }} (index0={{ loop.index0 }}, first={{ loop.first }}, last={{ loop.last }})
{% endfor %}
""".strip())

result = loop_template.render(items=["Red", "Green", "Blue"])
print(result)
print()

# Conditionals in loops
print("=== Conditionals ===")
conditional_template = Template("""
{% for task in tasks %}
{% if task.status == 'done' %}
[x] {{ task.name }}
{% elif task.status == 'in_progress' %}
[~] {{ task.name }} (working)
{% else %}
[ ] {{ task.name }}
{% endif %}
{% endfor %}
""".strip())

result = conditional_template.render(tasks=[
    {"name": "Setup database", "status": "done"},
    {"name": "Build API", "status": "in_progress"},
    {"name": "Write tests", "status": "pending"},
    {"name": "Deploy", "status": "pending"}
])
print(result)
print()

# Whitespace control with -
print("=== Whitespace Control ===")
# Without control (extra newlines)
no_control = Template("""Items:
{% for i in items %}
- {{ i }}
{% endfor %}
End""")

# With control (clean output)
with_control = Template("""Items:
{% for i in items -%}
- {{ i }}
{% endfor -%}
End""")

items = ["A", "B", "C"]
print("Without whitespace control:")
print(repr(no_control.render(items=items)))
print()
print("With whitespace control:")
print(repr(with_control.render(items=items)))
