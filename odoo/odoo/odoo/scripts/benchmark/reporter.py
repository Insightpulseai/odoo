#!/usr/bin/env python3
"""Report generator — produces Markdown and JSON benchmark reports."""

from __future__ import annotations

from datetime import datetime, timezone

# Domain code → display name
DOMAIN_NAMES = {
    "CRM": "CRM",
    "SAL": "Sales",
    "PUR": "Purchase",
    "ACC": "Accounting",
    "INV": "Inventory",
    "PRJ": "Project/Helpdesk",
    "ADM": "Settings/Admin",
    "KNW": "Knowledge/SOP",
    "DOC": "Documents",
}


def generate_markdown_report(envelopes: list[dict], scores: dict, config: dict) -> str:
    """Generate a Markdown summary report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    bv = config.get("benchmark", {}).get("version", "1.0.0")
    ov = envelopes[0].get("odoo_version", "19.0") if envelopes else "19.0"
    cv = envelopes[0].get("copilot_version", "0.0.0") if envelopes else "0.0.0"

    lines = [
        f"# Odoo Copilot Benchmark Report",
        "",
        f"- **Run**: {now}",
        f"- **Benchmark version**: {bv}",
        f"- **Odoo**: {ov}",
        f"- **Copilot**: {cv}",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total scenarios | {scores['total']} |",
        f"| Passed | {scores['passed']} |",
        f"| Failed | {scores['failed']} |",
        f"| Not implemented | {scores['not_implemented']} |",
        f"| Errors | {scores['errors']} |",
        f"| Pass rate | {scores['pass_rate']:.0%} |",
        f"| Avg weighted score | {scores['avg_weighted_score']:.1%} |",
        f"| Certified | {'YES' if scores['certified'] else 'NO'} (threshold: {scores['certification_threshold']:.0%}) |",
        "",
    ]

    # Domain breakdown
    domains = scores.get("domains", {})
    if domains:
        lines.extend([
            "## Domain Scores",
            "",
            "| Domain | Trans | Nav | Info | Overall | Pass Rate |",
            "|--------|-------|-----|------|---------|-----------|",
        ])
        for code, data in sorted(domains.items()):
            name = DOMAIN_NAMES.get(code, code)
            classes = data.get("classes", {})
            t_score = classes.get("transactional", {}).get("avg_score", 0)
            n_score = classes.get("navigational", {}).get("avg_score", 0)
            i_score = classes.get("informational", {}).get("avg_score", 0)
            overall = data.get("avg_score", 0)
            pr = data.get("pass_rate", 0)
            lines.append(
                f"| {name} | {t_score:.0%} | {n_score:.0%} | {i_score:.0%} | {overall:.0%} | {pr:.0%} |"
            )
        lines.append("")

    # Hard gate summary
    hard_gates = scores.get("hard_gates", {})
    if hard_gates:
        lines.extend([
            "## Hard Gate Summary",
            "",
            "| Gate | Applicable | Passed | Rate |",
            "|------|-----------|--------|------|",
        ])
        for gate, data in sorted(hard_gates.items()):
            if data["applicable"] > 0:
                lines.append(
                    f"| {gate} | {data['applicable']} | {data['passed']} | "
                    f"{data['pass_rate']:.0%} |"
                )
        lines.append("")

    # Per-scenario results
    lines.extend([
        "## Scenario Results",
        "",
        "| ID | Persona | Class | Result | Score | Latency |",
        "|---|---------|-------|--------|-------|---------|",
    ])
    for e in envelopes:
        sid = e["scenario_id"]
        persona = e.get("persona", "-")
        # Infer class from ID
        parts = sid.split("-")
        cls = {"T": "trans", "N": "nav", "I": "info"}.get(parts[2], "?") if len(parts) == 4 else "?"
        result = e["result"]
        score = f"{e.get('weighted_score', 0):.0%}" if result == "PASS" else "-"
        latency = f"{e.get('latency_ms', 0)}ms"
        lines.append(f"| {sid} | {persona} | {cls} | {result} | {score} | {latency} |")

    lines.append("")
    return "\n".join(lines)


def generate_comparison_report(current: dict, previous: dict) -> str:
    """Generate a comparison report between two benchmark runs.

    Args:
        current: scores dict from current run
        previous: scores dict from previous run

    Returns:
        Markdown comparison report
    """
    lines = [
        "# Odoo Copilot Benchmark — Comparison Report",
        "",
        "| Metric | Previous | Current | Delta |",
        "|--------|----------|---------|-------|",
    ]

    for key in ("pass_rate", "avg_weighted_score"):
        prev_val = previous.get(key, 0)
        curr_val = current.get(key, 0)
        delta = curr_val - prev_val
        sign = "+" if delta >= 0 else ""
        lines.append(f"| {key} | {prev_val:.1%} | {curr_val:.1%} | {sign}{delta:.1%} |")

    lines.append("")

    # Domain comparison
    prev_domains = previous.get("domains", {})
    curr_domains = current.get("domains", {})
    all_domain_codes = sorted(set(list(prev_domains.keys()) + list(curr_domains.keys())))

    if all_domain_codes:
        lines.extend([
            "## Domain Comparison",
            "",
            "| Domain | Prev Rate | Curr Rate | Delta | Regression? |",
            "|--------|-----------|-----------|-------|-------------|",
        ])
        tolerance = current.get("regression_tolerance", previous.get("regression_tolerance", 0.05))
        regressions = []
        for code in all_domain_codes:
            name = DOMAIN_NAMES.get(code, code)
            prev_pr = prev_domains.get(code, {}).get("pass_rate", 0)
            curr_pr = curr_domains.get(code, {}).get("pass_rate", 0)
            delta = curr_pr - prev_pr
            is_regression = delta < -tolerance
            sign = "+" if delta >= 0 else ""
            flag = "YES" if is_regression else ""
            lines.append(f"| {name} | {prev_pr:.0%} | {curr_pr:.0%} | {sign}{delta:.0%} | {flag} |")
            if is_regression:
                regressions.append(name)

        lines.append("")
        if regressions:
            lines.append(f"**Regressions detected in: {', '.join(regressions)}**")
        else:
            lines.append("**No regressions detected.**")
        lines.append("")

    return "\n".join(lines)
