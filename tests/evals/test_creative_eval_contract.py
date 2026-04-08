"""Contract tests for creative eval output."""

import json
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_report_schema_valid():
    """Report schema is valid JSON Schema."""
    schema_path = REPO_ROOT / "agents/evals/creative/report_schema.json"
    assert schema_path.exists(), f"Missing: {schema_path}"
    schema = json.loads(schema_path.read_text())
    assert schema["title"] == "Creative Benchmark Report"
    assert "models" in schema["required"]


def test_eval_result_contract():
    """EvalResult dataclass matches expected fields."""
    import sys
    sys.path.insert(0, str(REPO_ROOT / "infra/ai/provider_router"))
    from creative_eval import EvalResult

    result = EvalResult(
        asset_type="image",
        surface="brand_og",
        model_used="nano-banana-2-preview",
        score_overall=0.88,
        dimension_scores={
            "prompt_adherence": 0.9,
            "composition": 0.85,
            "aesthetic_quality": 0.9,
            "text_rendering_accuracy": 0.95,
            "brand_compliance": 1.0,
            "artifact_detection": 0.9,
        },
        pass_fail="pass",
        hard_fail_triggered=False,
        hard_fail_dimensions=[],
        issues=[],
        brand_violations=[],
        recommended_action="accept",
    )

    d = result.to_dict()
    assert d["asset_type"] == "image"
    assert d["pass_fail"] in ("pass", "warn", "fail")
    assert d["recommended_action"] in ("accept", "retry_same_model", "retry_higher_tier", "reject")
    assert 0.0 <= d["score_overall"] <= 1.0
    assert isinstance(d["dimension_scores"], dict)
    assert isinstance(d["issues"], list)
    assert isinstance(d["brand_violations"], list)

    j = result.to_json()
    parsed = json.loads(j)
    assert parsed["surface"] == "brand_og"
