---
id: CTRL-SOP-003
type: policy
name: Docker Container Management SOP
status: active
owner: devops_team
portfolio_initiative: PORT-2026-010
process_id: PROC-INFRA-001
effective_date: 2026-02-12
review_cycle: quarterly
---

# SOP-003: Docker Container Management

**Purpose**: Establish standards for Docker container orchestration, security, resource management, and operational lifecycle.

**Scope**: All Docker containers running in development and production environments.

**Owner**: devops_team

---

## 1. Container Classification

### 1.1 Always-On Containers
**Definition**: Production-grade containers required for daily operations.

**Criteria**:
- Single source of truth (SSOT) for critical data
- Daily active use for business operations
- High availability required

**Examples**:
- **Plane stack**: Project management and OKR tracking SSOT
  - `plane-deploy`, `plane-db-1`, `plane-mq-1`, `plane-minio-1`, `plane-redis-1`

**Action**: Must remain running at all times (`restart: unless-stopped`).

---

### 1.2 On-Demand Containers
**Definition**: Development and testing containers used intermittently.

**Criteria**:
- Not required for daily business operations
- Development or testing purposes only
- No high availability requirement

**Examples**:
- **Odoo dev stack**: Development sandbox
  - `odoo-dev`, `odoo-dev-db`
- **IDE helpers**: Development tooling
  - code-server, openvscode-server

**Action**: Stop when not actively in use (`restart: no`).

---

## 2. Resource Management

### 2.1 Resource Limits (Mandatory)
**Policy**: All containers MUST have CPU and memory limits.

**Rationale**: Prevent resource exhaustion and ensure fair resource distribution.

**Critical Services** (DB, cache, queue):
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 1G
```

**Non-Critical Services** (gateways, workers):
```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 1G
    reservations:
      cpus: '0.25'
      memory: 512M
```

**Development Services**:
```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 1G
    reservations:
      cpus: '0.25'
      memory: 512M
```

---

### 2.2 Restart Policies
**Production Containers**: `restart: unless-stopped`
- Automatically restart after Docker daemon restart
- Do not restart if manually stopped

**Development Containers**: `restart: no`
- Never auto-restart
- Manual start/stop required

**Temporary Containers**: `restart: on-failure` (optional)
- Restart only on failure
- Max restart attempts: 3

---

## 3. Network Isolation

### 3.1 Network Segmentation (Mandatory)
**Policy**: Each stack MUST have its own isolated Docker network.

**Rationale**: Prevent cross-stack communication and improve security.

**Implementation**:
```yaml
networks:
  <stack_name>_network:
    driver: bridge
    internal: false  # Set to true if no external access needed
```

**Validation**:
```bash
docker network ls | grep -E "plane_network|odoo_dev_network"
```

---

### 3.2 Port Publishing
**Policy**: Minimize port publishing to host.

**Rules**:
1. **Internal services** (DB, Redis, MQ): NO port publishing
2. **Gateway services**: Publish only required ports
3. **Development services**: Bind to `127.0.0.1` (localhost only)

**Example** (production DB - internal only):
```yaml
# ❌ WRONG
ports:
  - "5432:5432"

# ✅ CORRECT
# No ports section (internal only)
```

**Example** (development service - localhost only):
```yaml
# ❌ WRONG
ports:
  - "9069:8069"

# ✅ CORRECT
ports:
  - "127.0.0.1:9069:8069"
```

---

## 4. Security Requirements

### 4.1 Secrets Management
**Policy**: Never hardcode secrets in compose files.

**Approved Methods**:
1. **Environment files**: `.env` files (not committed to git)
2. **Docker secrets**: `docker secret create` (for Swarm)
3. **External secret managers**: Vault, AWS Secrets Manager

**Example**:
```yaml
# ✅ CORRECT
environment:
  POSTGRES_PASSWORD_FILE: /run/secrets/db_password
secrets:
  - db_password

# ❌ WRONG
environment:
  POSTGRES_PASSWORD: "hardcoded_password"
```

---

### 4.2 Image Sources
**Policy**: Use only verified image sources.

**Approved Sources**:
1. Official Docker Hub images (verified publisher)
2. Internal registry (if established)
3. Trusted vendor registries (e.g., `ghcr.io`, `quay.io`)

**Validation**:
```bash
# Check image provenance
docker inspect <image> --format '{{.RepoDigests}}'
```

---

### 4.3 Image Updates
**Policy**: Regularly update images for security patches.

**Frequency**:
- **Production containers**: Monthly or on critical CVE
- **Development containers**: Quarterly

**Process**:
1. Pull new images
2. Review changelogs
3. Test in dev environment
4. Update production
5. Verify health

**Commands**:
```bash
docker compose pull
docker compose up -d
docker compose ps
```

---

## 5. Backup Requirements

### 5.1 Production Container Backups (Mandatory)
**Policy**: All always-on containers MUST have automated backups.

**Frequency**: Daily

**Retention**:
- Daily backups: 7 days
- Weekly snapshots: 4 weeks

**Implementation**:
- **Script**: `scripts/docker/backup-<stack>.sh`
- **Schedule**: Cron or systemd timer
- **Validation**: Daily backup verification

**Example** (Plane stack):
```bash
# Backup script
bash scripts/docker/backup-plane.sh

