# Odoo 18 VS Code Development Setup
*Complete Development Environment for Delta Customization Approach*

## 🎯 Essential VS Code Extensions

### 1. Core Development Extensions

**Python (Microsoft)**
- **Purpose**: Python IntelliSense, debugging, and code navigation
- **Key Features**:
  - Auto-completion for Odoo fields and methods
  - "Go to Definition" (F12) to explore Odoo core code
  - Debugging support with breakpoints
- **Install**: Search "Python" in VS Code extensions

**XML (Red Hat)**
- **Purpose**: XML syntax highlighting and validation
- **Key Features**:
  - XPath syntax validation
  - XML tag auto-closing
  - Error detection before server restart
- **Install**: Search "XML" in VS Code extensions

**GitLens (GitKraken)**
- **Purpose**: Enhanced Git integration and conflict resolution
- **Key Features**:
  - Inline blame annotations
  - Code lens showing recent changes
  - Visual merge conflict resolution
- **Install**: Search "GitLens" in VS Code extensions

### 2. Odoo-Specific Extensions

**Odoo Snippets (Jérémy Kersten)**
- **Purpose**: Rapid Odoo development with code snippets
- **Key Features**:
  - `oo-inherit` - Model inheritance boilerplate
  - `oo-field` - Field definition snippets
  - `oo-view` - XML view templates
  - `oo-action` - Window action templates
- **Install**: Search "Odoo Snippets" in VS Code extensions

**Odoo Development (Odoo)**
- **Purpose**: Official Odoo development support
- **Key Features**:
  - Odoo file type recognition
  - Basic syntax highlighting
  - Project structure awareness
- **Install**: Search "Odoo Development" in VS Code extensions

### 3. Optional Productivity Extensions

**Auto Rename Tag**
- **Purpose**: Auto-rename paired XML/HTML tags
- **Install**: Search "Auto Rename Tag"

**Bracket Pair Colorizer**
- **Purpose**: Color matching brackets for better readability
- **Install**: Search "Bracket Pair Colorizer"

**Todo Tree**
- **Purpose**: Highlight and manage TODO comments
- **Install**: Search "Todo Tree"

## ⚙️ VS Code Configuration

### Launch Configuration for Debugging

**File**: `.vscode/launch.json`
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Odoo 18 Server",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/odoo-bin",
            "args": [
                "--config=${workspaceFolder}/deploy/odoo.conf",
                "--database=odoo",
                "--addons-path=${workspaceFolder}/addons,${workspaceFolder}/custom-addons"
            ],
            "console": "integratedTerminal",
            "justMyCode": false,
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "Odoo Shell",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/odoo-bin",
            "args": [
                "shell",
                "--config=${workspaceFolder}/deploy/odoo.conf",
                "-d",
                "odoo"
            ],
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

### Workspace Settings

**File**: `.vscode/settings.json`
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.analysis.extraPaths": [
        "${workspaceFolder}"
    ],
    "files.associations": {
        "*.xml": "xml",
        "*.csv": "csv"
    },
    "emmet.includeLanguages": {
        "xml": "html"
    },
    "xml.validation.enabled": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.git": true,
        "**/node_modules": true
    }
}
```

## 🚀 Odoo Snippets Quick Reference

### Python Model Snippets

**Model Inheritance**
```python
# Type: oo-inherit
class ProjectTask(models.Model):
    _inherit = 'project.task'

    # Your custom fields here
```

**Field Definitions**
```python
# Type: oo-field-char
name = fields.Char(string='Name')

# Type: oo-field-many2one
partner_id = fields.Many2one('res.partner', string='Partner')

# Type: oo-field-selection
state = fields.Selection([
    ('draft', 'Draft'),
    ('done', 'Done'),
], string='State')
```

### XML View Snippets

**Form View Extension**
```xml
<!-- Type: oo-view-form-inherit -->
<record id="view_model_form_inherit" model="ir.ui.view">
    <field name="name">model.form.inherit</field>
    <field name="model">your.model</field>
    <field name="inherit_id" ref="base_module.view_model_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='name']" position="after">
            <!-- Your fields here -->
        </xpath>
    </field>
