#!/usr/bin/env python3
"""
Well-Architected Score — CLI scorer for IPAI stack.

Reads the lens JSON, runs automated checks, scores each question,
computes weighted pillar scores and overall score.

Usage:
    python3 scripts/wa_score.py                     # Full assessment (auto + manual prompts)
    python3 scripts/wa_score.py --auto-only         # Automated checks only (CI mode)
    python3 scripts/wa_score.py --json              # JSON output
    python3 scripts/wa_score.py --pillar security   # Score single pillar
"""
import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


LENS_PATH = Path(__file__).parent.parent / "spec" / "well-architected" / "ipai-wa-lens.json"
REPO_ROOT = Path(__file__).parent.parent


@dataclass
class QuestionResult:
    question_id: str
    title: str
    score: int
    max_score: int
    risk: str
    method: str  # "auto" | "manual" | "skipped"
    evidence: str = ""


@dataclass
class PillarResult:
    pillar_id: str
    name: str
    weight: float
    questions: list = field(default_factory=list)
    score: float = 0.0
    max_score: float = 5.0

    @property
    def high_risk_count(self) -> int:
        return sum(1 for q in self.questions if q.risk == "HIGH_RISK")


@dataclass
class AssessmentResult:
    timestamp: str
    pillar_results: list = field(default_factory=list)
    overall_score: float = 0.0
    high_risk_findings: int = 0


