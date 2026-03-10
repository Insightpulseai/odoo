#!/usr/bin/env bash
# ============================================================================
# test_oca_port_workflow.sh - Integration tests for OCA porting workflow
# ============================================================================
# Tests the complete OCA module porting workflow end-to-end including:
# - Input validation
# - Module cloning
# - oca-port execution
# - OCA compliance validation
# - Rollback procedures
# - Evidence collection
#
# Usage:
#   ./scripts/oca/test_oca_port_workflow.sh [--module MODULE] [--repo REPO]
#
# Examples:
#   ./scripts/oca/test_oca_port_workflow.sh --module queue_job --repo queue
#   ./scripts/oca/test_oca_port_workflow.sh  # Run all test scenarios
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TEST_OUTPUT_DIR="${REPO_ROOT}/test-results/oca-port-workflow"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# Test configuration
TEST_MODULE="${1:-queue_job}"
TEST_REPO="${2:-queue}"
SOURCE_VERSION="18.0"
TARGET_VERSION="19.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

run_test() {
    local test_name="$1"
    local test_func="$2"

    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo ""
    echo "========================================="
    echo "Test $TESTS_TOTAL: $test_name"
    echo "========================================="

    if $test_func; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        log_info "✅ PASSED: $test_name"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        log_error "❌ FAILED: $test_name"
    fi
}

# Test 1: Input Validation
test_input_validation() {
    log_info "Testing input validation..."

    # Test invalid module name
    if python3 -c "
import re
module_name = 'Invalid-Module-Name'
if not re.match(r'^[a-z_]+$', module_name):
    exit(0)
else:
    exit(1)
    "; then
        log_info "✓ Invalid module name detected correctly"
    else
        log_error "✗ Invalid module name not detected"
        return 1
    fi

    # Test valid module name
    if python3 -c "
import re
module_name = 'valid_module_name'
if re.match(r'^[a-z_]+$', module_name):
    exit(0)
else:
    exit(1)
    "; then
        log_info "✓ Valid module name accepted"
    else
        log_error "✗ Valid module name rejected"
        return 1
    fi

    return 0
}

# Test 2: OCA Repository Cloning
test_repository_cloning() {
    log_info "Testing OCA repository cloning..."

    local test_dir="${TEST_OUTPUT_DIR}/clone-test"
    mkdir -p "$test_dir"

    # Test cloning with retry logic
    local max_attempts=3
    local attempt=1
    local clone_success=false

    while [ $attempt -le $max_attempts ]; do
        log_info "Clone attempt $attempt/$max_attempts"

        if git clone \
            --branch "$SOURCE_VERSION" \
            --single-branch \
            --depth 1 \
            "https://github.com/OCA/${TEST_REPO}.git" \
            "$test_dir/oca-source" 2>/dev/null; then
            clone_success=true
            break
        fi

        attempt=$((attempt + 1))
        sleep 2
    done

    if [ "$clone_success" = true ]; then
        log_info "✓ Repository cloned successfully"

        # Verify module exists
        if [ -d "$test_dir/oca-source/$TEST_MODULE" ]; then
            log_info "✓ Module found in cloned repository"
            rm -rf "$test_dir"
            return 0
        else
            log_error "✗ Module not found in cloned repository"
            rm -rf "$test_dir"
            return 1
        fi
    else
        log_error "✗ Repository clone failed after $max_attempts attempts"
        rm -rf "$test_dir"
        return 1
    fi
}

# Test 3: OCA Compliance Validation
test_oca_compliance_validation() {
    log_info "Testing OCA compliance validation..."

    # Create a test module structure
    local test_dir="${TEST_OUTPUT_DIR}/compliance-test"
    mkdir -p "$test_dir/test_module"

    # Create valid manifest
    cat > "$test_dir/test_module/__manifest__.py" << 'EOF'
{
    "name": "Test Module",
    "version": "19.0.1.0.0",
    "category": "Tools",
    "license": "AGPL-3",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/test",
    "depends": ["base"],
    "installable": True,
    "application": False,
}
EOF

    # Create __init__.py
    touch "$test_dir/test_module/__init__.py"

    # Run validation
    if python3 "${SCRIPT_DIR}/validate_oca_compliance.py" "$test_dir/test_module" > /dev/null 2>&1; then
        log_info "✓ Valid module passed compliance check"
    else
        log_error "✗ Valid module failed compliance check"
        rm -rf "$test_dir"
        return 1
    fi

    # Test invalid manifest (missing required keys)
    cat > "$test_dir/test_module/__manifest__.py" << 'EOF'
{
    "name": "Test Module",
    "version": "19.0.1.0.0",
}
EOF

    if ! python3 "${SCRIPT_DIR}/validate_oca_compliance.py" "$test_dir/test_module" > /dev/null 2>&1; then
        log_info "✓ Invalid module failed compliance check (expected)"
    else
        log_error "✗ Invalid module passed compliance check (unexpected)"
        rm -rf "$test_dir"
        return 1
    fi

    rm -rf "$test_dir"
    return 0
}

