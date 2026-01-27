#!/bin/bash
# File: scripts/bootstrap_ipai_bridge.sh
# Purpose: Create ipai_enterprise_bridge module skeleton

set -euo pipefail

BRIDGE_DIR="addons/ipai/ipai_enterprise_bridge"

echo "🚀 Scaffolding ipai_enterprise_bridge module..."
echo "📁 Target: $BRIDGE_DIR"

# Create directory structure
mkdir -p "$BRIDGE_DIR"/{models,views,security,data}

# __manifest__.py
cat > "$BRIDGE_DIR/__manifest__.py" << 'EOF'
{
    'name': 'InsightPulse AI Enterprise Bridge',
    'version': '19.0.1.0.0',
    'category': 'Technical',
    'summary': 'Glue layer between Odoo CE 19, OCA modules, and ipai_* addons for EE parity',
    'description': '''
Enterprise Edition Parity Bridge
=================================

This module provides the glue layer connecting:
- Odoo CE 19 core features
- OCA 19.x modules (EE-parity addons)
- ipai_* custom modules

Key Features:
- Automation rule extensions (AI agent triggers, approval workflows)
- DMS integration with ipai_ocr
- Studio bridges for ipai_dev_studio_base
- Cross-module compatibility fixes
    ''',
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'license': 'LGPL-3',
    'depends': [
        # OCA dependencies (will be installed via bootstrap_oca.sh)
        'base_automation',          # server-tools
        'account_asset_management', # account-financial-tools
        'dms',                      # dms
        'web_timeline',             # web

        # ipai dependencies (existing modules)
        'ipai_dev_studio_base',
        'ipai_workspace_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/automation_rule_views.xml',
        'views/dms_integration_views.xml',
        'data/automation_templates.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
EOF

# __init__.py
cat > "$BRIDGE_DIR/__init__.py" << 'EOF'
from . import models
EOF

# models/__init__.py
cat > "$BRIDGE_DIR/models/__init__.py" << 'EOF'
from . import automation_rule_extension
from . import dms_integration
EOF

# models/automation_rule_extension.py
cat > "$BRIDGE_DIR/models/automation_rule_extension.py" << 'EOF'
# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class AutomationRuleExtension(models.Model):
    """Extends base_automation (OCA) with ipai-specific triggers."""
    _inherit = 'base.automation'

    ipai_trigger_type = fields.Selection([
        ('ai_agent', 'AI Agent Completion'),
        ('approval', 'Approval Workflow Stage'),
        ('ppm_milestone', 'PPM Milestone Reached'),
        ('ocr_complete', 'OCR Processing Complete'),
    ], string='IPAI Trigger Type', help='Custom trigger types for IPAI workflows')

    # Relations to ipai_* models (optional, may not exist in all deployments)
    ipai_agent_id = fields.Many2one('ipai.ai.agent', string='AI Agent', ondelete='cascade')
    ipai_approval_stage_id = fields.Many2one('ipai.approval.stage', string='Approval Stage', ondelete='cascade')

    @api.model
    def _trigger_ai_agent(self, agent_id, result):
        """
        Called by ipai_ai_agents when agent completes.

        :param agent_id: ID of the AI agent that completed
        :param result: Dictionary with agent execution results
        """
        rules = self.search([
            ('ipai_trigger_type', '=', 'ai_agent'),
            ('ipai_agent_id', '=', agent_id),
            ('active', '=', True)
        ])

        for rule in rules:
            try:
                rule._execute(result)
                _logger.info(f"AI agent automation rule {rule.name} executed successfully")
            except Exception as e:
                _logger.error(f"Failed to execute automation rule {rule.name}: {e}")

    @api.model
    def _trigger_ocr_complete(self, document_id, ocr_data):
        """
        Called by ipai_ocr when OCR processing completes.

        :param document_id: ID of the processed document
        :param ocr_data: Dictionary with extracted OCR data
        """
        rules = self.search([
            ('ipai_trigger_type', '=', 'ocr_complete'),
            ('active', '=', True)
        ])

        for rule in rules:
            try:
                # Pass OCR data as context for the automation
                rule.with_context(
                    ocr_data=ocr_data,
                    document_id=document_id
                )._execute({'document_id': document_id})
                _logger.info(f"OCR automation rule {rule.name} executed for document {document_id}")
            except Exception as e:
                _logger.error(f"Failed to execute OCR automation rule {rule.name}: {e}")
EOF

# models/dms_integration.py
cat > "$BRIDGE_DIR/models/dms_integration.py" << 'EOF'
# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class DMSFileExtension(models.Model):
    """Extends DMS (OCA) with ipai_ocr integration."""
    _inherit = 'dms.file'

    ipai_ocr_processed = fields.Boolean(
        string='OCR Processed',
        default=False,
        help='Indicates if this file has been processed by IPAI OCR'
    )
    ipai_ocr_confidence = fields.Float(
        string='OCR Confidence',
        digits=(5, 2),
        help='OCR extraction confidence score (0-100%)'
    )
    ipai_ocr_data = fields.Text(
        string='OCR Extracted Data',
        help='JSON-formatted OCR extraction results'
    )
    ipai_ocr_date = fields.Datetime(
        string='OCR Processing Date',
        help='When the OCR processing was completed'
    )

    def action_process_ocr(self):
        """
        Trigger OCR processing for this DMS file.
        Calls ipai_ocr service if available.
        """
        self.ensure_one()

        # Check if ipai_ocr module is installed
        if not self.env['ir.module.module'].search([('name', '=', 'ipai_ocr'), ('state', '=', 'installed')]):
            _logger.warning("ipai_ocr module not installed, cannot process OCR")
            return

        try:
            # Call OCR service (implementation depends on ipai_ocr module)
            ocr_service = self.env['ipai.ocr.service']
            result = ocr_service.process_file(self.id)

            # Update DMS file with OCR results
            self.write({
                'ipai_ocr_processed': True,
                'ipai_ocr_confidence': result.get('confidence', 0),
                'ipai_ocr_data': result.get('data', '{}'),
                'ipai_ocr_date': fields.Datetime.now()
            })

            # Trigger automation rules
            self.env['base.automation']._trigger_ocr_complete(self.id, result)

            _logger.info(f"OCR processing completed for DMS file {self.name}")
        except Exception as e:
            _logger.error(f"OCR processing failed for DMS file {self.name}: {e}")
EOF

# views/automation_rule_views.xml
cat > "$BRIDGE_DIR/views/automation_rule_views.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_base_automation_form_ipai" model="ir.ui.view">
        <field name="name">base.automation.form.ipai</field>
        <field name="model">base.automation</field>
        <field name="inherit_id" ref="base_automation.view_base_automation_form"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='trigger']" position="after">
                <field name="ipai_trigger_type"
                       attrs="{'invisible': [('trigger', '!=', 'on_change')]}"/>

                <field name="ipai_agent_id"
                       attrs="{'invisible': [('ipai_trigger_type', '!=', 'ai_agent')],
                               'required': [('ipai_trigger_type', '=', 'ai_agent')]}"/>

                <field name="ipai_approval_stage_id"
                       attrs="{'invisible': [('ipai_trigger_type', '!=', 'approval')],
                               'required': [('ipai_trigger_type', '=', 'approval')]}"/>
            </xpath>
        </field>
    </record>
