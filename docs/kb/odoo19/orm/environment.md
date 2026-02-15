# Odoo 19 ORM: Environment

## Concept

The Environment (`self.env`) stores contextual data: database cursor (`cr`), current user (`uid`, `user`), and context dictionary (`context`). It provides access to the model registry.

## Applies To

- Server Actions
- Automated Actions
- Controller Logic
- Model Methods

## Core Primitives

- `self.env['model.name']`: Access a model registry.
- `self.env.user`: Current user record.
- `self.env.company`: Current active company.
- `self.env.cr`: Database cursor.
- `self.env.context`: Immutable dictionary of metadata (timezone, language, etc.).

## Extension Pattern

**Switching User (Sudo):**

```python
# Run as superuser (admin rights)
self.env['res.partner'].sudo().create(...)

# Run as specific user
self.env['res.partner'].with_user(user_record).create(...)
```

**Modifying Context:**

```python
# Add key to context
records.with_context(tracking_disable=True).write(...)
```

## Common Mistakes

- **Persistent Context Mutation:** The environment is immutable; `with_context` returns a _new_ environment.
- **Sudo Abuse:** Bypassing security rules unnecessarily reveals sensitive data.
- **Raw Cursor Usage:** Avoid `self.env.cr.commit()` inside transactions; let the framework handle it.

## Agent Notes

- `search_count`, `search`, `browse`, `create`, `write`, `unlink` are the CRUD methods accessed via `self.env['model']`.
- `env.ref('xml_id')` is the standard way to get a record by its External ID.

## Source Links

- [ORM API - Environment](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html#environment)