# Verification
ls -lah backups/plane/
```

---

### 5.2 Development Container Backups (Optional)
**Policy**: No automated backup requirement for development containers.

**Manual Backup** (if needed):
```bash
docker exec -t <container> pg_dumpall -U <user> > backups/dev/backup_$(date +%Y%m%d).sql
```

---

### 5.3 Backup Validation
**Policy**: Monthly restore testing for production backups.

**Process**:
1. Select random backup from last 7 days
2. Restore to temporary environment
3. Verify data integrity
4. Document results

**Evidence**: `docs/evidence/<YYYYMMDD-HHMM>/backup-restore-test/`

---

## 6. Monitoring and Logging

### 6.1 Health Checks
**Policy**: All production containers SHOULD implement health checks.

**Implementation**:
```yaml
healthcheck:
  test: ["CMD", "pg_isready", "-U", "postgres"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**Validation**:
```bash
docker inspect <container> --format '{{.State.Health.Status}}'
```

---

### 6.2 Log Management
**Policy**: Use Docker default JSON file driver with rotation.

**Configuration**:
```yaml
logging:
  driver: json-file
  options:
    max-size: "10m"
    max-file: "3"
```

**Log Access**:
```bash
# View logs
docker logs <container> --tail 50

# Follow logs
docker logs <container> --follow
```

---

### 6.3 Resource Monitoring
**Policy**: Regular resource usage monitoring.

**Frequency**: Daily for production containers

**Commands**:
```bash
# Real-time stats
docker stats <container> --no-stream

# Resource usage over time
docker stats
```

---

## 7. Operational Lifecycle

### 7.1 Container Start
**Checklist**:
1. Verify compose file syntax
2. Check environment variables
3. Ensure volumes exist
4. Verify network exists
5. Start containers
6. Verify health

**Commands**:
```bash
docker compose config
docker compose up -d
docker compose ps
```

---

### 7.2 Container Stop
**Checklist**:
1. Graceful shutdown (wait for active connections)
2. Backup critical data (if needed)
3. Stop containers
4. Verify stopped

**Commands**:
```bash
docker compose down
docker ps -a | grep <stack>
```

---

### 7.3 Container Update
**Checklist**:
1. Pull new images
2. Review changelogs
3. Test in dev environment (for production updates)
4. Stop existing containers
5. Start new containers
6. Verify health

**Commands**:
```bash
docker compose pull
docker compose up -d
docker compose ps
```

---

## 8. Compliance and Audit

### 8.1 Configuration Audit
**Frequency**: Quarterly

**Checklist**:
- [ ] All containers have resource limits
- [ ] Network isolation implemented
- [ ] Port publishing minimized
- [ ] Secrets not hardcoded
- [ ] Restart policies correct
- [ ] Backups configured and tested

**Evidence**: `docs/evidence/<YYYYMMDD-HHMM>/docker-audit/`

---

### 8.2 Baseline Snapshot
**Purpose**: Capture current container state for comparison.

**Frequency**: After major changes

**Script**: `scripts/docker/snapshot-baseline.sh`

**Contents**:
- Container list (`docker ps -a`)
- Network list (`docker network ls`)
- Volume list (`docker volume ls`)
- Image list (`docker images`)

**Evidence**: `docs/evidence/<YYYYMMDD-HHMM>/docker-baseline/`

---

## 9. Enforcement

### 9.1 Policy Violations
**Detection**:
- Automated checks via `scripts/docker/validate-compliance.sh`
- Manual quarterly audits

**Response**:
1. **Minor violations** (missing labels, suboptimal config): Remediate within 7 days
2. **Major violations** (no resource limits, exposed credentials): Immediate remediation
3. **Critical violations** (security exposure): Stop container immediately, remediate, evidence

**Escalation**: compliance_team

---

### 9.2 Exemption Process
**Procedure**: Document exemption with:
1. Justification (technical or business reason)
2. Compensating controls (alternative security measures)
3. Approval from devops_team and security_team
4. Time-bound (max 90 days)

**Documentation**: `docs/control/policies/exemptions/SOP-003-<stack>-exemption.md`

---

## 10. Related Documents

**Portfolio Initiative**: PORT-2026-010
**Process**: PROC-INFRA-001
**Control**: CTRL-SOP-003
**Evidence**: EVID-20260212-005

**Documentation**:
- `docs/integration/docker-infrastructure.md`
- `docs/TRACEABILITY_INDEX.yaml`

**Scripts**:
- `scripts/docker/backup-plane.sh`
- `scripts/docker/stop-dev-stacks.sh`
- `scripts/docker/snapshot-baseline.sh`
- `scripts/docker/validate-compliance.sh` (TBD)

---

## 11. Review and Updates

**Review Cycle**: Quarterly

**Next Review**: 2026-05-12

**Change Process**:
1. Propose change via GitHub issue
2. Review by devops_team
3. Approval by compliance_team
4. Update SOP document
5. Communicate to stakeholders
6. Evidence in `docs/evidence/`

---

*Effective Date: 2026-02-12*
*Version: 1.0*
*Owner: devops_team*
