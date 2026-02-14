# IPAI Control Plane Server

Python/FastAPI backend for VS Code extension.

## Architecture

```
VS Code Extension (TypeScript)
    ↓ HTTP
Control Plane Server (Python/FastAPI)
    ↓
Odoo / Filesystem / Evidence
```

## Installation

```bash
cd tools/vscode/ipai-control-plane/control-plane

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running

```bash
# From control-plane directory
python server.py

# Or with custom port
IPAI_CONTROL_PLANE_PORT=9999 python server.py
```

Server starts on `http://127.0.0.1:9876` by default.

## API Documentation

Once running, visit:
- **Interactive docs**: http://127.0.0.1:9876/docs
- **Health check**: http://127.0.0.1:9876/health

## Endpoints

### Project & Environment
- `GET /api/projects` - List discovered projects
- `GET /api/projects/{id}/environments` - List environments
- `GET /api/projects/{id}/environments/{env}/status` - Get environment status

### Validation
- `POST /api/validate/manifest` - Validate `__manifest__.py`
- `POST /api/validate/xml` - Validate XML files
- `POST /api/validate/security` - Validate security rules
- `POST /api/validate/all` - Run all validators

### Operations
- `POST /api/operations/install-modules` - Install modules with evidence
- `POST /api/operations/install-modules/preview` - Preview installation diffs
- `POST /api/operations/run-migration` - Run migration (TODO)
- `POST /api/operations/upgrade-odoo` - Upgrade Odoo (TODO)
- `POST /api/operations/rollback` - Rollback to snapshot (TODO)

### Evidence
- `GET /api/evidence/{project_id}` - List evidence bundles
- `GET /api/evidence/bundle/{bundle_id}` - Get evidence bundle details

### AI Relay
- `POST /api/ai/generate-patch` - Generate patch via AI (TODO)
- `POST /api/ai/explain-drift` - Explain schema drift (TODO)

## Components

### Project Registry (`project_registry.py`)
Discovers Odoo projects and environments using:
- Workspace files (`*.code-workspace`)
- Spec Kit markers (`spec/` directory)
- Odoo conventions (`addons/` directory)

### Evidence Bundler (`evidence.py`)
Generates immutable audit trails at:
```
docs/evidence/YYYYMMDD-HHMM-<operation>/
├── plan.md
├── operation.json
├── diffs/
├── validation/
├── logs/
└── artifacts/
```

### Validators (`validators/`)

#### Manifest Validator
Checks:
- Required keys (name, version, depends, installable)
- Dependency existence
- EE-only module detection
- Version format

#### XML Validator
Checks:
- Deprecated `<tree>` elements (use `<list>` in Odoo 19+)
- Missing external IDs
- View mode consistency
- XML syntax

#### Security Validator
Checks:
- `ir.model.access.csv` existence
- Access rule coverage for all models
- Record rule (RLS) completeness
- Empty domain detection

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Type checking
mypy .

# Linting
ruff check .
```

## Configuration

Environment variables:
- `IPAI_CONTROL_PLANE_PORT` - Server port (default: 9876)

## Integration with VS Code Extension

Extension calls this server via HTTP client:
```typescript
const client = new ControlPlaneClient('http://127.0.0.1:9876');
const projects = await client.getProjects();
```

Extension starts server automatically on activation.

## Next Steps

- [ ] Implement actual module installation
- [ ] Add diff generation
- [ ] Implement AI relay
- [ ] Add migration support
- [ ] Add rollback support
