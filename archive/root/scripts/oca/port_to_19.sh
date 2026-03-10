#!/usr/bin/env bash
# =============================================================================
# OCA Module Porting Harness: 18.0 → 19.0
# =============================================================================
# Automates the OCA canonical porting workflow (git format-patch + git am).
# Follows: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0
#
# USAGE:
#   ./scripts/oca/port_to_19.sh <repo> <module> [options]
#
# ARGUMENTS:
#   repo       OCA repository name (e.g., server-env, connector)
#   module     Module name to port (e.g., server_environment)
#
# OPTIONS:
#   --upstream-org ORG    Upstream GitHub org (default: OCA)
#   --fork-org ORG        Your fork org (for pushing branches)
#   --base-branch VER     Source version branch (default: 18.0)
#   --target-branch VER   Target version branch (default: 19.0)
#   --work-dir PATH       Working directory for clones (default: /tmp/oca-port)
#   --dry-run             Show what would be done without executing
#   --help                Show this help message
#
# EXAMPLES:
#   # Port server_environment from server-env repo
#   ./scripts/oca/port_to_19.sh server-env server_environment
#
#   # Port with custom fork org
#   ./scripts/oca/port_to_19.sh server-env server_environment --fork-org myusername
#
#   # Dry-run to see commands
#   ./scripts/oca/port_to_19.sh connector component --dry-run
#
# PREREQUISITES:
#   - git configured (user.name, user.email)
#   - pre-commit installed (pip install pre-commit) - optional but recommended
#   - Write access to fork if pushing branches
#
# OUTPUT:
#   - Cloned repo in: $WORK_DIR/<repo>
#   - Migration branch: 19.0-mig-<module>
#   - Next steps printed for manual review/testing
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

# Defaults
UPSTREAM_ORG="${UPSTREAM_ORG:-OCA}"
FORK_ORG="${FORK_ORG:-}"
BASE_BRANCH="${BASE_BRANCH:-18.0}"
TARGET_BRANCH="${TARGET_BRANCH:-19.0}"
WORK_DIR="${WORK_DIR:-/tmp/oca-port}"
DRY_RUN=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

log_info() {
    echo -e "${BLUE}ℹ ${NC}$*"
}

log_success() {
    echo -e "${GREEN}✓${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $*"
}

log_error() {
    echo -e "${RED}✗${NC} $*" >&2
}

show_help() {
    grep '^#' "$0" | grep -v '#!/usr/bin/env bash' | sed 's/^# //' | sed 's/^#//'
    exit 0
}

run_cmd() {
    local cmd="$*"
    if [[ "$DRY_RUN" == true ]]; then
        echo "[DRY-RUN] $cmd"
    else
        log_info "Running: $cmd"
        eval "$cmd"
    fi
}

# -----------------------------------------------------------------------------
# Argument Parsing
# -----------------------------------------------------------------------------

if [[ $# -eq 0 ]] || [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    show_help
fi

REPO_NAME=""
MODULE_NAME=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --upstream-org)
            UPSTREAM_ORG="$2"
            shift 2
            ;;
        --fork-org)
            FORK_ORG="$2"
            shift 2
            ;;
        --base-branch)
            BASE_BRANCH="$2"
            shift 2
            ;;
        --target-branch)
            TARGET_BRANCH="$2"
            shift 2
            ;;
        --work-dir)
            WORK_DIR="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            show_help
            ;;
        -*)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
        *)
            if [[ -z "$REPO_NAME" ]]; then
                REPO_NAME="$1"
            elif [[ -z "$MODULE_NAME" ]]; then
                MODULE_NAME="$1"
            else
                log_error "Too many positional arguments: $1"
                echo "Use --help for usage information"
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate required arguments
if [[ -z "$REPO_NAME" ]] || [[ -z "$MODULE_NAME" ]]; then
    log_error "Missing required arguments: <repo> <module>"
    echo "Use --help for usage information"
    exit 1
fi

# -----------------------------------------------------------------------------
# Main Porting Workflow
# -----------------------------------------------------------------------------

