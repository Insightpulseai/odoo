"""Agent platform knowledge contract tests.

Validates cross-manifest consistency across ssot/agent-platform/ YAML
manifests and .github/skills/ directory structure.

Run with:
    python -m pytest tests/agent_platform/test_knowledge_contract.py -v
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SSOT_DIR = REPO_ROOT / "ssot" / "agent-platform"
SKILLS_DIR = REPO_ROOT / ".github" / "skills"

TOPIC_MAP_PATH = SSOT_DIR / "learn_mcp_topic_map.yaml"
KNOWLEDGE_SOURCES_PATH = SSOT_DIR / "knowledge_sources.yaml"
SKILLS_MANIFEST_PATH = SSOT_DIR / "skills_manifest.yaml"
TAXONOMY_PATH = SSOT_DIR / "knowledge_taxonomy.yaml"

# source_precedence entries are objects; enforce this type order
EXPECTED_SOURCE_TYPE_ORDER = [
    "repo_ssot",
    "architecture_reference_docs",
    "microsoft_learn_mcp",
    "official_microsoft_github_samples",
    "secondary_sources",
]

# Required fields per topic entry in learn_mcp_topic_map.yaml
# (topics is a dict keyed by topic_id; each value must have these fields)
REQUIRED_TOPIC_FIELDS = {
    "topic_key",
    "canonical_product",
    "mvp_critical",
    "recommended_queries",
}

# Deferred topic entries must not have mvp_critical=True
# (they are blocked/deprecated services, not active tier topics)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load(path: Path) -> dict:
    """Load YAML file; return empty dict if missing or empty."""
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _skill_dirs() -> list[Path]:
    """Return skill subdirectories in .github/skills/."""
    if not SKILLS_DIR.exists():
        return []
    return [d for d in sorted(SKILLS_DIR.iterdir()) if d.is_dir()]


def _resolve_location(loc: str) -> Path:
    """Resolve a manifest location field to an absolute path.

    Locations are repo-relative strings like '.github/skills/foo/' or
    '.claude/skills/bar/'. Path(repo_root) / loc handles the leading dot.
    """
    return REPO_ROOT / loc


# ---------------------------------------------------------------------------
# Manifest existence
# ---------------------------------------------------------------------------

class TestManifestExistence:
    """All SSOT manifests must exist and parse as YAML mappings."""

    @pytest.mark.parametrize("path,label", [
        (TOPIC_MAP_PATH, "learn_mcp_topic_map.yaml"),
        (KNOWLEDGE_SOURCES_PATH, "knowledge_sources.yaml"),
        (SKILLS_MANIFEST_PATH, "skills_manifest.yaml"),
        (TAXONOMY_PATH, "knowledge_taxonomy.yaml"),
    ])
    def test_manifest_exists(self, path, label):
        rel = path.relative_to(REPO_ROOT)
        assert path.exists(), f"Required manifest missing: {rel}"

    @pytest.mark.parametrize("path,label", [
        (TOPIC_MAP_PATH, "learn_mcp_topic_map.yaml"),
        (KNOWLEDGE_SOURCES_PATH, "knowledge_sources.yaml"),
        (SKILLS_MANIFEST_PATH, "skills_manifest.yaml"),
        (TAXONOMY_PATH, "knowledge_taxonomy.yaml"),
    ])
    def test_manifest_is_valid_yaml(self, path, label):
        if not path.exists():
            pytest.skip(f"{label} missing (covered by test_manifest_exists)")
        data = _load(path)
        assert isinstance(data, dict), (
            f"{label} must parse as a YAML mapping, got {type(data)}"
        )


# ---------------------------------------------------------------------------
# knowledge_sources.yaml
# ---------------------------------------------------------------------------

class TestKnowledgeSources:
    """Validate source precedence order and repo-local path references."""

    @pytest.fixture(scope="class")
    def sources(self):
        return _load(KNOWLEDGE_SOURCES_PATH)

    def test_source_precedence_key_exists(self, sources):
        assert "source_precedence" in sources, (
            "knowledge_sources.yaml must declare 'source_precedence'"
        )

    def test_source_precedence_type_order(self, sources):
        """Types in source_precedence must match the canonical order."""
        entries = sources.get("source_precedence", [])
        actual = [
            e.get("type") if isinstance(e, dict) else e
            for e in entries
        ]
        assert actual == EXPECTED_SOURCE_TYPE_ORDER, (
            f"source_precedence types must be {EXPECTED_SOURCE_TYPE_ORDER},"
            f" got {actual}"
        )

    def test_repo_ssot_is_highest_priority(self, sources):
        entries = sources.get("source_precedence", [])
        if not entries:
            pytest.skip("source_precedence is empty")
        first = entries[0]
        first_type = first.get("type") if isinstance(first, dict) else first
        assert first_type == "repo_ssot", (
            f"First source must be repo_ssot, got {first_type!r}"
        )

    def test_has_at_least_one_repo_ssot_entry(self, sources):
        """Must include at least one repo_ssot source entry."""
        entries = [
            e for e in sources.get("sources", [])
            if e.get("type") == "repo_ssot"
        ]
        assert len(entries) > 0, (
            "knowledge_sources.yaml must have at least one 'repo_ssot'"
            " source entry"
        )

    def test_local_paths_exist(self, sources):
        """Repo-local paths in knowledge_sources must exist on disk."""
        missing = []
        for entry in sources.get("sources", []):
            src_type = entry.get("type", "")
            if src_type not in ("repo_ssot", "architecture_reference_docs"):
                continue
            for rel_path in entry.get("paths", []):
                if "*" in rel_path:
                    continue
                if not (REPO_ROOT / rel_path).exists():
                    missing.append(rel_path)
        assert not missing, (
            "Repo-local paths in knowledge_sources.yaml do not exist:"
            f" {missing}"
        )


# ---------------------------------------------------------------------------
# learn_mcp_topic_map.yaml
# ---------------------------------------------------------------------------

class TestTopicMap:
    """Each topic must have required fields; map must have topics."""

    @pytest.fixture(scope="class")
    def topic_map(self):
        return _load(TOPIC_MAP_PATH)

    @pytest.fixture(scope="class")
    def topics(self, topic_map):
        # topics is a dict keyed by topic_id
        raw = topic_map.get("topics", {})
        return raw if isinstance(raw, dict) else {}

    def test_has_topics(self, topics):
        assert len(topics) > 0, (
            "learn_mcp_topic_map.yaml must declare at least one topic"
        )

    def test_all_topics_have_required_fields(self, topics):
        violations = []
        for tid, entry in topics.items():
            if not isinstance(entry, dict):
                violations.append(f"{tid}: value must be a mapping")
                continue
            missing = REQUIRED_TOPIC_FIELDS - set(entry.keys())
            if missing:
                violations.append(f"{tid}: missing {sorted(missing)}")
        assert not violations, (
            "Topics missing required fields:\n" + "\n".join(violations)
        )

    def test_all_topics_have_recommended_queries(self, topics):
        violations = [
            tid for tid, v in topics.items()
            if not v.get("recommended_queries")
        ]
        assert not violations, (
            "Topics missing recommended_queries: " + str(violations)
        )

    def test_mvp_critical_field_is_boolean(self, topics):
        violations = [
            tid for tid, v in topics.items()
            if not isinstance(v.get("mvp_critical"), bool)
        ]
        assert not violations, (
            "Topics with non-boolean mvp_critical: " + str(violations)
        )

    def test_topic_key_matches_dict_key(self, topics):
        """Each entry's topic_key must equal the dict key."""
        violations = [
            f"{k}: topic_key={v.get('topic_key')!r}"
            for k, v in topics.items()
            if isinstance(v, dict) and v.get("topic_key") != k
        ]
        assert not violations, (
            "topic_key mismatch:\n" + "\n".join(violations)
        )


