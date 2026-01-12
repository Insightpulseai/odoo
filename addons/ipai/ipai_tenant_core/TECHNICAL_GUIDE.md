# ipai_tenant_core - Technical Implementation Guide

## OCA Compliance

This module follows **Odoo Community Association (OCA)** standards for custom addon development.

### OCA Standards Implemented

✅ **Module Structure**:
- Standard directory layout (`models/`, `views/`, `data/`, `security/`)
- Proper `__init__.py` and `__manifest__.py` structure
- reStructuredText documentation (`README.rst`, `readme/`)

✅ **Licensing**:
- AGPL-3 license (OCA standard)
- License header in `__manifest__.py`

✅ **Documentation**:
- `README.rst` with standard sections (Overview, Features, Usage, Credits)
- Modular documentation in `readme/` directory:
  - `DESCRIPTION.rst` - Core module overview
  - `USAGE.rst` - Practical implementation guidance
  - `CONTRIBUTORS.rst` - Attribution and maintainers
  - `CONFIGURE.rst` - Configuration parameters

✅ **Code Quality**:
- PEP8 compliant Python code
- Type hints and docstrings
- Validation methods with clear error messages
- Proper ORM usage (no raw SQL in models)

✅ **Security**:
- Row-Level Security via `ir.model.access.csv`
- Field validation (`@api.constrains`)
- SQL injection prevention (parameterized queries)

✅ **Data Management**:
- Seed data with `noupdate="1"` flag
- XML-ID naming convention (`module.record_id`)
- Proper sequencing and dependencies

## Module Architecture

### 1. Models (`models/ipai_tenant.py`)

#### ipai.tenant

**Purpose**: Track tenant configuration and coordinate platform operations

**Inheritance**:
```python
_inherit = ['mail.thread', 'mail.activity.mixin']
```
- Enables activity tracking and messaging
- Automatic `message_follower_ids`, `activity_ids`, `message_ids` fields

**Core Fields**:

| Field | Type | Purpose | Validation |
|-------|------|---------|------------|
| `code` | Char(16) | Unique tenant identifier | Lowercase alphanumeric + underscore |
| `db_name` | Char | Odoo database name | Unique, required |
| `supabase_schema` | Char | PostgreSQL schema | Valid schema name format |
| `primary_domain` | Char | Access URL | Optional |
| `superset_workspace` | Char | Superset folder | Optional |
| `industry` | Selection | Business category | Predefined choices |
| `country_id` | Many2one | Geographic location | Link to res.country |

**Constraints**:

1. **SQL Constraints** (`_sql_constraints`):
   ```python
   ('code_unique', 'UNIQUE(code)', 'Tenant code must be unique!')
   ('db_name_unique', 'UNIQUE(db_name)', 'Database name must be unique!')
   ```

2. **Python Constraints** (`@api.constrains`):
   ```python
   @api.constrains('code')
   def _check_code_format(self):
       """Validate tenant code format (lowercase alphanumeric + underscore)"""
       if not re.match(r'^[a-z0-9_]+$', record.code):
           raise ValidationError(...)

   @api.constrains('supabase_schema')
   def _check_schema_format(self):
       """Validate Supabase schema format"""
       if not re.match(r'^[a-z_][a-z0-9_]*$', record.supabase_schema):
           raise ValidationError(...)
   ```

**Custom Methods**:

```python
def name_get(self):
    """Display tenant as '[code] name'"""
    return [(record.id, f'[{record.code}] {record.name}') for record in self]

def action_provision_supabase_schema(self):
    """Action to provision Supabase schema for tenant"""
    # Triggers external script/API
    return notification_action

def action_open_superset_workspace(self):
    """Open Superset workspace for tenant"""
    return url_action
```

### 2. Views (`views/ipai_tenant_views.xml`)

#### Tree View

**Features**:
- Drag-and-drop reordering via `sequence` field (widget="handle")
- Inline boolean toggle for `active` status
- Essential fields visible: code, name, db_name, supabase_schema

#### Form View

**Layout**:

```
Header
├── Action Buttons
│   ├── Provision Supabase Schema
│   └── Open Superset
└── Web Ribbon (if archived)

Sheet
├── Title Section
│   ├── Name (h1)
│   └── Code
├── Technical Configuration Group
│   ├── DB Name
│   ├── Supabase Schema
│   ├── Primary Domain
│   └── Sequence
├── Superset Integration Group
│   ├── Base URL
│   └── Workspace
├── Business Information Group
│   ├── Company Name
│   ├── Industry
│   ├── Country
│   └── Onboarded Date
└── Contact Information Group
    ├── Admin Email
    └── Admin Phone

Chatter
├── Followers
├── Activities
└── Messages
```

**OCA Compliance**:
- Standard field grouping
- Proper use of `<group>` and `<notebook>` elements
- Responsive design (groups with name attributes)

#### Search View

