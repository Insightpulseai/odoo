#!/bin/bash

# =============================================
# Enhanced Health Check with Auto-Healing
# =============================================

set -e

# Configuration
LOG_FILE="/var/log/odoo_health_check.log"
AUTO_HEAL_SCRIPT="$(dirname "$0")/auto_error_handler.sh"
ALERT_THRESHOLD=3  # Number of consecutive failures before alert
HEALTH_CHECK_INTERVAL=60  # 1 minute

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

# Check if Odoo process is running
check_odoo_process() {
    if pgrep -f "odoo-bin" >/dev/null; then
        log "INFO" "✓ Odoo process is running"
        return 0
    else
        log "ERROR" "✗ Odoo process is not running"
        return 1
    fi
}

# Check database connectivity
check_database_connection() {
    if command -v psql >/dev/null 2>&1; then
        if psql -l >/dev/null 2>&1; then
            log "INFO" "✓ Database connection is healthy"
            return 0
        else
            log "ERROR" "✗ Database connection failed"
            return 1
        fi
    else
        log "WARNING" "PostgreSQL client not available, skipping database check"
        return 0
    fi
}

# Check disk space
check_disk_space() {
    local threshold=90  # 90% usage threshold
    local usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')

    if [ "$usage" -lt "$threshold" ]; then
        log "INFO" "✓ Disk usage: ${usage}% (below ${threshold}% threshold)"
        return 0
    else
        log "WARNING" "⚠ Disk usage: ${usage}% (above ${threshold}% threshold)"
        return 1
    fi
}

# Check memory usage
check_memory_usage() {
    local threshold=90  # 90% usage threshold
    local usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')

    if [ "$usage" -lt "$threshold" ]; then
        log "INFO" "✓ Memory usage: ${usage}% (below ${threshold}% threshold)"
        return 0
    else
        log "WARNING" "⚠ Memory usage: ${usage}% (above ${threshold}% threshold)"
        return 1
    fi
}

# Check recent errors in logs
check_recent_errors() {
    local error_count=0

    # Check system logs
    if command -v journalctl >/dev/null 2>&1; then
        error_count=$(journalctl -u odoo --since "5 minutes ago" 2>/dev/null | grep -i "error\|failed" | wc -l)
    fi

    # Check Odoo logs if available
    if [ -f "/var/log/odoo/odoo.log" ]; then
        local odoo_errors=$(tail -100 "/var/log/odoo/odoo.log" | grep -i "error\|failed" | wc -l)
        error_count=$((error_count + odoo_errors))
    fi

    if [ "$error_count" -eq 0 ]; then
        log "INFO" "✓ No recent errors found in logs"
        return 0
    else
        log "WARNING" "⚠ Found $error_count errors in recent logs"
        return 1
    fi
}

# Check service dependencies
check_service_dependencies() {
    local services=("postgresql" "redis" "nginx")
    local all_healthy=true

    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            log "INFO" "✓ Service $service is running"
        else
            log "WARNING" "⚠ Service $service is not running"
            all_healthy=false
        fi
    done

    if $all_healthy; then
        return 0
    else
        return 1
    fi
}

# Check network connectivity
check_network_connectivity() {
    local endpoints=("google.com" "github.com")
    local all_reachable=true

    for endpoint in "${endpoints[@]}"; do
        if ping -c 1 -W 2 "$endpoint" >/dev/null 2>&1; then
            log "INFO" "✓ Network reachable: $endpoint"
        else
            log "WARNING" "⚠ Network unreachable: $endpoint"
            all_reachable=false
        fi
    done

    if $all_reachable; then
        return 0
    else
        return 1
    fi
}

# Run comprehensive health check
run_health_check() {
    log "INFO" "Starting comprehensive health check..."

    local checks_failed=0
    local check_results=()

    # Run all checks
    check_odoo_process || ((checks_failed++))
    check_database_connection || ((checks_failed++))
    check_disk_space || ((checks_failed++))
    check_memory_usage || ((checks_failed++))
    check_recent_errors || ((checks_failed++))
    check_service_dependencies || ((checks_failed++))
    check_network_connectivity || ((checks_failed++))

    # Summary
    if [ "$checks_failed" -eq 0 ]; then
        log "SUCCESS" "✓ All health checks passed"
        return 0
    else
        log "WARNING" "⚠ $checks_failed health check(s) failed"
        return 1
    fi
}

