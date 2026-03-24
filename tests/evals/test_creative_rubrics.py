"""Rubric validation tests."""

import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path):
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)


class TestImageRubric:
    @pytest.fixture
    def rubric(self):
        return load_yaml(REPO_ROOT / "agents/evals/creative/rubric_image.yaml")

    def test_weights_sum_to_one(self, rubric):
        total = sum(d["weight"] for d in rubric["dimensions"].values())
        assert abs(total - 1.0) < 0.01, f"Weights sum to {total}, expected 1.0"

    def test_all_dimensions_have_scoring(self, rubric):
        for name, dim in rubric["dimensions"].items():
            assert "scoring" in dim, f"Dimension {name} missing scoring"
            assert "weight" in dim, f"Dimension {name} missing weight"

    def test_pass_threshold_gt_warn(self, rubric):
        assert rubric["aggregate"]["pass_threshold"] > rubric["aggregate"]["warn_threshold"]

    def test_no_deprecated_names_in_hard_fails(self, rubric):
        brand = rubric["dimensions"]["brand_compliance"]
        triggers = brand.get("hard_fail_triggers", [])
        # These should reference deprecated names as things to CATCH, which is correct
        assert any("Odoo Copilot" in t for t in triggers), "Should detect Odoo Copilot"
        assert any("Pulsar" in t for t in triggers), "Should detect Pulsar"


class TestVideoRubric:
    @pytest.fixture
    def rubric(self):
        return load_yaml(REPO_ROOT / "agents/evals/creative/rubric_video.yaml")

    def test_weights_sum_to_one(self, rubric):
        total = sum(d["weight"] for d in rubric["dimensions"].values())
        assert abs(total - 1.0) < 0.01, f"Weights sum to {total}, expected 1.0"

    def test_temporal_coherence_is_weighted_high(self, rubric):
        tc = rubric["dimensions"]["temporal_coherence"]
        assert tc["weight"] >= 0.20, "Temporal coherence should be heavily weighted for video"

    def test_has_hard_fail_dimensions(self, rubric):
        hard_fails = [
            name for name, dim in rubric["dimensions"].items()
            if "hard_fail_below" in dim
        ]
        assert len(hard_fails) >= 2, "Should have at least 2 hard-fail dimensions"


class TestRetryPolicy:
    def test_reroute_escalates(self):
        import sys
        sys.path.insert(0, str(REPO_ROOT / "infra/ai/provider_router"))
        from creative_eval import REROUTE_MAP

        assert REROUTE_MAP["stills_fast"] == "stills_standard"
        assert REROUTE_MAP["stills_standard"] == "stills_premium"
        assert REROUTE_MAP["stills_premium"] is None  # reject at top tier

    def test_thresholds_monotonic(self):
        import sys
        sys.path.insert(0, str(REPO_ROOT / "infra/ai/provider_router"))
        from creative_eval import PASS_THRESHOLD, WARN_THRESHOLD

        assert PASS_THRESHOLD > WARN_THRESHOLD
        assert WARN_THRESHOLD > 0.0


class TestFixtures:
    def test_image_fixtures_valid(self):
        fixtures = load_yaml(REPO_ROOT / "agents/evals/creative/fixtures/image_golden.yaml")
        assert len(fixtures["fixtures"]) >= 10, "Need at least 10 image fixtures"
        for f in fixtures["fixtures"]:
            assert "id" in f
            assert "surface" in f
            assert "prompt" in f
            assert "min_score" in f
            assert f["min_score"] > 0.0

    def test_video_fixtures_valid(self):
        fixtures = load_yaml(REPO_ROOT / "agents/evals/creative/fixtures/video_golden.yaml")
        assert len(fixtures["fixtures"]) >= 3, "Need at least 3 video fixtures"
        for f in fixtures["fixtures"]:
            assert "id" in f
            assert "prompt" in f
            assert "duration_s" in f

    def test_no_deprecated_names_in_expected_text(self):
        deprecated = ["Odoo Copilot", "Ask Odoo Copilot", "Pulsar"]
        for fixture_type in ("image", "video"):
            fixtures = load_yaml(
                REPO_ROOT / f"agents/evals/creative/fixtures/{fixture_type}_golden.yaml"
            )
            for f in fixtures["fixtures"]:
                for text in f.get("expected_text", []):
                    assert text not in deprecated, (
                        f"Fixture {f['id']} expects deprecated text: {text}"
                    )
