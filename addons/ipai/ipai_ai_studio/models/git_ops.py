# -*- coding: utf-8 -*-
"""
Git operations for AI Studio.

Provides optional Git branch + commit mode for generated modules.
When enabled, generated addons are committed to a new branch instead of just being written to disk.
"""
import os
import subprocess
from datetime import datetime


def _run(cmd, cwd):
    """Run a git command and return (returncode, output)."""
    p = subprocess.run(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    return p.returncode, p.stdout


def commit_generated_module(repo_root: str, module_rel_path: str, module_name: str):
    """
    Creates branch, stages module path, commits.

    Args:
        repo_root: Absolute path to git repository root
        module_rel_path: Relative path to the module from repo root
        module_name: Name of the generated module

    Returns:
        (branch, output): Tuple of branch name and command output log

    Raises:
        RuntimeError: If any git command fails
    """
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    branch = f"ai-studio/{module_name}-{ts}"

    out = []

    # Verify we're in a git repo
    rc, o = _run(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo_root)
    out.append(f"$ git rev-parse --is-inside-work-tree\n{o}")
    if rc != 0:
        raise RuntimeError(f"Not a git repository: {repo_root}\n{o}")

    # Save current branch to return to later (optional)
    rc, current_branch = _run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root
    )
    current_branch = current_branch.strip()

    # Create new branch
    rc, o = _run(["git", "checkout", "-b", branch], cwd=repo_root)
    out.append(f"$ git checkout -b {branch}\n{o}")
    if rc != 0:
        raise RuntimeError(f"Git checkout failed: {branch}\n{o}")

    # Stage the module files
    rc, o = _run(["git", "add", module_rel_path], cwd=repo_root)
    out.append(f"$ git add {module_rel_path}\n{o}")
    if rc != 0:
        # Try to go back to original branch
        _run(["git", "checkout", current_branch], cwd=repo_root)
        raise RuntimeError(f"Git add failed: {module_rel_path}\n{o}")

    # Commit
    commit_msg = f"feat(ai-studio): generate {module_name}"
    rc, o = _run(["git", "commit", "-m", commit_msg], cwd=repo_root)
    out.append(f'$ git commit -m "{commit_msg}"\n{o}')
    if rc != 0:
        # Try to go back to original branch
        _run(["git", "checkout", current_branch], cwd=repo_root)
        raise RuntimeError(f"Git commit failed:\n{o}")

    return branch, "\n\n".join(out)


def get_git_status(repo_root: str) -> str:
    """Get current git status for display."""
    rc, o = _run(["git", "status", "--short"], cwd=repo_root)
    if rc != 0:
        return f"Error getting git status: {o}"
    return o if o.strip() else "(clean)"


def get_current_branch(repo_root: str) -> str:
    """Get current git branch name."""
    rc, o = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)
    if rc != 0:
        return "unknown"
    return o.strip()