# Auto-healing procedure
auto_heal() {
    local failure_count=$1

    log "INFO" "Starting auto-healing procedure (failure count: $failure_count)"

    # Run auto error handler
    if [ -f "$AUTO_HEAL_SCRIPT" ]; then
        log "INFO" "Running auto error handler..."
        "$AUTO_HEAL_SCRIPT" detect

        # If we have multiple consecutive failures, run more aggressive fixes
        if [ "$failure_count" -ge "$ALERT_THRESHOLD" ]; then
            log "WARNING" "Multiple consecutive failures detected, running advanced healing..."
            "$AUTO_HEAL_SCRIPT" fix-cron
            "$AUTO_HEAL_SCRIPT" backup
        fi
    else
        log "ERROR" "Auto error handler script not found: $AUTO_HEAL_SCRIPT"
    fi

    # Attempt service restart if Odoo is not running
    if ! check_odoo_process; then
        log "INFO" "Attempting to restart Odoo service..."

        if command -v docker-compose >/dev/null 2>&1; then
            cd deploy && docker-compose restart odoo && cd - || log "ERROR" "Failed to restart Odoo via Docker"
        elif command -v systemctl >/dev/null 2>&1; then
            sudo systemctl restart odoo || log "ERROR" "Failed to restart Odoo via systemd"
        else
            log "WARNING" "No supported service manager found for Odoo restart"
        fi

        # Wait a bit and check again
        sleep 10
        if check_odoo_process; then
            log "SUCCESS" "Odoo service restarted successfully"
        else
            log "ERROR" "Odoo service restart failed"
        fi
    fi
}

# Continuous monitoring mode
monitor_mode() {
    log "INFO" "Starting continuous health monitoring..."

    local consecutive_failures=0
    local last_alert_time=0
    local alert_cooldown=300  # 5 minutes between alerts

    while true; do
        local current_time=$(date +%s)

        if run_health_check; then
            # Health check passed
            if [ "$consecutive_failures" -gt 0 ]; then
                log "SUCCESS" "System recovered after $consecutive_failures consecutive failures"
                consecutive_failures=0
            fi
        else
            # Health check failed
            ((consecutive_failures++))
            log "WARNING" "Health check failed ($consecutive_failures consecutive failures)"

            # Auto-heal on first failure
            if [ "$consecutive_failures" -eq 1 ]; then
                auto_heal "$consecutive_failures"
            fi

            # Alert on threshold breaches
            if [ "$consecutive_failures" -ge "$ALERT_THRESHOLD" ] && \
               [ $((current_time - last_alert_time)) -ge "$alert_cooldown" ]; then
                log "ALERT" "CRITICAL: $consecutive_failures consecutive health check failures"
                last_alert_time=$current_time

                # Run more aggressive healing
                auto_heal "$consecutive_failures"
            fi
        fi

        # Wait for next check
        sleep $HEALTH_CHECK_INTERVAL
    done
}

# Generate health report
generate_report() {
    local report_file="/tmp/odoo_health_report_$(date +%Y%m%d_%H%M%S).txt"

    {
        echo "Odoo Health Report - $(date)"
        echo "================================"
        echo ""
        echo "System Information:"
        echo "-------------------"
        uname -a
        echo ""
        echo "Disk Usage:"
        echo "-----------"
        df -h
        echo ""
        echo "Memory Usage:"
        echo "-------------"
        free -h
        echo ""
        echo "Recent Log Errors:"
        echo "------------------"
        journalctl -u odoo --since "1 hour ago" 2>/dev/null | grep -i "error\|failed" | tail -20
        echo ""
        echo "Running Processes:"
        echo "------------------"
        pgrep -f "odoo" | xargs ps -o pid,user,cmd -p 2>/dev/null || echo "No Odoo processes found"
    } > "$report_file"

    log "INFO" "Health report generated: $report_file"
    echo "$report_file"
}

# Main function
main() {
    local mode="${1:-check}"

    case "$mode" in
        "check")
            run_health_check
            ;;
        "monitor")
            monitor_mode
            ;;
        "report")
            generate_report
            ;;
        "auto-heal")
            auto_heal 1
            ;;
        *)
            echo "Usage: $0 {check|monitor|report|auto-heal}"
            echo "  check     - Run one-time health check"
            echo "  monitor   - Start continuous monitoring"
            echo "  report    - Generate detailed health report"
            echo "  auto-heal - Run auto-healing procedures"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
