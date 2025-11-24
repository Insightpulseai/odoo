#!/bin/bash

# =============================================
# Automated Error Handler & Self-Healing System
# =============================================

set -e

# Configuration
LOG_FILE="/var/log/odoo_auto_heal.log"
ERROR_PATTERNS_FILE="$(dirname "$0")/error_patterns.json"
BACKUP_DIR="/var/backups/odoo_auto"
MAX_BACKUPS=5
HEALTH_CHECK_INTERVAL=300  # 5 minutes

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

# Error patterns for automated fixes
ERROR_PATTERNS='
{
    "patterns": [
        {
            "regex": "Invalid field.*numbercall.*on model.*ir.cron",
            "type": "cron_field_deprecated",
            "severity": "high",
            "auto_fix": true,
            "fix_script": "fix_cron_fields",
            "description": "Odoo 18 removed numbercall field from ir.cron model"
        },
        {
            "regex": "Invalid field.*max_calls.*on model.*ir.cron",
            "type": "cron_field_deprecated",
            "severity": "high",
            "auto_fix": true,
            "fix_script": "fix_cron_fields",
            "description": "Odoo 18 removed max_calls field from ir.cron model"
        },
        {
            "regex": "Module.*not found",
            "type": "module_missing",
            "severity": "medium",
            "auto_fix": false,
            "description": "Required module not installed"
        },
        {
            "regex": "Database connection.*failed",
            "type": "database_connection",
            "severity": "critical",
            "auto_fix": true,
            "fix_script": "restart_database_service",
            "description": "Database connection issues"
        },
        {
            "regex": "Permission denied",
            "type": "permission_error",
            "severity": "medium",
            "auto_fix": true,
            "fix_script": "fix_permissions",
            "description": "File permission issues"
        }
    ]
}'

# Initialize error patterns
init_error_patterns() {
    if [ ! -f "$ERROR_PATTERNS_FILE" ]; then
        echo "$ERROR_PATTERNS" > "$ERROR_PATTERNS_FILE"
        log "INFO" "Error patterns file created at $ERROR_PATTERNS_FILE"
    fi
}

