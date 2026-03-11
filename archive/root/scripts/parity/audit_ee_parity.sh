#!/usr/bin/env bash
# audit_ee_parity.sh - Compute EE parity status from tasks.md and run enforcement scripts
# Usage: ./scripts/parity/audit_ee_parity.sh
# Environment: REPO_SLUG (default: jgtolentino/odoo-ce), TASKS_MD, OUT_DIR
set -euo pipefail

REPO_SLUG="${REPO_SLUG:-jgtolentino/odoo-ce}"
TASKS_MD="${TASKS_MD:-spec/enterprise-parity/tasks.md}"
OUT_DIR="${OUT_DIR:-reports/parity}"
OUT_JSON="$OUT_DIR/ee_parity_audit.json"
OUT_MD="$OUT_DIR/ee_parity_audit.md"

mkdir -p "$OUT_DIR"

if [[ ! -f "$TASKS_MD" ]]; then
  echo "ERROR: tasks file not found: $TASKS_MD" >&2
  exit 2
fi

echo "==> Running EE Parity Audit"
echo "    Repo: $REPO_SLUG"
echo "    Tasks file: $TASKS_MD"

# Count tasks - supports both markdown checkboxes and emoji format
# Markdown: "- [x]" / "- [ ]"
# Emoji: "- ✅" / "- ⬜" / "- 🟡"
count_matches() {
  local pattern="$1"
  local file="$2"
  local count
  count=$(grep -cE "$pattern" "$file" 2>/dev/null) || count=0
  echo "$count"
}

md_total=$(count_matches '^\s*-\s*\[[ xX]\]' "$TASKS_MD")
md_done=$(count_matches '^\s*-\s*\[[xX]\]' "$TASKS_MD")
emoji_done=$(count_matches '^\s*-\s*✅' "$TASKS_MD")
emoji_pending=$(count_matches '^\s*-\s*(⬜|🟡)' "$TASKS_MD")

# Combine counts
total=$((md_total + emoji_done + emoji_pending))
done=$((md_done + emoji_done))
todo=$((total - done))

# Calculate percentage
pct="0"
if [[ "$total" -gt 0 ]]; then
  pct="$(python3 -c "t=int('$total'); d=int('$done'); print(round((d/t)*100, 2))")"
fi

echo "    Progress: $done/$total ($pct%)"

# Collect completed task lines (for evidence)
done_lines="$(grep -nE '^\s*-\s*(\[[xX]\]|✅)' "$TASKS_MD" 2>/dev/null | sed 's/\t/  /g' | head -n 200 || true)"
todo_lines="$(grep -nE '^\s*-\s*(\[\s\]|⬜|🟡)' "$TASKS_MD" 2>/dev/null | sed 's/\t/  /g' | head -n 200 || true)"

# Run runnable-slice enforcement scripts if present
require_slice_status="missing"
check_foundation_status="missing"
require_slice_log=""
check_foundation_log=""

if [[ -x scripts/parity/require_runnable_slice.sh ]]; then
  echo "    Running require_runnable_slice.sh..."
  require_slice_status="pass"
  if ! require_slice_log="$(scripts/parity/require_runnable_slice.sh 2>&1)"; then
    require_slice_status="fail"
  fi
fi

if [[ -x scripts/parity/check_ipai_foundation.sh ]]; then
  echo "    Running check_ipai_foundation.sh..."
  check_foundation_status="pass"
  if ! check_foundation_log="$(scripts/parity/check_ipai_foundation.sh 2>&1)"; then
    check_foundation_status="fail"
  fi
fi

# Inventory checks
ipai_manifest_count="$(find addons/ipai -name '__manifest__.py' 2>/dev/null | wc -l | tr -d ' ' || echo "0")"
has_gate_workflow="no"
if [[ -f .github/workflows/ee-parity-gate.yml ]]; then has_gate_workflow="yes"; fi

echo "    ipai manifests: $ipai_manifest_count"
echo "    EE parity gate workflow: $has_gate_workflow"

