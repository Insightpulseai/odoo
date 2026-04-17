#!/usr/bin/env bash
# ci-validate.sh — all plugin validation + enterprise security review
# Called by GitHub Actions and Azure Pipelines.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

echo "=== IPAI plugin validation ==="
echo "Python: $(python3 --version)"
echo ""

pip install pyyaml jsonschema --break-system-packages --quiet

FAILED=0

run_check() {
  local name="$1"; local script="$2"
  echo "--- ${name}"
  if python3 "${script}"; then echo "    PASS"
  else echo "    FAIL"; FAILED=1; fi
  echo ""
}

run_check "marketplace.json"      scripts/validate_marketplace.py
run_check "plugin.json manifests" scripts/validate_plugins.py
run_check "SKILL.md frontmatter"  scripts/validate_skills.py
run_check "agent + hooks"         scripts/validate_agents.py

# ── Structural checks ──────────────────────────────────────────────────

echo "--- kebab-case naming"
python3 - <<'EOF'
import os, re, sys
errors = []
for root, dirs, files in os.walk("plugins"):
    dirs[:] = [d for d in dirs if d not in [".git","__pycache__","node_modules"]]
    for d in dirs:
        if not re.match(r'^[a-z0-9\-\.]+$', d):
            errors.append(f"Non-kebab-case directory: {os.path.join(root,d)}")
if errors:
    for e in errors: print(f"ERROR: {e}")
    sys.exit(1)
print("All directory names are kebab-case.")
EOF
[ $? -ne 0 ] && FAILED=1 && echo "    FAIL" || echo "    PASS"
echo ""

# ── Enterprise security review (Anthropic risk tier assessment) ────────

echo "--- [SEC] hardcoded credentials"
python3 - <<'EOF'
import os, re, sys
SKIP = ['.mcp.json']
# Credential patterns: quoted key = quoted non-template value
CRED_PATTERNS = [
    r"""['"](secret|password|api[_\-]?key|token|credential|private[_\-]?key)['"]\s*[:=]\s*['"][^'"$\{\s]{12,}['"]""",
    r'[A-Za-z0-9+/]{30,}[+][A-Za-z0-9+/]{5,}={0,2}',  # base64 with + char
    r'[A-Za-z0-9+/]{30,}={1,2}(?![A-Za-z0-9+/=])',      # padded base64
]
errors = []
for root, dirs, files in os.walk("plugins"):
    dirs[:] = [d for d in dirs if d not in [".git","__pycache__"]]
    for f in files:
        if any(f.endswith(s) for s in SKIP): continue
        path = os.path.join(root, f)
        try:
            content = open(path, errors='replace').read()
            for pat in CRED_PATTERNS:
                for m in re.finditer(pat, content, re.I):
                    errors.append(f"{path}: possible hardcoded credential: {m.group()[:40]}...")
        except Exception: pass
if errors:
    for e in errors: print(f"ERROR: {e}")
    sys.exit(1)
print("No hardcoded credentials detected.")
EOF
[ $? -ne 0 ] && FAILED=1 && echo "    FAIL" || echo "    PASS"
echo ""

echo "--- [SEC] network access patterns"
python3 - <<'EOF'
import os, re, sys
# Flag network access in skill instructions and bundled scripts
# .mcp.json legitimately contains URLs — skip it
SKIP_FILES = ['.mcp.json', 'MAPPING.md']
NET_PATTERNS = [
    r'(requests\.get|requests\.post|urllib\.request|fetch\(|curl\s|wget\s)',
    r'http[s]?://(?!.*example\.com|.*anthropic\.com|.*github\.com|.*microsoft\.com|.*azure\.com|.*pubmed\.ncbi\.nlm\.nih\.gov)',
]
warnings = []
for root, dirs, files in os.walk("plugins"):
    dirs[:] = [d for d in dirs if d not in [".git","__pycache__"]]
    for f in files:
        if f in SKIP_FILES: continue
        path = os.path.join(root, f)
        if not (f.endswith('.md') or f.endswith('.py') or f.endswith('.sh') or f.endswith('.js')): continue
        try:
            content = open(path, errors='replace').read()
            for pat in NET_PATTERNS:
                for m in re.finditer(pat, content, re.I):
                    warnings.append(f"REVIEW {path}: network access pattern: {m.group()[:60]}")
        except Exception: pass
if warnings:
    print("WARNING: Network access detected — manual review required:")
    for w in warnings: print(f"  {w}")
    # Warn but don't fail: network access is allowed (e.g. PubMed API) but must be reviewed
    sys.exit(0)
print("No unexpected network access patterns.")
EOF
[ $? -ne 0 ] && FAILED=1 && echo "    FAIL" || echo "    PASS"
echo ""

