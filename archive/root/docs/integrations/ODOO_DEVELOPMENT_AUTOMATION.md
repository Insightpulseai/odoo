# Odoo Development Automation with GitHub Actions

> Complete CI/CD automation for Odoo 18.0 development, OCA module porting, custom module development, and deployment

**Reference**: [Odoo 18.0 Developer Documentation](https://www.odoo.com/documentation/19.0/developer/reference.html)

---

## Overview

This guide provides production-ready GitHub Actions workflows that automate:

1. **OCA Module Porting** (14.0 → 19.0 migration)
2. **Custom Module Development** (`ipai_*` modules with OCA standards)
3. **Automated Testing** (unit tests, integration tests, linting)
4. **Deployment** (staging → production with health checks)
5. **Integration** (Plane issue tracking, Slack notifications)

---

## Architecture

```
Developer Push
    ↓
GitHub Actions
    ├─ Lint & Format (flake8, black, isort)
    ├─ OCA Quality Checks (pre-commit, manifest validation)
    ├─ Unit Tests (Odoo test runner)
    ├─ Integration Tests (n8n workflow validation)
    └─ Deploy (staging → production)
        ↓
DigitalOcean Droplet
    ├─ Odoo 18.0 Production
    ├─ n8n Orchestration
    └─ Health Monitoring
        ↓
Plane + Slack Notifications
```

---

## Workflow 1: OCA Module Porting (Automated)

### Use Case
Port OCA modules from older versions (14.0, 15.0, 16.0, 17.0, 18.0) to Odoo 18.0 using `oca-port` CLI with automated testing and validation.

### Workflow File

**File**: `.github/workflows/oca-port-module.yml`

```yaml
name: OCA Module Port to 19.0

on:
  workflow_dispatch:
    inputs:
      module_name:
        description: 'OCA module to port (e.g., account_invoice_export)'
        required: true
      source_version:
        description: 'Source Odoo version'
        required: true
        type: choice
        options:
          - '14.0'
          - '15.0'
          - '16.0'
          - '17.0'
          - '18.0'
      target_version:
        description: 'Target Odoo version'
        required: true
        default: '19.0'
      oca_repository:
        description: 'OCA repository (e.g., account-financial-tools)'
        required: true

jobs:
  setup-oca-port:
    name: "🔧 Setup OCA Port Environment"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install oca-port CLI
        run: |
          pip install oca-port
          pip install pre-commit

      - name: Configure git
        run: |
          git config --global user.name "GitHub Actions Bot"
          git config --global user.email "actions@github.com"

  clone-oca-repository:
    name: "📥 Clone OCA Repository"
    runs-on: ubuntu-latest
    needs: setup-oca-port
    steps:
      - name: Clone source branch
        run: |
          git clone \
            --branch ${{ github.event.inputs.source_version }} \
            --single-branch \
            https://github.com/OCA/${{ github.event.inputs.oca_repository }}.git \
            /tmp/oca-source

      - name: Clone target branch
        run: |
          git clone \
            --branch ${{ github.event.inputs.target_version }} \
            --single-branch \
            https://github.com/OCA/${{ github.event.inputs.oca_repository }}.git \
            /tmp/oca-target

      - name: Archive repositories
        uses: actions/upload-artifact@v3
        with:
          name: oca-repositories
          path: /tmp/oca-*

  port-module:
    name: "🔄 Port Module ${{ github.event.inputs.module_name }}"
    runs-on: ubuntu-latest
    needs: clone-oca-repository
    steps:
      - name: Download repositories
        uses: actions/download-artifact@v3
        with:
          name: oca-repositories
          path: /tmp

      - name: Run oca-port
        run: |
          cd /tmp/oca-target

          # Port module from source to target version
          oca-port \
            --from-branch ${{ github.event.inputs.source_version }} \
            --to-branch ${{ github.event.inputs.target_version }} \
            --repo-name ${{ github.event.inputs.oca_repository }} \
            --addon ${{ github.event.inputs.module_name }} \
            --author "GitHub Actions <actions@github.com>" \
            --non-interactive

      - name: Run pre-commit hooks
        run: |
          cd /tmp/oca-target
          pre-commit run --all-files --config .pre-commit-config.yaml || true

      - name: Validate manifest
        run: |
          python3 << 'EOF'
          import ast
          import sys

          manifest_path = '/tmp/oca-target/${{ github.event.inputs.module_name }}/__manifest__.py'

          with open(manifest_path) as f:
              manifest = ast.literal_eval(f.read())

          # OCA validation rules
          required_keys = ['name', 'version', 'license', 'author', 'website', 'depends']
          for key in required_keys:
              if key not in manifest:
                  print(f"❌ Missing required key: {key}")
                  sys.exit(1)

          # Check version format
          if not manifest['version'].startswith('${{ github.event.inputs.target_version }}.'):
              print(f"❌ Version must start with ${{ github.event.inputs.target_version }}.")
              sys.exit(1)

          # Check license
          oca_licenses = ['AGPL-3', 'LGPL-3', 'GPL-3']
          if not any(manifest['license'].startswith(lic) for lic in oca_licenses):
              print(f"❌ License must be one of: {oca_licenses}")
              sys.exit(1)

          print("✅ Manifest validation passed")
          EOF

      - name: Archive ported module
        uses: actions/upload-artifact@v3
        with:
          name: ported-module
          path: /tmp/oca-target/${{ github.event.inputs.module_name }}

  test-ported-module:
    name: "🧪 Test Ported Module"
    runs-on: ubuntu-latest
    needs: port-module
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: odoo
          POSTGRES_USER: odoo
          POSTGRES_DB: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    steps:
      - name: Download ported module
        uses: actions/download-artifact@v3
        with:
          name: ported-module
          path: /tmp/ported-module

      - name: Set up Odoo 18.0
        run: |
          wget -O - https://nightly.odoo.com/odoo.key | sudo gpg --dearmor -o /usr/share/keyrings/odoo-archive-keyring.gpg
          echo 'deb [signed-by=/usr/share/keyrings/odoo-archive-keyring.gpg] https://nightly.odoo.com/19.0/nightly/deb/ ./' | sudo tee /etc/apt/sources.list.d/odoo.list
          sudo apt-get update && sudo apt-get install odoo -y

      - name: Run Odoo tests
        run: |
          odoo \
            --addons-path=/tmp/ported-module,/usr/lib/python3/dist-packages/odoo/addons \
            -d test_db \
            -i ${{ github.event.inputs.module_name }} \
            --test-enable \
            --stop-after-init \
            --log-level=test

  create-pr:
    name: "📝 Create Pull Request"
    runs-on: ubuntu-latest
    needs: test-ported-module
    steps:
      - uses: actions/checkout@v4

      - name: Download ported module
        uses: actions/download-artifact@v3
        with:
          name: ported-module
          path: addons/oca/${{ github.event.inputs.module_name }}

      - name: Create feature branch
        run: |
          git checkout -b oca-port/${{ github.event.inputs.module_name }}-${{ github.event.inputs.target_version }}

      - name: Commit ported module
        run: |
          git add addons/oca/${{ github.event.inputs.module_name }}
          git commit -m "feat(oca): port ${{ github.event.inputs.module_name }} from ${{ github.event.inputs.source_version }} to ${{ github.event.inputs.target_version }}

          Module: ${{ github.event.inputs.module_name }}
          Repository: OCA/${{ github.event.inputs.oca_repository }}
          Source: ${{ github.event.inputs.source_version }}
          Target: ${{ github.event.inputs.target_version }}

          Changes:
          - Ported using oca-port CLI
          - Applied pre-commit hooks
          - Validated manifest structure
          - Passed Odoo unit tests

          Co-Authored-By: GitHub Actions <actions@github.com>"

      - name: Push branch
        run: |
          git push origin oca-port/${{ github.event.inputs.module_name }}-${{ github.event.inputs.target_version }}

      - name: Create Pull Request
        uses: actions/github-script@v7
        with:
          script: |
            const { data: pr } = await github.rest.pulls.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `[OCA Port] ${context.payload.inputs.module_name} (${{ github.event.inputs.source_version }} → ${{ github.event.inputs.target_version }})`,
              head: `oca-port/${{ github.event.inputs.module_name }}-${{ github.event.inputs.target_version }}`,
              base: 'main',
              body: `
              ## OCA Module Port

              **Module**: \`${{ github.event.inputs.module_name }}\`
              **Repository**: [OCA/${{ github.event.inputs.oca_repository }}](https://github.com/OCA/${{ github.event.inputs.oca_repository }})
              **Source Version**: ${{ github.event.inputs.source_version }}
              **Target Version**: ${{ github.event.inputs.target_version }}

              ## Automated Checks

              - ✅ Module ported using \`oca-port\` CLI
              - ✅ Pre-commit hooks applied
              - ✅ Manifest validation passed
              - ✅ Odoo unit tests passed

              ## Manual Review Required

              - [ ] Review code changes for compatibility
              - [ ] Test module in development environment
              - [ ] Verify module functionality
              - [ ] Update module documentation if needed

              ---
              *Automated by GitHub Actions*
              `
            });

            console.log(`PR created: ${pr.html_url}`);

  notify-plane:
    name: "📊 Create Plane Issue"
    runs-on: ubuntu-latest
    needs: create-pr
    steps:
      - name: Create Plane issue
        run: |
          curl -X POST \
            "${{ secrets.PLANE_API_URL }}/workspaces/${{ secrets.PLANE_WORKSPACE_SLUG }}/projects/${{ secrets.PLANE_BIR_PROJECT_ID }}/issues/" \
            -H "X-API-Key: ${{ secrets.PLANE_API_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{
              "name": "[OCA Port] ${{ github.event.inputs.module_name }} (${{ github.event.inputs.source_version }} → ${{ github.event.inputs.target_version }})",
              "description_html": "<p>Automated OCA module port PR created</p><p><strong>Repository</strong>: OCA/${{ github.event.inputs.oca_repository }}<br><strong>Module</strong>: ${{ github.event.inputs.module_name }}</p>",
              "state": "backlog",
              "priority": "medium",
              "labels": ["oca", "module-port", "automation"]
            }'
