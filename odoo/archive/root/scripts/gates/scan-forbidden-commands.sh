#!/usr/bin/env bash
#
# NO_CLI_NO_DOCKER Gate Enforcement
#
# Scans codebase for forbidden direct CLI/Docker commands
# Portfolio Initiative: PORT-2026-011
# Evidence: EVID-20260212-006
# Policy Reference: docs/constitution/NO_CLI_NO_DOCKER.md
#
# Usage:
#   bash scripts/gates/scan-forbidden-commands.sh
#   Exit code: 0 if no violations, 1 if violations found
#
# Forbidden patterns:
#   - docker run, docker exec, docker build, docker push
#   - kubectl (except in sanctioned automation)
#   - ssh (except localhost/loopback)
#   - psql -h (except localhost)
#
# Allowlist:
#   - scripts/docker/ (sanctioned automation)
#   - docker-compose.yml, Dockerfile (declarative config)
#   - docs/, *.md (documentation)
#

set -euo pipefail

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EVIDENCE_DIR="${REPO_ROOT}/docs/evidence/20260212-2000/no-cli-docker-gate"
SARIF_OUTPUT="${EVIDENCE_DIR}/scan-results.sarif"
VIOLATIONS_FOUND=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ensure evidence directory exists
mkdir -p "$EVIDENCE_DIR"

echo "=================================================="
echo "NO_CLI_NO_DOCKER Gate Enforcement"
echo "=================================================="
echo "Policy: docs/constitution/NO_CLI_NO_DOCKER.md"
echo "Portfolio Initiative: PORT-2026-011"
echo "Scanning: $REPO_ROOT"
echo ""

# Forbidden patterns (grep-compatible regex)
FORBIDDEN_PATTERNS=(
    'docker\s+(run|exec|build|push|pull|start|stop|restart)'
    'kubectl\s+'
    'ssh\s+[^@]*@(?!localhost|127\.0\.0\.1)'
    'psql\s+-h\s+(?!localhost|127\.0\.0\.1)'
)

# Allowlist paths (exclude from scan)
ALLOWLIST=(
    'scripts/docker/'
    'docs/'
    '*.md'
    '*.yml'
    '*.yaml'
    'Dockerfile'
    'docker-compose.yml'
    '.github/workflows/'
)

# Build grep exclude flags
EXCLUDE_FLAGS=""
for pattern in "${ALLOWLIST[@]}"; do
    EXCLUDE_FLAGS="$EXCLUDE_FLAGS --exclude=$pattern"
done