# Heuristic blockers (fast, deterministic)
blockers_json="[]"
add_blocker () {
  local code="$1"; shift
  local title="$1"; shift
  local detail="$1"; shift
  blockers_json="$(python3 -c "
import json
arr=json.loads('''$blockers_json''')
arr.append({'code':'$code','title':'$title','detail':'''$detail'''})
print(json.dumps(arr))
")"
}

if [[ "$require_slice_status" == "fail" ]]; then
  add_blocker "GATE-RUNNABLE-SLICE" \
    "Runnable slice gate failing" \
    "scripts/parity/require_runnable_slice.sh failed. Output: ${require_slice_log:0:800}"
fi

if [[ "$check_foundation_status" == "fail" ]]; then
  add_blocker "MOD-IPAI-FOUNDATION" \
    "ipai_foundation structural validation failing" \
    "scripts/parity/check_ipai_foundation.sh failed. Output: ${check_foundation_log:0:800}"
fi

if [[ "$ipai_manifest_count" -lt 1 ]]; then
  add_blocker "NO-IPAI-ADDONS" \
    "No installable ipai_* addon detected" \
    "Expected at least one addons/ipai/**/__manifest__.py but found none."
fi

if [[ "$has_gate_workflow" != "yes" ]]; then
  add_blocker "NO-EE-PARITY-GATE" \
    "Missing ee-parity-gate workflow" \
    ".github/workflows/ee-parity-gate.yml not found; required for parity enforcement."
fi

# Emit JSON report
python3 - <<PY
import json, os, subprocess, pathlib

def sh(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()

out = {
  "repo": "$REPO_SLUG",
  "commit": sh("git rev-parse HEAD"),
  "branch": sh("git rev-parse --abbrev-ref HEAD"),
  "tasks": {
    "file": "$TASKS_MD",
    "total": int("$total"),
    "done": int("$done"),
    "todo": int("$todo"),
    "percent_done": float("$pct"),
  },
  "runnable_gates": {
    "require_runnable_slice": "$require_slice_status",
    "check_ipai_foundation": "$check_foundation_status",
  },
  "inventory": {
    "ipai_manifest_count": int("$ipai_manifest_count"),
    "has_ee_parity_gate_workflow": "$has_gate_workflow" == "yes",
  },
  "blockers": json.loads('''$blockers_json'''),
}
path = pathlib.Path("$OUT_JSON")
path.write_text(json.dumps(out, indent=2))
print("Wrote", path)
PY

# Emit Markdown summary
cat > "$OUT_MD" <<MD
# EE Parity Audit

- Repo: \`$REPO_SLUG\`
- Commit: \`$(git rev-parse HEAD)\`
- Branch: \`$(git rev-parse --abbrev-ref HEAD)\`
- Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

## Task Progress
- Total tasks: **$total**
- Done: **$done**
- Remaining: **$todo**
- Completion: **$pct%**

## Runnable Gates
| Gate | Status |
|------|--------|
| require_runnable_slice.sh | **$require_slice_status** |
| check_ipai_foundation.sh | **$check_foundation_status** |

## Inventory
| Item | Value |
|------|-------|
| ipai manifests found | **$ipai_manifest_count** |
| ee-parity-gate workflow | **$has_gate_workflow** |

## Blockers
$(python3 -c "
import json
b=json.loads('''$blockers_json''')
if not b:
  print('- None detected by heuristic rules.')
else:
  for i,x in enumerate(b,1):
    print(f\"{i}. **{x['title']}** (\\\`{x['code']}\\\`)\")
    print(f\"   - {x['detail'][:200]}...\")
")

## Verification Commands
\`\`\`bash
./scripts/parity/audit_ee_parity.sh
cat reports/parity/ee_parity_audit.md
\`\`\`

---

## Sample Completed Tasks (first 200)
\`\`\`
$done_lines
\`\`\`

## Sample Remaining Tasks (first 200)
\`\`\`
$todo_lines
\`\`\`
MD

echo ""
echo "OK: Audit complete"
echo "    JSON: $OUT_JSON"
echo "    Markdown: $OUT_MD"
