"""
Repository Documentation Loader

Discovers and loads documentation files from the local repository.
Supports incremental loading via git diff for changed files only.
"""

import hashlib
import logging
import subprocess
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# Default include patterns for org documentation
DEFAULT_INCLUDE_PATTERNS = [
    "docs/**/*.md",
    "spec/**/*.md",
    "CLAUDE.md",
    "*/CLAUDE.md",
    "odoo18/*.md",
    "docs/ai/*.md",
    "docs/contracts/*.md",
    "docs/architecture/*.md",
    "docs/runtime/*.md",
    "docs/platform/*.md",
]

# Default exclude patterns
DEFAULT_EXCLUDE_PATTERNS = [
    "docs/evidence/**",
    "node_modules/**",
    ".git/**",
    "**/vendor/**",
]

# Priority mapping for source inventory filtering
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


@dataclass
class RepoDoc:
    """A single repo documentation file ready for chunking."""

    path: str
    content: str
    file_hash: str
    doc_type: str  # "markdown", "rst", "yaml"
    metadata: dict = field(default_factory=dict)


def _file_hash(content: str) -> str:
    """Deterministic content hash."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _detect_doc_type(path: str) -> str:
    """Detect document type from file extension."""
    if path.endswith(".md"):
        return "markdown"
    elif path.endswith(".rst"):
        return "rst"
    elif path.endswith((".yaml", ".yml")):
        return "yaml"
    return "text"


def _matches_any(path: str, patterns: list[str]) -> bool:
    """Check if path matches any of the glob patterns."""
    for pattern in patterns:
        if fnmatch(path, pattern):
            return True
        # Handle ** patterns by checking prefix
        prefix = pattern.split("**")[0].rstrip("/")
        if prefix and path.startswith(prefix):
            suffix = pattern.split("**")[-1].lstrip("/")
            if not suffix or fnmatch(Path(path).name, suffix):
                return True
    return False


class RepoDocsLoader:
    """Load documentation files from the local repository."""

    def __init__(
        self,
        repo_root: str,
        source_inventory_path: str | None = None,
    ):
        """
        Args:
            repo_root: Path to repo root.
            source_inventory_path: Optional path to source_inventory.yaml
                for filtering by priority.
        """
        self.repo_root = Path(repo_root).resolve()
        self.inventory = None
        if source_inventory_path:
            inv_path = Path(source_inventory_path)
            if inv_path.exists():
                with open(inv_path) as f:
                    self.inventory = yaml.safe_load(f)

    def _get_head_commit(self) -> str:
        """Get current HEAD commit SHA."""
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_root), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown"

    def _should_include(
        self,
        rel_path: str,
        include_patterns: list[str],
        exclude_patterns: list[str],
    ) -> bool:
        """Check if a file matches include/exclude rules."""
        if _matches_any(rel_path, exclude_patterns):
            return False
        return _matches_any(rel_path, include_patterns)

    def discover(
        self,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        min_priority: str = "P2",
    ) -> list[RepoDoc]:
        """Discover documentation files matching criteria.

        Args:
            include_patterns: Glob patterns for files to include.
            exclude_patterns: Glob patterns for files to exclude.
            min_priority: Minimum priority level from inventory (P0-P3).

        Returns:
            List of RepoDoc with path, content, doc_type, metadata.
        """
        includes = include_patterns or DEFAULT_INCLUDE_PATTERNS
        excludes = exclude_patterns or DEFAULT_EXCLUDE_PATTERNS
        min_priority_val = PRIORITY_ORDER.get(min_priority, 2)
        head_commit = self._get_head_commit()

        docs = []
        for pattern in includes:
            # Resolve glob pattern against repo root
            base_pattern = pattern.replace("**/*", "**")
            for path in sorted(self.repo_root.rglob("*")):
                if not path.is_file():
                    continue

                rel_path = str(path.relative_to(self.repo_root))
                if not self._should_include(rel_path, includes, excludes):
                    continue

                # Priority filtering via inventory
                if self.inventory and not self._passes_priority(
                    rel_path, min_priority_val
                ):
                    continue

                try:
                    content = path.read_text(encoding="utf-8", errors="replace")
                except Exception as e:
                    logger.warning("Failed to read %s: %s", rel_path, e)
                    continue

                if not content.strip():
                    continue

                doc_type = _detect_doc_type(rel_path)
                docs.append(
                    RepoDoc(
                        path=rel_path,
                        content=content,
                        file_hash=_file_hash(content),
                        doc_type=doc_type,
                        metadata={
                            "source": "repo-docs",
                            "repo": "Insightpulseai/odoo",
                            "branch": self._get_current_branch(),
                            "commit": head_commit,
                            "source_type": "internal-docs",
                        },
                    )
                )

        # Deduplicate by path
        seen = set()
        unique = []
        for doc in docs:
            if doc.path not in seen:
                seen.add(doc.path)
                unique.append(doc)

        logger.info("Discovered %d repo docs", len(unique))
        return unique

    def load_changed(
        self,
        since_commit: str | None = None,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> list[RepoDoc]:
        """Load only files changed since a commit (incremental).

        Uses git diff to find changed docs.

        Args:
            since_commit: Git commit SHA or ref (e.g., HEAD~5).
            include_patterns: Glob patterns for files to include.
            exclude_patterns: Glob patterns for files to exclude.

        Returns:
            List of RepoDoc for changed files.
        """
        includes = include_patterns or DEFAULT_INCLUDE_PATTERNS
        excludes = exclude_patterns or DEFAULT_EXCLUDE_PATTERNS

        if since_commit is None:
            logger.info("No since_commit provided, loading all docs")
            return self.discover(include_patterns=includes, exclude_patterns=excludes)

        head_commit = self._get_head_commit()

        try:
            result = subprocess.run(
                [
                    "git", "-C", str(self.repo_root),
                    "diff", "--name-status", since_commit, "HEAD",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            logger.warning(
                "git diff failed (commit %s may not exist): %s. Falling back to full load.",
                since_commit, e,
            )
            return self.discover(include_patterns=includes, exclude_patterns=excludes)

        changed_docs = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            status = parts[0][0]  # First char: A, M, D, R, C
            filepath = parts[-1]

            if status == "D":
                # Deleted files are tracked but not loaded
                continue

            if not self._should_include(filepath, includes, excludes):
                continue

            full_path = self.repo_root / filepath
            if not full_path.exists():
                continue

            try:
                content = full_path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                logger.warning("Failed to read changed file %s: %s", filepath, e)
                continue

            if not content.strip():
                continue

            doc_type = _detect_doc_type(filepath)
            changed_docs.append(
                RepoDoc(
                    path=filepath,
                    content=content,
                    file_hash=_file_hash(content),
                    doc_type=doc_type,
                    metadata={
                        "source": "repo-docs",
                        "repo": "Insightpulseai/odoo",
                        "branch": self._get_current_branch(),
                        "commit": head_commit,
                        "source_type": "internal-docs",
                        "change_since": since_commit,
                    },
                )
            )

        logger.info(
            "Found %d changed docs since %s",
            len(changed_docs),
            since_commit[:8] if len(since_commit) > 8 else since_commit,
        )
        return changed_docs

    def get_deleted_paths(
        self,
        since_commit: str,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> list[str]:
        """Get paths of files deleted since a commit.

        Args:
            since_commit: Git commit SHA or ref.

        Returns:
            List of deleted file paths.
        """
        includes = include_patterns or DEFAULT_INCLUDE_PATTERNS
        excludes = exclude_patterns or DEFAULT_EXCLUDE_PATTERNS

        try:
            result = subprocess.run(
                [
                    "git", "-C", str(self.repo_root),
                    "diff", "--name-status", "--diff-filter=D",
                    since_commit, "HEAD",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError:
            return []

        deleted = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            filepath = parts[-1]
            if self._should_include(filepath, includes, excludes):
                deleted.append(filepath)

        return deleted

    def _get_current_branch(self) -> str:
        """Get current git branch name."""
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_root), "rev-parse", "--abbrev-ref", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown"

    def _passes_priority(self, rel_path: str, min_priority_val: int) -> bool:
        """Check if a file passes the priority filter from inventory."""
        if not self.inventory:
            return True
        sources = self.inventory.get("sources", [])
        for source in sources:
            patterns = source.get("include_patterns", [])
            if _matches_any(rel_path, patterns):
                priority = source.get("priority", "P2")
                return PRIORITY_ORDER.get(priority, 2) <= min_priority_val
        # If not in inventory, include by default
        return True
