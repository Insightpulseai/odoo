# PRD — IPAI Odoo SaaS Platform

## 0) Summary

The IPAI Odoo SaaS Platform is an open-source alternative to Odoo.sh, providing a complete lifecycle for Odoo 19 CE + OCA modules, with enterprise-grade provisioning, billing, and AI integration.

## 1) Goals

- **Odoo.sh Parity**: CI/CD, dev branches, backups, and monitoring.
- **Multi-Tenancy**: Automated provisioning of Odoo instances.
- **AI Integration**: Built-in IPAI agents for accounting, devops, and support.
- **Billing**: Integrated subscription management (Stripe).

## 2) Architecture

### 2.1 Components

- **Control Plane (Vercel + Supabase)**: Customer portal, instance management, billing.
- **Compute Plane (Kubernetes)**: Individual Odoo pods with dedicated resource quotas.
- **Data Plane (PostgreSQL)**: DB-per-tenant with CloudNativePG for high availability.
- **Storage Plane (S3/MinIO)**: Isolated filestore prefixes for each tenant.

### 2.2 Odoo.sh Parity Matrix

| Feature      | Status | Approach                    |
| ------------ | ------ | --------------------------- |
| CI/CD        | Tier-0 | GitHub Actions + ArgoCD     |
| Dev Branches | Tier-0 | Ephemeral K8s namespaces    |
| Backups      | Tier-0 | Velero + S3 snapshots       |
| Monitoring   | Tier-0 | Prometheus + Grafana + Loki |
| Shell Access | Tier-0 | K8s Exec + Teleport         |

## 3) User Tiers

- **Starter**: Shared compute, 5GB storage, 3 users.
- **Pro**: Dedicated compute, 25GB storage, 10 users, Staging env.
- **Enterprise**: Custom workers, 100GB+ storage, Unlimited users, multi-region.

## 4) Core Requirements

- **Provisioning API**: Create DB, init Odoo, map subdomain in < 5 mins.
- **Edge Proxy**: HMAC-signed gateway for secure Odoo ↔ Supabase communication.
- **Addon Manager**: Integrated OCA module stack (v19).