log_info "OCA Module Porting Harness"
echo "============================================"
echo "Repository:      $REPO_NAME"
echo "Module:          $MODULE_NAME"
echo "Upstream Org:    $UPSTREAM_ORG"
echo "Fork Org:        ${FORK_ORG:-<none>}"
echo "Base Branch:     $BASE_BRANCH"
echo "Target Branch:   $TARGET_BRANCH"
echo "Work Directory:  $WORK_DIR"
echo "Dry Run:         $DRY_RUN"
echo "============================================"
echo ""

# Step 1: Setup work directory
log_info "Step 1: Setup work directory"
run_cmd "mkdir -p \"$WORK_DIR\""

REPO_DIR="$WORK_DIR/$REPO_NAME"
UPSTREAM_URL="https://github.com/$UPSTREAM_ORG/$REPO_NAME"
MIG_BRANCH="$TARGET_BRANCH-mig-$MODULE_NAME"

# Step 2: Clone repository
log_info "Step 2: Clone OCA repository"
if [[ -d "$REPO_DIR" ]]; then
    log_warn "Repository already exists: $REPO_DIR"
    log_info "Using existing clone (run 'git pull' manually if needed)"
else
    run_cmd "git clone -b \"$TARGET_BRANCH\" \"$UPSTREAM_URL\" \"$REPO_DIR\""
    log_success "Cloned $UPSTREAM_URL"
fi

# Step 3: Navigate to repo
if [[ "$DRY_RUN" == false ]]; then
    cd "$REPO_DIR"
    log_info "Working directory: $(pwd)"
fi

# Step 4: Fetch all branches
log_info "Step 3: Fetch all branches"
run_cmd "cd \"$REPO_DIR\" && git fetch origin"

# Step 5: Create migration branch
log_info "Step 4: Create migration branch"
if [[ "$DRY_RUN" == false ]]; then
    if git show-ref --verify --quiet "refs/heads/$MIG_BRANCH"; then
        log_warn "Migration branch already exists: $MIG_BRANCH"
        log_warn "Delete it first if you want to start fresh: git branch -D $MIG_BRANCH"
        echo ""
        log_info "Checking out existing branch..."
        run_cmd "git checkout \"$MIG_BRANCH\""
    else
        run_cmd "git checkout -b \"$MIG_BRANCH\""
        log_success "Created branch: $MIG_BRANCH"
    fi
fi

# Step 6: Check if module exists in source branch
log_info "Step 5: Check module existence in $BASE_BRANCH"
if [[ "$DRY_RUN" == false ]]; then
    if git ls-tree -d "origin/$BASE_BRANCH" "$MODULE_NAME" | grep -q "$MODULE_NAME"; then
        log_success "Module $MODULE_NAME found in $BASE_BRANCH"
    else
        log_error "Module $MODULE_NAME does NOT exist in $BASE_BRANCH branch"
        log_error "Cannot port via patch method. Options:"
        log_error "  1. Check earlier versions (17.0, 16.0)"
        log_error "  2. Create module from scratch"
        log_error "  3. Mark as abandoned in port queue"
        exit 1
    fi
fi

# Step 7: Extract patches from base branch
log_info "Step 6: Extract patches from $BASE_BRANCH"
PATCH_DIR="$REPO_DIR/patches-$MODULE_NAME"
run_cmd "cd \"$REPO_DIR\" && mkdir -p \"$PATCH_DIR\""
run_cmd "cd \"$REPO_DIR\" && git format-patch --relative=\"$MODULE_NAME\" -o \"$PATCH_DIR\" \"origin/$BASE_BRANCH..origin/$TARGET_BRANCH\" -- \"$MODULE_NAME/\""