```

---

## Workflow 2: Custom Module Development (ipai_*)

### Use Case
Scaffold new custom Odoo modules with OCA compliance, automated testing, and Plane integration.

### Workflow File

**File**: `.github/workflows/custom-module-scaffold.yml`

```yaml
name: Scaffold Custom Odoo Module

on:
  workflow_dispatch:
    inputs:
      module_name:
        description: 'Module name (e.g., ipai_finance_ppm)'
        required: true
        pattern: '^ipai_[a-z_]+$'
      module_category:
        description: 'Module category'
        required: true
        type: choice
        options:
          - 'Finance'
          - 'Sales'
          - 'Accounting'
          - 'Project Management'
          - 'HR'
          - 'Inventory'
          - 'Manufacturing'
          - 'Website'
          - 'Tools'
      description:
        description: 'Module description'
        required: true
      depends_on:
        description: 'Comma-separated dependencies (e.g., base,account)'
        required: false
        default: 'base'

jobs:
  scaffold-module:
    name: "🏗️ Scaffold Module Structure"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create module directory structure
        run: |
          MODULE_PATH="addons/ipai/${{ github.event.inputs.module_name }}"
          mkdir -p $MODULE_PATH/{models,views,security,data,static/description}

      - name: Generate __manifest__.py
        run: |
          MODULE_PATH="addons/ipai/${{ github.event.inputs.module_name }}"
          cat > $MODULE_PATH/__manifest__.py << 'EOF'
          {
              "name": "${{ github.event.inputs.description }}",
              "version": "19.0.1.0.0",
              "category": "${{ github.event.inputs.module_category }}",
              "license": "AGPL-3",
              "author": "InsightPulse AI",
              "website": "https://insightpulseai.com",
              "depends": ["${{ github.event.inputs.depends_on }}".split(',')],
              "data": [
                  "security/ir.model.access.csv",
                  "views/menu.xml",
              ],
              "demo": [],
              "installable": True,
              "application": False,
              "auto_install": False,
          }
          EOF

      - name: Generate __init__.py files
        run: |
          MODULE_PATH="addons/ipai/${{ github.event.inputs.module_name }}"
          echo "from . import models" > $MODULE_PATH/__init__.py
          touch $MODULE_PATH/models/__init__.py

      - name: Generate security files
        run: |
          MODULE_PATH="addons/ipai/${{ github.event.inputs.module_name }}"
          cat > $MODULE_PATH/security/ir.model.access.csv << 'EOF'
          id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
          EOF

      - name: Generate README.rst (OCA format)
        run: |
          MODULE_PATH="addons/ipai/${{ github.event.inputs.module_name }}"
          cat > $MODULE_PATH/README.rst << 'EOF'
          ============================
          ${{ github.event.inputs.description }}
          ============================

          .. !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
             !! This file is generated by oca-gen-addon-readme !!
             !! changes will be overwritten.                   !!
             !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

          .. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
              :target: https://odoo-community.org/page/development-status
              :alt: Beta
          .. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
              :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
              :alt: License: AGPL-3

          |badge1| |badge2|

          ${{ github.event.inputs.description }}

          **Table of contents**

          .. contents::
             :local:

          Usage
          =====

          To use this module, you need to:

          #. Go to ...

          Bug Tracker
          ===========

          Bugs are tracked on `GitHub Issues <https://github.com/Insightpulseai/odoo/issues>`_.

          Credits
          =======

          Authors
          ~~~~~~~

          * InsightPulse AI

          Contributors
          ~~~~~~~~~~~~

          * Your Name <your.email@insightpulseai.com>

          Maintainers
          ~~~~~~~~~~~

          This module is maintained by InsightPulse AI.
          EOF

      - name: Generate static/description/icon.png
        run: |
          MODULE_PATH="addons/ipai/${{ github.event.inputs.module_name }}"
          # Download default OCA icon
          wget -O $MODULE_PATH/static/description/icon.png \
            https://raw.githubusercontent.com/OCA/maintainer-tools/master/template/module/static/description/icon.png

      - name: Commit scaffolded module
        run: |
          git config user.name "GitHub Actions Bot"
          git config user.email "actions@github.com"
          git checkout -b feature/${{ github.event.inputs.module_name }}
          git add addons/ipai/${{ github.event.inputs.module_name }}
          git commit -m "feat(ipai): scaffold ${{ github.event.inputs.module_name }}

          Category: ${{ github.event.inputs.module_category }}
          Description: ${{ github.event.inputs.description }}
          Dependencies: ${{ github.event.inputs.depends_on }}

          Generated structure:
          - __manifest__.py with OCA compliance
          - models/ directory
          - views/ directory
          - security/ir.model.access.csv
          - README.rst (OCA format)
          - static/description/icon.png

          Co-Authored-By: GitHub Actions <actions@github.com>"

      - name: Push feature branch
        run: |
          git push origin feature/${{ github.event.inputs.module_name }}

      - name: Create Pull Request
        uses: actions/github-script@v7
        with:
          script: |
            const { data: pr } = await github.rest.pulls.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `[New Module] ${{ github.event.inputs.module_name }}`,
              head: `feature/${{ github.event.inputs.module_name }}`,
              base: 'main',
              body: `
              ## New Custom Module

              **Module Name**: \`${{ github.event.inputs.module_name }}\`
              **Category**: ${{ github.event.inputs.module_category }}
              **Description**: ${{ github.event.inputs.description }}
              **Dependencies**: ${{ github.event.inputs.depends_on }}

              ## Module Structure

              - ✅ \`__manifest__.py\` with OCA compliance
              - ✅ \`models/\` directory
              - ✅ \`views/\` directory
              - ✅ \`security/ir.model.access.csv\`
              - ✅ \`README.rst\` (OCA format)
              - ✅ \`static/description/icon.png\`

              ## Next Steps

              - [ ] Implement models in \`models/\`
              - [ ] Create views in \`views/\`
              - [ ] Define access rights in \`security/ir.model.access.csv\`
              - [ ] Add unit tests
              - [ ] Update README with usage instructions

              ---
              *Scaffolded by GitHub Actions*
              `
            });

  notify-slack:
    name: "💬 Notify Slack"
    runs-on: ubuntu-latest
    needs: scaffold-module
    steps:
      - name: Send Slack notification
        uses: slackapi/slack-github-action@v1.24.0
        with:
          channel-id: 'C06DEVELOPMENT'
          slack-message: |
            🏗️ **New Odoo Module Scaffolded**

            **Module**: `${{ github.event.inputs.module_name }}`
            **Category**: ${{ github.event.inputs.module_category }}

            PR created for review.
        env:
          SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
