# Coding Guidelines: Python, JS

## What it is

Standards for writing clean, maintainable Odoo code.

## Key concepts

- **Python:** Follow PEP8 (mostly). Meaningful variable names.
- **Javascript:** Use ESLint.
- **XML:** Proper indentation.

## Patterns

- **Do:** Use `_` for unused variables.
- **Don't:** Access `self.env` inside loops (performance killer).
- **Naming:** `res.partner` -> `ResPartner`.

## References

- [Odoo Coding Guidelines](https://www.odoo.com/documentation/19.0/contributing/coding_guidelines.html)
