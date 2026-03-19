# Examples — odoo-module-scaffolding

## Example 1: New finance module

**Input**: Create module `ipai_finance_ppm` for project profitability management

**Output**:
```
addons/ipai/ipai_finance_ppm/
  __init__.py
  __manifest__.py
  models/
    __init__.py
    project_profitability.py
  security/
    ir.model.access.csv
  views/
    project_profitability_views.xml
    menus.xml
  tests/
    __init__.py
    test_project_profitability.py
  README.rst
```

Manifest excerpt:
```python
{
    'name': 'IPAI Finance PPM',
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Project profitability management for InsightPulse AI',
    'license': 'LGPL-3',
    'depends': ['account', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_profitability_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
}
```

- Manifest validation: PASS
- Dependency check: PASS (no EE deps)

## Example 2: Module name rejected — wrong pattern

**Input**: Create module `finance_ppm`

**Output**:
- Validation: FAIL
- Reason: Module name `finance_ppm` does not match `ipai_<domain>_<feature>` pattern
- Recommendation: Rename to `ipai_finance_ppm`

## Example 3: Enterprise dependency detected

**Input**: Create module `ipai_hr_appraisal_ext` with dependency on `hr_appraisal`

**Output**:
- Dependency check: FAIL (BLOCKER)
- Reason: `hr_appraisal` is an Enterprise-only module
- Recommendation: Use OCA alternative or implement custom logic in CE-only module
