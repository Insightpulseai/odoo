#!/usr/bin/env bash
# =============================================================================
# Backup Restore Test Script - Odoo.sh Multi-DC Parity (GAP 3)
# =============================================================================
# Validates backup integrity and performs test restores
# Implements Odoo.sh-style backup verification
#
# Usage:
#   ./scripts/backup/restore_test.sh [options]
#
# Options:
#   --backup FILE     Specific backup file to test
#   --latest          Test the most recent backup
#   --region REGION   Restore from specific region
#   --db-name NAME    Target database name for restore test
#   --dry-run         Show what would be done
#   --verbose         Enable verbose output
# =============================================================================

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================

SCRIPT_VERSION="1.0.0"
SCRIPT_NAME=$(basename "$0")

# Directories
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-/var/backups/odoo}"
RESTORE_TEST_DIR="${RESTORE_TEST_DIR:-/tmp/odoo_restore_test}"

# Database
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-odoo}"
TEST_DB_NAME="${TEST_DB_NAME:-odoo_restore_test}"

# S3/Spaces
PRIMARY_BUCKET="${S3_PRIMARY_BUCKET:-odoo-backups-primary}"
PRIMARY_REGION="${PRIMARY_REGION:-sgp1}"

# Defaults
BACKUP_FILE=""
USE_LATEST=false
SPECIFIC_REGION=""
DRY_RUN=false
VERBOSE=false

# =============================================================================
# Helper Functions
# =============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case "$level" in
        INFO)  echo -e "[\033[0;32m$level\033[0m] $timestamp - $message" ;;
        WARN)  echo -e "[\033[0;33m$level\033[0m] $timestamp - $message" ;;
        ERROR) echo -e "[\033[0;31m$level\033[0m] $timestamp - $message" >&2 ;;
        DEBUG) [ "$VERBOSE" = true ] && echo -e "[\033[0;36m$level\033[0m] $timestamp - $message" ;;
        PASS)  echo -e "[\033[0;32m✓ PASS\033[0m] $timestamp - $message" ;;
        FAIL)  echo -e "[\033[0;31m✗ FAIL\033[0m] $timestamp - $message" ;;
    esac
}

die() {
    log ERROR "$@"
    exit 1
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --backup)
                BACKUP_FILE="$2"
                shift 2
                ;;
            --latest)
                USE_LATEST=true
                shift
                ;;
            --region)
                SPECIFIC_REGION="$2"
                shift 2
                ;;
            --db-name)
                TEST_DB_NAME="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                die "Unknown option: $1"
                ;;
        esac
    done
}

usage() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS]

Odoo Backup Restore Test (Odoo.sh Parity)

Options:
    --backup FILE     Specific backup file to test
    --latest          Test the most recent backup
    --region REGION   Restore from specific region
    --db-name NAME    Target database for restore test (default: $TEST_DB_NAME)
    --dry-run         Show what would be done
    --verbose, -v     Enable verbose output
    --help, -h        Show this help

Example:
    # Test latest backup
    PGPASSWORD=secret ./restore_test.sh --latest

    # Test specific backup
    PGPASSWORD=secret ./restore_test.sh --backup /path/to/backup.sql.gz

    # Dry run
    ./restore_test.sh --latest --dry-run

EOF
}

# =============================================================================
# Test Functions
# =============================================================================

find_latest_backup() {
    local backup_type="$1"  # "db" or "files"

    log INFO "Finding latest $backup_type backup..."

    # Check local backups first
    local local_backup=$(find "$BACKUP_BASE_DIR/$backup_type" -name "*.gz" -type f 2>/dev/null | sort -r | head -1)

    if [ -n "$local_backup" ]; then
        log INFO "Found local backup: $local_backup"
        echo "$local_backup"
        return 0
    fi

    # Check S3/Spaces
    if command -v aws &> /dev/null; then
        local s3_backup=$(aws s3 ls "s3://$PRIMARY_BUCKET/" --recursive 2>/dev/null | \
            grep "\.sql\.gz$\|\.tar\.gz$" | \
            sort -k1,2 -r | \
            head -1 | \
            awk '{print $4}')

        if [ -n "$s3_backup" ]; then
            log INFO "Found S3 backup: $s3_backup"
            echo "s3://$PRIMARY_BUCKET/$s3_backup"
            return 0
        fi
    fi

    log ERROR "No backup found"
    return 1
}