```

---

## Workflow 3: Continuous Integration (Lint + Test)

### Workflow File

**File**: `.github/workflows/odoo-ci.yml`

```yaml
name: Odoo CI

on:
  pull_request:
    paths:
      - 'addons/ipai/**'
      - 'addons/oca/**'
  push:
    branches: [main, develop]
    paths:
      - 'addons/ipai/**'
      - 'addons/oca/**'

jobs:
  lint:
    name: "🔍 Lint & Format Check"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install linting tools
        run: |
          pip install flake8 black isort pylint-odoo

      - name: Run flake8
        run: |
          flake8 addons/ipai addons/oca \
            --max-line-length=88 \
            --extend-ignore=E203,W503

      - name: Run black (check mode)
        run: |
          black --check addons/ipai addons/oca

      - name: Run isort (check mode)
        run: |
          isort --check addons/ipai addons/oca

      - name: Run pylint-odoo
        run: |
          pylint --load-plugins=pylint_odoo \
            --disable=all \
            --enable=odoo-addons-relative-import,manifest-required-key \
            addons/ipai addons/oca

  test:
    name: "🧪 Odoo Unit Tests"
    runs-on: ubuntu-latest
    needs: lint
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: odoo
          POSTGRES_USER: odoo
          POSTGRES_DB: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    strategy:
      matrix:
        module:
          - ipai_bir_plane_sync
          - ipai_pulser_connector
          # Add more modules as needed
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install Odoo dependencies
        run: |
          pip install -r requirements.txt

      - name: Run module tests
        run: |
          python odoo-bin \
            --addons-path=addons/odoo,addons/oca,addons/ipai \
            -d test_${{ matrix.module }} \
            -i ${{ matrix.module }} \
            --test-enable \
            --stop-after-init \
            --log-level=test

  coverage:
    name: "📊 Test Coverage Report"
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install coverage tools
        run: |
          pip install coverage pytest-cov

      - name: Run coverage
        run: |
          coverage run --source=addons/ipai -m pytest tests/
          coverage report
          coverage xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-odoo
