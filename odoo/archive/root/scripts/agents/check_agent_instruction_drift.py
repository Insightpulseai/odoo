#!/usr/bin/env python3
"""
Check for drift in agent instruction mirrors.

Regenerates CLAUDE.md, AGENTS.md, GEMINI.md to a temp directory and compares
with repo versions. Fails if any drift detected (manual edits to generated files).

Usage:
    python scripts/agents/check_agent_instruction_drift.py

Exit codes:
    0: No drift detected
    1: Drift detected (files differ from SSOT)
    2: Error during execution
"""

import sys
import tempfile
import difflib
from pathlib import Path
from typing import List, Tuple

# Import generator logic
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

# We'll import the generator functions directly
import sync_agent_instructions as gen

def compare_files(repo_file: Path, temp_file: Path) -> Tuple[bool, List[str]]:
    """
    Compare two files and return (is_identical, diff_lines).

    Returns:
        (True, []) if identical
        (False, diff_lines) if different
    """
    if not repo_file.exists():
        return False, [f"MISSING: {repo_file.name} does not exist in repo"]

    try:
        repo_content = repo_file.read_text(encoding="utf-8").splitlines(keepends=True)
        temp_content = temp_file.read_text(encoding="utf-8").splitlines(keepends=True)

        if repo_content == temp_content:
            return True, []

        # Generate unified diff
        diff = difflib.unified_diff(
            repo_content,
            temp_content,
            fromfile=f"repo/{repo_file.name}",
            tofile=f"expected/{repo_file.name}",
            lineterm="",
        )
        diff_lines = list(diff)
        return False, diff_lines

    except Exception as e:
        return False, [f"ERROR comparing {repo_file.name}: {e}"]


def main() -> None:
    """Main drift check."""
    print("Checking for agent instruction drift...")
    print(f"SSOT: {gen.SSOT_PATH.relative_to(gen.REPO_ROOT)}\n")

    # Read SSOT
    ssot_content = gen.read_ssot()
    body = gen.extract_body(ssot_content)

    # Create temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        drift_detected = False

        for filename in gen.OUTPUTS.keys():
            repo_path = gen.OUTPUTS[filename]
            temp_path = temp_dir / filename

            # Generate to temp
            header = gen.HEADERS[filename]
            temp_path.write_text(header + body, encoding="utf-8")

            # Compare
            is_identical, diff_lines = compare_files(repo_path, temp_path)

            if is_identical:
                print(f"✓ {filename}: No drift")
            else:
                print(f"✗ {filename}: DRIFT DETECTED")
                drift_detected = True

                # Show unified diff (capped at 200 lines for CI readability)
                if diff_lines:
                    print(f"\n  Unified diff (repo → expected):\n")
                    for i, line in enumerate(diff_lines):
                        if i >= 200:
                            remaining = len(diff_lines) - 200
                            print(f"\n  ... (diff truncated, {remaining} more lines)")
                            break
                        print(f"  {line.rstrip()}")
                print()

    if drift_detected:
        print("\n❌ DRIFT DETECTED: One or more generated files differ from SSOT.")
        print("\nTo fix:")
        print("  1. If SSOT is correct: python scripts/agents/sync_agent_instructions.py")
        print("  2. If generated file has manual improvements: port them to SSOT, then sync")
        print("  3. Never edit CLAUDE.md, AGENTS.md, or GEMINI.md directly\n")
        sys.exit(1)
    else:
        print("\n✅ No drift detected. All mirrors match SSOT.")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(2)
