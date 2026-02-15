# SKILL: dbml_schema

## Intent

Generate Database Markup Language (DBML) files to represent Odoo model relationships. This is useful for schema visualization, documentation, and diffing.

## Inputs

- **models:** List of Odoo models to include (e.g., `['res.partner', 'sale.order']`).
- **module:** Specific module to reverse-engineer.
- **output_file:** Target `.dbml` file path.

## Preconditions

- Must identify core fields (columns) and relationships (One2many, Many2one, Many2many).
- Must use valid DBML syntax (Table, Ref, Enum).

## Procedure

1.  **Extract Schema:** Identify the tables and columns.
    - Map `Many2one` to `Ref: > [table.id]`.
    - Map `One2many` to `Ref: < [table.id]`.
    - Map `Selection` fields to `Enum`.
2.  **Generate DBML:**
    ```dbml
    Table res_partner {
      id integer [pk]
      name varchar
      company_id integer [ref: > res_company.id]
      active boolean
    }
    ```
3.  **Save File:** Write to `docs/evidence/<YYYY-MM-DD>/dbml/<name>.dbml` or specified output.
4.  **Visualize (Optional):** Suggest using `dbdocs.io` or a VS Code extension to view.

## Evidence Outputs

- `*.dbml` file.

## Escalation

- If schema is ambiguous (e.g., dynamic model execution), approximate based on static code analysis.