# ---------------------------------------------------------------------------
# skills_manifest.yaml
# ---------------------------------------------------------------------------

class TestSkillsManifest:
    """skills_manifest.yaml must reference skills that exist on disk."""

    @pytest.fixture(scope="class")
    def manifest(self):
        return _load(SKILLS_MANIFEST_PATH)

    @pytest.fixture(scope="class")
    def declared_skills(self, manifest):
        return manifest.get("skills", [])

    def test_has_skills(self, declared_skills):
        assert len(declared_skills) > 0, (
            "skills_manifest.yaml must declare at least one skill"
        )

    def test_all_declared_skill_locations_exist_on_disk(
        self, declared_skills
    ):
        missing = []
        for skill in declared_skills:
            sid = skill.get("id", "<unknown>")
            loc = skill.get("location", f".github/skills/{sid}/")
            resolved = _resolve_location(loc)
            if not resolved.exists():
                missing.append(f"{sid} -> {loc}")
        assert not missing, (
            "Skills declared in manifest but missing on disk: "
            + str(missing)
        )

    def test_no_duplicate_skill_ids(self, declared_skills):
        ids = [s.get("id") for s in declared_skills]
        duplicates = {n for n in ids if ids.count(n) > 1}
        assert not duplicates, (
            f"Duplicate skill IDs in manifest: {duplicates}"
        )


# ---------------------------------------------------------------------------
# knowledge_taxonomy.yaml
# ---------------------------------------------------------------------------

