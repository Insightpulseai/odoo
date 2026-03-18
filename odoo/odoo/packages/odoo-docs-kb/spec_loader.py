"""
Spec Bundle Loader

Load and normalize spec bundles from the spec/ directory.
A spec bundle is a directory containing constitution.md, prd.md,
and optionally plan.md and tasks.md.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# Known spec bundle files (in priority order)
BUNDLE_FILES = [
    "constitution.md",
    "prd.md",
    "plan.md",
    "tasks.md",
]

# Optional additional files that may appear in spec bundles
OPTIONAL_FILES = [
    "architecture.md",
    "design.md",
    "api.md",
    "migration.md",
    "testing.md",
]


@dataclass
class SpecDoc:
    """A single document from a spec bundle."""

    path: str
    content: str
    file_hash: str
    bundle_name: str
    doc_role: str  # "constitution", "prd", "plan", "tasks", "supplement"
    metadata: dict = field(default_factory=dict)


def _file_hash(content: str) -> str:
    """Deterministic content hash."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _classify_role(filename: str) -> str:
    """Classify the role of a file within a spec bundle."""
    stem = Path(filename).stem.lower()
    if stem == "constitution":
        return "constitution"
    elif stem == "prd":
        return "prd"
    elif stem == "plan":
        return "plan"
    elif stem == "tasks":
        return "tasks"
    return "supplement"


class SpecBundleLoader:
    """Load and normalize spec bundles from spec/ directory."""

    def __init__(self, repo_root: str):
        """
        Args:
            repo_root: Path to repo root.
        """
        self.repo_root = Path(repo_root).resolve()

    def discover(self, spec_root: str = "spec") -> list[dict]:
        """Discover all spec bundles.

        A spec bundle is a directory containing at least one of:
        constitution.md, prd.md, plan.md, tasks.md.

        Args:
            spec_root: Relative path to spec directory from repo root.

        Returns:
            List of dicts with: bundle_name, path, files, metadata.
        """
        spec_dir = self.repo_root / spec_root
        if not spec_dir.exists():
            logger.warning("Spec directory not found: %s", spec_dir)
            return []

        bundles = []
        for entry in sorted(spec_dir.iterdir()):
            if not entry.is_dir():
                # Root-level spec files (constitution.md, prd.md at spec/ root)
                if entry.suffix == ".md" and entry.stem.lower() in {
                    "constitution", "prd", "plan", "tasks",
                }:
                    bundles.append({
                        "bundle_name": "root",
                        "path": str(entry.relative_to(self.repo_root)),
                        "files": [entry.name],
                        "is_root": True,
                    })
                continue

            # Check if directory contains spec bundle files
            found_files = []
            for candidate in BUNDLE_FILES + OPTIONAL_FILES:
                if (entry / candidate).exists():
                    found_files.append(candidate)

            # Also include any .md files not in the known lists
            for md_file in sorted(entry.glob("*.md")):
                if md_file.name not in found_files:
                    found_files.append(md_file.name)

            if found_files:
                bundle_name = entry.name
                bundles.append({
                    "bundle_name": bundle_name,
                    "path": str(entry.relative_to(self.repo_root)),
                    "files": found_files,
                    "is_root": False,
                })

        logger.info("Discovered %d spec bundles in %s", len(bundles), spec_root)
        return bundles

    def load_bundle(self, bundle_path: str) -> list[SpecDoc]:
        """Load all docs from a single spec bundle.

        Args:
            bundle_path: Relative path to the bundle directory from repo root.

        Returns:
            List of SpecDoc with proper metadata.
        """
        full_path = self.repo_root / bundle_path
        if not full_path.exists():
            logger.warning("Bundle path not found: %s", full_path)
            return []

        bundle_name = full_path.name
        docs = []

        if full_path.is_file():
            # Single file (root-level spec file)
            content = full_path.read_text(encoding="utf-8", errors="replace")
            if content.strip():
                rel_path = str(full_path.relative_to(self.repo_root))
                docs.append(
                    SpecDoc(
                        path=rel_path,
                        content=content,
                        file_hash=_file_hash(content),
                        bundle_name="root",
                        doc_role=_classify_role(full_path.name),
                        metadata={
                            "source": "spec-bundle",
                            "bundle": "root",
                            "doc_role": _classify_role(full_path.name),
                            "source_type": "spec",
                        },
                    )
                )
            return docs

        # Directory bundle
        for md_file in sorted(full_path.glob("*.md")):
            try:
                content = md_file.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                logger.warning("Failed to read %s: %s", md_file, e)
                continue

            if not content.strip():
                continue

            rel_path = str(md_file.relative_to(self.repo_root))
            role = _classify_role(md_file.name)

            docs.append(
                SpecDoc(
                    path=rel_path,
                    content=content,
                    file_hash=_file_hash(content),
                    bundle_name=bundle_name,
                    doc_role=role,
                    metadata={
                        "source": "spec-bundle",
                        "bundle": bundle_name,
                        "doc_role": role,
                        "source_type": "spec",
                    },
                )
            )

        logger.info("Loaded %d docs from bundle '%s'", len(docs), bundle_name)
        return docs

    def load_all(self, spec_root: str = "spec") -> list[SpecDoc]:
        """Load all documents from all spec bundles.

        Args:
            spec_root: Relative path to spec directory from repo root.

        Returns:
            List of all SpecDoc across all bundles.
        """
        bundles = self.discover(spec_root)
        all_docs = []

        for bundle in bundles:
            if bundle.get("is_root"):
                # Load individual root file
                docs = self.load_bundle(bundle["path"])
            else:
                docs = self.load_bundle(bundle["path"])
            all_docs.extend(docs)

        logger.info(
            "Loaded %d total spec docs from %d bundles",
            len(all_docs),
            len(bundles),
        )
        return all_docs
