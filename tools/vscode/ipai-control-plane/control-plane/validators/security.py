"""
Security Validator

Validates Odoo security configuration (access rules, record rules).
"""

import csv
from pathlib import Path
from typing import Dict, List, Set
from lxml import etree


class SecurityValidator:
    """
    Validates Odoo security configuration.

    Checks:
    - ir.model.access.csv existence
    - Access rule coverage for all models
    - Record rule (RLS) completeness
    - Empty domain detection
    """

    def validate(self, module_path: Path) -> Dict:
        """
        Validate security for a module.

        Returns:
            {
                'validator': 'security',
                'status': 'pass' | 'warn' | 'fail',
                'issues': [ValidationIssue, ...]
            }
        """
        issues = []

        # Find all models in module
        models = self._find_models(module_path)

        # Check ir.model.access.csv
        access_csv = module_path / 'security' / 'ir.model.access.csv'
        if not access_csv.exists():
            if models:
                issues.append({
                    'file': str(module_path),
                    'severity': 'warning',
                    'message': 'Missing ir.model.access.csv',
                    'rule': 'security.access-csv-missing'
                })
        else:
            self._check_access_coverage(access_csv, models, issues)

        # Check record rules (RLS)
        security_xml = module_path / 'security' / 'security.xml'
        if security_xml.exists():
            self._check_record_rules(security_xml, issues)

        # Determine status
        status = 'pass'
        if any(i['severity'] == 'error' for i in issues):
            status = 'fail'
        elif any(i['severity'] == 'warning' for i in issues):
            status = 'warn'

        return {
            'validator': 'security',
            'status': status,
            'issues': issues
        }

    def _find_models(self, module_path: Path) -> Set[str]:
        """Find all model names defined in module."""
        models = set()

        # Look for models in Python files
        models_dir = module_path / 'models'
        if not models_dir.exists():
            return models

        for py_file in models_dir.glob('*.py'):
            if py_file.name == '__init__.py':
                continue

            try:
                content = py_file.read_text()

                # Simple pattern matching for _name = 'model.name'
                for line in content.split('\n'):
                    if '_name' in line and '=' in line:
                        # Extract model name from line like: _name = 'res.partner'
                        parts = line.split('=')
                        if len(parts) >= 2:
                            model_name = parts[1].strip().strip('"').strip("'")
                            if model_name and '.' in model_name:
                                models.add(model_name)
            except Exception:
                continue

        return models

    def _check_access_coverage(self, access_csv: Path, models: Set[str], issues: List):
        """Check if all models have access rules."""
        access_models = set()

        try:
            with open(access_csv, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'model_id:id' in row:
                        model_ref = row['model_id:id']
                        # Extract model name from reference like 'model_res_partner'
                        if model_ref.startswith('model_'):
                            model_name = model_ref[6:].replace('_', '.')
                            access_models.add(model_name)
        except Exception as e:
            issues.append({
                'file': str(access_csv),
                'severity': 'error',
                'message': f"Failed to parse access CSV: {str(e)}",
                'rule': 'security.access-csv-parse-error'
            })
            return

        # Find models without access rules
        missing_access = models - access_models
        for model in missing_access:
            issues.append({
                'file': str(access_csv),
                'severity': 'error',
                'message': f"No access rule for model: {model}",
                'rule': 'security.model-not-covered'
            })

    def _check_record_rules(self, security_xml: Path, issues: List):
        """Check record rules (RLS) for completeness."""
        try:
            tree = etree.parse(str(security_xml))

            for rule in tree.xpath('//record[@model="ir.rule"]'):
                # Check for domain_force field
                domain = rule.find('.//field[@name="domain_force"]')

                if domain is None:
                    issues.append({
                        'file': str(security_xml),
                        'line': rule.sourceline,
                        'severity': 'warning',
                        'message': 'RLS rule missing domain_force field',
                        'rule': 'security.missing-domain'
                    })
                elif not domain.text or not domain.text.strip():
                    issues.append({
                        'file': str(security_xml),
                        'line': rule.sourceline,
                        'severity': 'warning',
                        'message': 'RLS rule with empty domain',
                        'rule': 'security.empty-domain'
                    })

        except etree.XMLSyntaxError as e:
            issues.append({
                'file': str(security_xml),
                'line': e.lineno if hasattr(e, 'lineno') else 1,
                'severity': 'error',
                'message': f"XML syntax error: {str(e)}",
                'rule': 'security.xml-syntax-error'
            })
        except Exception as e:
            issues.append({
                'file': str(security_xml),
                'severity': 'error',
                'message': f"Failed to parse security XML: {str(e)}",
                'rule': 'security.xml-parse-error'
            })
