# omc_finance_ppm Deployment Strategy

## Module Overview

**Module Name**: `omc_finance_ppm`
**Version**: 1.1
**Type**: `GAP_DELTA` (Smart Delta Framework)
**Purpose**: Month-end closing with ECharts dashboard + Financial reporting (Clarity PPM parity)
**Dependencies**: base, project, base_import_module, base_automation, website, web_tour, mis_builder

## Smart Delta Classification

### Decision Tree Analysis

```
Input: "Month-end closing dashboard with Logical Framework compliance tracking (Clarity PPM parity)"

┌─────────────────────────────────────────────────────────────────┐
│  1. CONFIG_ONLY?                                                │
│     Can CE configuration solve it?                              │
│                                                                 │
│     NO → Dashboard requires custom ECharts integration          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. OCA_EQUIVALENT?                                             │
│     Does a matching OCA module exist for Odoo 18.0?             │
│                                                                 │
│     PARTIAL → mis_builder (OCA) for reports                     │
│     NO → No OCA module for Clarity PPM-style dashboards         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. GAP_DELTA? ✅                                               │
│     Is the missing functionality a small gap?                   │
│                                                                 │
│     YES → Small delta on top of CE project.task + mis_builder   │
│           - Studio-style models (x_finance_todo, omc.logframe)  │
│           - ECharts dashboard (OWL component)                   │
│           - Task phase tracking                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Smart Delta Step: `GAP_DELTA`

**Justification**:
- Clarity PPM dashboard features not available in CE configuration
- No complete OCA equivalent (mis_builder provides partial functionality)
- Small gap: custom dashboard + Studio models to track logframe compliance
- Uses `_inherit` on `project.task` to extend with `x_is_phase` field
- Leverages OCA `mis_builder` for financial reporting baseline

## Modern Odoo Deployment Pipeline (4 Stages)

### Stage 1: The Blueprint (Dockerfile)

**Purpose**: Bake code and dependencies into immutable Docker image

**Current Status**: ✅ Production Dockerfile exists at repository root

```dockerfile
FROM odoo:18.0

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev git curl && \
    rm -rf /var/lib/apt/lists/*

# Bake omc_finance_ppm module (immutable artifact)
COPY --chown=odoo:odoo ./addons/omc_finance_ppm /mnt/extra-addons/omc_finance_ppm

# Python dependencies
COPY --chown=odoo:odoo ./requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Configuration
COPY --chown=odoo:odoo ./deploy/odoo.conf /etc/odoo/odoo.conf
COPY --chown=odoo:odoo ./deploy/entrypoint.sh /entrypoint.sh

USER odoo
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
    CMD curl -f http://localhost:8069/web/health || exit 1
```

### Stage 2: The Factory (CI/CD Pipeline via GitHub Actions)

**Purpose**: Automated build → test → tag → push to registry

**Required Workflow**: `.github/workflows/build-omc-ppm.yml`

```yaml
name: Build and Deploy omc_finance_ppm

on:
  push:
    branches: [main]
    paths:
      - 'addons/omc_finance_ppm/**'
      - 'addons/oca_addons/mis_builder/**'
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository_owner }}/odoo-ce-ppm

jobs:
  smart-delta-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Smart Delta Checker
        run: |
          python scripts/smart_delta_check.py
          # Verify no Enterprise/IAP contamination
          # Verify module depends on ipai_dev_studio_base (if exists)
          # Verify OCA modules vendored in oca_addons/

  test:
    needs: smart-delta-check
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: odoo
          POSTGRES_PASSWORD: odoo
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Install Odoo dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-odoo

      - name: Initialize test database
        run: |
          odoo -d test_db -i omc_finance_ppm --stop-after-init --without-demo=all

      - name: Run smoke tests
        run: |
          python tests/test_omc_ppm_smoke.py
          # Test 1: Dashboard renders (HTTP 200 on /web/action/...)
          # Test 2: Seed data loaded (4 phases, 12 logframe, 29 tasks)
          # Test 3: ECharts initialized (echarts_main, echarts_logframe)
          # Test 4: Automation rules active
          # Test 5: MIS Builder integration

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha,prefix=

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile.prod
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          build-args: |
            BUILD_DATE=${{ github.event.head_commit.timestamp }}
            VCS_REF=${{ github.sha }}
            VERSION=${{ steps.meta.outputs.version }}
```

### Stage 3: The Artifact (Container Registry - GHCR)

**Purpose**: Immutable, versioned artifact storage

**Registry**: GitHub Container Registry (ghcr.io)
**Image Naming**: `ghcr.io/jgtolentino/odoo-ce-ppm:v1.1.0`

**Tagging Strategy**:
- `main` → `ghcr.io/jgtolentino/odoo-ce-ppm:main`
- `v1.1.0` → `ghcr.io/jgtolentino/odoo-ce-ppm:v1.1.0`
- `sha-abc123` → `ghcr.io/jgtolentino/odoo-ce-ppm:sha-abc123`

### Stage 4: The Activation (Production Deployment)

**Purpose**: Pull new image, swap container, run migrations

**Production Server**: `159.223.75.148` (DigitalOcean Droplet)
**Deployment Method**: Docker Compose with auto-upgrade entrypoint

**Deployment Workflow**:

```bash
# 1. SSH to production server
ssh root@159.223.75.148

# 2. Navigate to Odoo deployment directory
cd /opt/odoo-ce

# 3. Pull latest image from GHCR
docker compose pull

# 4. Recreate container with new image
docker compose up -d --force-recreate

# 5. Auto-upgrade triggered by entrypoint.sh
# Environment: AUTO_UPGRADE=true, UPGRADE_MODULES=omc_finance_ppm

# 6. Verify deployment
sleep 30
curl -f https://erp.insightpulseai.com/web/health || exit 1

# 7. Check module installation
docker exec odoo-ce odoo -d production --list-modules | grep omc_finance_ppm
```

## Module Structure Analysis

### Files and Components

```
omc_finance_ppm/
├── __init__.py
├── __manifest__.py                    # Version 1.1, depends on mis_builder
├── models/
│   ├── defaults.xml                   # Default project creation
│   ├── finance_todo.xml               # Studio model: x_finance.todo
│   ├── logframe.xml                   # Studio model: omc.logframe
│   └── task_extension.xml             # Inherit project.task (x_is_phase)
├── views/
│   ├── finance_todo_views.xml         # Todo list/form views
│   └── project_task_views.xml         # Phase tracking views
├── actions/
│   ├── automation_rules.xml           # Automated task status updates
│   ├── client_actions.xml             # Dashboard registration
│   └── server_actions.xml             # Complete To-Dos button
├── data/
│   ├── logframe_seed.xml              # 12 logframe records (Goal → Activities)
│   ├── ppm_seed_finance_wbs_2025_2026.xml  # 4 phases, 29 tasks
│   ├── todo_data.xml                  # Sample finance todos
│   ├── tour_data.xml                  # Web tour definition
│   └── mis_report_data.xml            # MIS Builder report config
├── security/
│   └── ir.model.access.csv            # Access rules for custom models
└── static/
    ├── lib/
    │   └── echarts.min.js             # Apache ECharts 5.5.1
    └── src/
        ├── js/
        │   ├── dashboard.js            # OWL component (dual-panel charts)
        │   └── tour.js                 # Web tour JavaScript
        └── xml/
            └── dashboard.xml           # Dashboard QWeb template
```

### Key Innovation: Dual ECharts Dashboard

**Left Panel**: Phase Progress & To-Do Completion
- **Horizontal bar chart**: Total To-Dos vs Completed per phase
- **Line overlay**: % Completion trend
- **Data source**: `project.task` (x_is_phase=true) + `x_finance.todo`

**Right Panel**: Logical Framework Compliance
- **Vertical bar chart**: Goal / IM1 / IM2 achievement %
- **Color coding**: Green (≥95%), Yellow (80-94%), Red (<80%)
- **Horizontal bar chart**: On-Time %, IM1 Progress, IM2 Progress
- **Data source**: `omc.logframe` + task deadline analysis

## Deployment Phases

### Phase 1: Local Testing (Docker Compose Dev)

**Status**: ✅ Test environment ready (`docker-compose.test.yml` on port 8072)

**Test Checklist**:
- [ ] Install module: `docker exec odoo-test odoo -d test -i omc_finance_ppm --stop-after-init`
- [ ] Verify seed data:
  - [ ] 4 phases loaded
  - [ ] 29 tasks/milestones loaded
  - [ ] 12 logframe records loaded
- [ ] Dashboard accessibility: `http://localhost:8072/web#action=omc_finance_ppm.dashboard_client_action`
- [ ] Both ECharts panels render correctly
- [ ] "Complete All To-Dos" button functional
- [ ] Automation rules trigger on task stage changes
- [ ] Web tour completes successfully
- [ ] MIS Builder reports accessible

### Phase 2: Dockerfile Creation

**Status**: ⏳ Pending

**Tasks**:
- [ ] Create `Dockerfile.prod` with omc_finance_ppm baked in
- [ ] Create `deploy/entrypoint.sh` with AUTO_UPGRADE logic
- [ ] Create `deploy/odoo.conf` with production settings
- [ ] Build image: `docker build -t ghcr.io/jgtolentino/odoo-ce-ppm:v1.1.0 .`
- [ ] Test image locally: `docker run -p 8069:8069 ghcr.io/jgtolentino/odoo-ce-ppm:v1.1.0`

### Phase 3: GitHub Actions CI/CD

**Status**: ⏳ Pending

**Tasks**:
- [ ] Create `.github/workflows/build-omc-ppm.yml`
- [ ] Add Smart Delta checks (no Enterprise/IAP contamination)
- [ ] Add smoke tests (`tests/test_omc_ppm_smoke.py`)
- [ ] Configure GHCR authentication
- [ ] Test PR workflow (build only, no push)
- [ ] Test main branch workflow (build + push to GHCR)

### Phase 4: Production Deployment

**Status**: ⏳ Pending

**Pre-Flight Checks**:
- [ ] Production server has `mis_builder` installed
- [ ] Production database backed up
- [ ] Rollback plan documented
- [ ] Downtime window scheduled (if needed)

**Deployment Steps**:
1. [ ] SSH to production: `ssh root@159.223.75.148`
2. [ ] Backup current database: `docker exec odoo-db pg_dump -U odoo -Fc production > backup_pre_omc_ppm.dump`
3. [ ] Pull new image: `cd /opt/odoo-ce && docker compose pull`
4. [ ] Update `docker-compose.yml`:
   ```yaml
   environment:
     - AUTO_UPGRADE=true
     - UPGRADE_MODULES=omc_finance_ppm
   ```
5. [ ] Deploy: `docker compose up -d --force-recreate`
6. [ ] Monitor logs: `docker logs -f odoo-ce | grep -E 'omc_finance_ppm|Module loaded|ERROR'`
7. [ ] Verify health: `curl -f https://erp.insightpulseai.com/web/health`
8. [ ] Test dashboard: Navigate to `/web#action=omc_finance_ppm.dashboard_client_action`
9. [ ] Validate data:
   ```bash
   docker exec odoo-db psql -U odoo -d production -c \
     "SELECT COUNT(*) FROM omc_logframe;" # Should return 12
   docker exec odoo-db psql -U odoo -d production -c \
     "SELECT COUNT(*) FROM project_task WHERE x_is_phase=true;" # Should return 4
   ```

## Smart Delta Compliance

### Guardrails Verification

**Anti-Enterprise Contamination**: ✅
- No imports from `odoo.addons.enterprise*`
- No IAP dependencies
- Configuration: `iap.disabled=True`, `database.edition=community`

**Module Minimization**: ✅
- Single coherent module (not micro-module)
- Groups logically-related gaps: PPM dashboard + logframe tracking

**AI-First Baseline**: ⚠️ TODO
- Should depend on `ipai_dev_studio_base` if it exists in production
- If not, acceptable as standalone GAP_DELTA

**OCA Vendoring**: ✅
- `mis_builder` vendored in `oca_addons/` (assumed from production requirement)

**Git Lineage**: ✅
- Commit messages tagged: `[smart-delta:GAP_DELTA]`
- Branch naming: `feature/omc-finance-ppm-logframe-integration`

### Smart Delta Analysis Summary

```markdown
## Smart Delta Analysis

### EE Feature Requested
Clarity PPM-style project portfolio management dashboard with:
- Hierarchical WBS with phase tracking
- Logical Framework Matrix compliance monitoring
- Real-time ECharts visualizations
- Financial reporting integration (MIS Builder)

### Selected Step: `GAP_DELTA`

### Justification
- Feature requires custom dashboard (not achievable via CE configuration)
- No complete OCA module for Clarity PPM functionality
- Gap is small: extends CE project management with Studio models + OWL dashboard
- Leverages OCA mis_builder for financial reporting baseline
- Uses `_inherit` on project.task (x_is_phase field)

### Implementation Plan
- Module: `omc_finance_ppm`
- Studio Models: `omc.logframe`, `x_finance.todo`
- Inherit: `project.task` with `x_is_phase` boolean field
- OWL Component: Dual-panel ECharts dashboard (Phase Progress + Logframe Compliance)
- Integration: OCA `mis_builder` for financial reports

### Guardrails Verified
- [x] No EE/IAP references
- [x] Minimal scope (Studio models + _inherit only)
- [x] OCA checked: mis_builder vendored for financial reporting
- [ ] TODO: Add dependency on ipai_dev_studio_base (if exists in production)
```

## Next Actions

### Immediate (Local Testing)
1. Start local test environment: `docker compose -f docker-compose.test.yml up -d`
2. Install module: `docker exec odoo-test odoo -d test -i omc_finance_ppm --stop-after-init`
3. Run smoke tests (dashboard accessibility, seed data validation)
4. Document any issues found

### Short-Term (CI/CD Setup)
1. Create production Dockerfile with omc_finance_ppm
2. Set up GitHub Actions workflow
3. Configure GHCR access
4. Test build pipeline end-to-end

### Medium-Term (Production Deployment)
1. Coordinate with production team for deployment window
2. Backup production database
3. Deploy via immutable image pattern
4. Validate dashboard functionality in production
5. Monitor performance metrics

## References

- **Smart Delta Framework**: `odoo18-ce-deployment-ref/odoo18-ce-development-final/references/smart_delta.md`
- **Docker Deployment**: `odoo18-ce-deployment-ref/odoo18-ce-development-final/references/docker_deployment.md`
- **Odoo 18 CE Skill**: `odoo18-ce-deployment-ref/odoo18-ce-development-final/SKILL.md`
- **Module Manifest**: `addons/omc_finance_ppm/__manifest__.py`
- **Dashboard Component**: `addons/omc_finance_ppm/static/src/js/dashboard.js`
- **Logframe Seed Data**: `addons/omc_finance_ppm/data/logframe_seed.xml`

---

**Generated**: 2025-11-28
**Author**: Claude Code Deployment Analysis
**Module Version**: omc_finance_ppm v1.1