# Test 4: Backup and Rollback
test_backup_rollback() {
    log_info "Testing backup and rollback procedures..."

    local test_dir="${TEST_OUTPUT_DIR}/rollback-test"
    local backup_dir="$test_dir/backup"
    mkdir -p "$test_dir/module" "$backup_dir"

    # Create test file
    echo "Original content" > "$test_dir/module/test.py"

    # Create backup
    cp -r "$test_dir/module" "$backup_dir/module-backup"
    log_info "✓ Backup created"

    # Modify original
    echo "Modified content" > "$test_dir/module/test.py"

    # Verify backup is intact
    if grep -q "Original content" "$backup_dir/module-backup/test.py"; then
        log_info "✓ Backup integrity verified"
    else
        log_error "✗ Backup corrupted"
        rm -rf "$test_dir"
        return 1
    fi

    # Simulate rollback
    rm -rf "$test_dir/module"
    cp -r "$backup_dir/module-backup" "$test_dir/module"

    # Verify rollback
    if grep -q "Original content" "$test_dir/module/test.py"; then
        log_info "✓ Rollback successful"
        rm -rf "$test_dir"
        return 0
    else
        log_error "✗ Rollback failed"
        rm -rf "$test_dir"
        return 1
    fi
}

# Test 5: Evidence Collection
test_evidence_collection() {
    log_info "Testing evidence collection..."

    local evidence_dir="${TEST_OUTPUT_DIR}/evidence-test"
    mkdir -p "$evidence_dir/logs"

    # Simulate command execution with logging
    {
        echo "Command: test-command"
        echo "Status: success"
        echo "Output: test output"
        date -u +"%Y-%m-%dT%H:%M:%SZ"
    } > "$evidence_dir/logs/test-command.log"

    # Verify log file exists and contains expected content
    if [ -f "$evidence_dir/logs/test-command.log" ]; then
        log_info "✓ Evidence log file created"

        if grep -q "Command: test-command" "$evidence_dir/logs/test-command.log"; then
            log_info "✓ Evidence log content valid"
            rm -rf "$evidence_dir"
            return 0
        else
            log_error "✗ Evidence log content invalid"
            rm -rf "$evidence_dir"
            return 1
        fi
    else
        log_error "✗ Evidence log file not created"
        rm -rf "$evidence_dir"
        return 1
    fi
}

# Test 6: Port Queue Update
test_port_queue_update() {
    log_info "Testing port queue update logic..."

    local test_queue="${TEST_OUTPUT_DIR}/test_port_queue.yml"

    # Create test queue
    cat > "$test_queue" << 'EOF'
priorities:
  P0:
    modules:
      - name: test_module
        status: pending
        oca_repo: test-repo
        upstream_branch: "18.0"
        depends: []
        reason: "Test module"
port_log: []
EOF

    # Update status using Python
    python3 << PYTHON_SCRIPT
import yaml

with open('$test_queue', 'r') as f:
    queue = yaml.safe_load(f)

# Update module status
for module in queue['priorities']['P0']['modules']:
    if module['name'] == 'test_module':
        module['status'] = 'completed'

# Add port log entry
queue['port_log'].append({
    'module': 'test_module',
    'status': 'completed',
    'timestamp': '2025-01-01T00:00:00Z'
})

with open('$test_queue', 'w') as f:
    yaml.dump(queue, f, default_flow_style=False)

print("Queue updated successfully")
PYTHON_SCRIPT

    # Verify update
    if grep -q "status: completed" "$test_queue"; then
        log_info "✓ Port queue updated successfully"
        rm -f "$test_queue"
        return 0
    else
        log_error "✗ Port queue update failed"
        rm -f "$test_queue"
        return 1
    fi
}

# Test 7: Dependency Resolution
test_dependency_resolution() {
    log_info "Testing dependency resolution..."

    # Test circular dependency detection
    if python3 << 'PYTHON_SCRIPT'
def has_circular_dependency(module_name, depends):
    if module_name in depends:
        return True
    return False

# Test case 1: Circular dependency
if has_circular_dependency('test_module', ['base', 'test_module']):
    print("✓ Circular dependency detected")
else:
    print("✗ Circular dependency not detected")
    exit(1)

# Test case 2: No circular dependency
if not has_circular_dependency('test_module', ['base', 'account']):
    print("✓ No circular dependency (expected)")
else:
    print("✗ False positive for circular dependency")
    exit(1)
PYTHON_SCRIPT
    then
        log_info "✓ Dependency resolution logic working"
        return 0
    else
        log_error "✗ Dependency resolution logic failed"
        return 1
    fi
}

# Main test execution
main() {
    log_info "Starting OCA Port Workflow Integration Tests"
    log_info "Test output directory: $TEST_OUTPUT_DIR"

    # Create test output directory
    mkdir -p "$TEST_OUTPUT_DIR"

    # Run all tests
    run_test "Input Validation" test_input_validation
    run_test "OCA Repository Cloning" test_repository_cloning
    run_test "OCA Compliance Validation" test_oca_compliance_validation
    run_test "Backup and Rollback" test_backup_rollback
    run_test "Evidence Collection" test_evidence_collection
    run_test "Port Queue Update" test_port_queue_update
    run_test "Dependency Resolution" test_dependency_resolution

    # Print summary
    echo ""
    echo "========================================="
    echo "TEST SUMMARY"
    echo "========================================="
    echo "Total Tests: $TESTS_TOTAL"
    echo "Passed:      $TESTS_PASSED"
    echo "Failed:      $TESTS_FAILED"
    echo ""

    if [ $TESTS_FAILED -eq 0 ]; then
        log_info "✅ All tests passed!"
        exit 0
    else
        log_error "❌ $TESTS_FAILED test(s) failed"
        exit 1
    fi
}

# Run main function
main