class TestKnowledgeTaxonomy:
    """Taxonomy deferred list must not include mvp_critical items."""

    @pytest.fixture(scope="class")
    def taxonomy(self):
        return _load(TAXONOMY_PATH)

    @pytest.fixture(scope="class")
    def deferred_topics(self, taxonomy):
        # taxonomy.taxonomy.deferred_optional.topics
        return (
            taxonomy
            .get("taxonomy", {})
            .get("deferred_optional", {})
            .get("topics", [])
        )

    def test_taxonomy_key_exists(self, taxonomy):
        assert "taxonomy" in taxonomy, (
            "knowledge_taxonomy.yaml must have a top-level 'taxonomy' key"
        )

    def test_deferred_topics_have_id_field(self, deferred_topics):
        missing_id = [
            i for i, e in enumerate(deferred_topics)
            if not e.get("id")
        ]
        assert not missing_id, (
            "Deferred topics missing 'id' at indices: " + str(missing_id)
        )

    def test_deferred_topics_have_approved_alternative(
        self, deferred_topics
    ):
        missing = [
            e.get("id", f"index-{i}")
            for i, e in enumerate(deferred_topics)
            if not e.get("approved_alternative")
        ]
        assert not missing, (
            "Deferred topics missing approved_alternative: " + str(missing)
        )

    def test_no_mvp_critical_in_deferred(self, deferred_topics):
        """No topic in deferred_optional should be marked mvp_critical."""
        violations = [
            e.get("id", "<unknown>")
            for e in deferred_topics
            if e.get("mvp_critical") is True
        ]
        assert not violations, (
            "MVP-critical topics must not be in deferred_optional: "
            + str(violations)
        )


# ---------------------------------------------------------------------------
# .github/skills/ on-disk completeness
# ---------------------------------------------------------------------------

class TestSkillsOnDisk:
    """Every skill directory must contain SKILL.md and examples.md."""

    @pytest.fixture(scope="class")
    def skill_dirs(self):
        return _skill_dirs()

    def test_skills_dir_exists(self):
        assert SKILLS_DIR.exists(), (
            f".github/skills/ does not exist at {SKILLS_DIR}"
        )

    def test_all_skills_have_skill_md(self, skill_dirs):
        missing = [
            d.name for d in skill_dirs
            if not (d / "SKILL.md").exists()
        ]
        assert not missing, f"Skills missing SKILL.md: {missing}"

    def test_all_skills_have_examples_md(self, skill_dirs):
        missing = [
            d.name for d in skill_dirs
            if not (d / "examples.md").exists()
        ]
        assert not missing, f"Skills missing examples.md: {missing}"

    def test_at_least_one_skill_on_disk(self, skill_dirs):
        assert len(skill_dirs) > 0, (
            "No skill directories found in .github/skills/"
        )


# ---------------------------------------------------------------------------
# Cross-manifest consistency
# ---------------------------------------------------------------------------

class TestCrossManifestConsistency:
    """Skills and topics in manifests must be consistent with disk state."""

    def test_manifest_skill_locations_exist(self):
        """Every location in skills_manifest.yaml must resolve to a dir."""
        manifest = _load(SKILLS_MANIFEST_PATH)
        bad = []
        for skill in manifest.get("skills", []):
            sid = skill.get("id", "<unknown>")
            loc = skill.get("location", f".github/skills/{sid}/")
            if not _resolve_location(loc).exists():
                bad.append(f"{sid} -> {loc}")
        assert not bad, (
            "Manifest skill locations not found on disk: " + str(bad)
        )

    def test_source_precedence_first_entry_is_repo(self):
        """First source_precedence entry must be repo_ssot type."""
        sources = _load(KNOWLEDGE_SOURCES_PATH)
        entries = sources.get("source_precedence", [])
        if not entries:
            pytest.skip("source_precedence is empty")
        first = entries[0]
        first_type = first.get("type") if isinstance(first, dict) else first
        assert first_type == "repo_ssot", (
            f"First source must be repo_ssot, got {first_type!r}"
        )

    def test_taxonomy_deferred_ids_are_unique(self):
        """Deferred topic IDs in taxonomy must be unique."""
        taxonomy = _load(TAXONOMY_PATH)
        deferred = (
            taxonomy
            .get("taxonomy", {})
            .get("deferred_optional", {})
            .get("topics", [])
        )
        ids = [e.get("id") for e in deferred if e.get("id")]
        duplicates = {i for i in ids if ids.count(i) > 1}
        assert not duplicates, (
            "Duplicate deferred topic IDs in taxonomy: " + str(duplicates)
        )

    def test_topic_map_ids_do_not_overlap_deferred(self):
        """Active topic map keys must not appear in taxonomy deferred list."""
        topic_map = _load(TOPIC_MAP_PATH)
        taxonomy = _load(TAXONOMY_PATH)
        active_ids = set(topic_map.get("topics", {}).keys())
        deferred_ids = {
            e.get("id")
            for e in taxonomy
            .get("taxonomy", {})
            .get("deferred_optional", {})
            .get("topics", [])
            if e.get("id")
        }
        overlap = active_ids & deferred_ids
        assert not overlap, (
            "Topic IDs appear in both topic map and deferred list: "
            + str(overlap)
        )
