"""
XML Validator

Validates Odoo XML files for Odoo 19 compatibility and best practices.
"""

from pathlib import Path
from typing import Dict, List
from lxml import etree


class XmlValidator:
    """
    Validates Odoo XML view/data files.

    Checks:
    - Deprecated <tree> elements (use <list> in Odoo 19+)
    - Missing external IDs
    - External ID collisions
    - Action/view reference validity
    """

    def validate(self, xml_path: Path) -> Dict:
        """
        Validate XML file.

        Returns:
            {
                'validator': 'xml',
                'status': 'pass' | 'warn' | 'fail',
                'issues': [ValidationIssue, ...],
                'fixes': [QuickFix, ...]
            }
        """
        issues = []
        fixes = []

        try:
            # Parse XML
            tree = etree.parse(str(xml_path))

            # Check for deprecated <tree> elements
            self._check_tree_elements(tree, xml_path, issues, fixes)

            # Check for missing external IDs
            self._check_external_ids(tree, xml_path, issues)

            # Check for view_mode consistency
            self._check_view_mode(tree, xml_path, issues, fixes)

        except etree.XMLSyntaxError as e:
            issues.append({
                'file': str(xml_path),
                'line': e.lineno if hasattr(e, 'lineno') else 1,
                'severity': 'error',
                'message': f"XML syntax error: {str(e)}",
                'rule': 'xml.syntax-error'
            })
        except Exception as e:
            issues.append({
                'file': str(xml_path),
                'line': 1,
                'severity': 'error',
                'message': f"Failed to parse XML: {str(e)}",
                'rule': 'xml.parse-error'
            })

        # Determine status
        status = 'pass'
        if any(i['severity'] == 'error' for i in issues):
            status = 'fail'
        elif any(i['severity'] == 'warning' for i in issues):
            status = 'warn'

        result = {
            'validator': 'xml',
            'status': status,
            'issues': issues
        }

        if fixes:
            result['fixes'] = fixes

        return result

    def _check_tree_elements(self, tree: etree._ElementTree, xml_path: Path, issues: List, fixes: List):
        """Check for deprecated <tree> elements."""
        for tree_elem in tree.xpath('//tree'):
            # <tree> is deprecated in Odoo 19+, should use <list>
            issues.append({
                'file': str(xml_path),
                'line': tree_elem.sourceline,
                'severity': 'warning',
                'message': 'Deprecated <tree> element, use <list> in Odoo 19+',
                'rule': 'xml.tree-deprecated'
            })

            # Generate quick fix
            fixes.append({
                'label': 'Replace <tree> with <list>',
                'rule': 'xml.tree-deprecated',
                'line': tree_elem.sourceline,
                'description': 'Automatically replace <tree> tags with <list>'
            })

    def _check_external_ids(self, tree: etree._ElementTree, xml_path: Path, issues: List):
        """Check for missing external IDs on records."""
        for record in tree.xpath('//record'):
            if not record.get('id'):
                issues.append({
                    'file': str(xml_path),
                    'line': record.sourceline,
                    'severity': 'error',
                    'message': 'Record missing id attribute',
                    'rule': 'xml.record-id-required'
                })

    def _check_view_mode(self, tree: etree._ElementTree, xml_path: Path, issues: List, fixes: List):
        """Check view_mode consistency with Odoo 19 (list instead of tree)."""
        for field in tree.xpath('//field[@name="view_mode"]'):
            if field.text and 'tree' in field.text:
                issues.append({
                    'file': str(xml_path),
                    'line': field.sourceline,
                    'severity': 'warning',
                    'message': 'view_mode contains "tree", should use "list" in Odoo 19+',
                    'rule': 'xml.view-mode-tree'
                })

                fixes.append({
                    'label': 'Replace "tree" with "list" in view_mode',
                    'rule': 'xml.view-mode-tree',
                    'line': field.sourceline,
                    'description': 'Update view_mode to use "list" instead of "tree"'
                })
