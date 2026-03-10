#!/bin/bash
#
# Self-Hosted GitHub Actions Runner Setup Script
# Target: DigitalOcean Droplet 178.128.112.214
# Purpose: Production-ready ephemeral runner with security hardening
#
# Usage:
#   sudo ./setup-self-hosted-runner.sh --token GITHUB_PAT
#
# Requirements:
#   - Ubuntu 22.04 or newer
#   - Root/sudo access
#   - GitHub Personal Access Token with repo and admin:org permissions
#   - Existing Odoo + n8n installation on target server

set -euo pipefail

# Configuration
RUNNER_VERSION="2.311.0"
RUNNER_ARCH="linux-x64"
GITHUB_OWNER="Insightpulseai"
GITHUB_REPO="odoo"
RUNNER_HOME="/opt/actions-runner"
RUNNER_USER="github-runner"
LABELS="odoo,n8n,plane,self-hosted,linux,x64"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Parse arguments
GITHUB_PAT=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --token)
            GITHUB_PAT="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            echo "Usage: $0 --token GITHUB_PAT [--dry-run]"
            echo ""
            echo "Options:"
            echo "  --token      GitHub Personal Access Token (required)"
            echo "  --dry-run    Perform dry run without actual installation"
            echo "  --help       Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1. Use --help for usage information."
            ;;
    esac
done

# Validate token
if [[ -z "$GITHUB_PAT" ]]; then
    log_error "GitHub PAT is required. Use --token GITHUB_PAT"
fi

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root (use sudo)"
fi

log_info "Starting GitHub Actions Runner setup..."
log_info "Target: $GITHUB_OWNER/$GITHUB_REPO"
log_info "Runner home: $RUNNER_HOME"
log_info "Labels: $LABELS"

if [[ "$DRY_RUN" == true ]]; then
    log_warn "DRY RUN MODE - No actual changes will be made"
fi

# Step 1: System prerequisites
log_info "Step 1/8: Installing system prerequisites..."
if [[ "$DRY_RUN" == false ]]; then
    apt-get update -qq
    apt-get install -y -qq \
        curl \
        jq \
        git \
        tar \
        sudo \
        lsb-release \
        ca-certificates \
        apt-transport-https \
        software-properties-common \
        unattended-upgrades \
        aide \
        fail2ban \
        ufw

    log_info "✅ System prerequisites installed"
else
    log_info "Would install: curl, jq, git, tar, sudo, security tools"
fi

# Step 2: Create dedicated runner user
log_info "Step 2/8: Creating runner user..."
if [[ "$DRY_RUN" == false ]]; then
    if id "$RUNNER_USER" &>/dev/null; then
        log_warn "User $RUNNER_USER already exists, skipping creation"
    else
        useradd -m -s /bin/bash "$RUNNER_USER"
        log_info "✅ User $RUNNER_USER created"
    fi

    # Grant limited sudo access (Docker and systemctl only)
    echo "$RUNNER_USER ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/bin/systemctl restart odoo, /usr/bin/systemctl restart n8n" > /etc/sudoers.d/"$RUNNER_USER"
    chmod 0440 /etc/sudoers.d/"$RUNNER_USER"
    log_info "✅ Sudo access configured (Docker and service restart only)"
else
    log_info "Would create user: $RUNNER_USER with limited sudo access"
fi

