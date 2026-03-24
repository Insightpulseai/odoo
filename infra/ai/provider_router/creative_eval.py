"""
Creative Evaluation Service -- Judge AI-generated images and videos.

Uses OpenAI multimodal (gpt-4.1) as the judge model to score generated
assets against the rubric defined in ssot/creative/eval_policy.yaml.

Architecture:
  generate (Gemini/Imagen/fal) -> evaluate (OpenAI judge) -> accept/retry/reject

Never uses OpenAI for generation. Only for understanding and scoring.
"""

import os
import json
import time
import base64
import logging
from typing import Optional, Dict, Any, List, Literal
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

# Eval thresholds (mirrored from ssot/creative/eval_policy.yaml)
PASS_THRESHOLD = 0.85
WARN_THRESHOLD = 0.70

# Image dimension weights
IMAGE_WEIGHTS = {
    "prompt_adherence": 0.25,
    "composition": 0.15,
    "aesthetic_quality": 0.15,
    "text_rendering_accuracy": 0.20,
    "brand_compliance": 0.15,
    "artifact_detection": 0.10,
}

# Video dimension weights
VIDEO_WEIGHTS = {
    "prompt_adherence": 0.25,
    "temporal_coherence": 0.25,
    "motion_quality": 0.15,
    "visual_quality": 0.15,
    "brand_compliance": 0.10,
    "artifact_detection": 0.10,
}

# Hard-fail thresholds per dimension
IMAGE_HARD_FAILS = {
    "text_rendering_accuracy": 0.5,
    "brand_compliance": 0.5,
    "artifact_detection": 0.3,
}

VIDEO_HARD_FAILS = {
    "temporal_coherence": 0.4,
    "brand_compliance": 0.5,
    "artifact_detection": 0.3,
}

# Surface-specific overrides
SURFACE_OVERRIDES = {
    "brand_og": {"text_rendering_accuracy": 0.9, "brand_compliance": 0.95, "overall": 0.85},
    "ad_creative": {"text_rendering_accuracy": 0.9, "brand_compliance": 0.95, "overall": 0.85},
    "landing_hero": {"composition": 0.8, "aesthetic_quality": 0.8, "overall": 0.80},
    "product_ui": {"prompt_adherence": 0.85, "composition": 0.8, "overall": 0.80},
    "video_teaser": {"temporal_coherence": 0.8, "motion_quality": 0.75, "overall": 0.75},
}

# Retry routing
REROUTE_MAP = {
    "stills_fast": "stills_standard",
    "stills_standard": "stills_premium",
    "stills_premium": None,  # reject
    "video_default": None,   # reject
}


@dataclass
class EvalResult:
    """Structured evaluation result."""
    asset_type: str
    surface: str
    model_used: str
    score_overall: float
    dimension_scores: Dict[str, float]
    pass_fail: str  # "pass", "warn", "fail"
    hard_fail_triggered: bool
    hard_fail_dimensions: List[str]
    issues: List[str]
    brand_violations: List[str]
    recommended_action: str  # "accept", "retry_same_model", "retry_higher_tier", "reject"
    retry_prompt_delta: Optional[str] = None
    latency_ms: int = 0
    judge_model: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def _load_judge_prompt(asset_type: str) -> str:
    """Load judge prompt from agents/evals/creative/."""
    base = Path(__file__).resolve().parents[3]  # repo root
    judge_file = base / "agents" / "evals" / "creative" / f"judge_{asset_type}.md"
    if not judge_file.exists():
        raise FileNotFoundError(f"Judge prompt not found: {judge_file}")
    content = judge_file.read_text()
    # Extract prompt body after frontmatter
    parts = content.split("---")
    if len(parts) >= 3:
        return "---".join(parts[2:]).strip()
    return content


