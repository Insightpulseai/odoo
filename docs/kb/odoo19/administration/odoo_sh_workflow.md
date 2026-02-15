# Odoo.sh Development Workflow

## 1. Branching Strategy

- **Production (`master`)**: Live database. Protected.
- **Staging**: Replica of production data (sanitized). Used for final testing.
- **Development**: Fresh database with demo data. Used for coding features.

## 2. Creating a Module

### Scaffolding

Use the Odoo CLI to create the standard structure:

```bash
odoo-bin scaffold <module_name> <path/to/addons>
```

### Key Files

- `__manifest__.py`: Module metadata and dependencies.
- `__init__.py`: Python package initialization.
- `models/`: Database schema and logic.
- `views/`: UI definitions (XML).
- `security/ir.model.access.csv`: Access control lists (ACLs).

## 3. Development Cycle

1. **Create Branch**: `git checkout -b feature-xyz master`
2. **Code**: Implement features.
3. **Commit & Push**:
   ```bash
   git add .
   git commit -m "[IMP] module: description"
   git push -u origin feature-xyz
   ```
4. **Test**: Odoo.sh automatically builds the branch. Connect to the build to test.

## 4. Staging & Production

1. **To Staging**: Drag & drop `feature-xyz` onto the Staging branch in Odoo.sh UI (or merge via git).
   - _Triggers a rebuild with production data._
2. **To Production**: Drag & drop the validated Staging branch onto Production.
   - _Merges code and updates the live server._

## 5. External Dependencies

To use external Python libraries (e.g., `unidecode`):

1. Create `requirements.txt` in the repository root.
2. Add the library name (e.g., `unidecode`).
3. **Important**: Increment the module version in `__manifest__.py` to trigger dependency installation on deployment.

## Source Links

- [First Module Guide](https://www.odoo.com/documentation/19.0/administration/odoo_sh/first_module.html)