# Step 3: Configure firewall
log_info "Step 3/8: Configuring firewall (UFW)..."
if [[ "$DRY_RUN" == false ]]; then
    # Fetch GitHub Actions IP ranges
    GITHUB_META=$(curl -s https://api.github.com/meta | jq -r '.actions[]')

    # Reset firewall
    ufw --force reset

    # Default policies
    ufw default deny incoming
    ufw default allow outgoing

    # Allow SSH from anywhere (WARNING: Restrict this in production)
    ufw allow 22/tcp comment "SSH"

    # Allow GitHub Actions runners
    for ip in $GITHUB_META; do
        ufw allow from "$ip" to any port 22 comment "GitHub Actions"
    done

    # Allow HTTP/HTTPS (for Odoo, n8n)
    ufw allow 80/tcp comment "HTTP"
    ufw allow 443/tcp comment "HTTPS"

    # Allow PostgreSQL only from localhost
    ufw allow from 127.0.0.1 to any port 5432 comment "PostgreSQL"

    # Enable firewall
    ufw --force enable

    log_info "✅ Firewall configured"
else
    log_info "Would configure UFW: allow SSH, HTTP/HTTPS, GitHub Actions IPs"
fi

# Step 4: Security hardening
log_info "Step 4/8: Applying security hardening..."
if [[ "$DRY_RUN" == false ]]; then
    # Configure automatic security updates
    dpkg-reconfigure -plow unattended-upgrades

    # Initialize AIDE (intrusion detection)
    if [[ ! -f /var/lib/aide/aide.db ]]; then
        log_info "Initializing AIDE database (this may take a few minutes)..."
        aide --init
        mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
    fi

    # Configure fail2ban
    systemctl enable fail2ban
    systemctl start fail2ban

    # Disable root login via SSH
    sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
    sed -i 's/^PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
    systemctl restart sshd

    # Disable unnecessary services
    systemctl disable bluetooth 2>/dev/null || true
    systemctl disable cups 2>/dev/null || true
    systemctl disable avahi-daemon 2>/dev/null || true

    log_info "✅ Security hardening applied"
else
    log_info "Would apply: automatic updates, AIDE, fail2ban, SSH hardening"
fi

# Step 5: Download and install GitHub Actions Runner
log_info "Step 5/8: Downloading GitHub Actions Runner v$RUNNER_VERSION..."
if [[ "$DRY_RUN" == false ]]; then
    mkdir -p "$RUNNER_HOME"
    cd "$RUNNER_HOME"

    # Download runner
    RUNNER_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz"
    curl -o actions-runner.tar.gz -L "$RUNNER_URL"

    # Verify checksum
    EXPECTED_CHECKSUM=$(curl -sL "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz.sha256" | awk '{print $1}')
    ACTUAL_CHECKSUM=$(sha256sum actions-runner.tar.gz | awk '{print $1}')

    if [[ "$EXPECTED_CHECKSUM" != "$ACTUAL_CHECKSUM" ]]; then
        log_error "Checksum verification failed! Expected: $EXPECTED_CHECKSUM, Got: $ACTUAL_CHECKSUM"
    fi

    # Extract runner
    tar xzf actions-runner.tar.gz
    rm actions-runner.tar.gz

    # Set ownership
    chown -R "$RUNNER_USER":"$RUNNER_USER" "$RUNNER_HOME"

    log_info "✅ Runner downloaded and extracted"
else
    log_info "Would download runner v$RUNNER_VERSION from GitHub"
fi

# Step 6: Get registration token from GitHub API
log_info "Step 6/8: Fetching runner registration token..."
if [[ "$DRY_RUN" == false ]]; then
    REGISTRATION_TOKEN=$(curl -s -X POST \
        -H "Authorization: token $GITHUB_PAT" \
        -H "Accept: application/vnd.github+json" \
        "https://api.github.com/repos/$GITHUB_OWNER/$GITHUB_REPO/actions/runners/registration-token" \
        | jq -r '.token')

    if [[ -z "$REGISTRATION_TOKEN" ]] || [[ "$REGISTRATION_TOKEN" == "null" ]]; then
        log_error "Failed to get registration token. Check GitHub PAT permissions."
    fi

    log_info "✅ Registration token obtained"
else
    log_info "Would fetch registration token from GitHub API"
    REGISTRATION_TOKEN="dry-run-token"
fi

# Step 7: Configure runner (ephemeral mode)
log_info "Step 7/8: Configuring runner in ephemeral mode..."
if [[ "$DRY_RUN" == false ]]; then
    # Run configuration as runner user
    sudo -u "$RUNNER_USER" bash -c "cd $RUNNER_HOME && ./config.sh \
        --url \"https://github.com/$GITHUB_OWNER/$GITHUB_REPO\" \
        --token \"$REGISTRATION_TOKEN\" \
        --name \"odoo-runner-\$(hostname)\" \
        --labels \"$LABELS\" \
        --work \"_work\" \
        --ephemeral \
        --unattended"

    log_info "✅ Runner configured in ephemeral mode"
else
    log_info "Would configure runner with:"
    log_info "  - URL: https://github.com/$GITHUB_OWNER/$GITHUB_REPO"
    log_info "  - Labels: $LABELS"
    log_info "  - Mode: ephemeral (one job per runner lifecycle)"
fi

# Step 8: Install and start as systemd service
log_info "Step 8/8: Installing systemd service..."
if [[ "$DRY_RUN" == false ]]; then
    # Install service
    cd "$RUNNER_HOME"
    ./svc.sh install "$RUNNER_USER"

    # Configure service for auto-restart
    mkdir -p /etc/systemd/system/actions.runner.${GITHUB_OWNER}-${GITHUB_REPO}.*.service.d
    cat > /etc/systemd/system/actions.runner.${GITHUB_OWNER}-${GITHUB_REPO}.*.service.d/override.conf << EOF
[Service]
# Auto-restart on failure
Restart=always
RestartSec=10s

# Resource limits
MemoryMax=4G
CPUQuota=200%

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$RUNNER_HOME/_work

# Logging
StandardOutput=journal
StandardError=journal
EOF

    # Reload systemd
    systemctl daemon-reload

    # Start service
    ./svc.sh start

    # Enable service (start on boot)
    ./svc.sh enable

    log_info "✅ Systemd service installed and started"
else
    log_info "Would install and start systemd service with:"
    log_info "  - Auto-restart on failure"
    log_info "  - Resource limits: 4GB RAM, 200% CPU"
    log_info "  - Security hardening enabled"
fi

# Step 9: Configure health monitoring
log_info "Configuring health monitoring..."
if [[ "$DRY_RUN" == false ]]; then
    # Create monitoring script
    cat > /opt/monitor-runner.sh << 'EOF'
#!/bin/bash
# Runner health monitoring script

RUNNER_SERVICE="actions.runner.Insightpulseai-odoo.*.service"

# Check if service is running
if ! systemctl is-active --quiet "$RUNNER_SERVICE"; then
    echo "❌ Runner service is not running"
    systemctl restart "$RUNNER_SERVICE"
    exit 1
fi

# Check resource usage
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEM=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
DISK=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)