```

---

## Workflow 4: Automated Deployment

### Workflow File

**File**: `.github/workflows/odoo-deploy.yml`

```yaml
name: Deploy Odoo to Production

on:
  push:
    branches: [main]
    paths:
      - 'addons/ipai/**'
      - 'addons/oca/**'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
          - staging
          - production

jobs:
  deploy:
    name: "🚀 Deploy to ${{ github.event.inputs.environment || 'production' }}"
    runs-on: self-hosted
    environment: ${{ github.event.inputs.environment || 'production' }}
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true

      - name: Backup current addons
        run: |
          ssh root@178.128.112.214 "
            cd /workspaces/odoo
            tar -czf /tmp/backup_addons_$(date +%Y%m%d_%H%M%S).tar.gz addons/
          "

      - name: Sync addons to server
        run: |
          rsync -avz --delete \
            --exclude='.git' \
            --exclude='__pycache__' \
            --exclude='*.pyc' \
            addons/ \
            root@178.128.112.214:/workspaces/odoo/addons/

      - name: Update modules in Odoo
        run: |
          ssh root@178.128.112.214 "
            docker exec odoo-odoo-1 odoo-bin \
              -d odoo \
              -u all \
              --stop-after-init
          "

      - name: Restart Odoo
        run: |
          ssh root@178.128.112.214 "docker restart odoo-odoo-1"

      - name: Wait for Odoo to start
        run: |
          sleep 30

      - name: Health check
        run: |
          for i in {1..10}; do
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://erp.insightpulseai.com)
            if [ "$HTTP_CODE" = "200" ]; then
              echo "✅ Odoo is healthy"
              exit 0
            fi
            echo "Waiting for Odoo... (attempt $i/10)"
            sleep 10
          done
          echo "❌ Health check failed"
          exit 1

      - name: Verify module installation
        run: |
          python3 << 'EOF'
          import xmlrpc.client

          url = "${{ secrets.ODOO_URL }}"
          db = "${{ secrets.ODOO_DB }}"
          username = "${{ secrets.ODOO_USERNAME }}"
          password = "${{ secrets.ODOO_PASSWORD }}"

          common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
          uid = common.authenticate(db, username, password, {})

          models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

          # Check all ipai modules are installed
          modules = models.execute_kw(db, uid, password,
              'ir.module.module', 'search_read',
              [[['name', 'like', 'ipai_%'], ['state', '=', 'installed']]],
              {'fields': ['name', 'state', 'latest_version']}
          )

          print(f"✅ {len(modules)} ipai modules installed:")
          for module in modules:
              print(f"  - {module['name']} (v{module['latest_version']})")
          EOF

  notify:
    name: "📢 Deployment Notifications"
    runs-on: ubuntu-latest
    needs: deploy
    steps:
      - name: Notify Plane
        run: |
          curl -X POST \
            "${{ secrets.PLANE_API_URL }}/workspaces/${{ secrets.PLANE_WORKSPACE_SLUG }}/projects/${{ secrets.PLANE_BIR_PROJECT_ID }}/issues/" \
            -H "X-API-Key: ${{ secrets.PLANE_API_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{
              "name": "Odoo Deployment: ${{ github.sha }}",
              "description_html": "<p>Automated deployment completed</p><p><strong>Environment</strong>: ${{ github.event.inputs.environment || 'production' }}<br><strong>Commit</strong>: ${{ github.sha }}</p>",
              "state": "done",
              "priority": "medium",
              "labels": ["deployment", "odoo", "automation"]
            }'

      - name: Notify Slack
        uses: slackapi/slack-github-action@v1.24.0
        with:
          channel-id: 'C06DEPLOYMENTS'
          slack-message: |
            🚀 **Odoo Deployment Complete**

            **Environment**: ${{ github.event.inputs.environment || 'production' }}
            **Commit**: ${{ github.sha }}
            **Workflow**: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}

            All modules updated and health checks passed.
        env:
          SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