# Backup current configuration
backup_config() {
    local backup_name="odoo_config_$(date +%Y%m%d_%H%M%S).tar.gz"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup Odoo configuration files
    tar -czf "$backup_path" \
        addons/*/data/*.xml \
        deploy/odoo.conf \
        deploy/docker-compose.yml \
        2>/dev/null || true
    
    # Clean up old backups
    ls -tp "$BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs -I {} rm -- {}
    
    log "INFO" "Configuration backed up to $backup_path"
    echo "$backup_path"
}

# Fix cron field issues
fix_cron_fields() {
    log "INFO" "Attempting to fix cron field issues..."
    
    # Find and fix all cron XML files
    local cron_files=$(find addons -name "*.xml" -type f | xargs grep -l "ir.cron" 2>/dev/null || true)
    
    for file in $cron_files; do
        if [ -f "$file" ]; then
            log "INFO" "Processing cron file: $file"
            
            # Remove deprecated fields
            sed -i.bak '/<field name="numbercall">/d' "$file"
            sed -i.bak '/<field name="max_calls">/d' "$file"
            
            # Remove backup files
            rm -f "${file}.bak"
            
            log "SUCCESS" "Fixed cron fields in $file"
        fi
    done
}

# Restart database service
restart_database_service() {
    log "INFO" "Restarting database service..."
    
    if command -v docker-compose >/dev/null 2>&1; then
        cd deploy && docker-compose restart db && cd - || return 1
    elif command -v systemctl >/dev/null 2>&1; then
        sudo systemctl restart postgresql || return 1
    else
        log "WARNING" "No supported service manager found"
        return 1
    fi
    
    log "SUCCESS" "Database service restarted"
    return 0
}

# Fix file permissions
fix_permissions() {
    log "INFO" "Fixing file permissions..."
    
    # Set proper permissions for Odoo files
    find addons -type f -name "*.py" -exec chmod 644 {} \;
    find addons -type f -name "*.xml" -exec chmod 644 {} \;
    find scripts -type f -name "*.sh" -exec chmod +x {} \;
    
    log "SUCCESS" "File permissions fixed"
}

# Health check function
health_check() {
    log "INFO" "Running health check..."
    
    local errors=0
    
    # Check if Odoo is running
    if pgrep -f "odoo-bin" >/dev/null; then
        log "INFO" "✓ Odoo process is running"
    else
        log "ERROR" "✗ Odoo process is not running"
        ((errors++))
    fi
    
    # Check database connection
    if command -v psql >/dev/null 2>&1; then
        if psql -l >/dev/null 2>&1; then
            log "INFO" "✓ Database connection is healthy"
        else
            log "ERROR" "✗ Database connection failed"
            ((errors++))
        fi
    fi
    
    # Check for common error patterns in logs
    local recent_errors=$(journalctl -u odoo --since "5 minutes ago" 2>/dev/null | grep -i "error\|failed" | wc -l)
    if [ "$recent_errors" -gt 0 ]; then
        log "WARNING" "Found $recent_errors errors in recent logs"
        ((errors++))
    fi
    
    return $errors
}

# Automated error detection and fixing
auto_detect_and_fix() {
    log "INFO" "Starting automated error detection..."
    
    local log_source="$1"
    local errors_found=0
    local errors_fixed=0
    
    # Get recent logs
    local recent_logs=""
    if [ "$log_source" = "journal" ]; then
        recent_logs=$(journalctl -u odoo --since "10 minutes ago" 2>/dev/null)
    elif [ -f "$log_source" ]; then
        recent_logs=$(tail -100 "$log_source")
    else
        log "ERROR" "Invalid log source: $log_source"
        return 1
    fi
    
    # Load error patterns
    local patterns=$(cat "$ERROR_PATTERNS_FILE" 2>/dev/null || echo "$ERROR_PATTERNS")
    
    # Check each pattern
    while IFS= read -r pattern; do
        local regex=$(echo "$pattern" | jq -r '.regex' 2>/dev/null)
        local type=$(echo "$pattern" | jq -r '.type' 2>/dev/null)
        local severity=$(echo "$pattern" | jq -r '.severity' 2>/dev/null)
        local auto_fix=$(echo "$pattern" | jq -r '.auto_fix' 2>/dev/null)
        local fix_script=$(echo "$pattern" | jq -r '.fix_script' 2>/dev/null)
        local description=$(echo "$pattern" | jq -r '.description' 2>/dev/null)
        
        if echo "$recent_logs" | grep -qE "$regex"; then
            log "ERROR" "Found error: $description (Type: $type, Severity: $severity)"
            ((errors_found++))
            
            if [ "$auto_fix" = "true" ] && [ -n "$fix_script" ]; then
                log "INFO" "Attempting auto-fix using: $fix_script"
                if $fix_script; then
                    log "SUCCESS" "Auto-fix completed for: $description"
                    ((errors_fixed++))
                else
                    log "ERROR" "Auto-fix failed for: $description"
                fi
            fi
        fi
    done < <(echo "$patterns" | jq -c '.patterns[]' 2>/dev/null)
    
    log "INFO" "Error detection completed: $errors_found errors found, $errors_fixed auto-fixed"
    return $errors_found
}

# Continuous monitoring mode
monitor_mode() {
    log "INFO" "Starting continuous monitoring mode..."
    
    while true; do
        # Run health check
        if ! health_check; then
            log "WARNING" "Health check failed, running auto-fix procedures"
            auto_detect_and_fix "journal"
        fi
        
        # Wait for next check
        sleep $HEALTH_CHECK_INTERVAL
    done
}

# Main function
main() {
    local mode="${1:-detect}"
    local log_source="${2:-journal}"
    
    # Initialize
    init_error_patterns
    
    case "$mode" in
        "detect")
            auto_detect_and_fix "$log_source"
            ;;
        "health")
            health_check
            ;;
        "monitor")
            monitor_mode
            ;;
        "backup")
            backup_config
            ;;
        "fix-cron")
            fix_cron_fields
            ;;
        *)
            echo "Usage: $0 {detect|health|monitor|backup|fix-cron} [log_source]"
            echo "  detect   - Detect and auto-fix errors"
            echo "  health   - Run health check"
            echo "  monitor  - Start continuous monitoring"
            echo "  backup   - Backup current configuration"
            echo "  fix-cron - Fix cron field issues"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
