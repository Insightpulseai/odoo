"""
Creative Generation Benchmark

Runs golden fixtures against multiple models and produces a comparison report.
Models: Nano Banana 2, Nano Banana Pro, Imagen 4, Veo 3.1.

Usage:
    python -m agents.evals.creative.benchmark --fixtures image --output docs/evidence/
    python -m agents.evals.creative.benchmark --fixtures all --output docs/evidence/
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "infra" / "ai" / "provider_router"))

FIXTURES_DIR = Path(__file__).parent / "fixtures"

IMAGE_MODELS = [
    {"id": "nano-banana-2-preview", "tier": "fast", "cost_relative": 1.0},
    {"id": "nano-banana-pro-preview", "tier": "standard", "cost_relative": 3.0},
    {"id": "imagen-4", "tier": "premium", "cost_relative": 5.0},
]

VIDEO_MODELS = [
    {"id": "veo-3.1-preview", "tier": "premium", "cost_relative": 10.0},
]


def load_fixtures(fixture_type: str) -> List[Dict]:
    """Load golden fixtures from YAML."""
    try:
        import yaml
    except ImportError:
        raise RuntimeError("PyYAML required. Run: pip install pyyaml")

    path = FIXTURES_DIR / f"{fixture_type}_golden.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Fixtures not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)
    return data.get("fixtures", [])


def run_image_benchmark(
    output_dir: Path,
    models: Optional[List[Dict]] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Run image fixtures against all image models."""
    from creative import CreativeGenerator, CreativeError
    from creative_eval import evaluate_image

    models = models or IMAGE_MODELS
    fixtures = load_fixtures("image")
    results = {"timestamp": datetime.now(timezone.utc).isoformat(), "models": {}}

    for model_info in models:
        model_id = model_info["id"]
        tier = model_info["tier"]
        model_results = {"scores": [], "failures": [], "total_time_ms": 0}

        for fixture in fixtures:
            logger.info(f"[{model_id}] Running fixture: {fixture['id']}")

            if dry_run:
                model_results["scores"].append({
                    "fixture_id": fixture["id"],
                    "score_overall": 0.0,
                    "pass_fail": "skip",
                    "note": "dry_run",
                })
                continue

            try:
                gen = CreativeGenerator()
                tier_map = {"fast": "fast", "standard": "standard", "premium": "premium"}

                gen_start = time.time()
                assets = gen.generate_image(
                    prompt=fixture["prompt"],
                    tier=tier_map.get(tier, "fast"),
                )
                gen_time = int((time.time() - gen_start) * 1000)

                if not assets:
                    model_results["failures"].append({
                        "fixture_id": fixture["id"],
                        "reason": "no_assets_returned",
                    })
                    continue

                eval_result = evaluate_image(
                    image_data=assets[0].data,
                    prompt=fixture["prompt"],
                    surface=fixture["surface"],
                    model_used=model_id,
                    expected_text=fixture.get("expected_text", []),
                    forbidden_text=fixture.get("forbidden_text", []),
                    current_tier=f"stills_{tier}",
                )

                model_results["scores"].append({
                    "fixture_id": fixture["id"],
                    "score_overall": eval_result.score_overall,
                    "dimension_scores": eval_result.dimension_scores,
                    "pass_fail": eval_result.pass_fail,
                    "issues": eval_result.issues,
                    "brand_violations": eval_result.brand_violations,
                    "gen_time_ms": gen_time,
                    "eval_time_ms": eval_result.latency_ms,
                })
                model_results["total_time_ms"] += gen_time + eval_result.latency_ms

            except (CreativeError, Exception) as e:
                logger.error(f"[{model_id}] Fixture {fixture['id']} failed: {e}")
                model_results["failures"].append({
                    "fixture_id": fixture["id"],
                    "reason": str(e),
                })

        # Aggregate
        passing = [s for s in model_results["scores"] if s["pass_fail"] == "pass"]
        all_scores = [s["score_overall"] for s in model_results["scores"] if s["pass_fail"] != "skip"]
        model_results["summary"] = {
            "total_fixtures": len(fixtures),
            "passed": len(passing),
            "failed": len(model_results["failures"]),
            "avg_score": round(sum(all_scores) / max(len(all_scores), 1), 3),
            "cost_relative": model_info["cost_relative"],
        }

        results["models"][model_id] = model_results

    return results