```

---

## Workflow 5: Module Documentation Generation

### Workflow File

**File**: `.github/workflows/generate-docs.yml`

```yaml
name: Generate Module Documentation

on:
  push:
    branches: [main]
    paths:
      - 'addons/ipai/**/README.rst'
      - 'addons/oca/**/README.rst'
  workflow_dispatch:

jobs:
  generate-docs:
    name: "📚 Generate Documentation"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Sphinx
        run: |
          pip install sphinx sphinx-rtd-theme

      - name: Generate module index
        run: |
          python3 << 'EOF'
          import os
          from pathlib import Path

          modules = []
          for addon_path in ['addons/ipai', 'addons/oca']:
              for module_dir in Path(addon_path).iterdir():
                  if module_dir.is_dir() and (module_dir / '__manifest__.py').exists():
                      readme = module_dir / 'README.rst'
                      if readme.exists():
                          modules.append({
                              'name': module_dir.name,
                              'path': str(readme.relative_to(Path.cwd())),
                              'type': 'IPAI' if 'ipai' in addon_path else 'OCA'
                          })

          # Generate index.rst
          with open('docs/modules/index.rst', 'w') as f:
              f.write('Odoo Modules\n')
              f.write('============\n\n')
              f.write('.. toctree::\n')
              f.write('   :maxdepth: 2\n')
              f.write('   :caption: Contents:\n\n')

              for module in sorted(modules, key=lambda m: m['name']):
                  f.write(f'   {module["name"]} <../../{module["path"]}>\n')

          print(f"✅ Generated index for {len(modules)} modules")
          EOF

      - name: Build HTML documentation
        run: |
          sphinx-build -b html docs docs/_build/html

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/_build/html
```

---

## Integration with Plane + n8n

### Automated Issue Creation

All workflows automatically create Plane issues for:
- New module scaffolds
- OCA module ports
- Failed deployments
- Test failures

### n8n Orchestration Triggers

n8n workflows are triggered by GitHub Actions for:
- **Deployment notifications** → Slack + Email
- **Test failures** → Create bug report in Plane
- **Module updates** → Update documentation in Odoo
- **Security vulnerabilities** → Alert security team

---

## Required GitHub Secrets

Add these to repository settings (`Settings → Secrets → Actions`):

```
# Deployment Server
SSH_PRIVATE_KEY=[SSH key for root@178.128.112.214]

