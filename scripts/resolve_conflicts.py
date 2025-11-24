"""AI-assisted merge conflict helper for Odoo repositories.

This script automates the boring parts of merge conflict resolution while
keeping humans in control of risky decisions. It can:

* Detect files containing Git conflict markers.
* Auto-resolve common `__manifest__.py` conflicts by picking the higher
  version string and merging dependency lists.
* Generate an AI-ready prompt with Odoo-specific rules, or optionally call a
  supported provider to attempt an automatic rewrite.

Usage examples:

    python scripts/resolve_conflicts.py
    python scripts/resolve_conflicts.py --auto-manifest
    python scripts/resolve_conflicts.py --provider openai --model gpt-4o

Only the safe manifest resolver writes to disk by default. AI-powered rewrites
require opting in via the ``--provider`` flag and a compatible API key in the
environment.
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence


VERSION_PATTERN = r"(?P<prefix>[\t ]*['\"]version['\"]\s*:\s*['\"])(?P<version>[^'\"]+)(?P<suffix>['\"]\s*,?)"
DEPENDS_PATTERN = r"(?P<prefix>[\t ]*['\"]depends['\"]\s*:\s*)(?P<depends>\[[^\]]*\])(?P<suffix>\s*,?)"


@dataclass
class ConflictFile:
    path: Path
    content: str


class ConflictFinder:
    def __init__(self, git_root: Path) -> None:
        self.git_root = git_root

    def list_conflicted_files(self, paths: Optional[Sequence[str]] = None) -> List[ConflictFile]:
        cmd = ["git", "grep", "-l", "<<<<<<<"]
        if paths:
            cmd.extend(paths)
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.git_root)
        if result.returncode not in (0, 1):
            raise RuntimeError(result.stderr.strip())
        files = [self.git_root / Path(line) for line in result.stdout.splitlines() if line.strip()]
        return [ConflictFile(path=f, content=f.read_text(encoding="utf-8")) for f in files]


def parse_version(value: str) -> Optional[List[int]]:
    try:
        return [int(part) for part in value.strip().split(".")]
    except ValueError:
        return None


def choose_highest_version(ours: Optional[str], theirs: Optional[str]) -> Optional[str]:
    if not ours:
        return theirs
    if not theirs:
        return ours
    ours_parts = parse_version(ours)
    theirs_parts = parse_version(theirs)
    if not ours_parts or not theirs_parts:
        return max(ours, theirs)
    max_len = max(len(ours_parts), len(theirs_parts))
    ours_parts.extend([0] * (max_len - len(ours_parts)))
    theirs_parts.extend([0] * (max_len - len(theirs_parts)))
    return ours if ours_parts >= theirs_parts else theirs


def extract_version(text: str) -> Optional[str]:
    import re

    match = re.search(VERSION_PATTERN, text)
    if not match:
        return None
    return match.group("version").strip()


def replace_version(text: str, new_version: str) -> str:
    import re

    match = re.search(VERSION_PATTERN, text)
    if not match:
        return text
    replacement = f"{match.group('prefix')}{new_version}{match.group('suffix')}"
    return text[: match.start()] + replacement + text[match.end() :]


def extract_depends(text: str) -> Optional[List[str]]:
    import re

    match = re.search(DEPENDS_PATTERN, text, flags=re.DOTALL)
    if not match:
        return None
    try:
        depends = ast.literal_eval(match.group("depends"))
    except (ValueError, SyntaxError):
        return None
    return [str(item) for item in depends]


def replace_depends(text: str, new_depends: Sequence[str]) -> str:
    import re

    match = re.search(DEPENDS_PATTERN, text, flags=re.DOTALL)
    if not match:
        return text
    prefix = match.group("prefix")
    suffix = match.group("suffix")
    formatted = ", ".join(f"'{dep}'" for dep in new_depends)
    replacement = f"{prefix}[{formatted}]{suffix}"
    return text[: match.start()] + replacement + text[match.end() :]


def unique_ordered(values: Iterable[str]) -> List[str]:
    seen = set()
    merged: List[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        merged.append(value)
    return merged


def resolve_manifest_block(ours: str, theirs: str) -> str:
    ours_version = extract_version(ours)
    theirs_version = extract_version(theirs)
    chosen_version = choose_highest_version(ours_version, theirs_version)

    ours_depends = extract_depends(ours) or []
    theirs_depends = extract_depends(theirs) or []
    merged_depends = unique_ordered([*ours_depends, *theirs_depends]) if (ours_depends or theirs_depends) else None

    # Prefer the block that already contains the winning version when possible.
    base_text = theirs if chosen_version and chosen_version == theirs_version else ours
    if not base_text.strip():
        base_text = theirs or ours

    resolved = base_text
    if chosen_version:
        resolved = replace_version(resolved, chosen_version)
    if merged_depends:
        resolved = replace_depends(resolved, merged_depends)
    return resolved


def resolve_manifest_file(content: str) -> str:
    lines = content.splitlines()
    output: List[str] = []
    state = "normal"
    ours: List[str] = []
    theirs: List[str] = []

    for line in lines:
        if line.startswith("<<<<<<<"):
            state = "ours"
            ours = []
            theirs = []
            continue
        if state == "ours" and line.startswith("======="):
            state = "theirs"
            continue
        if state in {"ours", "theirs"} and line.startswith(">>>>>>>"):
            output.append(resolve_manifest_block("\n".join(ours), "\n".join(theirs)))
            state = "normal"
            continue
        if state == "ours":
            ours.append(line)
        elif state == "theirs":
            theirs.append(line)
        else:
            output.append(line)
    return "\n".join(output) + ("\n" if content.endswith("\n") else "")


def build_prompt(file_path: Path, content: str) -> str:
    return f"""
