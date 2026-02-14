# IPAI Control Plane

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/Insightpulseai/odoo)
[![License](https://img.shields.io/badge/license-AGPL--3.0-green.svg)](LICENSE)
[![VS Code](https://img.shields.io/badge/VS%20Code-1.90%2B-007ACC.svg)](https://code.visualstudio.com/)

> **SaaS-grade developer control plane for Odoo CE + OCA + IPAI**
>
> Treats Odoo as a managed runtime with deterministic deploys, environment visibility, and governed AI assistance.

## 🎯 What Makes This Different

Unlike traditional Odoo extensions (snippets, syntax highlighting), IPAI Control Plane replicates **modern SaaS platform workflows**:

| Traditional Odoo Development | IPAI Control Plane |
|------------------------------|-------------------|
| Manual module installation | Diff preview → confirm → evidence |
| UI-driven operations | API-driven, auditable |
| Hidden state changes | Visible diffs (SQL, XML, Python) |
| No rollback safety | Evidence bundles for every operation |
| Blind AI suggestions | Governed AI with validation gates |

**Think**: Vercel/Supabase/Odoo.sh control plane, but embedded in VS Code.

---

## ✨ Features

### 🏗️ Project & Environment Management
Visual tree view of Odoo projects with multi-environment support:
- **dev** - Local development
- **stage** - Pre-production testing
- **prod** - Production (read-only by default)

### 🔍 Deterministic Operations
**No blind execution**. Every mutation shows:
1. **Diff preview** (SQL schema + XML views)
2. **Validation checks** (naming, EE detection, security)
3. **Evidence bundle ID** (audit trail)

### ✅ Validation Engine
Real-time validation surfaced in Problems panel:
- **Manifest** - Required keys, dependencies, EE detection
- **XML** - Deprecated `<tree>` → `<list>`, external ID collisions
- **Security** - Access rule coverage, RLS completeness

### 📦 Evidence Bundles
Immutable audit trails at `docs/evidence/YYYYMMDD-HHMM-<operation>/`:
```
├── plan.md              # Human-readable summary
├── operation.json       # Machine-readable metadata
├── diffs/               # SQL, XML, Python changes
├── validation/          # Check results
└── logs/                # Execution logs
```

### 🤖 Governed AI (Coming Soon)
AI commands that produce **patch-only diffs** with validation gates:
- Generate module patch
- Explain schema drift
- Plan upgrades

## Requirements

- VS Code 1.85.0 or higher
- IPAI Control Plane server (Python/Node backend)
- Odoo 19 CE development environment

## 📦 Installation

### From VS Code Marketplace (Coming Soon)
```
1. Open VS Code
2. Extensions panel (Ctrl+Shift+X)
3. Search "IPAI Control Plane"
4. Click Install
```

### From VSIX (Current)
```bash
# Download latest release
# https://github.com/Insightpulseai/odoo/releases

# Install
code --install-extension ipai-control-plane-0.1.0.vsix
```

### Control Plane Server Setup
```bash
cd tools/vscode/ipai-control-plane/control-plane

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server (port 9876)
python server.py
```

**Note**: Extension auto-starts server on activation (future enhancement).

## Configuration

```json
{
  "ipai.controlPlane.port": 9876,
  "ipai.projects.repoRoot": "/path/to/odoo/repo",
  "ipai.projects.defaultEnvironment": "dev",
  "ipai.validation.autoRun": true,
  "ipai.evidence.autoGenerate": true,
  "ipai.ai.provider": "claude"
}
```

## Commands

| Command | Description |
|---------|-------------|
| `IPAI: Refresh Projects` | Reload project and environment list |
| `IPAI: Select Project` | Switch active project |
| `IPAI: Deploy to Environment` | Deploy changes with diff preview |
| `IPAI: Validate Manifest` | Check `__manifest__.py` compliance |
| `IPAI: Validate XML` | Check XML schema and external IDs |
| `IPAI: Install Modules` | Install with diff preview |
| `IPAI AI: Generate Patch` | AI-assisted patch generation |

## Spec Kit Alignment

This extension enforces Spec Kit governance:
- Operations blocked without spec bundles
- All mutations generate evidence
- Read-only by default
- AI constrained to patch-only output

See `spec/ipai-vscode-control-plane/` for complete specification.

## 🚀 Quick Start

1. **Open Odoo project** in VS Code
2. **Start control plane server** (see Installation)
3. **Open IPAI sidebar** (Activity Bar icon)
4. **Right-click environment** → "Install Modules"
5. **Enter modules**: `sale,account`
6. **Review diff preview**
7. **Click "Install Modules"**
8. **View evidence bundle** in tree

---

## 🛠️ Development

### Build & Test
```bash
cd tools/vscode/ipai-control-plane

npm install          # Install dependencies
npm run build        # Compile TypeScript → dist/
npm run watch        # Watch mode (incremental)
npm test             # Run unit tests (vitest)
npm run test:integration  # Run integration tests
npm run lint         # ESLint check
npm run package      # Create .vsix
```

📖 **Comprehensive testing guide**: See [TESTING.md](TESTING.md) for unit tests, integration tests, TDD workflows, and debugging strategies.

### Debug Extension
1. Open extension folder in VS Code
2. Press **F5** (Launch Extension)
3. Extension Development Host opens
4. Test features in development window

### Project Structure
```
tools/vscode/ipai-control-plane/
├── src/                    # TypeScript source
│   ├── extension.ts       # Entry point
│   ├── client/            # API client
│   ├── providers/         # Tree view providers
│   └── commands/          # Command handlers
├── control-plane/         # Python FastAPI server
│   ├── server.py          # Main server
│   ├── validators/        # Manifest, XML, security
│   └── operations.py      # Operation state manager
├── dist/                  # Compiled output
└── package.json           # Extension manifest
```

## Architecture

```
VS Code Extension (TS)
    ↓
Control Plane API (Python/Node)
    ↓
Runtime Targets (Odoo/Supabase/CI)
```

Extension is **stateless**. All business logic lives in control plane.

## 📄 License

AGPL-3.0-or-later - See [LICENSE](../../LICENSE)

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## 🐛 Issues

Report bugs at: https://github.com/Insightpulseai/odoo/issues

## 📚 Documentation

- **Spec Kit Bundle**: `spec/ipai-vscode-control-plane/`
- **Control Plane API**: `control-plane/README.md`
- **Architecture**: `spec/ipai-vscode-control-plane/plan.md`
- **Testing**: `tools/vscode/ipai-control-plane/TESTING.md` (unit, VS Code integration, control-plane pytest) — run via CI gates; local optional

## 🙏 Acknowledgments

Built with:
- [VS Code Extension API](https://code.visualstudio.com/api)
- [FastAPI](https://fastapi.tiangolo.com/)
- Inspired by Vercel, Supabase, and Odoo.sh control planes

---

**Made with ❤️ by InsightPulse AI**