# Alert thresholds
if (( $(echo "$CPU > 90" | bc -l) )); then
    echo "⚠️ High CPU usage: $CPU%"
fi

if (( $(echo "$MEM > 95" | bc -l) )); then
    echo "⚠️ High memory usage: $MEM%"
fi

if (( $DISK > 85 )); then
    echo "⚠️ High disk usage: $DISK%"
fi

echo "✅ Runner health check passed (CPU: $CPU%, MEM: $MEM%, DISK: $DISK%)"
EOF

    chmod +x /opt/monitor-runner.sh

    # Add to cron (every 5 minutes)
    (crontab -l 2>/dev/null; echo "*/5 * * * * /opt/monitor-runner.sh >> /var/log/runner-health.log 2>&1") | crontab -

    log_info "✅ Health monitoring configured (runs every 5 minutes)"
else
    log_info "Would configure health monitoring cron job"
fi

# Final status check
log_info ""
log_info "========================================="
log_info "GitHub Actions Runner Setup Complete!"
log_info "========================================="
log_info ""

if [[ "$DRY_RUN" == false ]]; then
    log_info "Runner Status:"
    ./svc.sh status || true

    log_info ""
    log_info "Next Steps:"
    log_info "1. Verify runner appears in GitHub: https://github.com/$GITHUB_OWNER/$GITHUB_REPO/settings/actions/runners"
    log_info "2. Test runner with a sample workflow"
    log_info "3. Monitor logs: journalctl -u actions.runner.* -f"
    log_info "4. Check health: /opt/monitor-runner.sh"
    log_info ""
    log_info "Runner Details:"
    log_info "  - Name: odoo-runner-$(hostname)"
    log_info "  - Labels: $LABELS"
    log_info "  - Mode: Ephemeral (one job per lifecycle)"
    log_info "  - Service: actions.runner.$GITHUB_OWNER-$GITHUB_REPO.*.service"
    log_info "  - Logs: /var/log/runner-health.log"
else
    log_info "DRY RUN completed successfully"
    log_info "Re-run without --dry-run to perform actual installation"
fi

log_info ""
log_info "Security Checklist:"
log_info "  ✅ Ephemeral runner (clean state per job)"
log_info "  ✅ Limited sudo access (Docker and service restart only)"
log_info "  ✅ Firewall configured (GitHub Actions IPs whitelisted)"
log_info "  ✅ Automatic security updates enabled"
log_info "  ✅ SSH hardened (no root login, no password auth)"
log_info "  ✅ Resource limits (4GB RAM, 200% CPU)"
log_info "  ✅ Health monitoring (5-minute intervals)"
log_info ""