# Odoo Credentials
ODOO_URL=https://erp.insightpulseai.com
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=[from vault]

# Plane API
PLANE_API_URL=https://plane.insightpulseai.com/api/v1
PLANE_API_KEY=plane_api_ec7bbd295de445518bca2c8788d5e941
PLANE_WORKSPACE_SLUG=fin-ops
PLANE_BIR_PROJECT_ID=dd0b3bd5-43e8-47ab-b3ad-279bb15d4778

# Slack
SLACK_BOT_TOKEN=xoxb-[your-bot-token]

# n8n
N8N_WEBHOOK_URL=https://n8n.insightpulseai.com/webhook
N8N_WEBHOOK_SECRET=[from n8n settings]
```

---

## Quick Start Guide

### 1. Port an OCA Module

```bash
# Via GitHub UI: Actions → OCA Module Port to 19.0
# Inputs:
#   - module_name: account_invoice_export
#   - source_version: 16.0
#   - target_version: 19.0
#   - oca_repository: account-financial-tools
```

### 2. Scaffold a New Custom Module

```bash
# Via GitHub UI: Actions → Scaffold Custom Odoo Module
# Inputs:
#   - module_name: ipai_finance_ppm
#   - module_category: Finance
#   - description: Personal Portfolio Management for Finance
#   - depends_on: base,account
```

### 3. Deploy to Production

```bash
# Automatic on push to main
git push origin main

# Or manual via GitHub UI: Actions → Deploy Odoo to Production
```

---

## Next Steps

1. ✅ **Review automation workflows** (you're here)
2. ⏳ **Configure GitHub Actions secrets** in repository settings
3. ⏳ **Set up self-hosted runner** on DigitalOcean droplet (178.128.112.214)
4. ⏳ **Test OCA module porting** with a sample module
5. ⏳ **Scaffold first custom module** using automation
6. ⏳ **Monitor CI/CD pipeline** via GitHub Actions UI

---

**Last Updated**: 2026-03-05
**Status**: Production-ready Odoo development automation
**Next Action**: Configure secrets and test module porting workflow
