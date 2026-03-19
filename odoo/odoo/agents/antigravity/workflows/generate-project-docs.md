---
description: Generate or refresh project documentation (README.md) based on repository structure
---

# Generate Project Docs

## Goal

Produce/refresh README.md based on repository structure and actual usage, with verified quickstart commands.

## Steps

### 1. Inventory Repository

- Top-level directories and their purposes
- Key entrypoints (main.py, index.js, odoo-bin, etc.)
- Configuration files (package.json, pyproject.toml, **manifest**.py)
- Documentation files (existing README, CONTRIBUTING, etc.)

### 2. Detect Runtime & Tooling

- **Runtime**: Node.js, Python, Go, Odoo, etc.
- **Package manager**: npm, pnpm, yarn, pip, poetry
- **Build tooling**: webpack, vite, rollup, setuptools
- **Test framework**: jest, pytest, mocha
- **Linter/formatter**: eslint, ruff, black

### 3. Draft README Sections

#### Overview

- Project name and purpose
- Key features (3-5 bullets)
- Tech stack

#### Prerequisites

- Runtime version (Node 18+, Python 3.12+, etc.)
- System dependencies (PostgreSQL, Redis, etc.)
- Required tools (Docker, git, etc.)

#### Quickstart

```bash
# Clone
git clone <repo-url>
cd <repo-name>

# Install dependencies
npm install  # or pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings

# Run
npm run dev  # or python main.py
```

#### Scripts/Commands

| Command         | Description              |
| --------------- | ------------------------ |
| `npm start`     | Start development server |
| `npm test`      | Run tests                |
| `npm run build` | Build for production     |

#### Environment Variables

Reference `.env.example` with descriptions:

```bash
DATABASE_URL=postgresql://localhost/mydb  # Database connection string
API_KEY=your-key-here                     # External API key
PORT=3000                                 # Server port
```

#### Tests

```bash
# Run all tests
npm test

# Run specific test file
npm test -- path/to/test.js

# Coverage
npm run test:coverage
```

#### Deployment

- CI/CD setup (GitHub Actions, GitLab CI)
- Deployment targets (Vercel, Heroku, DigitalOcean)
- Production build steps

### 4. Validate Quickstart

Run the quickstart commands (best-effort) and record results:

```bash
# Test install
npm install 2>&1 | tee install.log

# Test build
npm run build 2>&1 | tee build.log

# Test start (with timeout)
timeout 10s npm start 2>&1 | tee start.log || true
```

Include validation results in artifact.

## Output Format

### README.md

Complete, production-ready README with all sections.

### Validation Report

```markdown
## Quickstart Validation

### Install

✅ `npm install` completed successfully (47 packages installed)

### Build

✅ `npm run build` completed successfully (bundle size: 234KB)

### Start

✅ Server started on http://localhost:3000
⚠️ Stopped after 10s timeout (expected for validation)

### Issues Found

- Missing `.env.example` file (created from `.env` template)
- Outdated Node version in README (updated to 18+)
```

## Verification

- [ ] README is complete and accurate
- [ ] Quickstart commands are verified
- [ ] All scripts are documented
- [ ] Environment variables are explained
- [ ] Deployment steps are clear