You are an Expert Odoo Developer. Fix the git merge conflicts in this file.

RULES:
1. For XML: If both branches add fields via xpath, KEEP BOTH fields.
2. For Python: If both branches verify logic, merge them if possible.
3. For Manifest: Always pick the HIGHER version number. Combine 'depends'.
4. Return ONLY the fixed code. No markdown.

FILE PATH: {file_path}
FILE CONTENT:
{content}
"""


def call_openai(prompt: str, model: str) -> str:
    try:
        import openai
    except ImportError as exc:  # pragma: no cover - import guard
        raise RuntimeError("openai package not installed") from exc

    client = openai.OpenAI()
    response = client.responses.create(
        model=model,
        input=[{"role": "user", "content": prompt}],
        max_output_tokens=16_000,
    )
    return response.output_text


def attempt_ai_resolution(conflict: ConflictFile, provider: Optional[str], model: Optional[str]) -> Optional[str]:
    if not provider:
        return None

    prompt = build_prompt(conflict.path, conflict.content)

    if provider == "openai":
        return call_openai(prompt, model or "gpt-4o")

    if provider == "anthropic":
        try:  # pragma: no cover - optional dependency
            import anthropic
        except ImportError as exc:
            raise RuntimeError("anthropic package not installed") from exc

        client = anthropic.Anthropic()
        message = client.messages.create(
            model=model or "claude-3-5-sonnet-latest",
            max_tokens=16_000,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in message.content if hasattr(block, "text"))

    raise ValueError(f"Unsupported provider: {provider}")


def handle_conflict(conflict: ConflictFile, args: argparse.Namespace) -> None:
    if conflict.path.name == "__manifest__.py" and args.auto_manifest:
        resolved = resolve_manifest_file(conflict.content)
        if "<<<<<<<" not in resolved:
            conflict.path.write_text(resolved, encoding="utf-8")
            print(f"✅ Auto-resolved manifest conflict in {conflict.path}")
            return
        print(f"⚠️ Manifest auto-resolve incomplete for {conflict.path}; markers remain.")

    ai_result = attempt_ai_resolution(conflict, args.provider, args.model)
    if ai_result is None:
        print(f"⚠️ Found conflict in {conflict.path}. Copy the prompt below into your AI tool:\n")
        print(build_prompt(conflict.path, conflict.content))
        print("\n---\n")
        return

    conflict.path.write_text(ai_result, encoding="utf-8")
    print(f"✅ Applied AI suggestion to {conflict.path}")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI-assisted Git conflict resolver")
    parser.add_argument("paths", nargs="*", help="Optional subset of files or directories to scan")
    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic"],
        help="AI provider to call. If omitted, only prompts are printed.",
    )
    parser.add_argument("--model", help="Model to use with the chosen provider")
    parser.add_argument(
        "--auto-manifest",
        action="store_true",
        help="Automatically resolve manifest conflicts by choosing the higher version and merging depends.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    git_root = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip())
    conflicts = ConflictFinder(git_root).list_conflicted_files(args.paths)
    if not conflicts:
        print("✅ No conflicts found.")
        return 0

    print("🔥 Found conflicts in:")
    for conflict in conflicts:
        print(f" - {conflict.path.relative_to(git_root)}")
    print()

    for conflict in conflicts:
        handle_conflict(conflict, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