**Filters**:
- Active/Archived
- Group by: Industry, Country

**Search Fields**:
- name, code, db_name, supabase_schema

### 3. Security (`security/ir.model.access.csv`)

**Access Control List**:

| ID | Group | Read | Write | Create | Delete |
|----|-------|------|-------|--------|--------|
| access_ipai_tenant_manager | base.group_system | ✅ | ✅ | ✅ | ✅ |
| access_ipai_tenant_user | base.group_user | ✅ | ❌ | ❌ | ❌ |

**Rationale**:
- **System Administrators**: Full CRUD access for tenant management
- **Regular Users**: Read-only access for tenant information lookup

### 4. Data (`data/tenant_seed_data.xml`)

**Seed Records** (with `noupdate="1"`):

1. **platform** - Internal operations
   - DB: `odoo_platform`
   - Schema: `public`
   - Workspace: `platform`

2. **tbwa** - TBWA Philippines client
   - DB: `odoo_tbwa`
   - Schema: `tbwa`
   - Workspace: `tbwa`

3. **scout** - Shared retail analytics
   - DB: `odoo_platform`
   - Schema: `scout`
   - Workspace: `scout`

**XML-ID Format**: `module.record_type_code`
- Example: `ipai_tenant_core.tenant_tbwa`

### 5. Menu (`views/menu.xml`)

**Hierarchy**:
```
Platform (root)
└── Tenants
    └── action_ipai_tenant
```

**Icon**: `ipai_tenant_core,static/description/icon.png`

## Integration Points

### External Scripts

#### provision_tenant.sh

**Location**: `scripts/provision_tenant.sh`

**Purpose**: Automated tenant setup

**Workflow**:
1. Check tenant exists in `ipai.tenant` table
2. Create Supabase schema
3. Initialize Odoo database
4. Install base modules
5. Set admin password
6. Prepare Superset workspace

**Environment Variables**:
```bash
POSTGRES_URL              # Supabase connection string
SUPABASE_SERVICE_ROLE_KEY # Supabase admin token
ODOO_ADMIN_PASSWORD       # Default admin password
ODOO_URL                  # Odoo instance URL (optional)
```

**Usage**:
```bash
./scripts/provision_tenant.sh tbwa
```

#### xmlrpc_set_admin_password.py

**Location**: `scripts/xmlrpc_set_admin_password.py`

**Purpose**: Set Odoo admin password via XML-RPC or SQL

**Fallback Strategy**:
1. Try XML-RPC authentication
2. If fails (new database), use SQL with bcrypt
3. Validate success

### Cross-Module Dependencies

**Depends**:
- `base` - Core Odoo functionality
- `mail` - Activity tracking and messaging
- `web` - Web interface components

**Reverse Dependencies** (modules that depend on ipai_tenant_core):
- `ipai_bi_superset_embed` - Uses tenant metadata for workspace routing
- `ipai_finance_ppm` - Uses tenant context for BIR compliance

### Supabase Integration

**Schema Isolation**:

```sql
-- Each tenant gets isolated schema
CREATE SCHEMA IF NOT EXISTS tbwa;
ALTER SCHEMA tbwa OWNER TO postgres;

-- RLS policies enforce tenant filtering
CREATE POLICY tenant_isolation ON tbwa.expenses
  USING (tenant_id = current_setting('app.tenant_id'));
```

**Connection Pattern**:
```python
# Odoo models query Supabase via external DB connector
# Connection string stored in ir.config_parameter
supabase_url = self.env['ir.config_parameter'].sudo().get_param('supabase.url')
```

### Superset Integration

**Workspace Mapping**:
```python
# Tenant record stores Superset workspace
tenant = self.env['ipai.tenant'].search([('code', '=', 'tbwa')])
workspace_url = f"{tenant.superset_base_url}/superset/dashboard/?workspace={tenant.superset_workspace}"
```

**Guest Token Generation** (via `ipai_bi_superset_embed`):
```python
# Call Superset API to generate guest token
token = requests.post(
    f"{tenant.superset_base_url}/api/v1/security/guest_token",
    headers={'Authorization': f'Bearer {admin_token}'},
    json={'user': {'username': user.login}, 'resources': [{'type': 'dashboard', 'id': dashboard_id}]}
)
```

## Testing

### Unit Tests (Recommended)

**Location**: `tests/test_ipai_tenant.py` (to be created)