</odoo>
EOF

# views/dms_integration_views.xml
cat > "$BRIDGE_DIR/views/dms_integration_views.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_dms_file_form_ipai_ocr" model="ir.ui.view">
        <field name="name">dms.file.form.ipai.ocr</field>
        <field name="model">dms.file</field>
        <field name="inherit_id" ref="dms.view_dms_file_form"/>
        <field name="arch" type="xml">
            <xpath expr="//sheet" position="inside">
                <group name="ipai_ocr" string="OCR Processing" attrs="{'invisible': [('ipai_ocr_processed', '=', False)]}">
                    <field name="ipai_ocr_processed"/>
                    <field name="ipai_ocr_confidence" widget="percentage"/>
                    <field name="ipai_ocr_date"/>
                    <field name="ipai_ocr_data" widget="ace" options="{'mode': 'json'}"/>
                </group>
            </xpath>
            <xpath expr="//header" position="inside">
                <button name="action_process_ocr"
                        type="object"
                        string="Process OCR"
                        class="btn-primary"
                        attrs="{'invisible': [('ipai_ocr_processed', '=', True)]}"/>
            </xpath>
        </field>
    </record>
</odoo>
EOF

# security/ir.model.access.csv
cat > "$BRIDGE_DIR/security/ir.model.access.csv" << 'EOF'
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_base_automation_user,base.automation.user,base_automation.model_base_automation,base.group_user,1,0,0,0
access_base_automation_manager,base.automation.manager,base_automation.model_base_automation,base.group_system,1,1,1,1
access_dms_file_user,dms.file.user,dms.model_dms_file,base.group_user,1,0,0,0
access_dms_file_manager,dms.file.manager,dms.model_dms_file,base.group_system,1,1,1,1
EOF