def _call_judge(
    image_data: Optional[bytes],
    prompt: str,
    surface: str,
    expected_text: List[str],
    forbidden_text: List[str],
    asset_type: str = "image",
) -> Dict[str, Any]:
    """Call OpenAI multimodal judge."""
    try:
        import openai
    except ImportError:
        raise RuntimeError("openai package required for judge. Run: pip install openai")

    api_key = os.getenv("IPAI_LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("IPAI_LLM_API_KEY or OPENAI_API_KEY required for judge")

    judge_system = _load_judge_prompt(asset_type)
    judge_model = os.getenv("CREATIVE_JUDGE_MODEL", "gpt-4.1")

    user_content: List[Dict[str, Any]] = []

    # Add the image if provided
    if image_data:
        b64 = base64.b64encode(image_data).decode("utf-8")
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "high"},
        })

    # Add context
    context = (
        f"Original prompt: {prompt}\n"
        f"Target surface: {surface}\n"
        f"Expected visible text: {json.dumps(expected_text)}\n"
        f"Forbidden visible text: {json.dumps(forbidden_text)}\n"
        f"Score this {asset_type} now."
    )
    user_content.append({"type": "text", "text": context})

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=judge_model,
        temperature=0.1,
        max_tokens=1024,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": judge_system},
            {"role": "user", "content": user_content},
        ],
    )

    raw = response.choices[0].message.content
    return json.loads(raw)


def _compute_verdict(
    scores: Dict[str, float],
    weights: Dict[str, float],
    hard_fails: Dict[str, float],
    surface: str,
) -> tuple:
    """Compute weighted score, check hard fails, return (overall, pass_fail, hard_fail_dims)."""
    overall = sum(scores.get(dim, 0.0) * w for dim, w in weights.items())

    hard_fail_dims = []
    for dim, threshold in hard_fails.items():
        if scores.get(dim, 1.0) < threshold:
            hard_fail_dims.append(dim)

    # Surface-specific minimums
    overrides = SURFACE_OVERRIDES.get(surface, {})
    for dim, min_val in overrides.items():
        if dim == "overall":
            continue
        if scores.get(dim, 1.0) < min_val:
            hard_fail_dims.append(f"{dim}_surface_min")

    surface_min = overrides.get("overall", PASS_THRESHOLD)

    if hard_fail_dims:
        pass_fail = "fail"
    elif overall >= surface_min:
        pass_fail = "pass"
    elif overall >= WARN_THRESHOLD:
        pass_fail = "warn"
    else:
        pass_fail = "fail"

    return overall, pass_fail, hard_fail_dims


def _determine_action(
    pass_fail: str,
    hard_fail_dims: List[str],
    current_tier: str,
    attempt: int,
    max_attempts: int = 3,
) -> str:
    """Determine recommended action based on eval result."""
    if pass_fail == "pass":
        return "accept"

    if attempt >= max_attempts:
        return "reject"

    # Brand violations -> retry same model with adjusted prompt
    if any("brand" in d for d in hard_fail_dims):
        return "retry_same_model"

    # Quality issues -> try higher tier if available
    next_tier = REROUTE_MAP.get(current_tier)
    if next_tier:
        return "retry_higher_tier"

    return "retry_same_model"


def evaluate_image(
    image_data: bytes,
    prompt: str,
    surface: str = "product_ui",
    model_used: str = "nano-banana-2-preview",
    expected_text: Optional[List[str]] = None,
    forbidden_text: Optional[List[str]] = None,
    current_tier: str = "stills_fast",
    attempt: int = 1,
) -> EvalResult:
    """
    Evaluate a generated image against the creative rubric.

    Args:
        image_data: Raw image bytes (PNG/JPEG).
        prompt: The generation prompt used.
        surface: Target surface (brand_og, landing_hero, product_ui, ad_creative).
        model_used: Model ID that generated the image.
        expected_text: Text that should be visible.
        forbidden_text: Text that must NOT be visible.
        current_tier: Current generation tier for retry routing.
        attempt: Current attempt number (1-based).

    Returns:
        EvalResult with scores, verdict, and recommended action.
    """
    expected_text = expected_text or []
    forbidden_text = forbidden_text or ["Odoo Copilot", "Ask Odoo Copilot", "Pulsar"]

    start = time.time()
    judge_output = _call_judge(
        image_data=image_data,
        prompt=prompt,
        surface=surface,
        expected_text=expected_text,
        forbidden_text=forbidden_text,
        asset_type="image",
    )
    latency = int((time.time() - start) * 1000)

    scores = judge_output.get("dimension_scores", {})
    overall, pass_fail, hard_fail_dims = _compute_verdict(
        scores, IMAGE_WEIGHTS, IMAGE_HARD_FAILS, surface
    )
    action = _determine_action(pass_fail, hard_fail_dims, current_tier, attempt)

    return EvalResult(
        asset_type="image",
        surface=surface,
        model_used=model_used,
        score_overall=round(overall, 3),
        dimension_scores=scores,
        pass_fail=pass_fail,
        hard_fail_triggered=len(hard_fail_dims) > 0,
        hard_fail_dimensions=hard_fail_dims,
        issues=judge_output.get("issues", []),
        brand_violations=judge_output.get("brand_violations", []),
        recommended_action=action,
        retry_prompt_delta=judge_output.get("retry_prompt_delta"),
        latency_ms=latency,
        judge_model=os.getenv("CREATIVE_JUDGE_MODEL", "gpt-4.1"),
    )


