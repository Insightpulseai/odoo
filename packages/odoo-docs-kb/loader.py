"""
Odoo 18 Documentation Loader

Clones/pulls odoo/documentation@19.0 and yields document files
for chunking. Supports incremental loading via commit tracking.
"""

import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class DocFile:
    """A single documentation file ready for chunking."""

    path: str  # relative to content root
    content: str
    file_hash: str
    metadata: dict = field(default_factory=dict)


class OdooDocsLoader:
    """Load Odoo 18 documentation from git source."""

    def __init__(
        self,
        source_config_path: str = "agents/knowledge/odoo18_docs/source.yaml",
        clone_dir: str = "/tmp/odoo-documentation-19",
    ):
        with open(source_config_path) as f:
            self.config = yaml.safe_load(f)

        self.repo_url = self.config["source"]["repo"]
        self.branch = self.config["source"]["branch"]
        self.clone_dir = Path(clone_dir)
        self.include_patterns = self.config["ingestion"]["include"]
        self.exclude_patterns = self.config["ingestion"]["exclude"]
        self.file_types = self.config["ingestion"]["file_types"]
        self.metadata_base = self.config["metadata"]

    def clone_or_pull(self) -> str:
        """Clone or update the documentation repo. Returns HEAD commit SHA."""
        if (self.clone_dir / ".git").exists():
            subprocess.run(
                ["git", "-C", str(self.clone_dir), "fetch", "origin", self.branch],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "-C", str(self.clone_dir), "reset", "--hard", f"origin/{self.branch}"],
                check=True,
                capture_output=True,
            )
        else:
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    self.branch,
                    self.repo_url,
                    str(self.clone_dir),
                ],
                check=True,
                capture_output=True,
            )

        result = subprocess.run(
            ["git", "-C", str(self.clone_dir), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def get_head_commit(self) -> str:
        """Get current HEAD commit of the cloned repo."""
        result = subprocess.run(
            ["git", "-C", str(self.clone_dir), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def _should_include(self, path: Path) -> bool:
        """Check if a file matches include/exclude rules."""
        rel = str(path)

        # Check file type
        if not any(path.match(ft) for ft in self.file_types):
            return False

        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if path.match(pattern):
                return False

        # Check include patterns
        for pattern in self.include_patterns:
            if path.match(pattern) or rel.startswith(pattern.replace("/**", "")):
                return True

        return False

    def _file_hash(self, content: str) -> str:
        """Deterministic content hash."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    def load_all(self) -> list[DocFile]:
        """Load all matching documentation files."""
        content_root = self.clone_dir / "content"
        if not content_root.exists():
            raise FileNotFoundError(f"Content root not found: {content_root}")

        docs = []
        for path in sorted(content_root.rglob("*")):
            if not path.is_file():
                continue

            rel_path = path.relative_to(self.clone_dir)
            if not self._should_include(rel_path):
                continue

            content = path.read_text(encoding="utf-8", errors="replace")
            file_hash = self._file_hash(content)

            docs.append(
                DocFile(
                    path=str(rel_path),
                    content=content,
                    file_hash=file_hash,
                    metadata={
                        **self.metadata_base,
                        "repo": "odoo/documentation",
                        "branch": self.branch,
                    },
                )
            )

        return docs

    def load_changed(self, last_commit: str) -> tuple[list[DocFile], list[str]]:
        """Load only files changed since last_commit.

        Returns:
            (changed_files, deleted_paths)
        """
        result = subprocess.run(
            [
                "git",
                "-C",
                str(self.clone_dir),
                "diff",
                "--name-status",
                last_commit,
                "HEAD",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        changed = []
        deleted = []

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            status = parts[0]
            filepath = parts[-1]

            if status == "D":
                deleted.append(filepath)
            elif filepath.startswith("content/"):
                full_path = self.clone_dir / filepath
                if full_path.exists():
                    rel_path = Path(filepath)
                    if self._should_include(rel_path):
                        content = full_path.read_text(encoding="utf-8", errors="replace")
                        changed.append(
                            DocFile(
                                path=filepath,
                                content=content,
                                file_hash=self._file_hash(content),
                                metadata={
                                    **self.metadata_base,
                                    "repo": "odoo/documentation",
                                    "branch": self.branch,
                                },
                            )
                        )

        return changed, deleted
