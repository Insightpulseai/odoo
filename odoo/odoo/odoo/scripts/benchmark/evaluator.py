#!/usr/bin/env python3
"""Scoring engine — hard gate evaluation and soft score aggregation."""

from __future__ import annotations


def evaluate_hard_gates(envelopes: list[dict], config: dict) -> dict:
    """Aggregate hard gate results across all envelopes.

    Returns per-gate pass counts and total counts.
    """
    gate_names = ["capability", "correctness", "permission_check",
                  "confirmation_required", "audit_trace", "grounding"]
    results = {}

    for gate in gate_names:
        applicable = [e for e in envelopes if gate in e.get("hard_gates", {})]
        passed = [e for e in applicable if e["hard_gates"].get(gate) is True]
        results[gate] = {
            "applicable": len(applicable),
            "passed": len(passed),
            "pass_rate": len(passed) / len(applicable) if applicable else None,
        }

    return results


def compute_scenario_score(envelope: dict, config: dict) -> float:
    """Compute weighted score for a single scenario envelope."""
    if envelope["result"] != "PASS":
        return 0.0

    cap_class = None
    # Infer class from scenario ID: BM-XXX-T/N/I-NNN
    sid = envelope.get("scenario_id", "")
    parts = sid.split("-")
    if len(parts) == 4:
        class_code = parts[2]
        cap_class = {"T": "transactional", "N": "navigational", "I": "informational"}.get(class_code)

    if not cap_class:
        return 0.0

    weights = config.get("scoring", {}).get("weights", {}).get(cap_class, {})
    soft_scores = envelope.get("soft_scores", {})

    weighted = sum(
        soft_scores.get(dim, 0) * weight
        for dim, weight in weights.items()
    )
    return round(weighted, 4)


def compute_domain_scores(envelopes: list[dict], config: dict) -> dict:
    """Compute per-domain scores."""
    domains: dict[str, list[dict]] = {}
    for e in envelopes:
        # Extract domain from scenario ID prefix mapping or envelope
        sid = e.get("scenario_id", "")
        parts = sid.split("-")
        if len(parts) >= 2:
            domain_code = parts[1]
        else:
            domain_code = "unknown"
        domains.setdefault(domain_code, []).append(e)

    results = {}
    for domain_code, domain_envelopes in sorted(domains.items()):
        total = len(domain_envelopes)
        passed = sum(1 for e in domain_envelopes if e["result"] == "PASS")

        # Per-class breakdown
        classes = {}
        for cap_code, cap_name in [("T", "transactional"), ("N", "navigational"), ("I", "informational")]:
            class_envs = [e for e in domain_envelopes if f"-{cap_code}-" in e.get("scenario_id", "")]
            class_total = len(class_envs)
            class_passed = sum(1 for e in class_envs if e["result"] == "PASS")
            class_scores = [e.get("weighted_score", 0) for e in class_envs if e["result"] == "PASS"]
            classes[cap_name] = {
                "total": class_total,
                "passed": class_passed,
                "pass_rate": class_passed / class_total if class_total else 0,
                "avg_score": sum(class_scores) / len(class_scores) if class_scores else 0,
            }

        all_scores = [e.get("weighted_score", 0) for e in domain_envelopes if e["result"] == "PASS"]
        results[domain_code] = {
            "total": total,
            "passed": passed,
            "pass_rate": passed / total if total else 0,
            "avg_score": sum(all_scores) / len(all_scores) if all_scores else 0,
            "classes": classes,
        }

    return results


def compute_overall_scores(envelopes: list[dict], config: dict) -> dict:
    """Compute the full scoring summary."""
    total = len(envelopes)
    passed = sum(1 for e in envelopes if e["result"] == "PASS")
    failed = sum(1 for e in envelopes if e["result"] == "FAIL")
    not_impl = sum(1 for e in envelopes if e["result"] == "NOT_IMPLEMENTED")
    errors = sum(1 for e in envelopes if e["result"] == "ERROR")

    all_scores = [e.get("weighted_score", 0) for e in envelopes if e["result"] == "PASS"]
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0

    threshold = config.get("scoring", {}).get("certification_threshold", 0.70)
    certified = avg_score >= threshold and failed == 0

    hard_gate_summary = evaluate_hard_gates(envelopes, config)
    domain_scores = compute_domain_scores(envelopes, config)

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "not_implemented": not_impl,
        "errors": errors,
        "pass_rate": passed / total if total else 0,
        "avg_weighted_score": round(avg_score, 4),
        "certification_threshold": threshold,
        "certified": certified,
        "hard_gates": hard_gate_summary,
        "domains": domain_scores,
    }