download_backup() {
    local backup_path="$1"
    local local_path="$2"

    if [[ "$backup_path" == s3://* ]]; then
        log INFO "Downloading from S3: $backup_path"

        if [ "$DRY_RUN" = true ]; then
            log INFO "[DRY-RUN] Would download $backup_path to $local_path"
            return 0
        fi

        mkdir -p "$(dirname "$local_path")"
        aws s3 cp "$backup_path" "$local_path" --only-show-errors
    else
        # Local file
        if [ ! -f "$backup_path" ]; then
            die "Backup file not found: $backup_path"
        fi
        cp "$backup_path" "$local_path"
    fi
}

test_backup_integrity() {
    local backup_file="$1"

    log INFO "Testing backup integrity: $backup_file"

    if [ "$DRY_RUN" = true ]; then
        log INFO "[DRY-RUN] Would test integrity of $backup_file"
        return 0
    fi

    # Test gzip integrity
    if [[ "$backup_file" == *.gz ]]; then
        if gzip -t "$backup_file" 2>/dev/null; then
            log PASS "Gzip integrity check passed"
        else
            log FAIL "Gzip integrity check failed"
            return 1
        fi
    fi

    # Test tar integrity (for filestore backups)
    if [[ "$backup_file" == *.tar.gz ]]; then
        if tar -tzf "$backup_file" &>/dev/null; then
            log PASS "Tar archive integrity check passed"
        else
            log FAIL "Tar archive integrity check failed"
            return 1
        fi
    fi

    return 0
}

test_database_restore() {
    local backup_file="$1"

    log INFO "Testing database restore: $backup_file"

    if [ "$DRY_RUN" = true ]; then
        log INFO "[DRY-RUN] Would restore database from $backup_file"
        return 0
    fi

    # Drop test database if exists
    log DEBUG "Dropping existing test database..."
    dropdb --host="$DB_HOST" --port="$DB_PORT" --username="$DB_USER" \
           --if-exists "$TEST_DB_NAME" 2>/dev/null || true

    # Create test database
    log DEBUG "Creating test database..."
    createdb --host="$DB_HOST" --port="$DB_PORT" --username="$DB_USER" \
             "$TEST_DB_NAME" || die "Failed to create test database"

    # Restore backup
    log INFO "Restoring backup..."
    local restore_start=$(date +%s)

    if [[ "$backup_file" == *.sql.gz ]]; then
        gunzip -c "$backup_file" | psql \
            --host="$DB_HOST" \
            --port="$DB_PORT" \
            --username="$DB_USER" \
            --dbname="$TEST_DB_NAME" \
            --quiet 2>/dev/null
    elif [[ "$backup_file" == *.sql ]]; then
        psql \
            --host="$DB_HOST" \
            --port="$DB_PORT" \
            --username="$DB_USER" \
            --dbname="$TEST_DB_NAME" \
            --file="$backup_file" \
            --quiet 2>/dev/null
    else
        # Try pg_restore for custom format
        pg_restore \
            --host="$DB_HOST" \
            --port="$DB_PORT" \
            --username="$DB_USER" \
            --dbname="$TEST_DB_NAME" \
            --no-owner \
            --no-acl \
            "$backup_file" 2>/dev/null || {
                log WARN "pg_restore failed, trying plain restore..."
                gunzip -c "$backup_file" 2>/dev/null | psql \
                    --host="$DB_HOST" \
                    --port="$DB_PORT" \
                    --username="$DB_USER" \
                    --dbname="$TEST_DB_NAME" \
                    --quiet 2>/dev/null
            }
    fi

    local restore_end=$(date +%s)
    local restore_duration=$((restore_end - restore_start))

    log PASS "Database restore completed in ${restore_duration}s"

    # Verify restore
    verify_database_restore
}

verify_database_restore() {
    log INFO "Verifying database restore..."

    # Count tables
    local table_count=$(psql \
        --host="$DB_HOST" \
        --port="$DB_PORT" \
        --username="$DB_USER" \
        --dbname="$TEST_DB_NAME" \
        --tuples-only \
        --command="SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')

    if [ -z "$table_count" ] || [ "$table_count" -eq 0 ]; then
        log FAIL "No tables found in restored database"
        return 1
    fi

    log PASS "Found $table_count tables in restored database"

    # Check critical Odoo tables
    local critical_tables=("ir_module_module" "res_users" "res_company")
    for table in "${critical_tables[@]}"; do
        local exists=$(psql \
            --host="$DB_HOST" \
            --port="$DB_PORT" \
            --username="$DB_USER" \
            --dbname="$TEST_DB_NAME" \
            --tuples-only \
            --command="SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '$table');" 2>/dev/null | tr -d ' ')

        if [ "$exists" = "t" ]; then
            log PASS "Critical table exists: $table"
        else
            log FAIL "Critical table missing: $table"
            return 1
        fi
    done

    # Check data integrity
    local user_count=$(psql \
        --host="$DB_HOST" \
        --port="$DB_PORT" \
        --username="$DB_USER" \
        --dbname="$TEST_DB_NAME" \
        --tuples-only \
        --command="SELECT COUNT(*) FROM res_users;" 2>/dev/null | tr -d ' ')

    log INFO "Users in restored database: $user_count"

    return 0
}

test_filestore_restore() {
    local backup_file="$1"

    log INFO "Testing filestore restore: $backup_file"

    if [ "$DRY_RUN" = true ]; then
        log INFO "[DRY-RUN] Would restore filestore from $backup_file"
        return 0
    fi

    local restore_dir="$RESTORE_TEST_DIR/filestore"
    rm -rf "$restore_dir"
    mkdir -p "$restore_dir"

    # Extract filestore
    tar -xzf "$backup_file" -C "$restore_dir"

    # Verify extraction
    local file_count=$(find "$restore_dir" -type f | wc -l)

    if [ "$file_count" -gt 0 ]; then
        log PASS "Filestore restored: $file_count files"
    else
        log FAIL "No files extracted from filestore backup"
        return 1
    fi

    return 0
}

cleanup_test() {
    log INFO "Cleaning up test resources..."

    if [ "$DRY_RUN" = true ]; then
        log INFO "[DRY-RUN] Would clean up test resources"
        return 0
    fi

    # Drop test database
    dropdb --host="$DB_HOST" --port="$DB_PORT" --username="$DB_USER" \
           --if-exists "$TEST_DB_NAME" 2>/dev/null || true

    # Clean up restore test directory
    rm -rf "$RESTORE_TEST_DIR"

    log INFO "Cleanup complete"
}

generate_report() {
    local results="$1"

    log INFO "=== Restore Test Report ==="

    echo ""
    echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "Test Database: $TEST_DB_NAME"
    echo ""
    echo "Results:"
    echo "$results"
    echo ""

    # Write report to file
    local report_file="$BACKUP_BASE_DIR/reports/restore_test_$(date +%Y%m%d_%H%M%S).txt"

    if [ "$DRY_RUN" = false ]; then
        mkdir -p "$(dirname "$report_file")"
        echo "Restore Test Report - $(date)" > "$report_file"
        echo "" >> "$report_file"
        echo "$results" >> "$report_file"
        log INFO "Report saved: $report_file"
    fi
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
    log INFO "=== Odoo Backup Restore Test v$SCRIPT_VERSION ==="

    # Parse arguments
    parse_args "$@"

    # Setup
    mkdir -p "$RESTORE_TEST_DIR"

    # Track results
    local results=""
    local overall_status="PASS"

    # Find backup to test
    if [ "$USE_LATEST" = true ]; then
        BACKUP_FILE=$(find_latest_backup "db")
    fi

    if [ -z "$BACKUP_FILE" ]; then
        die "No backup file specified. Use --backup FILE or --latest"
    fi

    # Download if remote
    local local_backup="$RESTORE_TEST_DIR/$(basename "$BACKUP_FILE")"

    if [[ "$BACKUP_FILE" == s3://* ]]; then
        download_backup "$BACKUP_FILE" "$local_backup"
        BACKUP_FILE="$local_backup"
    fi

    # Run tests
    log INFO "Starting restore tests..."

    # Test 1: Integrity check
    if test_backup_integrity "$BACKUP_FILE"; then
        results="${results}✓ Integrity check: PASS\n"
    else
        results="${results}✗ Integrity check: FAIL\n"
        overall_status="FAIL"
    fi

    # Test 2: Database restore (if SQL backup)
    if [[ "$BACKUP_FILE" == *.sql* ]]; then
        if test_database_restore "$BACKUP_FILE"; then
            results="${results}✓ Database restore: PASS\n"
        else
            results="${results}✗ Database restore: FAIL\n"
            overall_status="FAIL"
        fi
    fi

    # Test 3: Filestore restore (if tar backup)
    if [[ "$BACKUP_FILE" == *.tar.gz ]]; then
        if test_filestore_restore "$BACKUP_FILE"; then
            results="${results}✓ Filestore restore: PASS\n"
        else
            results="${results}✗ Filestore restore: FAIL\n"
            overall_status="FAIL"
        fi
    fi

    # Generate report
    results="${results}\n=== Overall: $overall_status ==="
    generate_report "$results"

    # Cleanup
    cleanup_test

    # Exit with appropriate code
    if [ "$overall_status" = "PASS" ]; then
        log INFO "=== All restore tests PASSED ==="
        exit 0
    else
        log ERROR "=== Some restore tests FAILED ==="
        exit 1
    fi
}

# Run main
main "$@"
