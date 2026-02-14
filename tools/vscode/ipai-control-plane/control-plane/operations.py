"""
Operations State Manager

Manages operation lifecycle: plan → execute → complete
"""

import uuid
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path


class OperationState:
    """In-memory operation state (production would use database)."""

    def __init__(self):
        self.operations: Dict[str, Dict] = {}

    def create_operation(self, operation_type: str, params: Dict) -> Dict:
        """Create new operation in 'planned' state."""
        op_id = str(uuid.uuid4())

        operation = {
            'op_id': op_id,
            'type': operation_type,
            'status': 'planned',
            'params': params,
            'created_at': datetime.now().isoformat(),
            'diffs': [],
            'checks': [],
            'bundle_id': None
        }

        self.operations[op_id] = operation
        return operation

    def get_operation(self, op_id: str) -> Optional[Dict]:
        """Get operation by ID."""
        return self.operations.get(op_id)

    def update_status(self, op_id: str, status: str, **kwargs):
        """Update operation status and optional fields."""
        if op_id in self.operations:
            self.operations[op_id]['status'] = status
            self.operations[op_id]['updated_at'] = datetime.now().isoformat()

            for key, value in kwargs.items():
                self.operations[op_id][key] = value

    def add_diffs(self, op_id: str, diffs: List[Dict]):
        """Add diffs to operation."""
        if op_id in self.operations:
            self.operations[op_id]['diffs'] = diffs

    def add_checks(self, op_id: str, checks: List[Dict]):
        """Add validation checks to operation."""
        if op_id in self.operations:
            self.operations[op_id]['checks'] = checks


class DiffGenerator:
    """Generate realistic diffs for operations."""

    def generate_install_diffs(self, modules: List[str]) -> List[Dict]:
        """
        Generate diffs for module installation.

        Returns SQL, XML, and Python diffs.
        """
        diffs = []

        # SQL diff (database schema changes)
        sql_statements = []
        for module in modules:
            sql_statements.extend([
                f"-- Module: {module}",
                f"CREATE TABLE IF NOT EXISTS {module.replace('.', '_')}_model (",
                "    id SERIAL PRIMARY KEY,",
                "    create_date TIMESTAMP,",
                "    write_date TIMESTAMP",
                ");",
                ""
            ])

        diffs.append({
            'type': 'sql',
            'path': 'database',
            'summary': f'Schema changes for {len(modules)} module(s)',
            'patch': '\n'.join(sql_statements),
            'safe': True
        })

        # XML diff (views/actions)
        for module in modules:
            xml_diff = f"""<?xml version="1.0"?>
<odoo>
    <record id="{module}_action" model="ir.actions.act_window">
        <field name="name">{module.title()}</field>
        <field name="res_model">{module}.model</field>
        <field name="view_mode">list,form</field>
    </record>

    <menuitem id="{module}_menu"
              name="{module.title()}"
              action="{module}_action"/>
</odoo>"""

            diffs.append({
                'type': 'xml',
                'path': f'addons/{module}/views/views.xml',
                'summary': f'Add views and menus for {module}',
                'patch': xml_diff,
                'safe': True
            })

        return diffs


class ValidationRunner:
    """Run validation checks on operations."""

    def run_checks(self, operation_type: str, params: Dict) -> List[Dict]:
        """
        Run validation checks before operation execution.

        Returns list of check results.
        """
        checks = []

        if operation_type == 'install_modules':
            modules = params.get('modules', [])

            # Check: modules list not empty
            if not modules:
                checks.append({
                    'id': 'modules_not_empty',
                    'status': 'fail',
                    'severity': 'error',
                    'message': 'No modules specified for installation'
                })
            else:
                checks.append({
                    'id': 'modules_not_empty',
                    'status': 'pass',
                    'severity': 'info',
                    'message': f'{len(modules)} module(s) to install'
                })

            # Check: module naming convention
            for module in modules:
                if not module.replace('_', '').replace('.', '').isalnum():
                    checks.append({
                        'id': f'module_naming_{module}',
                        'status': 'fail',
                        'severity': 'error',
                        'message': f'Invalid module name: {module}'
                    })

            # Check: no Enterprise modules (example)
            ee_modules = ['web_studio', 'account_accountant', 'helpdesk']
            found_ee = [m for m in modules if m in ee_modules]
            if found_ee:
                checks.append({
                    'id': 'no_ee_modules',
                    'status': 'fail',
                    'severity': 'error',
                    'message': f'Enterprise modules not allowed: {", ".join(found_ee)}'
                })

        return checks
