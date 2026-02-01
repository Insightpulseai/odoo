# Infrastructure Summary - Odoo 18 CE + DO Managed PostgreSQL

Complete infrastructure alignment: Local sandbox → Production deployment.

---

## 📊 Infrastructure Overview

### DigitalOcean Production Stack

```
Internet (erp.insightpulseai.com)
    ↓ HTTPS (Caddy automatic SSL)
Droplet 178.128.112.214
    ├─ Caddy (80/443) → Reverse proxy
    ├─ Odoo 18 (127.0.0.1:8069) → Application
    └─ stunnel (127.0.0.1:5432) → SSL tunnel
        ↓ TLS
DO Managed PostgreSQL (odoo-db-sgp1)
    ├─ Host: odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com
    ├─ Port: 25060
    └─ Database: odoo (canonical)
```

---

## 🗄️ Database Architecture

### DO Managed PostgreSQL Cluster

| Property | Value |
|----------|-------|
| **Cluster Name** | odoo-db-sgp1 |
| **Version** | PostgreSQL 16 |
| **Region** | SGP1 (Singapore) |
| **RAM** | 2 GB |
| **CPU** | 1 vCPU |
| **Disk** | 30 GiB |
| **Cost** | $30.45/month |

### Canonical Database Naming

| Service | Database | User | Purpose |
|---------|----------|------|---------|
| **Odoo** | `odoo` | `odoo_app` | ERP application data |
| **Superset** | `superset` | `superset_app` | BI metadata |
| **n8n** | `n8n` | `n8n_app` | Workflow metadata |

**Key Principle:** Database name `odoo` is canonical across all environments.

---

## 🚀 Deployment Configurations

### 1. Local Sandbox (Development)

**Location:** `sandbox/dev/`

**Purpose:** Isolated local development with no production risk

**Database:** Local PostgreSQL 16 container

**Start:**
```bash
cd sandbox/dev
docker compose up -d
open http://localhost:8069
```

**Documentation:**
- `sandbox/dev/README.md` - Quick start
- `sandbox/dev/ARCHITECTURE.md` - Infrastructure details
- `sandbox/dev/CANONICAL_NAMING.md` - Database standards
- `sandbox/dev/Makefile` - Development shortcuts

---

### 2. Production Connection (Local → DO Managed DB)

**Location:** `sandbox/dev/` (advanced configuration)

**Purpose:** Connect local Odoo to production DO Managed Database

**Configuration:** `docker-compose.production.yml`

**Use Cases:**
- Production troubleshooting
- Database migrations testing
- Read-only production data analysis

**Start:**
```bash
cd sandbox/dev
# After configuring .env.production
docker compose -f docker-compose.production.yml --env-file .env.production up -d
```

**Documentation:**
- `sandbox/dev/README_PRODUCTION.md` - Production connection guide

---

### 3. Production Droplet Deployment

**Location:** `deploy/`

**Purpose:** Full production deployment on DigitalOcean droplet

**Components:**
- Caddy reverse proxy (automatic HTTPS)
- Odoo 18 CE application
- stunnel SSL tunnel to DO Managed DB

**Deploy:**
```bash
# On droplet 178.128.112.214
cd /opt/odoo-ce/deploy
docker compose up -d
```

**Access:** `https://erp.insightpulseai.com`

**Documentation:**
- `deploy/PRODUCTION_SETUP.md` - Complete runbook
- `deploy/DROPLET_DEPLOYMENT.md` - Deployment guide

---

## 📁 Repository Structure

```
odoo-ce/
├── sandbox/dev/                        # Local development sandbox
│   ├── docker-compose.yml              # Local sandbox (default)
│   ├── docker-compose.production.yml   # Production connection (advanced)
│   ├── odoo.conf                       # Local configuration
│   ├── odoo.conf.production            # Production configuration
│   ├── .env.example                    # Local environment template
│   ├── .env.production.example         # Production environment template
│   ├── README.md                       # Quick start guide
│   ├── README_PRODUCTION.md            # Production connection guide
│   ├── ARCHITECTURE.md                 # Infrastructure alignment
│   ├── CANONICAL_NAMING.md             # Database naming standards
│   └── Makefile                        # Development shortcuts
│
├── deploy/                             # Production deployment
│   ├── docker-compose.yml              # Production compose (Caddy + Odoo + stunnel)
│   ├── odoo.conf                       # Production Odoo config
│   ├── Caddyfile                       # Reverse proxy + SSL config
│   ├── .env.example                    # Production environment template
│   ├── PRODUCTION_SETUP.md             # Complete production runbook
│   └── DROPLET_DEPLOYMENT.md           # Deployment guide
│
├── addons/                             # Odoo modules
│   ├── oca/                            # OCA community modules
│   └── ipai/                           # Custom IPAI modules
│
├── INFRASTRUCTURE_SUMMARY.md           # This file
├── CLAUDE.md                           # Project orchestration rules
└── .gitignore                          # Security (production secrets excluded)
```

---

## 🔒 Security Configuration

### Network Access Control

**DO Managed Database Allowlist:**
- `178.128.112.214` ✅ (Production droplet)
- `10.104.0.0/20` (VPC network, if using private connectivity)

**Droplet Firewall (UFW):**
- SSH (22/tcp) ✅
- HTTP (80/tcp) ✅
- HTTPS (443/tcp) ✅
- **Port 8069 NOT exposed** (internal only, via Caddy)
- **Port 5432 NOT exposed** (internal only, via stunnel)

### Secret Management

**Local Sandbox:**
- `.env` file (optional, defaults work)
- No production secrets

