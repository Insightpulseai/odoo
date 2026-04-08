"""Validate all JSON schemas in agents/schemas/ are valid JSON Schema draft-07."""
import pathlib
import json
import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
SCHEMAS_DIR = REPO_ROOT / "agents" / "schemas"

EXPECTED_SCHEMAS = [
    "agent/agent-manifest.schema.json",
    "skill/skill-contract.schema.json",
    "judge/judge-rubric.schema.json",
    "workflow/workflow-graph.schema.json",
]


def _find_schema_files():
    return sorted(SCHEMAS_DIR.rglob("*.schema.json"))


def test_expected_schemas_exist():
    for rel_path in EXPECTED_SCHEMAS:
        full_path = SCHEMAS_DIR / rel_path
        assert full_path.exists(), f"Missing expected schema: {rel_path}"


def test_all_schemas_are_valid_json():
    failures = []
    for filepath in _find_schema_files():
        try:
            with open(filepath) as f:
                json.load(f)
        except json.JSONDecodeError as exc:
            failures.append(f"{filepath.name}: {exc}")
    assert not failures, f"JSON parse failures:\n" + "\n".join(failures)


def test_all_schemas_have_required_meta_fields():
    """Each schema must have $schema, title, and type."""
    failures = []
    for filepath in _find_schema_files():
        with open(filepath) as f:
            data = json.load(f)
        for field in ("$schema", "title", "type"):
            if field not in data:
                failures.append(f"{filepath.name} missing '{field}'")
    assert not failures, "\n".join(failures)


def test_all_schemas_reference_draft_07():
    for filepath in _find_schema_files():
        with open(filepath) as f:
            data = json.load(f)
        schema_ref = data.get("$schema", "")
        assert "draft-07" in schema_ref, (
            f"{filepath.name} does not reference draft-07: {schema_ref}"
        )