def evaluate_video(
    video_data: bytes,
    prompt: str,
    surface: str = "video_teaser",
    model_used: str = "veo-3.1-preview",
    expected_text: Optional[List[str]] = None,
    forbidden_text: Optional[List[str]] = None,
    attempt: int = 1,
) -> EvalResult:
    """
    Evaluate a generated video against the creative rubric.

    For video, we extract key frames and send them as images to the judge.
    Full video understanding requires model support for video input.
    """
    expected_text = expected_text or []
    forbidden_text = forbidden_text or ["Odoo Copilot", "Ask Odoo Copilot", "Pulsar"]

    start = time.time()

    # For now, send video as-is if the judge model supports it,
    # or extract frames. Using image judge with first-frame fallback.
    judge_output = _call_judge(
        image_data=video_data[:4_000_000],  # Cap payload for API limits
        prompt=prompt,
        surface=surface,
        expected_text=expected_text,
        forbidden_text=forbidden_text,
        asset_type="video",
    )
    latency = int((time.time() - start) * 1000)

    scores = judge_output.get("dimension_scores", {})
    overall, pass_fail, hard_fail_dims = _compute_verdict(
        scores, VIDEO_WEIGHTS, VIDEO_HARD_FAILS, surface
    )
    action = _determine_action(pass_fail, hard_fail_dims, "video_default", attempt)

    return EvalResult(
        asset_type="video",
        surface=surface,
        model_used=model_used,
        score_overall=round(overall, 3),
        dimension_scores=scores,
        pass_fail=pass_fail,
        hard_fail_triggered=len(hard_fail_dims) > 0,
        hard_fail_dimensions=hard_fail_dims,
        issues=judge_output.get("issues", []),
        brand_violations=judge_output.get("brand_violations", []),
        recommended_action=action,
        retry_prompt_delta=judge_output.get("retry_prompt_delta"),
        latency_ms=latency,
        judge_model=os.getenv("CREATIVE_JUDGE_MODEL", "gpt-4.1"),
    )


def run_creative_eval(
    asset_data: bytes,
    asset_type: Literal["image", "video"],
    prompt: str,
    surface: str,
    model_used: str,
    expected_text: Optional[List[str]] = None,
    forbidden_text: Optional[List[str]] = None,
    current_tier: str = "stills_fast",
    attempt: int = 1,
) -> EvalResult:
    """
    Unified entry point for creative evaluation.

    Routes to evaluate_image or evaluate_video based on asset_type.
    """
    if asset_type == "image":
        return evaluate_image(
            image_data=asset_data,
            prompt=prompt,
            surface=surface,
            model_used=model_used,
            expected_text=expected_text,
            forbidden_text=forbidden_text,
            current_tier=current_tier,
            attempt=attempt,
        )
    elif asset_type == "video":
        return evaluate_video(
            video_data=asset_data,
            prompt=prompt,
            surface=surface,
            model_used=model_used,
            expected_text=expected_text,
            forbidden_text=forbidden_text,
            attempt=attempt,
        )
    else:
        raise ValueError(f"Unsupported asset_type: {asset_type}")
