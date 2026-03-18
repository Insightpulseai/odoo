---
description: Scaffold a new IPAI custom module following the standard
---

1. Create the module directory structure.

```bash
mkdir -p addons/ipai_NEW_MODULE/{models,views,security,data,static/description}
```

2. Create the initial Python files.

```bash
touch addons/ipai_NEW_MODULE/{__init__.py,__manifest__.py}
touch addons/ipai_NEW_MODULE/models/__init__.py
```

3. Create the initial Security file.

```bash
echo "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink" > addons/ipai_NEW_MODULE/security/ir.model.access.csv
```

4. Create the Manifest file using the Odoo 19 / IPAI standard template.

```python
{
    "name": "IPAI New Module",
    "version": "19.0.1.0.0",  # Odoo 19 versioning
    "category": "Custom",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
```

5. Follow Odoo 19 ORM and OWL 2.0+ standards as defined in `.agent/rules.md`.
