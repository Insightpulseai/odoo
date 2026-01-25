#!/usr/bin/env bash
# =============================================================================
# Model Repo Scanner - Find & Score Repositories
# =============================================================================
# Discovers and ranks repositories in a GitHub org based on:
# - CI & governance maturity
# - Integration surfaces (Supabase, MCP, n8n, Vercel)
# - Automation maturity
# - Recency & adoption readiness
#
# Usage:
#   ./scripts/find_model_repo.sh [options]
#
# Options:
#   -o, --org <org>       GitHub organization (default: from config)
#   -c, --config <file>   Config file path (default: config/scoring.yaml)
#   -v, --verbose         Verbose output
#   -h, --help            Show help
#
# Output:
#   artifacts/model-repo-scores.json
#   artifacts/model-repo-report.md
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Defaults
CONFIG_FILE="${BASE_DIR}/config/scoring.yaml"
CACHE_DIR="${BASE_DIR}/.cache/repos"
ARTIFACTS_DIR="${BASE_DIR}/artifacts"
VERBOSE=false
GITHUB_ORG="${GITHUB_ORG:-}"

# =============================================================================
# Functions
# =============================================================================
log() { echo -e "${BLUE}[INFO]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
debug() { [[ "$VERBOSE" == "true" ]] && echo -e "${CYAN}[DEBUG]${NC} $*" || true; }

show_help() {
    cat << 'EOF'
Model Repo Scanner - Find & Score Repositories

USAGE:
    find_model_repo.sh [options]

OPTIONS:
    -o, --org <org>       GitHub organization (or set GITHUB_ORG env)
    -c, --config <file>   Config file path (default: config/scoring.yaml)
    -v, --verbose         Verbose output
    -h, --help            Show help

ENVIRONMENT:
    GITHUB_ORG            Target GitHub organization
    GITHUB_TOKEN          GitHub API token (for private repos)

OUTPUT:
    artifacts/model-repo-scores.json   Machine-readable scores
    artifacts/model-repo-report.md     Human-readable report
EOF
}

check_dependencies() {
    local missing=()

    command -v jq &>/dev/null || missing+=("jq")
    command -v gh &>/dev/null || missing+=("gh")

    if [[ ${#missing[@]} -gt 0 ]]; then
        error "Missing dependencies: ${missing[*]}"
        echo "Install with: apt-get install ${missing[*]} / brew install ${missing[*]}"
        exit 1
    fi

    # Check gh auth
    if ! gh auth status &>/dev/null 2>&1; then
        warn "gh not authenticated - will use GITHUB_TOKEN if available"
    fi
}

parse_yaml_value() {
    local file="$1"
    local key="$2"
    # Simple YAML parser for single values
    grep -E "^${key}:" "$file" 2>/dev/null | head -1 | sed 's/.*: *//' | tr -d '"' || echo ""
}

get_org_repos() {
    local org="$1"
    log "Fetching repositories for org: $org"

    gh repo list "$org" --limit 100 --json name,isArchived,pushedAt,defaultBranchRef \
        --jq '.[] | select(.isArchived == false) | .name' 2>/dev/null || {
        # Fallback to API
        curl -sS -H "Authorization: token ${GITHUB_TOKEN:-}" \
            "https://api.github.com/orgs/${org}/repos?per_page=100" \
            | jq -r '.[] | select(.archived == false) | .name'
    }
}

clone_repo() {
    local org="$1"
    local repo="$2"
    local target="${CACHE_DIR}/${repo}"

    if [[ -d "$target" ]]; then
        debug "Using cached: $target"
        (cd "$target" && git fetch --depth=1 origin 2>/dev/null || true)
    else
        debug "Cloning: $org/$repo"
        gh repo clone "$org/$repo" "$target" -- --depth=1 2>/dev/null || {
            git clone --depth=1 "https://github.com/${org}/${repo}.git" "$target" 2>/dev/null || {
                warn "Failed to clone $org/$repo"
                return 1
            }
        }
    fi
    echo "$target"
}

count_pattern_matches() {
    local repo_path="$1"
    local pattern="$2"
    local count=0

    # Use find for glob patterns
    if [[ "$pattern" == *"**"* ]] || [[ "$pattern" == *"*"* ]]; then
        count=$(find "$repo_path" -path "$repo_path/$pattern" -type f 2>/dev/null | wc -l | tr -d ' ')
    else
        [[ -f "$repo_path/$pattern" ]] && count=1
    fi

    echo "$count"
}

search_content_pattern() {
    local repo_path="$1"
    local pattern="$2"
    local matches=""

    # Use ripgrep if available, else grep
    if command -v rg &>/dev/null; then
        matches=$(rg -l --no-messages "$pattern" "$repo_path" 2>/dev/null | head -5 || true)
    else
        matches=$(grep -rl "$pattern" "$repo_path" 2>/dev/null | head -5 || true)
    fi

    echo "$matches"
}

collect_evidence() {
    local repo_path="$1"
    local pattern="$2"
    local max_lines="${3:-5}"

    local evidence=""
    local files

    if command -v rg &>/dev/null; then
        files=$(rg -l --no-messages "$pattern" "$repo_path" 2>/dev/null | head -3 || true)
    else
        files=$(grep -rl "$pattern" "$repo_path" 2>/dev/null | head -3 || true)
    fi

    for file in $files; do
        local rel_path="${file#$repo_path/}"
        local context
        if command -v rg &>/dev/null; then
            context=$(rg -C1 --no-heading "$pattern" "$file" 2>/dev/null | head -"$max_lines" || true)
        else
            context=$(grep -C1 "$pattern" "$file" 2>/dev/null | head -"$max_lines" || true)
        fi
        if [[ -n "$context" ]]; then
            evidence+="  - \`$rel_path\`: \`${context:0:100}...\`\n"
        fi
    done

    echo -e "$evidence"
}

score_ci_governance() {
    local repo_path="$1"
    local score=0
    local evidence=""

    # CI scripts (max 10)
    local ci_patterns=("scripts/ci" "scripts/run_all.sh" "scripts/ci_local.sh" "scripts/verify")
    for pattern in "${ci_patterns[@]}"; do
        if [[ -e "$repo_path/$pattern" ]] || [[ -d "$repo_path/$pattern" ]]; then
            score=$((score + 2))
            evidence+="  - Found: \`$pattern\`\n"
        fi
    done
    [[ $score -gt 10 ]] && score=10

    # Workflows (max 10)
    local wf_count
    wf_count=$(find "$repo_path/.github/workflows" -name "*.yml" -o -name "*.yaml" 2>/dev/null | wc -l | tr -d ' ')
    if [[ $wf_count -gt 0 ]]; then
        local wf_score=$((wf_count > 10 ? 10 : wf_count))
        score=$((score + wf_score))
        evidence+="  - Workflows: $wf_count files\n"
    fi

    # Governance (max 10)
    local gov_score=0
    [[ -f "$repo_path/CODEOWNERS" ]] || [[ -f "$repo_path/.github/CODEOWNERS" ]] && { gov_score=$((gov_score + 3)); evidence+="  - CODEOWNERS: present\n"; }
    [[ -d "$repo_path/.github/ISSUE_TEMPLATE" ]] && { gov_score=$((gov_score + 2)); evidence+="  - Issue templates: present\n"; }
    [[ -f "$repo_path/.github/pull_request_template.md" ]] && { gov_score=$((gov_score + 2)); evidence+="  - PR template: present\n"; }
    [[ -d "$repo_path/spec" ]] && { gov_score=$((gov_score + 3)); evidence+="  - Spec Kit: present\n"; }
    score=$((score + gov_score))

    [[ $score -gt 30 ]] && score=30

    echo "$score"
    echo -e "$evidence" >&2
}

score_integration() {
    local repo_path="$1"
    local score=0
    local evidence=""

    # Supabase (max 8)
    local supa_score=0
    [[ -f "$repo_path/supabase/config.toml" ]] && { supa_score=$((supa_score + 3)); evidence+="  - Supabase config: present\n"; }
    [[ -d "$repo_path/supabase/migrations" ]] && { supa_score=$((supa_score + 3)); evidence+="  - Supabase migrations: present\n"; }
    [[ -d "$repo_path/supabase/functions" ]] && { supa_score=$((supa_score + 2)); evidence+="  - Supabase functions: present\n"; }
    [[ $supa_score -gt 8 ]] && supa_score=8
    score=$((score + supa_score))

    # MCP (max 10)
    local mcp_score=0
    [[ -d "$repo_path/mcp" ]] && { mcp_score=$((mcp_score + 5)); evidence+="  - MCP directory: present\n"; }
    [[ -f "$repo_path/.claude/mcp-servers.json" ]] && { mcp_score=$((mcp_score + 3)); evidence+="  - MCP servers config: present\n"; }
    local mcp_content
    mcp_content=$(search_content_pattern "$repo_path" "mcp-server")
    [[ -n "$mcp_content" ]] && { mcp_score=$((mcp_score + 2)); evidence+="  - MCP references: found\n"; }
    [[ $mcp_score -gt 10 ]] && mcp_score=10
    score=$((score + mcp_score))

    # n8n (max 7)
    local n8n_score=0
    [[ -d "$repo_path/n8n" ]] && { n8n_score=$((n8n_score + 4)); evidence+="  - n8n directory: present\n"; }
    local n8n_content
    n8n_content=$(search_content_pattern "$repo_path" "n8n")
    [[ -n "$n8n_content" ]] && { n8n_score=$((n8n_score + 3)); evidence+="  - n8n references: found\n"; }
    [[ $n8n_score -gt 7 ]] && n8n_score=7
    score=$((score + n8n_score))

    # Vercel (max 5)
    local vercel_score=0
    [[ -f "$repo_path/vercel.json" ]] && { vercel_score=$((vercel_score + 3)); evidence+="  - vercel.json: present\n"; }
    local vercel_content
    vercel_content=$(search_content_pattern "$repo_path" "vercel.app")
    [[ -n "$vercel_content" ]] && { vercel_score=$((vercel_score + 2)); evidence+="  - Vercel references: found\n"; }
    [[ $vercel_score -gt 5 ]] && vercel_score=5
    score=$((score + vercel_score))

    # Ops platform (max 5)
    local ops_score=0
    [[ -d "$repo_path/apps/control-room" ]] && { ops_score=$((ops_score + 3)); evidence+="  - Control room: present\n"; }
    [[ -d "$repo_path/ops" ]] && { ops_score=$((ops_score + 2)); evidence+="  - Ops directory: present\n"; }
    [[ $ops_score -gt 5 ]] && ops_score=5
    score=$((score + ops_score))

    [[ $score -gt 35 ]] && score=35

    echo "$score"
    echo -e "$evidence" >&2
}

score_automation() {
    local repo_path="$1"
    local score=0
    local evidence=""

    # Drift gates (max 10)
    local drift_score=0
    local gen_scripts
    gen_scripts=$(find "$repo_path/scripts" -name "gen_*.sh" -o -name "generate_*.sh" 2>/dev/null | wc -l | tr -d ' ')
    [[ $gen_scripts -gt 0 ]] && { drift_score=$((drift_score + 4)); evidence+="  - Generator scripts: $gen_scripts\n"; }
    local drift_content
    drift_content=$(search_content_pattern "$repo_path" "git diff --exit-code")
    [[ -n "$drift_content" ]] && { drift_score=$((drift_score + 4)); evidence+="  - Drift gates: found\n"; }
    local skip_ci
    skip_ci=$(search_content_pattern "$repo_path" "skip ci")
    [[ -n "$skip_ci" ]] && { drift_score=$((drift_score + 2)); evidence+="  - Auto-update patterns: found\n"; }
    [[ $drift_score -gt 10 ]] && drift_score=10
    score=$((score + drift_score))

    # Branch hygiene (max 8)
    local hygiene_score=0
    local branch_wf
    branch_wf=$(find "$repo_path/.github/workflows" -name "*branch*" 2>/dev/null | wc -l | tr -d ' ')
    [[ $branch_wf -gt 0 ]] && { hygiene_score=$((hygiene_score + 4)); evidence+="  - Branch workflows: $branch_wf\n"; }
    local protection
    protection=$(search_content_pattern "$repo_path" "branch_protection")
    [[ -n "$protection" ]] && { hygiene_score=$((hygiene_score + 4)); evidence+="  - Branch protection: found\n"; }
    [[ $hygiene_score -gt 8 ]] && hygiene_score=8
    score=$((score + hygiene_score))

    # Security (max 7)
    local sec_score=0
    [[ -f "$repo_path/.gitleaks.toml" ]] && { sec_score=$((sec_score + 4)); evidence+="  - Gitleaks config: present\n"; }
    local sec_scan
    sec_scan=$(search_content_pattern "$repo_path" "secret_scanning")
    [[ -n "$sec_scan" ]] && { sec_score=$((sec_score + 3)); evidence+="  - Secret scanning: found\n"; }
    [[ $sec_score -gt 7 ]] && sec_score=7
    score=$((score + sec_score))

    [[ $score -gt 25 ]] && score=25

    echo "$score"
    echo -e "$evidence" >&2
}

score_recency() {
    local repo_path="$1"
    local score=0
    local evidence=""

    # Documentation (max 5)
    local doc_score=0
    [[ -f "$repo_path/README.md" ]] && { doc_score=$((doc_score + 2)); evidence+="  - README: present\n"; }
    [[ -f "$repo_path/CLAUDE.md" ]] && { doc_score=$((doc_score + 2)); evidence+="  - CLAUDE.md: present\n"; }
    [[ -d "$repo_path/docs" ]] && { doc_score=$((doc_score + 1)); evidence+="  - docs/: present\n"; }
    [[ $doc_score -gt 5 ]] && doc_score=5
    score=$((score + doc_score))

    # Activity (max 5) - check git log
    local recent_commits=0
    if [[ -d "$repo_path/.git" ]]; then
        recent_commits=$(cd "$repo_path" && git log --oneline --since="30 days ago" 2>/dev/null | wc -l | tr -d ' ')
    fi
    local activity_score=0
    [[ $recent_commits -gt 50 ]] && activity_score=5
    [[ $recent_commits -gt 20 ]] && [[ $recent_commits -le 50 ]] && activity_score=4
    [[ $recent_commits -gt 5 ]] && [[ $recent_commits -le 20 ]] && activity_score=3
    [[ $recent_commits -gt 0 ]] && [[ $recent_commits -le 5 ]] && activity_score=2
    evidence+="  - Recent commits (30d): $recent_commits\n"
    score=$((score + activity_score))

    [[ $score -gt 10 ]] && score=10

    echo "$score"
    echo -e "$evidence" >&2
}

scan_repo() {
    local repo_path="$1"
    local repo_name="$2"

    log "Scanning: $repo_name"

    # Create temp files for evidence
    local ci_evidence_file=$(mktemp)
    local int_evidence_file=$(mktemp)
    local auto_evidence_file=$(mktemp)
    local rec_evidence_file=$(mktemp)

    # Score each category
    local ci_score
    ci_score=$(score_ci_governance "$repo_path" 2>"$ci_evidence_file")
    local ci_evidence
    ci_evidence=$(cat "$ci_evidence_file")

    local int_score
    int_score=$(score_integration "$repo_path" 2>"$int_evidence_file")
    local int_evidence
    int_evidence=$(cat "$int_evidence_file")

    local auto_score
    auto_score=$(score_automation "$repo_path" 2>"$auto_evidence_file")
    local auto_evidence
    auto_evidence=$(cat "$auto_evidence_file")

    local rec_score
    rec_score=$(score_recency "$repo_path" 2>"$rec_evidence_file")
    local rec_evidence
    rec_evidence=$(cat "$rec_evidence_file")

    # Cleanup temp files
    rm -f "$ci_evidence_file" "$int_evidence_file" "$auto_evidence_file" "$rec_evidence_file"

    local total_score=$((ci_score + int_score + auto_score + rec_score))

    # Output JSON
    cat << EOF
{
  "repo": "$repo_name",
  "total_score": $total_score,
  "scores": {
    "ci_governance": $ci_score,
    "integration": $int_score,
    "automation": $auto_score,
    "recency": $rec_score
  },
  "evidence": {
    "ci_governance": $(echo -e "$ci_evidence" | jq -Rs .),
    "integration": $(echo -e "$int_evidence" | jq -Rs .),
    "automation": $(echo -e "$auto_evidence" | jq -Rs .),
    "recency": $(echo -e "$rec_evidence" | jq -Rs .)
  }
}
EOF
}

generate_report() {
    local scores_file="$1"
    local output_file="$2"

    cat > "$output_file" << 'EOF'
# Model Repo Scanner Report

Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

## Summary

This report ranks repositories by their suitability as a "model repository" for
integration and automation across the organization.

## Scoring Categories

| Category | Max Points | Description |
|----------|------------|-------------|
| CI & Governance | 30 | CI scripts, workflows, CODEOWNERS, Spec Kit |
| Integration | 35 | Supabase, MCP, n8n, Vercel, Ops platform |
| Automation | 25 | Drift gates, branch hygiene, security scanning |
| Recency | 10 | Documentation, recent activity |

## Rankings

EOF

    # Parse scores and generate table
    echo "| Rank | Repository | Total | CI/Gov | Integration | Automation | Recency |" >> "$output_file"
    echo "|------|------------|-------|--------|-------------|------------|---------|" >> "$output_file"

    local rank=1
    jq -r 'sort_by(-.total_score) | .[] | "\(.repo)|\(.total_score)|\(.scores.ci_governance)|\(.scores.integration)|\(.scores.automation)|\(.scores.recency)"' "$scores_file" | \
    while IFS='|' read -r repo total ci int auto rec; do
        echo "| $rank | $repo | $total | $ci | $int | $auto | $rec |" >> "$output_file"
        rank=$((rank + 1))
    done

    # Add recommendation
    local top_repo
    top_repo=$(jq -r 'sort_by(-.total_score) | .[0].repo' "$scores_file")
    local top_score
    top_score=$(jq -r 'sort_by(-.total_score) | .[0].total_score' "$scores_file")

    cat >> "$output_file" << EOF

## Recommendation

**Model Repository:** \`$top_repo\` (Score: $top_score/100)

### Evidence Summary

EOF

    # Add top repo evidence
    jq -r --arg repo "$top_repo" '.[] | select(.repo == $repo) | .evidence | to_entries[] | "#### \(.key | gsub("_"; " ") | ascii_upcase)\n\(.value)"' "$scores_file" >> "$output_file"

    cat >> "$output_file" << 'EOF'

---

*Generated by Model Repo Scanner*
EOF

    # Fix the date in the report
    sed -i "s/\$(date -u +\"%Y-%m-%dT%H:%M:%SZ\")/$(date -u +"%Y-%m-%dT%H:%M:%SZ")/" "$output_file" 2>/dev/null || \
    sed -i '' "s/\$(date -u +\"%Y-%m-%dT%H:%M:%SZ\")/$(date -u +"%Y-%m-%dT%H:%M:%SZ")/" "$output_file"
}

# =============================================================================
# Main
# =============================================================================
main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -o|--org)
                GITHUB_ORG="$2"
                shift 2
                ;;
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Check dependencies
    check_dependencies

    # Load org from config if not set
    if [[ -z "$GITHUB_ORG" ]] && [[ -f "$CONFIG_FILE" ]]; then
        GITHUB_ORG=$(parse_yaml_value "$CONFIG_FILE" "organization")
    fi

    if [[ -z "$GITHUB_ORG" ]]; then
        error "GitHub organization not specified"
        echo "Set GITHUB_ORG env var or use -o/--org flag"
        exit 1
    fi

    log "Starting Model Repo Scanner"
    log "Organization: $GITHUB_ORG"

    # Setup directories
    mkdir -p "$CACHE_DIR" "$ARTIFACTS_DIR"

    # Get repos
    local repos
    repos=$(get_org_repos "$GITHUB_ORG")

    if [[ -z "$repos" ]]; then
        error "No repositories found for org: $GITHUB_ORG"
        exit 1
    fi

    local repo_count
    repo_count=$(echo "$repos" | wc -l | tr -d ' ')
    log "Found $repo_count repositories"

    # Initialize scores array
    echo "[" > "${ARTIFACTS_DIR}/model-repo-scores.json.tmp"
    local first=true

    # Scan each repo
    while IFS= read -r repo; do
        [[ -z "$repo" ]] && continue

        # Skip excluded repos
        if grep -qE "^exclude_repos:" "$CONFIG_FILE" 2>/dev/null; then
            if grep -q "\"$repo\"" "$CONFIG_FILE" 2>/dev/null || grep -q "- $repo" "$CONFIG_FILE" 2>/dev/null; then
                debug "Skipping excluded repo: $repo"
                continue
            fi
        fi

        # Clone/update repo
        local repo_path
        repo_path=$(clone_repo "$GITHUB_ORG" "$repo") || continue

        # Scan and score
        local result
        result=$(scan_repo "$repo_path" "$repo")

        # Append to JSON array
        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo "," >> "${ARTIFACTS_DIR}/model-repo-scores.json.tmp"
        fi
        echo "$result" >> "${ARTIFACTS_DIR}/model-repo-scores.json.tmp"

    done <<< "$repos"

    echo "]" >> "${ARTIFACTS_DIR}/model-repo-scores.json.tmp"

    # Validate and format JSON
    if jq '.' "${ARTIFACTS_DIR}/model-repo-scores.json.tmp" > "${ARTIFACTS_DIR}/model-repo-scores.json" 2>/dev/null; then
        rm -f "${ARTIFACTS_DIR}/model-repo-scores.json.tmp"
    else
        error "Failed to generate valid JSON"
        mv "${ARTIFACTS_DIR}/model-repo-scores.json.tmp" "${ARTIFACTS_DIR}/model-repo-scores.json"
    fi

    # Generate report
    log "Generating report..."
    generate_report "${ARTIFACTS_DIR}/model-repo-scores.json" "${ARTIFACTS_DIR}/model-repo-report.md"

    # Summary
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  Scan Complete${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Show top 5
    echo "Top 5 Model Repos:"
    jq -r 'sort_by(-.total_score) | .[0:5] | .[] | "  \(.total_score)/100  \(.repo)"' "${ARTIFACTS_DIR}/model-repo-scores.json"

    echo ""
    echo "Output:"
    echo "  - ${ARTIFACTS_DIR}/model-repo-scores.json"
    echo "  - ${ARTIFACTS_DIR}/model-repo-report.md"
}

main "$@"
