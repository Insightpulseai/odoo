"""
Manifest Validator

Validates __manifest__.py files for OCA compliance and IPAI standards.
"""

import ast
from pathlib import Path
from typing import Dict, List


class ManifestValidator:
    """
    Validates Odoo __manifest__.py files.

    Checks:
    - Required keys (name, version, depends, data, installable)
    - Dependency existence
    - EE-only module detection
    - Version format
    """

    REQUIRED_KEYS = ['name', 'version', 'depends', 'installable']
    RECOMMENDED_KEYS = ['author', 'license', 'category', 'summary']

    # Known Enterprise-only modules (CE cannot depend on these)
    EE_MODULES = [
        'account_accountant',
        'account_reports',
        'web_studio',
        'sale_subscription',
        'website_studio',
        'mass_mailing_themes',
        'quality_control',
        'mrp_plm',
        'helpdesk',
        'approvals'
    ]

    def validate(self, manifest_path: Path) -> Dict:
        """
        Validate manifest file.

        Returns:
            {
                'validator': 'manifest',
                'status': 'pass' | 'warn' | 'fail',
                'issues': [ValidationIssue, ...]
            }
        """
        issues = []

        try:
            # Parse manifest
            manifest = self._parse_manifest(manifest_path)

            # Check required keys
            for key in self.REQUIRED_KEYS:
                if key not in manifest:
                    issues.append({
                        'file': str(manifest_path),
                        'line': 1,
                        'severity': 'error',
                        'message': f"Missing required key: {key}",
                        'rule': 'manifest.required-keys'
                    })

            # Check recommended keys
            for key in self.RECOMMENDED_KEYS:
                if key not in manifest:
                    issues.append({
                        'file': str(manifest_path),
                        'line': 1,
                        'severity': 'warning',
                        'message': f"Missing recommended key: {key}",
                        'rule': 'manifest.recommended-keys'
                    })

            # Check dependencies
            if 'depends' in manifest:
                self._check_dependencies(manifest, manifest_path, issues)

            # Check version format
            if 'version' in manifest:
                self._check_version_format(manifest['version'], manifest_path, issues)

            # Check installable
            if 'installable' in manifest and not manifest['installable']:
                issues.append({
                    'file': str(manifest_path),
                    'line': 1,
                    'severity': 'warning',
                    'message': 'Module marked as non-installable',
                    'rule': 'manifest.installable-false'
                })

        except Exception as e:
            issues.append({
                'file': str(manifest_path),
                'line': 1,
                'severity': 'error',
                'message': f"Failed to parse manifest: {str(e)}",
                'rule': 'manifest.parse-error'
            })

        # Determine status
        status = 'pass'
        if any(i['severity'] == 'error' for i in issues):
            status = 'fail'
        elif any(i['severity'] == 'warning' for i in issues):
            status = 'warn'

        return {
            'validator': 'manifest',
            'status': status,
            'issues': issues
        }

    def _parse_manifest(self, manifest_path: Path) -> Dict:
        """Parse __manifest__.py as Python dict."""
        content = manifest_path.read_text()

        # Parse as Python AST
        tree = ast.parse(content)

        # Find the dict assignment
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                # Convert AST dict to Python dict
                return ast.literal_eval(ast.unparse(node))

        return {}

    def _check_dependencies(self, manifest: Dict, manifest_path: Path, issues: List):
        """Check dependency validity."""
        depends = manifest.get('depends', [])

        if not isinstance(depends, list):
            issues.append({
                'file': str(manifest_path),
                'severity': 'error',
                'message': 'depends must be a list',
                'rule': 'manifest.depends-type'
            })
            return

        # Check for EE-only dependencies
        ee_deps = [d for d in depends if d in self.EE_MODULES]
        if ee_deps:
            issues.append({
                'file': str(manifest_path),
                'severity': 'error',
                'message': f"Enterprise-only dependencies detected: {', '.join(ee_deps)}",
                'rule': 'manifest.no-ee-deps'
            })

        # TODO: Check if dependencies exist in addons path
        # This requires knowing the project structure

    def _check_version_format(self, version: str, manifest_path: Path, issues: List):
        """Check version format (should be X.Y.Z.W or X.Y)."""
        if not isinstance(version, str):
            issues.append({
                'file': str(manifest_path),
                'severity': 'error',
                'message': 'version must be a string',
                'rule': 'manifest.version-type'
            })
            return

        parts = version.split('.')
        if len(parts) < 2:
            issues.append({
                'file': str(manifest_path),
                'severity': 'error',
                'message': f"Invalid version format: {version} (expected X.Y or X.Y.Z.W)",
                'rule': 'manifest.version-format'
            })
