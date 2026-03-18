# Live State Definition

> "Live" is not one state. It is four separate truths, each independently verifiable.

## Four gates

### 1. Engineering-live

The local development runtime works deterministically.

| Check | Verification |
|-------|-------------|
| One canonical Docker context | `docker context inspect colima-odoo` succeeds |
| Devcontainer boots | VS Code Dev Containers connects without error |
| Odoo + PostgreSQL reachable | `odoo-bin --stop-after-init` exits 0 |
| Tests can run | `scripts/dev/docker_contract_check.sh` exits 0 |

**Blocker if not met**: Cannot develop, test, or verify changes locally.

### 2. Platform-live

Azure target environment exists and resources are provisioned.

| Check | Verification |
|-------|-------------|
| Container Apps provisioned | ARM REST query shows `provisioningState: Succeeded` |
| PostgreSQL Flexible Server reachable | `az postgres flexible-server show` returns healthy |
| Key Vaults exist | `az keyvault list` shows `kv-ipai-dev` |
| Container Registries exist | `az acr list` shows `ipaiodoodevacr` |

**Blocker if not met**: Cannot deploy workloads to Azure.

### 3. Edge-live

Front Door route reaches a healthy backend through the public ingress.

| Check | Verification |
|-------|-------------|
| Front Door endpoint resolves | `nslookup ipai-fd-dev-ep-*.azurefd.net` returns IP |
| TLS terminates | `curl -sI https://erp.insightpulseai.com` returns HTTP headers |
| Origin health probe passes | Front Door health probe returns 200 from origin |
| Response is not just SPA shell | Body contains Odoo content, not empty React shell |

**Blocker if not met**: Public users cannot reach the platform.

### 4. Business-live

The first target workflow completes end-to-end through the production path.

| Check | Verification |
|-------|-------------|
| ERP login works via public edge | User authenticates at `erp.insightpulseai.com` |
| First business workflow passes | Target workflow (e.g., invoice creation) completes |
| Rollback path documented and tested | Rollback runbook exists and has been dry-run |
| Evidence pack produced | `docs/evidence/<date>/` contains proof artifacts |

**Blocker if not met**: Platform is deployed but not operational.

## Current state (2026-03-17)

| Gate | Status | Notes |
|------|--------|-------|
| Engineering-live | Yellow | Containers running but Docker context drift causes terminal failures |
| Platform-live | Green | 82 resources confirmed via ARM REST API |
| Edge-live | Yellow | Front Door exists but origin health unverified |
| Business-live | Red | No end-to-end workflow evidence |