```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestIpaiTenant(TransactionCase):

    def setUp(self):
        super(TestIpaiTenant, self).setUp()
        self.tenant_model = self.env['ipai.tenant']

    def test_create_tenant(self):
        """Test tenant creation with valid data"""
        tenant = self.tenant_model.create({
            'name': 'Test Tenant',
            'code': 'test',
            'db_name': 'odoo_test',
            'supabase_schema': 'test',
        })
        self.assertEqual(tenant.code, 'test')

    def test_code_unique_constraint(self):
        """Test SQL unique constraint on code"""
        self.tenant_model.create({
            'name': 'Tenant 1',
            'code': 'test',
            'db_name': 'odoo_test1',
            'supabase_schema': 'test1',
        })
        with self.assertRaises(Exception):  # IntegrityError
            self.tenant_model.create({
                'name': 'Tenant 2',
                'code': 'test',  # Duplicate code
                'db_name': 'odoo_test2',
                'supabase_schema': 'test2',
            })

    def test_code_format_validation(self):
        """Test Python constraint on code format"""
        with self.assertRaises(ValidationError):
            self.tenant_model.create({
                'name': 'Invalid Tenant',
                'code': 'Test-123',  # Invalid: uppercase + hyphen
                'db_name': 'odoo_invalid',
                'supabase_schema': 'invalid',
            })
```

### Manual Testing

**Installation Test**:
```bash
# Install module
odoo-bin -d odoo_platform -i ipai_tenant_core --stop-after-init

# Verify seed data
psql "$POSTGRES_URL" -c "SELECT code, name FROM ipai_tenant ORDER BY sequence;"
```

**Provisioning Test**:
```bash
# Provision test tenant
export ODOO_ADMIN_PASSWORD='test123'
./scripts/provision_tenant.sh test

# Verify database created
psql "$POSTGRES_URL" -c "SELECT datname FROM pg_database WHERE datname = 'odoo_test';"

# Verify schema created
psql "$POSTGRES_URL" -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'test';"
```

## Deployment

### Installation

**Prerequisites**:
- Odoo 18.0 CE
- PostgreSQL 15+ (Supabase)
- Python 3.11+

**Steps**:
1. Place module in `addons/` directory
2. Update addon list: Settings > Technical > Modules > Update Apps List
3. Install: Apps > Search "IPAI Tenant Core" > Install

**Or via CLI**:
```bash
odoo-bin -d odoo_platform -i ipai_tenant_core --stop-after-init
```

### Upgrade

**For module updates**:
```bash
odoo-bin -d odoo_platform -u ipai_tenant_core --stop-after-init
```

**Data migration**:
- Use `noupdate="1"` for seed data to prevent overwrites
- Create migration scripts in `migrations/18.0.1.1.0/`

### Uninstallation

```bash
odoo-bin -d odoo_platform --uninstall ipai_tenant_core --stop-after-init
```

**Note**: This will:
- Remove `ipai.tenant` table and all records
- Remove menu items and views
- Keep provisioned tenant databases (manual cleanup required)

## Performance Considerations

### Database Indexes

**Recommended indexes** (add via migration):
```sql
CREATE INDEX idx_ipai_tenant_code ON ipai_tenant(code);
CREATE INDEX idx_ipai_tenant_active ON ipai_tenant(active);
```

### Query Optimization

**Use `search_read` for list views**:
```python
# Good
tenants = self.env['ipai.tenant'].search_read(
    [('active', '=', True)],
    ['code', 'name', 'db_name']
)

# Avoid
tenants = self.env['ipai.tenant'].search([('active', '=', True)])
all_data = tenants.read(['code', 'name', 'db_name'])  # Extra query
```

## Troubleshooting

### Common Issues

**Issue**: "Module not found after installation"
**Solution**: Clear cache, restart Odoo, update module list

**Issue**: "Seed data not loading"
**Solution**: Check `noupdate="1"` flag, verify XML-IDs unique

**Issue**: "Provisioning script fails"
**Solution**: Check environment variables, verify Supabase connection, check logs

### Logs

**Odoo Logs**:
```bash
grep "ipai.tenant" /var/log/odoo/odoo-server.log
```

**Provisioning Logs**:
```bash
./scripts/provision_tenant.sh tbwa 2>&1 | tee provision.log
```

## Contributing

### Code Style

**Python**:
- Follow PEP8
- Use 4-space indentation
- Max line length: 79 characters
- Add docstrings to all methods

**XML**:
- Use 4-space indentation
- Close self-closing tags: `<field name="x"/>`
- Group related fields with `<group>` elements

### Pull Request Process

1. Create feature branch: `git checkout -b feature/tenant-export`
2. Make changes following OCA standards
3. Add tests for new functionality
4. Update documentation (README.rst, TECHNICAL_GUIDE.md)
5. Submit PR with clear description

## References

- **OCA Style Guide**: https://github.com/OCA/maintainer-tools
- **Odoo Development**: https://www.odoo.com/documentation/18.0/developer.html
- **Supabase Docs**: https://supabase.com/docs
- **Repository**: https://github.com/jgtolentino/odoo-ce

---

**Module Version**: 18.0.1.0.0
**Odoo Version**: 18.0
**License**: AGPL-3
**Author**: InsightPulse AI
**Maintainer**: Jake Tolentino <jake.tolentino@tbwa.com.ph>