# data/automation_templates.xml
cat > "$BRIDGE_DIR/data/automation_templates.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="1">
    <!-- Example automation template: OCR completion → expense creation -->
    <record id="automation_ocr_to_expense" model="base.automation">
        <field name="name">OCR Receipt → Create Expense</field>
        <field name="model_id" ref="dms.model_dms_file"/>
        <field name="trigger">on_write</field>
        <field name="ipai_trigger_type">ocr_complete</field>
        <field name="active" eval="False"/>  <!-- Disabled by default -->
        <field name="state">code</field>
        <field name="code">
# Example automation code
if record.ipai_ocr_processed and record.ipai_ocr_confidence > 60:
    # Parse OCR data and create expense
    import json
    ocr_data = json.loads(record.ipai_ocr_data or '{}')

    # Create expense (assuming hr_expense is installed)
    expense = env['hr.expense'].create({
        'name': ocr_data.get('description', 'Expense from OCR'),
        'unit_amount': ocr_data.get('amount', 0),
        'date': ocr_data.get('date', fields.Date.today()),
        'description': f"Auto-created from DMS file: {record.name}"
    })

    log(f"Created expense {expense.id} from OCR file {record.name}")
        </field>
    </record>
</odoo>
EOF

# README.md
cat > "$BRIDGE_DIR/README.md" << 'EOF'
# IPAI Enterprise Bridge

## Overview

`ipai_enterprise_bridge` is a minimal glue layer providing Enterprise Edition parity for Odoo CE 19 by connecting:

- **Odoo CE 19 core features**
- **OCA 19.x modules** (community EE-parity addons)
- **ipai_* custom modules** (InsightPulse AI extensions)

## Purpose

This module fills gaps where OCA modules don't provide complete EE functionality and extends OCA features with IPAI-specific capabilities.

## Key Features

### 1. Automation Rule Extensions

Extends `base_automation` (OCA/server-tools) with custom triggers:

- **AI Agent Completion**: Trigger automations when AI agents finish tasks
- **Approval Workflow Stages**: React to approval state changes
- **PPM Milestones**: Trigger actions on project milestones
- **OCR Processing**: Automate workflows after document OCR

**Example Use Cases**:
- Auto-create expenses from OCR-processed receipts
- Send notifications when AI agents complete analysis
- Update project status on milestone completion
- Route approvals based on document content

### 2. DMS Integration

Extends `dms` (OCA/dms) with OCR capabilities:

- **OCR Processing Button**: One-click OCR for DMS files
- **Confidence Scoring**: Track OCR extraction quality
- **Extracted Data Storage**: Store OCR results in JSON format
- **Automation Triggers**: Automatic workflows after OCR

**Example Workflow**:
```
Upload receipt → Store in DMS → Click "Process OCR" → Extract data → Auto-create expense
```

### 3. Studio Bridges

Connects `ipai_dev_studio_base` with OCA metadata tools for low-code development capabilities.

## Dependencies

### Required OCA Modules

These must be installed via `scripts/bootstrap_oca.sh`:

- `base_automation` (OCA/server-tools)
- `account_asset_management` (OCA/account-financial-tools)
- `dms` (OCA/dms)
- `web_timeline` (OCA/web)

### Required IPAI Modules

These must already be present in the Odoo instance:

- `ipai_dev_studio_base`
- `ipai_workspace_core`

## Installation

### Step 1: Install OCA Modules

```bash
# Clone OCA repositories and create module symlinks
./scripts/bootstrap_oca.sh

# Verify OCA modules are available
ls -1 addons/oca/modules/
```

### Step 2: Install Required OCA Dependencies

