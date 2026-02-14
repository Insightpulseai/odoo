"""
Domain Policy Enforcement Check

HARD POLICY: No insightpulseai.net references allowed anywhere in the codebase.

This check scans the entire repository for any occurrence of the deprecated
.net domain and fails the audit if any are found. This prevents accidental
deployment of configuration pointing to the wrong domain.

Canonical domain: insightpulseai.com
Mailgun subdomain: mg.insightpulseai.com
"""

import os
import re
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.audit.lib import ok, fail, run_cmd


# Forbidden patterns - these should NEVER appear in the codebase
FORBIDDEN_PATTERNS = [
    r"insightpulseai\.net",
]

# Excluded paths (already handled by ripgrep defaults, but explicit here)
EXCLUDED_PATHS = [
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    "__pycache__",
    ".tox",
    "*.pyc",
]


def is_policy_meta_reference(line: str) -> bool:
    """
    Check if a line is a meta-reference (documentation about the policy,
    not an actual forbidden usage).

    Lines like "no insightpulseai.net references" or "Checking for insightpulseai.net"
    are descriptions of what we're looking for, not actual usages.
    """
    meta_patterns = [
        r"no\s+insightpulseai\.net",           # "no insightpulseai.net references"
        r"forbidden.*insightpulseai\.net",      # "forbidden domain 'insightpulseai.net'"
        r"checking.*insightpulseai\.net",       # "Checking for insightpulseai.net"
        r"insightpulseai\.net.*forbidden",      # "insightpulseai.net is forbidden"
        r"block.*insightpulseai\.net",          # "block .net references"
        r"ensure.*insightpulseai\.net",         # "Ensures no insightpulseai.net"
        r"insightpulseai\\\.net",               # Escaped regex pattern
        r"FAIL.*insightpulseai\.net",           # Test expectations
        r"pattern.*insightpulseai\.net",        # Pattern definitions
        r"policy.*insightpulseai\.net",         # Policy descriptions
    ]
    line_lower = line.lower()
    for mp in meta_patterns:
        if re.search(mp, line_lower, re.IGNORECASE):
            return True
    return False


def run():
    """
    Scan repository for forbidden domain references.

    Returns FAIL if any actual insightpulseai.net usage is found.
    Meta-references (policy documentation) are excluded.
    This is a hard policy check that blocks CI.
    """
    results = []

    for pattern in FORBIDDEN_PATTERNS:
        # Use ripgrep for fast searching
        # --hidden: search hidden files
        # --no-ignore-vcs: don't respect .gitignore (we want to catch everything)
        # -n: show line numbers
        # -l: only show filenames (for counting)
        cmd = [
            "rg",
            "-n",
            "--hidden",
            "--no-ignore-vcs",
            "--glob", "!.git/**",
            "--glob", "!node_modules/**",
            "--glob", "!.venv/**",
            "--glob", "!venv/**",
            "--glob", "!dist/**",
            "--glob", "!build/**",
            "--glob", "!.next/**",
            "--glob", "!__pycache__/**",
            "--glob", "!*.pyc",
            "--glob", "!*.pyo",
            "--glob", "!*.so",
            "--glob", "!*.dylib",
            pattern,
            "."
        ]

        result = run_cmd(cmd, timeout=60)

        # ripgrep returns exit code 1 if no matches (which is what we want)
        if result["returncode"] == 0 and result["stdout"]:
            # Filter out meta-references (policy documentation)
            raw_matches = result["stdout"].strip().split("\n")
            real_violations = []

            for match in raw_matches:
                if not is_policy_meta_reference(match):
                    real_violations.append(match)

            if real_violations:
                # Limit to first 50 matches to avoid huge output
                violations = real_violations[:50]

                return fail("forbidden_domain_found", {
                    "pattern": pattern,
                    "match_count": len(violations),
                    "matches": violations,
                    "message": (
                        f"Found {len(violations)} actual usage(s) of forbidden domain pattern "
                        f"'{pattern}'. All references must use 'insightpulseai.com'."
                    ),
                    "fix": (
                        "Run: find . -type f -not -path '*/.git/*' -print0 | "
                        "xargs -0 perl -pi -e 's/insightpulseai\\.net/insightpulseai.com/g'"
                    )
                })

        # Check if ripgrep itself failed (not just "no matches")
        if result["returncode"] not in [0, 1]:
            # Error running ripgrep
            results.append({
                "pattern": pattern,
                "status": "error",
                "error": result.get("stderr", "Unknown error")
            })
        else:
            # No matches found - good!
            results.append({
                "pattern": pattern,
                "status": "clean"
            })

    # Check if we had any errors
    errors = [r for r in results if r.get("status") == "error"]
    if errors:
        # Ripgrep errors - warn but don't fail
        return fail("domain_check_error", {
            "errors": errors,
            "message": "Could not complete domain policy scan"
        })

    # All patterns clean
    return ok("domain_policy_ok", {
        "policy": "no insightpulseai.net references",
        "canonical_domain": "insightpulseai.com",
        "mailgun_domain": "mg.insightpulseai.com",
        "patterns_checked": FORBIDDEN_PATTERNS
    })


if __name__ == "__main__":
    import json
    result = run()
    print(json.dumps(result, indent=2))