# Initialize SARIF output
cat > "$SARIF_OUTPUT" <<'EOF'
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "NO_CLI_NO_DOCKER Gate",
          "version": "1.0.0",
          "informationUri": "https://github.com/Insightpulseai/odoo/blob/main/docs/constitution/NO_CLI_NO_DOCKER.md",
          "rules": [
            {
              "id": "NO_CLI_DOCKER_001",
              "name": "ForbiddenDirectDockerCommand",
              "shortDescription": {
                "text": "Direct Docker CLI command detected"
              },
              "fullDescription": {
                "text": "Direct Docker CLI commands (docker run, exec, build, push) are forbidden. Use sanctioned automation in scripts/docker/ or declarative docker-compose.yml instead."
              },
              "help": {
                "text": "See docs/constitution/NO_CLI_NO_DOCKER.md for policy rationale and approved patterns."
              },
              "defaultConfiguration": {
                "level": "error"
              }
            },
            {
              "id": "NO_CLI_DOCKER_002",
              "name": "ForbiddenKubectlCommand",
              "shortDescription": {
                "text": "kubectl command detected"
              },
              "fullDescription": {
                "text": "Direct kubectl commands are forbidden. Use GitOps (ArgoCD/Flux) or sanctioned automation scripts instead."
              },
              "defaultConfiguration": {
                "level": "error"
              }
            },
            {
              "id": "NO_CLI_DOCKER_003",
              "name": "ForbiddenSSHCommand",
              "shortDescription": {
                "text": "ssh command detected"
              },
              "fullDescription": {
                "text": "Direct ssh commands are forbidden. Use Ansible playbooks or sanctioned automation scripts instead."
              },
              "defaultConfiguration": {
                "level": "error"
              }
            },
            {
              "id": "NO_CLI_DOCKER_004",
              "name": "ForbiddenPsqlRemoteCommand",
              "shortDescription": {
                "text": "Remote psql command detected"
              },
              "fullDescription": {
                "text": "Direct remote psql commands are forbidden. Use migrations, Supabase client, or sanctioned automation scripts instead."
              },
              "defaultConfiguration": {
                "level": "error"
              }
            }
          ]
        }
      },
      "results": [
EOF

# Scan for violations
echo "Scanning for forbidden patterns..."
echo ""

TEMP_RESULTS=$(mktemp)

for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
    echo "Pattern: $pattern"

    # Determine rule ID based on pattern
    RULE_ID=""
    case "$pattern" in
        *docker*)
            RULE_ID="NO_CLI_DOCKER_001"
            PATTERN_NAME="docker CLI"
            ;;
        *kubectl*)
            RULE_ID="NO_CLI_DOCKER_002"
            PATTERN_NAME="kubectl"
            ;;
        *ssh*)
            RULE_ID="NO_CLI_DOCKER_003"
            PATTERN_NAME="ssh"
            ;;
        *psql*)
            RULE_ID="NO_CLI_DOCKER_004"
            PATTERN_NAME="psql remote"
            ;;
    esac

    # Scan with grep (excluding allowlist)
    # Use -P for Perl regex, -n for line numbers, -H for filenames
    set +e
    grep -rPn $EXCLUDE_FLAGS "$pattern" "$REPO_ROOT" 2>/dev/null | while IFS=: read -r file line content; do
        # Skip if file is in allowlist
        SKIP=0
        for allowed in "${ALLOWLIST[@]}"; do
            if [[ "$file" == *"$allowed"* ]]; then
                SKIP=1
                break
            fi
        done

        if [ $SKIP -eq 0 ]; then
            echo -e "${RED}[VIOLATION]${NC} $file:$line"
            echo "  Content: $content"
            echo ""

            VIOLATIONS_FOUND=$((VIOLATIONS_FOUND + 1))

            # Append to SARIF results
            cat >> "$SARIF_OUTPUT" <<EOF
        {
          "ruleId": "$RULE_ID",
          "level": "error",
          "message": {
            "text": "Forbidden $PATTERN_NAME command detected: $content"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "${file#$REPO_ROOT/}"
                },
                "region": {
                  "startLine": $line
                }
              }
            }
          ]
        },
EOF
        fi
    done
    set -e
done < "$TEMP_RESULTS"

# Finalize SARIF output (remove trailing comma, close array)
sed -i '$ s/,$//' "$SARIF_OUTPUT"
cat >> "$SARIF_OUTPUT" <<'EOF'
      ]
    }
  ]
}
EOF

# Clean up
rm -f "$TEMP_RESULTS"

# Report results
echo "=================================================="
if [ $VIOLATIONS_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ NO VIOLATIONS FOUND${NC}"
    echo "All scanned files comply with NO_CLI_NO_DOCKER policy."
    echo ""
    echo "SARIF output: $SARIF_OUTPUT"
    exit 0
else
    echo -e "${RED}❌ $VIOLATIONS_FOUND VIOLATIONS FOUND${NC}"
    echo ""
    echo "Policy violations detected. See output above for details."
    echo "SARIF output: $SARIF_OUTPUT"
    echo ""
    echo "Remediation:"
    echo "  1. Move direct CLI/Docker commands to sanctioned automation (scripts/docker/)"
    echo "  2. Use declarative config (docker-compose.yml) instead of CLI commands"
    echo "  3. See docs/constitution/NO_CLI_NO_DOCKER.md for approved patterns"
    echo ""
    exit 1
fi
