# SAP Benchmark Pattern Adaptation

> SAP on Azure is treated as a **benchmark** for enterprise-grade automation rigor.
> This project does NOT run SAP workloads. No SAP services are implemented.

---

## What was borrowed

### 1. Deployment rigor
SAP Deployment Automation Framework enforces strict stage ordering: validate → plan → deploy → verify. This pattern is adopted in all deploy pipelines via the `base-deploy.yml` extends template (Build → Deploy → Smoke → Evidence).

### 2. Landing-zone structure
SAP workload-zone separation (deployer, library, workload, system) maps to our domain separation:
- **deployer** → `infra/` (IaC, Bicep, DNS)
- **library** → `azure-pipelines/templates/` (reusable pipeline components)
- **workload zone** → domain-specific entrypoints (`web/`, `addons/ipai/`, `platform/`, `data-intelligence/`)
- **system** → individual container apps or Databricks bundles

### 3. Automation discipline
SAP automation framework mandates:
- Parameterized deployments (no hardcoded values)
- Environment overlays (dev/staging/prod)
- Azure DevOps as the execution plane
- Evidence artifacts for every deployment

All of these are adopted via shared templates and variable groups.

### 4. Workload-zone separation
Each domain owns its entrypoint pipeline but shares the template spine. This prevents drift while preserving domain autonomy — the same principle SAP uses to separate workload zones from the control plane.

## What was intentionally NOT adopted

### 1. SAP services
No SAP-specific services (NetWeaver, HANA, S/4HANA, LaMa, BTP) are deployed or referenced as runtime dependencies.

### 2. SAP runtime assumptions
SAP assumes specific VM SKUs, OS images (SLES, RHEL), and storage configurations. Our stack uses Azure Container Apps, which has a fundamentally different compute model.

### 3. SAP-specific tooling
- SAP Installation Wizard → not applicable (Odoo installs via pip/Docker)
- SAP Landscape Management → not applicable (ACA manages revisions natively)
- SAP Cloud Connector → not applicable (no SAP BTP integration)
- Concur/Joule → benchmark-only for copilot UX patterns, not integrated

### 4. SAP infrastructure hosting templates
Azure quickstart templates for SAP (e.g., `sap-3-tier-marketplace-image`) are not used. Our IaC is Bicep-native under `infra/azure/`.

## How to verify benchmark-only usage

```bash
# Should return zero results in active pipeline/infra code:
grep -rn "SAP\|HANA\|NetWeaver\|S4HANA\|BTP\|Concur" \
  azure-pipelines/ infra/ platform/ agents/ web/ \
  --include="*.yml" --include="*.bicep" --include="*.tf" \
  | grep -v "benchmark\|reference\|docs\|BENCHMARK\|SAP_BENCHMARK"
```

If this returns hits, those references must be either:
1. Removed (if they introduce SAP runtime dependencies)
2. Documented as benchmark-only with a comment

## Benchmark registry

| SAP Pattern | Adapted As | Location |
|-------------|-----------|----------|
| Deployer/Library convention | Template spine + domain entrypoints | `azure-pipelines/templates/` |
| Workload-zone separation | Domain-owned pipelines with shared templates | `web/`, `platform/`, `data-intelligence/` |
| Parameter files per environment | Bicep parameter overlays | `infra/azure/parameters/` |
| Automation discipline | `extends` policy enforcement | `azure-pipelines/templates/extends/` |
| Evidence/validation gates | Smoke + evidence stages | `smoke-http.yml`, `publish-evidence.yml` |