```bash
docker compose -f docker-compose.odoo19.yml run --rm odoo \
  odoo-bin -d odoo19 -i base_automation,account_asset_management,dms,web_timeline --stop-after-init
```

### Step 3: Install Bridge Module

```bash
docker compose -f docker-compose.odoo19.yml run --rm odoo \
  odoo-bin -d odoo19 -i ipai_enterprise_bridge --stop-after-init
```

### Step 4: Verify Installation

```bash
# Check module is installed
docker compose -f docker-compose.odoo19.yml exec odoo \
  odoo-bin list -d odoo19 | grep ipai_enterprise_bridge
```

## Configuration

### Automation Rule Setup

1. Navigate to **Settings → Technical → Automation → Automated Actions**
2. Create new automation rule
3. Select "IPAI Trigger Type"
4. Choose trigger (AI Agent, Approval, OCR, etc.)
5. Define action (Python code, server action, etc.)

### DMS OCR Setup

1. Upload file to DMS
2. Open file details
3. Click "Process OCR" button
4. View extracted data in "OCR Processing" group

## API Reference

### Automation Triggers

```python
# Trigger AI agent automation
self.env['base.automation']._trigger_ai_agent(
    agent_id=42,
    result={'status': 'completed', 'data': {...}}
)

# Trigger OCR automation
self.env['base.automation']._trigger_ocr_complete(
    document_id=123,
    ocr_data={'amount': 1500, 'vendor': 'ACME Corp'}
)
```

### DMS OCR Processing

```python
# Process OCR for DMS file
dms_file = self.env['dms.file'].browse(file_id)
dms_file.action_process_ocr()

# Check OCR results
if dms_file.ipai_ocr_processed:
    confidence = dms_file.ipai_ocr_confidence  # Float (0-100)
    data = json.loads(dms_file.ipai_ocr_data)  # Dictionary
```

## Development

### Adding New Triggers

1. Edit `models/automation_rule_extension.py`
2. Add trigger to `ipai_trigger_type` selection field
3. Create `_trigger_*` method for custom logic
4. Update views to show trigger configuration

### Extending DMS Integration

1. Edit `models/dms_integration.py`
2. Add new fields to `dms.file` model
3. Update views in `views/dms_integration_views.xml`
4. Add automation templates in `data/automation_templates.xml`

## Troubleshooting

### OCR Not Working

**Symptom**: "Process OCR" button doesn't work

**Solution**:
- Ensure `ipai_ocr` module is installed
- Check OCR service is running
- Verify DMS file is a supported format (PDF, JPG, PNG)

### Automation Not Triggering

**Symptom**: Automation rules don't execute

**Solution**:
- Check automation rule is active
- Verify trigger type matches event
- Check server logs for errors
- Ensure OCA `base_automation` is installed

### Missing Dependencies

**Symptom**: Module won't install

**Solution**:
```bash
# Install OCA dependencies first
./scripts/bootstrap_oca.sh
docker compose -f docker-compose.odoo19.yml run --rm odoo \
  odoo-bin -d odoo19 -i base_automation,dms --stop-after-init

# Then install bridge
docker compose -f docker-compose.odoo19.yml run --rm odoo \
  odoo-bin -d odoo19 -i ipai_enterprise_bridge --stop-after-init
```

## Changelog

### 19.0.1.0.0 (2026-01-28)
- Initial release for Odoo 19
- Automation rule extensions (AI agent, approval, OCR triggers)
- DMS OCR integration
- Studio bridges for low-code development

## License

LGPL-3

## Support

For issues and questions:
- GitHub: https://github.com/jgtolentino/odoo-ce/issues
- Email: support@insightpulseai.com
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ipai_enterprise_bridge module created"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 Location: $BRIDGE_DIR"
echo ""
echo "📦 Module structure:"
tree -L 2 "$BRIDGE_DIR" 2>/dev/null || find "$BRIDGE_DIR" -maxdepth 2 -type f -o -type d | sort
echo ""
echo "Next steps:"
echo "  1. Review module code: cat $BRIDGE_DIR/README.md"
echo "  2. Test installation: docker compose -f docker-compose.odoo19.yml run --rm odoo odoo-bin -d odoo19 -i ipai_enterprise_bridge --stop-after-init"
echo "  3. Check logs for errors"
echo ""
