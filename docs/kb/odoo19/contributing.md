# Odoo 19 Contributing Guidelines

## Development Workflow

1. **Fork & Clone:** Fork `odoo/odoo` (or `enterprise`).
2. **Branching:**
   - Base: `19.0` (or target version).
   - Name: `19.0-fix-invoices` (Community) or `19.0-fix-invoices-xyz` (Odoo Employees).
3. **Commit:**
   - Clear commit messages (Tag: Title).
   - One logical change per commit (atomic commits).
4. **Pull Request:**
   - Open PR against `odoo/odoo` base `19.0`.
   - Sign CLA (if external).
   - Wait for Runbot (CI) green light.

## Coding Guidelines

### Python

- **Style:** PEP8.
- **Imports:** Grouped by: System, Third-party, Odoo modules.
- **Security:** Avoid SQL injection (use ORM methods), XSS (templates auto-escape).
- **Idiomatics:** Use `mapped()`, `filtered()`, `search_read()` for batch efficiency.

### XML

- **Format:** 4 spaces indentation.
- **IDs:** `model_name_view_type` (e.g., `sale_order_view_form`).
- **Inheritance:** Use unique `priority` if needed.

### Javascript (Owl)

- **Modularity:** ES6 Modules.
- **Static Files:** `static/src/components/...`
- **Conventions:** Use `setup()` hook, avoid side-effects in constructors.

### CSS / SCSS

- **Naming:** BEM-like (Block Element Modifier) encouraged.
- **Variables:** Use standard Odoo Bootstrap variables.

## Documentation

- **Format:** reStructuredText (RST).
- **Workflow:** "Edit on GitHub" -> Fork -> Edit -> PR.
- **Preview:** Use the "Preview" button on GitHub (limited) or build locally with Sphinx.

## Source Links

- [Development Workflow](https://www.odoo.com/documentation/19.0/contributing/development.html)
- [Coding Guidelines](https://www.odoo.com/documentation/19.0/contributing/development/coding_guidelines.html)
- [Documentation Guide](https://www.odoo.com/documentation/19.0/contributing/documentation.html)