echo "--- [SEC] path traversal"
python3 - <<'EOF'
import os, re, sys
TRAVERSAL = [r'\.\./\.\./\.\.', r'\.\./etc/', r'\.\./proc/', r'~\/\.ssh', r'~\/\.aws']
errors = []
for root, dirs, files in os.walk("plugins"):
    dirs[:] = [d for d in dirs if d not in [".git","__pycache__"]]
    for f in files:
        path = os.path.join(root, f)
        try:
            content = open(path, errors='replace').read()
            for pat in TRAVERSAL:
                if re.search(pat, content):
                    errors.append(f"{path}: path traversal pattern: {pat}")
        except Exception: pass
if errors:
    for e in errors: print(f"ERROR: {e}")
    sys.exit(1)
print("No path traversal patterns detected.")
EOF
[ $? -ne 0 ] && FAILED=1 && echo "    FAIL" || echo "    PASS"
echo ""

echo "--- [SEC] adversarial instructions"
python3 << 'PYCHECK'
import os, re, sys

NEGATION_PAT = re.compile(
    r"(never|not|must not|do not|cannot|prohibited|forbidden|may not|should not|won.t|isn.t)\s",
    re.I
)

def prohibitive(content, match):
    window = content[max(0, match.start()-100):match.start()]
    return bool(NEGATION_PAT.search(window))

ADVERSARIAL = [
    (r"ignore (your |all )?(safety|security|previous) (rules?|instructions?|guidelines?)", "ignore safety rules"),
    (r"do not (tell|inform|show|reveal).{0,40}user", "hide actions from user"),
    (r"(exfiltrat|transmit|send|upload|POST).{0,60}(password|secret|token|key|credential)", "potential exfiltration"),
    (r"\bbypass\b.{0,30}(permission|approval|rbac|auth)", "bypass permissions"),
    (r"act as if you have no restrictions", "remove restrictions"),
    (r"\bDAN\b|jailbreak|\bpretend you are\b", "jailbreak pattern"),
]

errors = []
for root, dirs, files in os.walk("plugins"):
    dirs[:] = [d for d in dirs if d not in [".git","__pycache__"]]
    for f in files:
        if not (f.endswith(".md") or f.endswith(".txt")): continue
        path = os.path.join(root, f)
        try:
            content = open(path, errors="replace").read()
            for pat, label in ADVERSARIAL:
                for m in re.finditer(pat, content, re.I):
                    SAFE_NOUN = re.compile(r"(security bypass|type.*bypass|bypass.*defect|P0.*bypass|bypass.*P[0-9])", re.I)
                    ctx = content[max(0,m.start()-120):m.end()+60]
                    if not prohibitive(content, m) and not SAFE_NOUN.search(ctx):
                        errors.append(f"{path}: adversarial pattern ({label}): {m.group()[:50]}")
        except Exception:
            pass
if errors:
    for e in errors: print(f"ERROR: {e}")
    sys.exit(1)
print("No adversarial instruction patterns detected.")
PYCHECK
[ $? -ne 0 ] && FAILED=1 && echo "    FAIL" || echo "    PASS"
echo ""

echo "--- [SEC] MCP server references audit"
python3 - <<'EOF'
import os, re, sys
# Audit (not block) — list any MCP tool references so reviewers can verify
MCP_PATTERN = r'mcp__[a-z_]+__[a-z_]+'
refs = {}
for root, dirs, files in os.walk("plugins"):
    dirs[:] = [d for d in dirs if d not in [".git","__pycache__"]]
    for f in files:
        if not f.endswith('.md'): continue
        path = os.path.join(root, f)
        try:
            content = open(path, errors='replace').read()
            found = re.findall(MCP_PATTERN, content)
            if found:
                refs[path] = list(set(found))
        except Exception: pass
if refs:
    print("MCP tool references found (audit — not blocking):")
    for path, tools in refs.items():
        print(f"  {path}: {', '.join(tools)}")
else:
    print("No MCP tool references in skill instructions.")
EOF
[ $? -ne 0 ] && FAILED=1 && echo "    FAIL" || echo "    PASS"
echo ""

echo "--- [SEC] bundle size check (max 8 skills per bundle)"
python3 - <<'EOF'
import json, sys, os
registry_path = "skills-registry.json"
bundles_path = "skill-bundles.json"
if not os.path.exists(bundles_path):
    print("skill-bundles.json not found — skipping bundle check")
    sys.exit(0)
with open(bundles_path) as f:
    bundles = json.load(f)
errors = []
for name, bundle in bundles.get("bundles", {}).items():
    count = len(bundle.get("skills", []))
    if count > 8:
        errors.append(f"Bundle '{name}' has {count} skills — max is 8 per API request")
if errors:
    for e in errors: print(f"ERROR: {e}")
    sys.exit(1)
print("All bundles are within the 8-skill API limit.")
EOF
[ $? -ne 0 ] && FAILED=1 && echo "    FAIL" || echo "    PASS"
echo ""

echo "=== Summary ==="
if [ "${FAILED}" -eq 0 ]; then
  echo "All checks passed."
  exit 0
else
  echo "One or more checks failed."
  exit 1
fi