**Production:**
- `/opt/odoo-ce/deploy/.env` (chmod 600)
- NEVER committed to git
- Managed by `.gitignore`

**Excluded from git:**
```gitignore
.env
.env.*
.env.production
sandbox/dev/certs/
sandbox/dev/*.local
deploy/.env
```

---

## 🛠️ Quick Start Commands

### Local Development

```bash
# Navigate to sandbox
cd sandbox/dev

# Start services
make start
# or
docker compose up -d

# Open browser
make open
# or
open http://localhost:8069

# Install module
make install MODULE=ipai_finance_ppm

# View logs
make logs-odoo

# Stop services
make stop
```

---

### Production Deployment

```bash
# SSH to droplet
ssh root@178.128.112.214

# Navigate to deploy directory
cd /opt/odoo-ce/deploy

# Start services
docker compose up -d

# View logs
docker compose logs -f odoo

# Restart Odoo
docker compose restart odoo

# Stop services
docker compose down
```

**Access:** https://erp.insightpulseai.com

---

## 📚 Documentation Quick Reference

| Task | Document |
|------|----------|
| **Local development setup** | `sandbox/dev/README.md` |
| **Production deployment** | `deploy/PRODUCTION_SETUP.md` |
| **Database naming standards** | `sandbox/dev/CANONICAL_NAMING.md` |
| **Infrastructure alignment** | `sandbox/dev/ARCHITECTURE.md` |
| **Production connection (advanced)** | `sandbox/dev/README_PRODUCTION.md` |
| **Droplet deployment** | `deploy/DROPLET_DEPLOYMENT.md` |
| **Project orchestration rules** | `CLAUDE.md` |
| **This summary** | `INFRASTRUCTURE_SUMMARY.md` |

---

## ✅ Acceptance Checklist

### Local Sandbox
- [x] Docker Compose configuration created
- [x] PostgreSQL 16 local database
- [x] Odoo 18.0 official image
- [x] Canonical database name `odoo`
- [x] OCA + IPAI addons mounted
- [x] Makefile shortcuts
- [x] Documentation complete

### Production Deployment
- [x] Droplet configured (178.128.112.214)
- [x] Docker + Docker Compose installed
- [x] Firewall configured (UFW)
- [x] DO Managed PostgreSQL accessible
- [x] stunnel SSL tunnel configured
- [x] Caddy reverse proxy with automatic HTTPS
- [x] DNS configured (erp.insightpulseai.com)
- [x] Systemd auto-start service
- [x] Complete runbook documentation

### Database Configuration
- [x] Canonical naming `odoo` across all environments
- [x] Separate users per service (`odoo_app`, `superset_app`, `n8n_app`)
- [x] Network access allowlist configured
- [x] SSL/TLS enforced via stunnel
- [x] Permissions documented

### Security
- [x] Production secrets never committed
- [x] `.gitignore` configured correctly
- [x] File permissions secured (chmod 600/700)
- [x] Firewall allows only necessary ports
- [x] SSL/TLS enforced for all external connections

---

## 🎯 Next Steps

### For Local Development

1. **Clone repository:**
   ```bash
   git clone https://github.com/jgtolentino/odoo-ce.git
   cd odoo-ce
   ```

2. **Start local sandbox:**
   ```bash
   cd sandbox/dev
   docker compose up -d
   open http://localhost:8069
   ```

3. **Develop modules:**
   ```bash
   # Edit modules in addons/ipai/
   # Install/upgrade via make commands
   ```

---

### For Production Deployment

1. **Prepare droplet:**
   ```bash
   ssh root@178.128.112.214
   # Follow deploy/PRODUCTION_SETUP.md
   ```

2. **Configure environment:**
   ```bash
   cd /opt/odoo-ce/deploy
   cp .env.example .env
   # Edit with real credentials
   ```

3. **Start services:**
   ```bash
   docker compose up -d
   ```

4. **Verify:**
   ```bash
   curl -I https://erp.insightpulseai.com/web/login
   ```

---

## 🔄 Development Workflow

```
1. Local Development
   ├─ Clone repo
   ├─ Start local sandbox
   ├─ Develop modules in addons/ipai/
   ├─ Test locally (http://localhost:8069)
   └─ Commit changes

2. Testing (if staging available)
   ├─ Deploy to staging environment
   ├─ Run integration tests
   └─ Verify functionality

3. Production Deployment
   ├─ Backup production database
   ├─ Deploy to production droplet
   ├─ Run smoke tests
   └─ Monitor for issues
```

---

## 💰 Cost Analysis

| Component | Monthly Cost |
|-----------|-------------|
| **DO Managed PostgreSQL** | $30.45 |
| **Droplet (178.128.112.214)** | Variable (based on size) |
| **Domain (erp.insightpulseai.com)** | Variable |
| **SSL Certificate** | $0 (Let's Encrypt via Caddy) |
| **Local Sandbox** | $0 (runs locally) |

**Total Production:** ~$30.45/month + droplet cost

---

## 🆘 Support Resources

- **DigitalOcean Dashboard:** https://cloud.digitalocean.com
- **Database Management:** DigitalOcean → Databases → odoo-db-sgp1
- **Network Access:** DigitalOcean → Databases → odoo-db-sgp1 → Network Access
- **Droplet Console:** DigitalOcean → Droplets → 178.128.112.214

---

**Last Updated:** 2026-01-14
**Infrastructure Version:** Odoo 18 CE + PostgreSQL 16
**Production URL:** https://erp.insightpulseai.com
**Repository:** https://github.com/jgtolentino/odoo-ce