def load_lens(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def classify_risk(score: int, risk_map: dict) -> str:
    for risk_level, score_range in risk_map.items():
        if score in score_range:
            return risk_level
    return "UNKNOWN"


def run_check(command: str, timeout: int = 15) -> tuple[bool, str]:
    """Run a check command and return (success, output)."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(REPO_ROOT),
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)


def auto_score_question(question: dict, risk_map: dict) -> Optional[QuestionResult]:
    """Attempt to auto-score a question using its check_command."""
    if not question.get("automatable") or not question.get("check_command"):
        return None

    cmd = question["check_command"]
    success, output = run_check(cmd)

    choices = question["choices"]

    if len(choices) == 2:
        # Binary check: success = max score, failure = min score
        score = choices[-1]["score"] if success and output else choices[0]["score"]
    else:
        # Multi-choice: heuristic based on output presence
        if not success or not output:
            score = choices[0]["score"]
        elif output.strip():
            # Default to middle score for non-empty output
            mid = len(choices) // 2
            score = choices[mid]["score"]
        else:
            score = choices[0]["score"]

    risk = classify_risk(score, risk_map)
    return QuestionResult(
        question_id=question["id"],
        title=question["title"],
        score=score,
        max_score=5,
        risk=risk,
        method="auto",
        evidence=output[:200] if output else "no output",
    )


def manual_score_question(question: dict, risk_map: dict) -> QuestionResult:
    """Prompt user to score a question manually."""
    print(f"\n  {question['id']}: {question['title']}")
    for i, choice in enumerate(question["choices"]):
        print(f"    [{i}] {choice['label']} (score: {choice['score']})")

    while True:
        try:
            idx = int(input(f"  Select [0-{len(question['choices'])-1}]: ").strip())
            if 0 <= idx < len(question["choices"]):
                break
        except (ValueError, EOFError):
            pass
        print("  Invalid selection, try again.")

    chosen = question["choices"][idx]
    risk = classify_risk(chosen["score"], risk_map)
    return QuestionResult(
        question_id=question["id"],
        title=question["title"],
        score=chosen["score"],
        max_score=5,
        risk=risk,
        method="manual",
        evidence=chosen["label"],
    )


def score_pillar(
    pillar: dict, risk_map: dict, auto_only: bool = False
) -> PillarResult:
    """Score all questions in a pillar."""
    result = PillarResult(
        pillar_id=pillar["id"],
        name=pillar["name"],
        weight=pillar["weight"],
    )

    for question in pillar["questions"]:
        q_result = auto_score_question(question, risk_map)

        if q_result is None:
            if auto_only:
                q_result = QuestionResult(
                    question_id=question["id"],
                    title=question["title"],
                    score=0,
                    max_score=5,
                    risk="MEDIUM_RISK",
                    method="skipped",
                    evidence="manual question skipped in auto-only mode",
                )
            else:
                q_result = manual_score_question(question, risk_map)

        result.questions.append(q_result)

    if result.questions:
        total = sum(q.score for q in result.questions)
        result.score = total / len(result.questions)

    return result


def run_assessment(
    lens: dict,
    auto_only: bool = False,
    pillar_filter: Optional[str] = None,
    quiet: bool = False,
) -> AssessmentResult:
    """Run full assessment."""
    risk_map = lens["scoring"]["risk_map"]
    assessment = AssessmentResult(
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    pillars = lens["pillars"]
    if pillar_filter:
        pillars = [p for p in pillars if p["id"] == pillar_filter]
        if not pillars:
            print(f"Pillar '{pillar_filter}' not found.", file=sys.stderr)
            sys.exit(1)

    for pillar in pillars:
        if not quiet:
            print(f"\n{'='*60}")
            print(f"  Pillar: {pillar['name']} (weight: {pillar['weight']*100:.0f}%)")
            print(f"{'='*60}")

        pr = score_pillar(pillar, risk_map, auto_only=auto_only)
        assessment.pillar_results.append(pr)

    # Compute weighted overall score
    weighted_sum = sum(pr.score * pr.weight for pr in assessment.pillar_results)
    weight_total = sum(pr.weight for pr in assessment.pillar_results)
    assessment.overall_score = weighted_sum / weight_total if weight_total > 0 else 0

    assessment.high_risk_findings = sum(
        pr.high_risk_count for pr in assessment.pillar_results
    )

    return assessment


def print_report(assessment: AssessmentResult, lens: dict):
    """Print console summary."""
    labels = lens["scoring"]["labels"]

    print(f"\n{'='*60}")
    print("  IPAI Well-Architected Assessment Report")
    print(f"  {assessment.timestamp}")
    print(f"{'='*60}")

    for pr in assessment.pillar_results:
        label = labels.get(str(int(pr.score)), "N/A")
        bar = "#" * int(pr.score) + "." * (5 - int(pr.score))
        high = f" [{pr.high_risk_count} HIGH_RISK]" if pr.high_risk_count else ""
        print(f"\n  {pr.name:<30} [{bar}] {pr.score:.1f}/5.0 ({label}){high}")

        for q in pr.questions:
            risk_icon = {"HIGH_RISK": "X", "MEDIUM_RISK": "~", "NO_RISK": "+"}.get(
                q.risk, "?"
            )
            method_tag = f"[{q.method}]"
            print(f"    {risk_icon} {q.question_id}: {q.title} = {q.score} {method_tag}")

    print(f"\n{'='*60}")
    overall_label = labels.get(str(int(assessment.overall_score)), "N/A")
    print(f"  OVERALL SCORE: {assessment.overall_score:.2f}/5.0 ({overall_label})")
    print(f"  HIGH_RISK FINDINGS: {assessment.high_risk_findings}")
    print(f"{'='*60}")


def to_json(assessment: AssessmentResult) -> dict:
    """Convert assessment to JSON-serializable dict."""
    return {
        "timestamp": assessment.timestamp,
        "overall_score": round(assessment.overall_score, 2),
        "high_risk_findings": assessment.high_risk_findings,
        "pillars": [
            {
                "id": pr.pillar_id,
                "name": pr.name,
                "weight": pr.weight,
                "score": round(pr.score, 2),
                "high_risk_count": pr.high_risk_count,
                "questions": [
                    {
                        "id": q.question_id,
                        "title": q.title,
                        "score": q.score,
                        "risk": q.risk,
                        "method": q.method,
                        "evidence": q.evidence,
                    }
                    for q in pr.questions
                ],
            }
            for pr in assessment.pillar_results
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="IPAI Well-Architected Scorer")
    parser.add_argument(
        "--auto-only",
        action="store_true",
        help="Run automated checks only (CI mode, no prompts)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON report",
    )
    parser.add_argument(
        "--pillar",
        type=str,
        help="Score a single pillar (e.g., security, reliability, operations, devops, governance)",
    )
    parser.add_argument(
        "--lens",
        type=str,
        default=str(LENS_PATH),
        help="Path to lens JSON file",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=3.0,
        help="Minimum overall score (exit non-zero if below, default 3.0)",
    )
    args = parser.parse_args()

    lens = load_lens(Path(args.lens))
    assessment = run_assessment(
        lens,
        auto_only=args.auto_only,
        pillar_filter=args.pillar,
        quiet=args.json,
    )

    if args.json:
        print(json.dumps(to_json(assessment), indent=2))
    else:
        print_report(assessment, lens)

    # CI gate: exit non-zero if below threshold or any HIGH_RISK
    if assessment.overall_score < args.threshold:
        print(
            f"\nFAIL: Overall score {assessment.overall_score:.2f} < threshold {args.threshold}",
            file=sys.stderr,
        )
        sys.exit(1)

    if assessment.high_risk_findings > 0:
        print(
            f"\nFAIL: {assessment.high_risk_findings} HIGH_RISK finding(s)",
            file=sys.stderr,
        )
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