if [[ "$DRY_RUN" == false ]]; then
    PATCH_COUNT=$(find "$PATCH_DIR" -name "*.patch" 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$PATCH_COUNT" -eq 0 ]]; then
        log_warn "No patches created - module may not have changes between $BASE_BRANCH and $TARGET_BRANCH"
        log_warn "This could mean:"
        log_warn "  - Module already exists in $TARGET_BRANCH"
        log_warn "  - Module was deleted in $TARGET_BRANCH"
        log_warn "  - No commit history for module in range"
        echo ""
        log_info "Check manually:"
        echo "  cd $REPO_DIR"
        echo "  git log origin/$BASE_BRANCH..origin/$TARGET_BRANCH -- $MODULE_NAME/"
        exit 1
    else
        log_success "Created $PATCH_COUNT patch(es) in $PATCH_DIR"
    fi
fi

# Step 8: Apply patches
log_info "Step 7: Apply patches to $TARGET_BRANCH"
run_cmd "cd \"$REPO_DIR\" && git am -3 --keep \"$PATCH_DIR\"/*.patch"

if [[ "$DRY_RUN" == false ]]; then
    # Check if git am succeeded
    if git -C "$REPO_DIR" status | grep -q "git am in progress"; then
        log_error "Patch application failed with conflicts!"
        log_error "To resolve:"
        echo "  1. cd $REPO_DIR"
        echo "  2. Edit conflicted files (look for <<<<<<< markers)"
        echo "  3. git add <fixed-files>"
        echo "  4. git am --continue"
        echo ""
        log_error "Or retry with --ignore-whitespace:"
        echo "  git am -3 --keep --ignore-whitespace $PATCH_DIR/*.patch"
        echo ""
        log_error "To abort: git am --abort"
        exit 1
    else
        log_success "Patches applied successfully"
    fi
fi

# Step 9: Run pre-commit (if available)
log_info "Step 8: Run pre-commit auto-fixes"
if command -v pre-commit &> /dev/null; then
    run_cmd "cd \"$REPO_DIR\" && pre-commit run -a || true"

    if [[ "$DRY_RUN" == false ]]; then
        # Check if pre-commit made changes
        if ! git -C "$REPO_DIR" diff --quiet; then
            log_warn "Pre-commit made changes - committing auto-fixes"
            run_cmd "cd \"$REPO_DIR\" && git add ."
            run_cmd "cd \"$REPO_DIR\" && git commit -m \"[IMP] $MODULE_NAME: pre-commit auto fixes\" --no-verify"
            log_success "Committed pre-commit fixes"
        else
            log_info "No pre-commit changes needed"
        fi
    fi
else
    log_warn "pre-commit not installed - skipping auto-fixes"
    log_warn "Install with: pip install pre-commit"
fi

# Step 10: Summary and next steps
echo ""
echo "============================================"
log_success "Automated porting steps complete!"
echo "============================================"
echo ""
echo "📁 Repository:  $REPO_DIR"
echo "🌿 Branch:      $MIG_BRANCH"
echo "📦 Module:      $MODULE_NAME"
echo ""
echo "NEXT STEPS (Manual Review Required):"
echo ""
echo "1. Review changes:"
echo "   cd $REPO_DIR"
echo "   git log --oneline -10"
echo "   git diff origin/$TARGET_BRANCH"
echo ""
echo "2. Manual framework updates (check docs/oca/PORTING_19_RUNBOOK.md):"
echo "   - API changes: groups_id → group_ids, self._cr → self.env.cr"
echo "   - Remove @api.multi decorators"
echo "   - Update view XML if needed"
echo ""
echo "3. Test installation:"
echo "   odoo-bin -i $MODULE_NAME --stop-after-init --database odoo_test"
echo ""
echo "4. Run tests:"
echo "   odoo-bin -i $MODULE_NAME --test-enable --stop-after-init --database odoo_test"
echo ""
echo "5. Update port queue:"
echo "   Edit: config/oca/port_queue.yml"
echo "   Change status from 'missing' to 'complete'"
echo ""
if [[ -n "$FORK_ORG" ]]; then
    echo "6. Push to your fork:"
    echo "   cd $REPO_DIR"
    echo "   git remote add fork https://github.com/$FORK_ORG/$REPO_NAME"
    echo "   git push fork $MIG_BRANCH"
    echo ""
    echo "7. Create PR to OCA:"
    echo "   Visit: https://github.com/$UPSTREAM_ORG/$REPO_NAME/compare/$TARGET_BRANCH...$FORK_ORG:$MIG_BRANCH"
    echo "   Title: [MIG] $MODULE_NAME: migration to $TARGET_BRANCH"
    echo ""
fi
echo "Runbook: docs/oca/PORTING_19_RUNBOOK.md"
echo "Queue:   config/oca/port_queue.yml"
echo "============================================"