def run_video_benchmark(
    output_dir: Path,
    models: Optional[List[Dict]] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Run video fixtures against video models."""
    from creative import CreativeGenerator, CreativeError
    from creative_eval import evaluate_video

    models = models or VIDEO_MODELS
    fixtures = load_fixtures("video")
    results = {"timestamp": datetime.now(timezone.utc).isoformat(), "models": {}}

    for model_info in models:
        model_id = model_info["id"]
        model_results = {"scores": [], "failures": [], "total_time_ms": 0}

        for fixture in fixtures:
            logger.info(f"[{model_id}] Running video fixture: {fixture['id']}")

            if dry_run:
                model_results["scores"].append({
                    "fixture_id": fixture["id"],
                    "score_overall": 0.0,
                    "pass_fail": "skip",
                    "note": "dry_run",
                })
                continue

            try:
                gen = CreativeGenerator()
                gen_start = time.time()
                asset = gen.generate_video(
                    prompt=fixture["prompt"],
                    model=model_id,
                    duration_s=fixture.get("duration_s", 5),
                )
                gen_time = int((time.time() - gen_start) * 1000)

                eval_result = evaluate_video(
                    video_data=asset.data,
                    prompt=fixture["prompt"],
                    surface=fixture["surface"],
                    model_used=model_id,
                    expected_text=fixture.get("expected_text", []),
                    forbidden_text=fixture.get("forbidden_text", []),
                )

                model_results["scores"].append({
                    "fixture_id": fixture["id"],
                    "score_overall": eval_result.score_overall,
                    "dimension_scores": eval_result.dimension_scores,
                    "pass_fail": eval_result.pass_fail,
                    "issues": eval_result.issues,
                    "gen_time_ms": gen_time,
                    "eval_time_ms": eval_result.latency_ms,
                })
                model_results["total_time_ms"] += gen_time + eval_result.latency_ms

            except (CreativeError, Exception) as e:
                logger.error(f"[{model_id}] Video fixture {fixture['id']} failed: {e}")
                model_results["failures"].append({
                    "fixture_id": fixture["id"],
                    "reason": str(e),
                })

        passing = [s for s in model_results["scores"] if s["pass_fail"] == "pass"]
        all_scores = [s["score_overall"] for s in model_results["scores"] if s["pass_fail"] != "skip"]
        model_results["summary"] = {
            "total_fixtures": len(fixtures),
            "passed": len(passing),
            "failed": len(model_results["failures"]),
            "avg_score": round(sum(all_scores) / max(len(all_scores), 1), 3),
            "cost_relative": model_info["cost_relative"],
        }

        results["models"][model_id] = model_results

    return results


def save_report(results: Dict, output_dir: Path, name: str) -> str:
    """Save benchmark report to JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    path = output_dir / f"{name}-{stamp}.json"
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Report saved: {path}")
    return str(path)


def main():
    parser = argparse.ArgumentParser(description="Creative generation benchmark")
    parser.add_argument("--fixtures", choices=["image", "video", "all"], default="all")
    parser.add_argument("--output", default="docs/evidence/creative-benchmark")
    parser.add_argument("--dry-run", action="store_true", help="Skip actual generation/eval")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    output_dir = Path(args.output)

    if args.fixtures in ("image", "all"):
        image_results = run_image_benchmark(output_dir, dry_run=args.dry_run)
        save_report(image_results, output_dir, "image-benchmark")
        print("\n=== IMAGE BENCHMARK SUMMARY ===")
        for model_id, data in image_results["models"].items():
            s = data.get("summary", {})
            print(f"  {model_id}: avg={s.get('avg_score', 'N/A')} "
                  f"passed={s.get('passed', 0)}/{s.get('total_fixtures', 0)} "
                  f"cost={s.get('cost_relative', '?')}x")

    if args.fixtures in ("video", "all"):
        video_results = run_video_benchmark(output_dir, dry_run=args.dry_run)
        save_report(video_results, output_dir, "video-benchmark")
        print("\n=== VIDEO BENCHMARK SUMMARY ===")
        for model_id, data in video_results["models"].items():
            s = data.get("summary", {})
            print(f"  {model_id}: avg={s.get('avg_score', 'N/A')} "
                  f"passed={s.get('passed', 0)}/{s.get('total_fixtures', 0)} "
                  f"cost={s.get('cost_relative', '?')}x")


if __name__ == "__main__":
    main()
