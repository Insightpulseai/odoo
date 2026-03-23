# Architecture Benchmark: OUR_ODOOSH_AZURE vs CLOUDPEPPER

## Comparison Matrix

| Dimension | Cloudpepper | Our Azure-Native Stack |
| :--- | :--- | :--- |
| **Hosting Model** | Odoo-specific Hosting Panel | Azure-Native Governed Runtime (ACA) |
| **Staging** | 1-Click Staging (Strong) | Managed via Staging Rehearsal (Rigorous) |
| **Git Deploy** | Built-in Git support | CI/CD via ACR/GitHub Actions |
| **Backups** | Multi-provider (S3/Azure/SFTP) | Azure Snapshot/Backup (Infra-level) |
| **Governance** | Platform/Ops Focused | **Agent Factory V2 (Differentiator)** |
| **AI Plane** | Basic / Generic | **Azure Foundry + Eval Suite (Differentiator)** |

## Key Gaps to Close (Backlog PR-02)

### 1. Staging UX (High Priority)
- **Problem**: Cloudpepper's "1-click staging" is the UX benchmark.
- **Mitigation**: Standardize the `scripts/execute_ap_rehearsal.py` pattern into a productized "Stage" button in the control plane.

### 2. Git-to-ACA Flow
- **Problem**: Cloudpepper simplifies Odoo-specific git deployments.
- **Mitigation**: Normalize the ACR build-and-deploy flow to be as predictable as Odoo.sh.

### 3. Backup Visualization
- **Problem**: Cloudpepper surfaces backup health and targets to the user.
- **Mitigation**: Mirror Azure Backup status into the Supabase control-plane dashboard.

## Strategic Verdict
Cloudpepper is the benchmark for **Developer/Operator Experience (DX/OX)**. Our stack remains the choice for **Enterprise Governance (GX)** and **Agentic Integrity (AX)**. We will adopt Cloudpepper's operational ergonomics without sacrificing our Azure-Foundry-SSOT architecture.