</record>
```

**Tree View**
```xml
<!-- Type: oo-view-tree -->
<record id="view_model_tree" model="ir.ui.view">
    <field name="name">model.tree</field>
    <field name="model">your.model</field>
    <field name="arch" type="xml">
        <tree>
            <field name="name"/>
        </tree>
    </field>
</record>
```

**Window Action**
```xml
<!-- Type: oo-action -->
<record id="action_model" model="ir.actions.act_window">
    <field name="name">Model</field>
    <field name="res_model">your.model</field>
    <field name="view_mode">tree,form</field>
</record>
```

## 🔧 Browser Extensions for Odoo Development

### Odoo Debug (Chrome/Firefox)

**Features**:
- One-click debug mode (`?debug=1`)
- View metadata and XML IDs
- Technical features menu
- Asset debugging

**Installation**:
- Chrome Web Store: Search "Odoo Debug"
- Firefox Add-ons: Search "Odoo Debug"

## 🎯 Keyboard Shortcuts for Odoo Development

### Essential Shortcuts

| Action | Shortcut | Purpose |
|--------|----------|---------|
| Go to Definition | `F12` | Navigate to Odoo core code |
| Find All References | `Shift+F12` | Find where code is used |
| Quick Open | `Ctrl+P` | Quickly open files |
| Command Palette | `Ctrl+Shift+P` | Access all commands |
| Toggle Terminal | `Ctrl+`` | Open/close terminal |
| Format Document | `Shift+Alt+F` | Auto-format code |

### Odoo Snippets Shortcuts

| Snippet | Trigger | Result |
|---------|---------|--------|
| Model Inheritance | `oo-inherit` | Complete inheritance class |
| Char Field | `oo-field-char` | `fields.Char()` template |
| Many2one Field | `oo-field-many2one` | `fields.Many2one()` template |
| Form View | `oo-view-form` | Complete form view XML |
| Tree View | `oo-view-tree` | Complete tree view XML |

## 🐛 Debugging Workflow

### 1. Setting Breakpoints
- Click left gutter in Python files to set breakpoints
- Use conditional breakpoints for specific conditions

### 2. Debugging Session
1. Press `F5` to start Odoo server in debug mode
2. Perform action in Odoo that triggers your code
3. VS Code will pause at breakpoints
4. Use debug toolbar to step through code

### 3. Debug Console
- Access Python console during debugging
- Execute commands in current context
- Inspect variables and objects

## 📁 Project Structure Template

```
odoo-ce/
├── .vscode/
│   ├── launch.json          # Debug configurations
│   └── settings.json        # Workspace settings
├── addons/
│   └── ipai_finance_ppm/    # Your custom module
│       ├── __init__.py
│       ├── __manifest__.py
│       ├── models/
│       ├── views/
│       └── data/
├── deploy/
│   └── odoo.conf           # Odoo configuration
└── odoo-bin               # Odoo executable
```

## 🔍 Troubleshooting Common Issues

### Python Path Issues
```json
// In settings.json
{
    "python.defaultInterpreterPath": "/path/to/your/venv/bin/python",
    "python.analysis.extraPaths": [
        "${workspaceFolder}",
        "${workspaceFolder}/odoo",
        "${workspaceFolder}/addons"
    ]
}
```

### Debugging Not Working
- Ensure `justMyCode: false` in launch.json
- Check Python interpreter path
- Verify Odoo configuration file path

### XML Validation Errors
- Check for unclosed tags
- Verify XPath expressions
- Ensure proper XML structure

## 🚀 Quick Start Checklist

- [ ] Install essential VS Code extensions
- [ ] Configure launch.json for debugging
- [ ] Set up workspace settings
- [ ] Install browser debug extension
- [ ] Test debugging with breakpoints
- [ ] Practice using Odoo snippets

This setup will dramatically accelerate your Odoo 18 development workflow, especially for the "Delta" customization approach where you frequently inherit and extend core functionality.
