# Kubernetes Migration Specification
## InsightPulse ERP - DOKS Migration Task

## 🎯 Task for Kubernetes Genius: Migrate to DOKS

**Objective:** Convert the existing Docker Compose stack to a production-grade Kubernetes deployment on DigitalOcean Kubernetes (DOKS).

## 📋 Current Stack Analysis

**Current Components (docker-compose.prod.yml):**
- **Odoo**: Application container (port 8069)
- **Postgres**: Database with persistent storage
- **Traefik**: Reverse proxy and ingress
- **Keycloak**: Identity provider
- **Network**: odoo_backend bridge network

## 🚀 Required Agent Deliverables

### 1. Odoo Service
**File:** `kubernetes/odoo-deployment.yaml`
- **Deployment.yaml**: Odoo application container with proper resource limits
- **Service.yaml**: Internal service mapping port 8069
- **HorizontalPodAutoscaler.yaml**: Auto-scaling based on Odoo worker usage

### 2. Postgres Service  
**File:** `kubernetes/postgres-statefulset.yaml`
- **StatefulSet.yaml**: Database with persistent storage
- **PersistentVolumeClaim.yaml**: Secure, persistent data storage
- **Service.yaml**: Internal database service

### 3. Keycloak Service
**File:** `kubernetes/keycloak-deployment.yaml`
- **Deployment.yaml**: Keycloak identity provider
- **Service.yaml**: Internal service

### 4. Ingress & Routing
**File:** `kubernetes/ingress.yaml`
- **Ingress.yaml**: Public routing replacing Traefik labels
- **Domains**: 
  - `erp.insightpulseai.net` → Odoo service
  - `auth.insightpulseai.net` → Keycloak service

### 5. Configuration Management
**File:** `kubernetes/config.yaml`
- **ConfigMap.yaml**: odoo.conf configuration
- **Secret.yaml**: Database credentials and sensitive data

## 🔧 Technical Requirements

### Odoo Deployment Requirements
- **Replicas**: 2+ for high availability
- **Resource Limits**: CPU 2, Memory 4GB (matching current)
- **Health Checks**: Liveness and readiness probes
- **Environment Variables**: Database connection, ODOO_RC path
- **Volume Mounts**: Filestore persistence

### Postgres StatefulSet Requirements
- **Replicas**: 1 (or 3 for production HA)
- **Storage**: Persistent volume with 20GB minimum
- **Backup Strategy**: Automated backups configuration
- **Resource Limits**: CPU 2, Memory 2GB

### Ingress Requirements
- **TLS/SSL**: Automatic certificate management
- **Path Routing**: Proper path-based routing
- **Load Balancing**: Even traffic distribution
- **Security**: Rate limiting, CORS policies

### Security Requirements
- **RBAC**: Role-Based Access Control for Odoo API access
- **Network Policies**: Isolate services appropriately
- **Secrets Management**: Secure credential handling
- **Pod Security**: Security context configurations

## 📊 Migration Strategy

### Phase 1: Component Migration
1. Deploy Postgres StatefulSet with data migration
2. Deploy Odoo Deployment with existing database
3. Deploy Keycloak with user data migration
4. Configure Ingress routing

### Phase 2: Data Migration
- Database dump/restore from Docker Compose
- Filestore migration to persistent volumes
- Keycloak realm and user export/import

### Phase 3: Validation
- End-to-end functionality testing
- Performance benchmarking
- Rollback procedure validation

## 🛠️ Kubernetes Genius Capabilities

| Agent Capability | Odoo Stack Utility |
|------------------|-------------------|
| **Cluster Setup & Management** | Generating robust Kubernetes YAML files for Odoo, Postgres, and Keycloak |
| **Configuration & Optimization** | Defining Horizontal Pod Autoscaler (HPA) rules based on Odoo worker usage |
| **Debugging & Troubleshooting** | Diagnosing persistent fe_sendauth or deployment errors in cluster environment |
| **Best Practices** | Establishing RBAC (Role-Based Access Control) for Odoo API access |

## 📈 Expected Benefits

### Current State (Docker Compose)
- Single point of failure
- Manual scaling
- Limited monitoring
- Basic networking

### Target State (Kubernetes)
- High availability with auto-scaling
- Automated health checks and self-healing
- Comprehensive monitoring and logging
- Advanced networking and security

## 🔄 Rollback Strategy

**Quick Rollback:** Maintain Docker Compose environment until Kubernetes validation complete
**Data Safety:** Automated database backups before migration
**Monitoring:** Comprehensive health checks during transition

## 🎯 Success Criteria

- ✅ All services running in Kubernetes cluster
- ✅ Data integrity maintained through migration
- ✅ Performance equal or better than Docker Compose
- ✅ Automated scaling functioning correctly
- ✅ Security policies properly enforced
- ✅ Zero downtime during migration

This specification provides the Kubernetes Genius Agent with the complete architectural requirements for migrating the InsightPulse ERP stack to a production-grade Kubernetes environment.
