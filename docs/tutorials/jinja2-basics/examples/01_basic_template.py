#!/usr/bin/env python3
"""
Basic Jinja2 template rendering.

Demonstrates:
- Creating templates from strings
- Variable interpolation
- Basic context passing
"""
from jinja2 import Template

# Simple string template
template = Template("Hello, {{ name }}!")
result = template.render(name="World")
print("Example 1 - Simple variable:")
print(f"  {result}")
print()

# Multiple variables
template = Template("""
Project: {{ project.name }}
Owner: {{ project.owner }}
Status: {{ project.status }}
""".strip())

result = template.render(project={
    "name": "IPAI Finance Module",
    "owner": "Jake",
    "status": "In Progress"
})
print("Example 2 - Nested object:")
print(result)
print()

# Accessing dict keys and list items
template = Template("""
First item: {{ items[0] }}
Config value: {{ config['timeout'] }}
Nested: {{ data.users[0].name }}
""".strip())

result = template.render(
    items=["apple", "banana", "cherry"],
    config={"timeout": 30, "retries": 3},
    data={"users": [{"name": "Alice"}, {"name": "Bob"}]}
)
print("Example 3 - Dict and list access:")
print(result)
