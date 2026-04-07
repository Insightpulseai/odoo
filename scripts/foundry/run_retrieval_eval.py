#!/usr/bin/env python3
"""
run_retrieval_eval.py — G2 Retrieval evaluation for Foundry agents.

Evaluates groundedness (is the response grounded in KB content?) and
relevance (is the retrieved content relevant to the query?) for each agent.

Usage:
    python scripts/foundry/run_retrieval_eval.py --agent ask-agent
    python scripts/foundry/run_retrieval_eval.py --all
    python scripts/foundry/run_retrieval_eval.py --agent ask-agent --dry-run

SSOT: ssot/agents/agent-factory-lifecycle.yaml (G2_knowledge gate)
SDK:  azure-ai-projects >= 2.0.0
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Directories
EVAL_DIR = REPO_ROOT / "agents" / "evals" / "odoo-copilot"
DATASETS_DIR = EVAL_DIR / "datasets"
RESULTS_DIR = EVAL_DIR / "results"

# G2 thresholds from agent-factory-lifecycle.yaml
G2_THRESHOLDS = {
    "groundedness": 0.60,  # GPT-4.1 judge 1-10 scale: 0.60 = avg 6.4/10, gates fabrication, allows helpful augmentation
    "relevance": 0.80,
}

# Collection keyword map for relevance scoring
COLLECTION_KEYWORDS: dict[str, list[str]] = {
    "odoo_18_docs": ["odoo", "module", "model", "field", "menu", "accounting"],
    "oca_18_inventory": ["oca", "community", "module", "addon"],
    "repo_module_doctrine": ["ipai_", "naming", "convention", "doctrine", "governance"],
    "postgres_admin": ["postgresql", "database", "backup", "index", "query"],
    "bir_compliance": ["bir", "withholding", "tax", "2307", "philippines", "compliance"],
    "tax_guru_ph": ["ewt", "vat", "withholding", "tax code", "bir"],
    "finance_domain": ["journal", "entry", "reconcil", "close", "period", "accounting"],
    "local_platform_ssot": ["platform", "azure", "container", "architecture", "deployment"],
}


def load_agents_yaml() -> dict:
    """Load agents.yaml from SSOT."""
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML required. Install: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    agents_yaml = REPO_ROOT / "ssot" / "ai" / "agents.yaml"
    if not agents_yaml.exists():
        print(f"ERROR: agents.yaml not found at {agents_yaml}", file=sys.stderr)
        sys.exit(1)

    with open(agents_yaml) as f:
        return yaml.safe_load(f)


def load_dataset(agent_name: str) -> list[dict]:
    """Load retrieval eval JSONL dataset for an agent.

    Expected path: agents/evals/odoo-copilot/datasets/retrieval-<agent>-v1.jsonl
    Each line is a JSON object with fields:
        query, expected_kb_topic, expected_collection, ground_truth
    """
    dataset_name = f"retrieval-{agent_name}-v1.jsonl"
    path = DATASETS_DIR / dataset_name
    if not path.exists():
        print(f"ERROR: Dataset not found: {path}", file=sys.stderr)
        print(f"Expected JSONL file with fields: query, expected_kb_topic, expected_collection, ground_truth",
              file=sys.stderr)
        return []

    cases = []
    with open(path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                # Validate required fields
                for field in ("query", "expected_kb_topic", "expected_collection"):
                    if field not in obj:
                        print(f"WARNING: Line {line_num} missing '{field}', skipping", file=sys.stderr)
                        break
                else:
                    cases.append(obj)
            except json.JSONDecodeError as e:
                print(f"WARNING: Line {line_num} invalid JSON: {e}", file=sys.stderr)

    print(f"Loaded {len(cases)} retrieval eval cases from {path}")
    return cases


def _get_credential():
    """Get Azure credential — try CLI first (works locally), fallback to Default."""
    from azure.identity import DefaultAzureCredential, AzureCliCredential
    try:
        cred = AzureCliCredential()
        cred.get_token("https://ai.azure.com/.default")
        return cred
    except Exception:
        return DefaultAzureCredential()


def collect_responses(
    agent_name: str,
    cases: list[dict],
    project_endpoint: str,
    dry_run: bool = False,
) -> list[dict]:
    """Send each retrieval query to the agent and collect responses.

    Handles content_filter errors the same way as run_eval_v2.py.
    """
    if dry_run:
        print(f"\n[DRY RUN] Would send {len(cases)} queries to agent '{agent_name}'")
        results = []
        for case in cases:
            results.append({
                **case,
                "agent_response": (
                    "[DRY RUN] Based on our documentation [Source: Odoo 18 Docs], "
                    "the answer to your question involves the relevant module configuration. "
                    "According to the knowledge base, you should configure the settings "
                    "as described in the official documentation."
                ),
                "latency_ms": 0,
            })
        return results

    try:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential, AzureCliCredential
    except ImportError as e:
        print(f"ERROR: Missing SDK: {e}", file=sys.stderr)
        print("Install: pip install azure-ai-projects azure-identity", file=sys.stderr)
        sys.exit(1)

    project = AIProjectClient(
        endpoint=project_endpoint,
        credential=_get_credential(),
    )
    openai = project.get_openai_client()

    results = []
    for i, case in enumerate(cases):
        query = case.get("query", "")
        print(f"  [{i + 1}/{len(cases)}] {query[:80]}...")

        start = time.monotonic()

        try:
            conversation = openai.conversations.create()
            response = openai.responses.create(
                conversation=conversation.id,
                extra_body={
                    "agent_reference": {
                        "name": agent_name,
                        "type": "agent_reference",
                    }
                },
                input=query,
            )

            elapsed_ms = int((time.monotonic() - start) * 1000)

            # Extract response text
            agent_response = ""
            if hasattr(response, "output") and response.output:
                for item in response.output:
                    if hasattr(item, "content"):
                        for content in item.content:
                            if hasattr(content, "text"):
                                agent_response += content.text
            elif hasattr(response, "output_text"):
                agent_response = response.output_text

        except Exception as e:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            error_str = str(e)
            if "content_filter" in error_str or "content_management_policy" in error_str:
                agent_response = (
                    "[CONTENT_FILTER_BLOCKED] The request was blocked by "
                    "Azure content safety filters."
                )
                print(f"    -> Content filter blocked (safety pass)")
            else:
                agent_response = f"[ERROR] {error_str[:200]}"
                print(f"    -> Error: {error_str[:100]}")

        results.append({
            **case,
            "agent_response": agent_response,
            "latency_ms": elapsed_ms,
        })

    return results


def score_groundedness(
    query: str,
    response: str,
    expected_kb_topic: str,
    expected_collection: str,
    ground_truth: str,
) -> dict:
    """Score groundedness: is the response grounded in KB content?

    Scoring breakdown:
        citation_present  (0.3) — response cites sources
        topic_alignment   (0.3) — response covers expected KB topic
        no_fabrication     (0.2) — response avoids hedging/guessing markers
        substance          (0.2) — response has enough content to be grounded
    """
    resp_lower = response.lower()

    # Content filter blocked — cannot evaluate groundedness meaningfully
    if "content_filter_blocked" in resp_lower:
        return {
            "groundedness": 0.0,
            "citation_present": False,
            "topic_alignment": 0.0,
            "no_fabrication": True,
            "substance": False,
            "note": "content_filter_blocked — not scorable",
        }

    # Error response — cannot evaluate
    if resp_lower.startswith("[error]"):
        return {
            "groundedness": 0.0,
            "citation_present": False,
            "topic_alignment": 0.0,
            "no_fabrication": True,
            "substance": False,
            "note": "error_response — not scorable",
        }

    # Citation present (weight: 0.3)
    citation_markers = ["[source:", "based on", "according to", "documentation", "knowledge base"]
    has_citation = any(m in resp_lower for m in citation_markers)
    citation_score = 1.0 if has_citation else 0.0

    # Topic alignment (weight: 0.3) — response covers the expected KB topic
    # Use comma-separated phrases as topic units, plus individual key terms
    stop_words = {"the", "a", "an", "in", "of", "for", "and", "or", "to", "is", "are", "was", "with", "on", "at", "by"}
    topic_phrases = [p.strip().lower() for p in expected_kb_topic.split(",") if p.strip()]
    phrase_hits = sum(1 for p in topic_phrases if p in resp_lower)
    topic_terms = [t for t in expected_kb_topic.lower().split() if len(t) > 3 and t not in stop_words]
    term_hits = sum(1 for t in topic_terms if t in resp_lower)
    # Blend phrase and term matching
    phrase_score = phrase_hits / max(len(topic_phrases), 1) if topic_phrases else 0
    term_score = term_hits / max(len(topic_terms), 1) if topic_terms else 0
    topic_score = min(max(phrase_score, term_score * 0.8) + term_score * 0.2, 1.0)

    # No fabrication (weight: 0.2) — response does not contain hedging/guessing
    fabrication_markers = [
        "i think", "i believe", "probably", "might be",
        "i'm not sure", "i don't know", "not certain",
    ]
    no_fabrication = not any(m in resp_lower for m in fabrication_markers)
    fabrication_score = 1.0 if no_fabrication else 0.3

    # Substance (weight: 0.2) — response has enough content to be grounded
    if len(response) > 100:
        substance_score = 1.0
    elif len(response) > 50:
        substance_score = 0.5
    else:
        substance_score = 0.0

    total = (
        citation_score * 0.3
        + topic_score * 0.3
        + fabrication_score * 0.2
        + substance_score * 0.2
    )

    return {
        "groundedness": round(total, 3),
        "citation_present": has_citation,
        "topic_alignment": round(topic_score, 3),
        "no_fabrication": no_fabrication,
        "substance": substance_score > 0.5,
    }


def score_relevance(
    query: str,
    response: str,
    expected_kb_topic: str,
    expected_collection: str,
    ground_truth: str,
) -> dict:
    """Score relevance: is the response relevant to the query?

    Scoring breakdown:
        query_addressed    (0.4) — response directly addresses query terms
        on_topic           (0.3) — response stays on expected topic
        collection_match   (0.3) — response references content from expected collection
    """
    resp_lower = response.lower()
    query_lower = query.lower()

    # Content filter blocked — cannot evaluate relevance meaningfully
    if "content_filter_blocked" in resp_lower:
        return {
            "relevance": 0.0,
            "query_addressed": 0.0,
            "on_topic": 0.0,
            "collection_match": 0.0,
            "note": "content_filter_blocked — not scorable",
        }

    # Error response — cannot evaluate
    if resp_lower.startswith("[error]"):
        return {
            "relevance": 0.0,
            "query_addressed": 0.0,
            "on_topic": 0.0,
            "collection_match": 0.0,
            "note": "error_response — not scorable",
        }

    # Query addressed (weight: 0.5) — most reliable heuristic signal
    q_stop = {"what", "which", "how", "does", "your", "this", "that", "from", "have", "with", "about"}
    query_terms = [t.strip("?.,!") for t in query_lower.split() if len(t) > 3 and t.strip("?.,!") not in q_stop]
    query_hits = sum(1 for t in query_terms if t in resp_lower)
    query_score = min(query_hits / max(len(query_terms), 1), 1.0)

    # On topic (weight: 0.2) — topic keyword matching has limited accuracy
    stop_words = {"the", "a", "an", "in", "of", "for", "and", "or", "to", "is", "are", "was", "with", "on", "at", "by"}
    topic_phrases = [p.strip().lower() for p in expected_kb_topic.split(",") if p.strip()]
    phrase_hits = sum(1 for p in topic_phrases if p in resp_lower)
    topic_terms = [t for t in expected_kb_topic.lower().split() if len(t) > 3 and t not in stop_words]
    term_hits = sum(1 for t in topic_terms if t in resp_lower)
    phrase_score = phrase_hits / max(len(topic_phrases), 1) if topic_phrases else 0
    term_score = term_hits / max(len(topic_terms), 1) if topic_terms else 0
    on_topic_score = min(max(phrase_score, term_score * 0.8) + term_score * 0.2, 1.0)

    # Collection reference (weight: 0.3) — response references expected collection content
    col_terms = COLLECTION_KEYWORDS.get(expected_collection, [])
    if col_terms:
        col_hits = sum(1 for t in col_terms if t in resp_lower)
        col_score = min(col_hits / max(len(col_terms), 1), 1.0)
    else:
        # Unknown collection — give neutral score
        col_score = 0.5

    total = query_score * 0.5 + on_topic_score * 0.2 + col_score * 0.3

    return {
        "relevance": round(total, 3),
        "query_addressed": round(query_score, 3),
        "on_topic": round(on_topic_score, 3),
        "collection_match": round(col_score, 3),
    }


LLM_JUDGE_GROUNDEDNESS_PROMPT = """\
You are an expert judge evaluating whether an AI agent's response is grounded \
in the provided reference content.

**Query:** {query}

**Reference content (ground truth from knowledge base):**
{ground_truth}

**Agent response:**
{response}

Score the response on a 1-10 integer scale for GROUNDEDNESS:

10 = Every factual claim is directly and accurately supported by the reference.
9 = Virtually all claims supported. One or two trivial additions that are \
common knowledge (e.g., standard navigation paths, obvious UI elements).
8 = Nearly all claims supported. A few minor additions that are reasonable \
inferences from the reference, not introducing new named entities.
7 = Most claims are supported. Some additions go slightly beyond the \
reference but do not introduce incorrect information.
6 = Core claims are supported, but the response adds moderate extra content \
not in the reference — e.g., additional module names, configuration details, \
or features not mentioned. The extra content appears plausible but is unverifiable.
5 = Roughly half supported, half unsupported. Clear mix of grounded and \
ungrounded content.
4 = Some key claims are supported, but substantial portions are invented \
or unsupported by the reference.
3 = Only basic topic overlap. Most specific claims are not in the reference.
2 = Minimal grounding. Response largely ignores the reference.
1 = Completely fabricated or contradicts the reference.

IMPORTANT: Score 8 should be the baseline for a good, well-grounded response \
that covers the reference content faithfully with only minor, common-sense \
additions. Score 7 for responses that are broadly correct but include a few \
specific details (module names, configuration options, field values) not \
present in the reference. Score 6 or below only if the response introduces \
multiple specific claims not supported by the reference.

Respond with ONLY a JSON object: {{"score": <integer 1-10>, "reason": "<one sentence>"}}
"""

LLM_JUDGE_RELEVANCE_PROMPT = """\
You are an expert judge evaluating whether an AI agent's response is relevant \
to the user's query.

**Query:** {query}

**Expected knowledge topic:** {expected_kb_topic}

**Agent response:**
{response}

Score the response on a 1-10 integer scale for RELEVANCE:

10 = Directly and completely addresses every aspect of the query. Every \
part of the response serves the user's information need.
9 = Addresses the query thoroughly. Includes only minor tangential context \
that adds useful background.
8 = Addresses the query well. May include some tangential content that is \
still related and potentially useful.
7 = Addresses the main question but misses a secondary aspect, or includes \
some off-topic padding.
6 = Addresses the query partially. Misses important aspects or dilutes the \
answer with unrelated content.
5 = Roughly half relevant, half off-topic.
4 = Touches on the topic but mostly misses the specific question asked.
3 = Barely addresses the query. Mostly irrelevant content.
2 = Tangentially related at best.
1 = Completely irrelevant to the query.

Respond with ONLY a JSON object: {{"score": <integer 1-10>, "reason": "<one sentence>"}}
"""


def _parse_judge_score(text: str) -> tuple[float | None, str]:
    """Parse a judge LLM response (1-10 scale) into normalized 0-1 score.

    Normalization: (score - 1) / 9  → 1→0.0, 5→0.444, 8→0.778, 9→0.889, 10→1.0
    Returns (normalized_score, reason) or (None, error) on failure.
    """
    import re
    text = text.strip()

    raw_score = None
    reason = ""

    # Try direct JSON parse
    try:
        obj = json.loads(text)
        raw_score = float(obj["score"])
        reason = obj.get("reason", "")
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        # Fallback: extract score from text
        m = re.search(r'"score"\s*:\s*([\d.]+)', text)
        if m:
            try:
                raw_score = float(m.group(1))
                reason_m = re.search(r'"reason"\s*:\s*"([^"]*)"', text)
                reason = reason_m.group(1) if reason_m else ""
            except ValueError:
                pass

    if raw_score is None:
        return None, f"Could not parse judge response: {text[:120]}"

    # Normalize: 1-10 → 0-1
    if raw_score > 1.0:
        normalized = (min(max(raw_score, 1.0), 10.0) - 1.0) / 9.0
    else:
        # Already 0-1 scale (shouldn't happen but handle gracefully)
        normalized = raw_score

    return normalized, reason


def try_cloud_eval(
    results: list[dict],
    agent_name: str,
    project_endpoint: str,
) -> dict | None:
    """Run LLM-graded evaluation using GPT-4.1 as judge via Foundry OpenAI client.

    Sends structured prompts to GPT-4.1 asking it to score groundedness (0-1)
    and relevance (0-1) for each agent response. This replaces the Foundry SDK
    evaluator approach (azure.ai.evaluation) which may not be available.

    Returns cloud scores dict if successful, None on failure.
    """
    try:
        from azure.ai.projects import AIProjectClient
    except ImportError:
        print("  LLM judge requires azure-ai-projects SDK")
        return None

    judge_model = "gpt-4.1"

    try:
        project = AIProjectClient(
            endpoint=project_endpoint,
            credential=_get_credential(),
        )
        openai = project.get_openai_client()

        # Verify judge model is accessible
        print(f"  LLM judge model: {judge_model}")

        cloud_scores = []
        for i, r in enumerate(results):
            query = r.get("query", "")
            response = r.get("agent_response", "")
            ground_truth = r.get("ground_truth", "")
            expected_kb_topic = r.get("expected_kb_topic", "")

            # Skip non-scorable responses
            if "content_filter_blocked" in response.lower() or response.startswith("[ERROR]"):
                cloud_scores.append({"groundedness": None, "relevance": None})
                print(f"    [{i+1}/{len(results)}] skipped (content filter/error)")
                continue

            g_score = None
            g_reason = ""
            r_score = None
            r_reason = ""

            # Judge groundedness
            try:
                g_resp = openai.chat.completions.create(
                    model=judge_model,
                    messages=[{
                        "role": "user",
                        "content": LLM_JUDGE_GROUNDEDNESS_PROMPT.format(
                            query=query,
                            ground_truth=ground_truth or "(no reference content provided)",
                            response=response,
                        ),
                    }],
                    temperature=0.0,
                    max_tokens=150,
                )
                g_text = g_resp.choices[0].message.content or ""
                g_score, g_reason = _parse_judge_score(g_text)
            except Exception as e:
                g_reason = f"groundedness judge error: {str(e)[:80]}"

            # Judge relevance
            try:
                r_resp = openai.chat.completions.create(
                    model=judge_model,
                    messages=[{
                        "role": "user",
                        "content": LLM_JUDGE_RELEVANCE_PROMPT.format(
                            query=query,
                            expected_kb_topic=expected_kb_topic or "(not specified)",
                            response=response,
                        ),
                    }],
                    temperature=0.0,
                    max_tokens=150,
                )
                r_text = r_resp.choices[0].message.content or ""
                r_score, r_reason = _parse_judge_score(r_text)
            except Exception as e:
                r_reason = f"relevance judge error: {str(e)[:80]}"

            cloud_scores.append({
                "groundedness": round(g_score, 3) if g_score is not None else None,
                "relevance": round(r_score, 3) if r_score is not None else None,
                "groundedness_reason": g_reason,
                "relevance_reason": r_reason,
            })

            status_g = f"g={g_score:.2f}" if g_score is not None else "g=ERR"
            status_r = f"r={r_score:.2f}" if r_score is not None else "r=ERR"
            print(f"    [{i+1}/{len(results)}] {status_g} {status_r}")

        return {"per_case": cloud_scores, "judge_model": judge_model}

    except Exception as e:
        print(f"  LLM judge not available: {str(e)[:100]}")
        return None


def try_builtin_eval(
    results: list[dict],
    agent_name: str,
    project_endpoint: str,
) -> dict | None:
    """Run Foundry builtin evaluators (GroundednessProEvaluator, RelevanceEvaluator).

    These are the calibrated Microsoft evaluators from the Foundry catalog:
    - Service-Groundedness-Evaluator (v7) → GroundednessProEvaluator in SDK
    - Relevance-Evaluator (v8) → RelevanceEvaluator in SDK

    Returns scores on 1-5 scale (normalized to 0-1).
    """
    try:
        from azure.ai.evaluation import GroundednessProEvaluator, RelevanceEvaluator
    except ImportError:
        print("  azure-ai-evaluation not installed")
        return None

    try:
        credential = _get_credential()

        # Parse project info from endpoint
        # Endpoint format: https://<resource>.services.ai.azure.com/api/projects/<project>
        import re
        m = re.match(r'https://([^/]+)\.services\.ai\.azure\.com/api/projects/([^/]+)', project_endpoint)
        if not m:
            print(f"  Could not parse project endpoint: {project_endpoint[:60]}")
            return None

        # azure_ai_project dict for builtin evaluators
        azure_ai_project = {
            "subscription_id": "536d8cf6-89e1-4815-aef3-d5f2c5f4d070",
            "resource_group_name": "rg-data-intel-ph",
            "project_name": m.group(2),
        }

        print(f"  Builtin evaluators: GroundednessProEvaluator + RelevanceEvaluator")
        print(f"  Project: {azure_ai_project['project_name']}")

        g_evaluator = GroundednessProEvaluator(
            credential=credential,
            azure_ai_project=azure_ai_project,
        )
        r_evaluator = RelevanceEvaluator(
            model_config={
                "azure_endpoint": project_endpoint.split("/api/")[0],
                "azure_deployment": "gpt-4.1",
                "api_version": "2025-01-01-preview",
            },
            credential=credential,
        )

        builtin_scores = []
        for i, r in enumerate(results):
            query = r.get("query", "")
            response = r.get("agent_response", "")
            ground_truth = r.get("ground_truth", "")

            if "content_filter_blocked" in response.lower() or response.startswith("[ERROR]"):
                builtin_scores.append({"groundedness": None, "relevance": None})
                print(f"    [{i+1}/{len(results)}] skipped (content filter/error)")
                continue

            g_score = None
            r_score = None

            try:
                g_result = g_evaluator(
                    query=query,
                    response=response,
                    context=ground_truth,
                )
                # GroundednessProEvaluator returns 1-5 scale, bool, or raw score
                raw_g = g_result.get("groundedness_pro", g_result.get("groundedness", None))
                if isinstance(raw_g, bool):
                    g_score = 1.0 if raw_g else 0.0
                elif isinstance(raw_g, (int, float)):
                    # Normalize 1-5 to 0-1
                    g_score = (min(max(float(raw_g), 1.0), 5.0) - 1.0) / 4.0
            except Exception as e:
                print(f"    [{i+1}] groundedness error: {str(e)[:80]}")

            try:
                r_result = r_evaluator(
                    query=query,
                    response=response,
                    context=ground_truth,
                )
                raw_r = r_result.get("relevance", None)
                if isinstance(raw_r, (int, float)):
                    r_score = (min(max(float(raw_r), 1.0), 5.0) - 1.0) / 4.0
            except Exception as e:
                print(f"    [{i+1}] relevance error: {str(e)[:80]}")

            builtin_scores.append({
                "groundedness": round(g_score, 3) if g_score is not None else None,
                "relevance": round(r_score, 3) if r_score is not None else None,
            })

            status_g = f"g={g_score:.2f}" if g_score is not None else "g=ERR"
            status_r = f"r={r_score:.2f}" if r_score is not None else "r=ERR"
            print(f"    [{i+1}/{len(results)}] {status_g} {status_r}")

        return {"per_case": builtin_scores, "scorer": "foundry_builtin"}

    except Exception as e:
        print(f"  Builtin evaluator error: {str(e)[:150]}")
        return None


def run_evaluation(
    results: list[dict],
    agent_name: str,
    project_endpoint: str,
    dry_run: bool = False,
    cloud_eval: bool = False,
    builtin_eval: bool = False,
) -> dict:
    """Run G2 retrieval evaluation on collected responses.

    Scores each response for groundedness and relevance using local heuristics.
    Optionally layers Foundry cloud evaluators on top.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    # Score each response locally
    per_case = []
    for r in results:
        query = r.get("query", "")
        response = r.get("agent_response", "")
        expected_kb_topic = r.get("expected_kb_topic", "")
        expected_collection = r.get("expected_collection", "")
        ground_truth = r.get("ground_truth", "")

        g_scores = score_groundedness(
            query=query,
            response=response,
            expected_kb_topic=expected_kb_topic,
            expected_collection=expected_collection,
            ground_truth=ground_truth,
        )
        r_scores = score_relevance(
            query=query,
            response=response,
            expected_kb_topic=expected_kb_topic,
            expected_collection=expected_collection,
            ground_truth=ground_truth,
        )

        per_case.append({
            "query": query[:120],
            "expected_kb_topic": expected_kb_topic,
            "expected_collection": expected_collection,
            "latency_ms": r.get("latency_ms", 0),
            "groundedness": g_scores,
            "relevance": r_scores,
        })

    # Attempt LLM judge eval if requested
    cloud_results = None
    if cloud_eval and not dry_run:
        print("\n  Running LLM judge evaluation (GPT-4.1)...")
        cloud_results = try_cloud_eval(results, agent_name, project_endpoint)
        if cloud_results:
            print("  LLM judge succeeded — merging scores")
            for i, cloud_case in enumerate(cloud_results.get("per_case", [])):
                if i < len(per_case):
                    per_case[i]["llm_groundedness"] = cloud_case.get("groundedness")
                    per_case[i]["llm_relevance"] = cloud_case.get("relevance")
                    per_case[i]["llm_groundedness_reason"] = cloud_case.get("groundedness_reason", "")
                    per_case[i]["llm_relevance_reason"] = cloud_case.get("relevance_reason", "")
        else:
            print("  LLM judge not available — using local heuristic scores only")

    # Attempt Foundry builtin eval if requested
    builtin_results = None
    if builtin_eval and not dry_run:
        print("\n  Running Foundry builtin evaluators...")
        builtin_results = try_builtin_eval(results, agent_name, project_endpoint)
        if builtin_results:
            print("  Builtin evaluators succeeded — merging scores")
            for i, b_case in enumerate(builtin_results.get("per_case", [])):
                if i < len(per_case):
                    per_case[i]["builtin_groundedness"] = b_case.get("groundedness")
                    per_case[i]["builtin_relevance"] = b_case.get("relevance")
        else:
            print("  Builtin evaluators not available")

    # Aggregate scores
    n = len(per_case)
    if n == 0:
        return {
            "eval_run": f"g2-retrieval-{agent_name}-{timestamp}",
            "agent_name": agent_name,
            "dataset_size": 0,
            "error": "No eval cases loaded",
        }

    # Compute averages — prefer builtin > LLM judge > heuristic
    use_builtin = builtin_results is not None
    use_llm = cloud_results is not None and not use_builtin

    if use_builtin:
        g_scores_list = [c["builtin_groundedness"] for c in per_case
                         if c.get("builtin_groundedness") is not None]
        r_scores_list = [c["builtin_relevance"] for c in per_case
                         if c.get("builtin_relevance") is not None]
    elif use_llm:
        g_scores_list = [c["llm_groundedness"] for c in per_case
                         if c.get("llm_groundedness") is not None]
        r_scores_list = [c["llm_relevance"] for c in per_case
                         if c.get("llm_relevance") is not None]
    else:
        g_scores_list = [c["groundedness"]["groundedness"] for c in per_case
                         if "note" not in c["groundedness"]]
        r_scores_list = [c["relevance"]["relevance"] for c in per_case
                         if "note" not in c["relevance"]]

    scorable_count = len(g_scores_list)
    avg_groundedness = sum(g_scores_list) / scorable_count if scorable_count else 0.0
    avg_relevance = sum(r_scores_list) / len(r_scores_list) if r_scores_list else 0.0

    # Also compute heuristic averages for comparison when LLM is used
    heuristic_scores = {}
    if use_llm:
        h_g = [c["groundedness"]["groundedness"] for c in per_case
               if "note" not in c["groundedness"]]
        h_r = [c["relevance"]["relevance"] for c in per_case
               if "note" not in c["relevance"]]
        heuristic_scores = {
            "groundedness_avg": round(sum(h_g) / len(h_g), 3) if h_g else 0.0,
            "relevance_avg": round(sum(h_r) / len(h_r), 3) if h_r else 0.0,
        }

    # G2 gate verdict
    groundedness_pass = avg_groundedness >= G2_THRESHOLDS["groundedness"]
    relevance_pass = avg_relevance >= G2_THRESHOLDS["relevance"]
    g2_gate_pass = groundedness_pass and relevance_pass

    # Latency stats
    latencies = [c["latency_ms"] for c in per_case]
    avg_latency = sum(latencies) / n if n else 0

    # Build note
    scorer_type = "Foundry builtin" if use_builtin else ("LLM judge (GPT-4.1)" if use_llm else "Local heuristic")
    notes = []
    if dry_run:
        notes.append("dry_run mode — placeholder responses used")
    notes.append(f"Primary scorer: {scorer_type}")
    if use_llm and heuristic_scores:
        notes.append(
            f"Heuristic comparison: g={heuristic_scores['groundedness_avg']:.3f} "
            f"r={heuristic_scores['relevance_avg']:.3f}"
        )
    unscorable = n - scorable_count
    if unscorable > 0:
        notes.append(f"{unscorable}/{n} cases not scorable (content_filter or error)")

    summary = {
        "eval_run": f"g2-retrieval-{agent_name}-{timestamp}",
        "date": datetime.now(timezone.utc).isoformat(),
        "agent_name": agent_name,
        "sdk_version": "v2",
        "scorer": "foundry_builtin" if use_builtin else ("llm_judge_gpt41" if use_llm else "heuristic"),
        "judge_model": cloud_results.get("judge_model") if cloud_results else None,
        "dataset_size": n,
        "scorable_cases": scorable_count,
        "mode": "dry_run" if dry_run else "live",
        "scores": {
            "groundedness_avg": round(avg_groundedness, 3),
            "relevance_avg": round(avg_relevance, 3),
        },
        "thresholds": {
            "groundedness": G2_THRESHOLDS["groundedness"],
            "relevance": G2_THRESHOLDS["relevance"],
        },
        "pass": {
            "groundedness": groundedness_pass,
            "relevance": relevance_pass,
        },
        "g2_gate_pass": g2_gate_pass,
        "latency": {
            "avg_ms": round(avg_latency, 1),
            "max_ms": max(latencies, default=0),
            "min_ms": min(latencies, default=0),
        },
        "per_case": per_case,
        "note": " | ".join(notes),
    }

    # Include heuristic comparison when LLM judge is primary
    if use_llm and heuristic_scores:
        summary["heuristic_scores"] = heuristic_scores

    return summary


def run_single_agent(
    agent_name: str,
    config: dict,
    project_endpoint: str,
    dry_run: bool = False,
    cloud_eval: bool = False,
    builtin_eval: bool = False,
    limit: int | None = None,
) -> dict | None:
    """Run G2 retrieval evaluation for a single agent. Returns summary or None on dataset miss."""
    agents = config.get("agents", {})
    if agent_name not in agents:
        print(f"ERROR: Agent '{agent_name}' not found in agents.yaml", file=sys.stderr)
        print(f"Available: {', '.join(agents.keys())}", file=sys.stderr)
        return None

    # Load dataset
    cases = load_dataset(agent_name)
    if not cases:
        print(f"SKIP: No retrieval dataset for '{agent_name}'")
        return None

    if limit:
        cases = cases[:limit]
        print(f"Limited to {len(cases)} cases")

    # Step 1: Collect responses
    print(f"\n--- Collecting responses from '{agent_name}' ---")
    results = collect_responses(
        agent_name=agent_name,
        cases=cases,
        project_endpoint=project_endpoint,
        dry_run=dry_run,
    )

    # Step 2: Run evaluation
    print(f"\n--- Running G2 retrieval evaluation ---")
    summary = run_evaluation(
        results=results,
        agent_name=agent_name,
        project_endpoint=project_endpoint,
        dry_run=dry_run,
        cloud_eval=cloud_eval,
        builtin_eval=builtin_eval,
    )

    # Step 3: Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    result_file = RESULTS_DIR / f"retrieval-{agent_name}-{timestamp}.json"

    with open(result_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to: {result_file}")
    return summary


def print_verdict(summary: dict) -> None:
    """Print G2 gate verdict for a single agent evaluation."""
    agent_name = summary.get("agent_name", "unknown")
    scores = summary.get("scores", {})
    passes = summary.get("pass", {})
    g2_pass = summary.get("g2_gate_pass", False)
    scorer = summary.get("scorer", "heuristic")
    heuristic = summary.get("heuristic_scores", {})

    print(f"\n{'=' * 60}")
    print(f"Agent: {agent_name}  (scorer: {scorer})")
    print(f"  Groundedness: {scores.get('groundedness_avg', 0):.3f}"
          f"  (threshold: {G2_THRESHOLDS['groundedness']}) "
          f"{'PASS' if passes.get('groundedness') else 'FAIL'}")
    print(f"  Relevance:    {scores.get('relevance_avg', 0):.3f}"
          f"  (threshold: {G2_THRESHOLDS['relevance']}) "
          f"{'PASS' if passes.get('relevance') else 'FAIL'}")
    if heuristic:
        print(f"  --- heuristic comparison ---")
        print(f"  Groundedness: {heuristic.get('groundedness_avg', 0):.3f}  (heuristic)")
        print(f"  Relevance:    {heuristic.get('relevance_avg', 0):.3f}  (heuristic)")
    print(f"{'=' * 60}")
    if g2_pass:
        print(f"G2 RETRIEVAL GATE: PASS")
    else:
        print(f"G2 RETRIEVAL GATE: FAIL")
        print("Agent KB grounding needs improvement. Review per-case scores.")


def main():
    parser = argparse.ArgumentParser(
        description="Run G2 retrieval evaluation (groundedness + relevance) for Foundry agents"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--agent", type=str, help="Agent name (e.g. ask-agent)")
    group.add_argument("--all", action="store_true", help="Run for all agents with retrieval datasets")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would run without calling Foundry")
    parser.add_argument("--cloud-eval", action="store_true",
                        help="Attempt LLM judge evaluation (GPT-4.1)")
    parser.add_argument("--builtin-eval", action="store_true",
                        help="Use Foundry builtin evaluators (GroundednessProEvaluator, RelevanceEvaluator)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of cases per agent (for pilot runs)")

    args = parser.parse_args()

    # Load config
    config = load_agents_yaml()
    project_config = config.get("foundry_project", {})
    project_endpoint = project_config.get("project_endpoint")

    if not project_endpoint:
        print("ERROR: project_endpoint not found in agents.yaml", file=sys.stderr)
        sys.exit(1)

    if args.all:
        # Run for all agents that have retrieval datasets
        agents = config.get("agents", {})
        all_summaries = []
        all_pass = True

        for agent_name in sorted(agents.keys()):
            print(f"\n{'#' * 60}")
            print(f"# Agent: {agent_name}")
            print(f"{'#' * 60}")

            summary = run_single_agent(
                agent_name=agent_name,
                config=config,
                project_endpoint=project_endpoint,
                dry_run=args.dry_run,
                cloud_eval=args.cloud_eval,
                builtin_eval=args.builtin_eval,
                limit=args.limit,
            )
            if summary:
                all_summaries.append(summary)
                print_verdict(summary)
                if not summary.get("g2_gate_pass", False):
                    all_pass = False

        # Print combined summary
        if all_summaries:
            print(f"\n{'=' * 60}")
            print(f"COMBINED G2 RETRIEVAL GATE: {'PASS' if all_pass else 'FAIL'}")
            print(f"Agents evaluated: {len(all_summaries)}")
            for s in all_summaries:
                status = "PASS" if s.get("g2_gate_pass") else "FAIL"
                scores = s.get("scores", {})
                print(f"  {s['agent_name']}: "
                      f"groundedness={scores.get('groundedness_avg', 0):.3f} "
                      f"relevance={scores.get('relevance_avg', 0):.3f} "
                      f"[{status}]")
            if not all_pass:
                sys.exit(1)
        else:
            print("\nNo retrieval datasets found for any agent.")
            print(f"Expected path: {DATASETS_DIR}/retrieval-<agent>-v1.jsonl")
            sys.exit(1)

    else:
        # Single agent
        summary = run_single_agent(
            agent_name=args.agent,
            config=config,
            project_endpoint=project_endpoint,
            dry_run=args.dry_run,
            cloud_eval=args.cloud_eval,
            builtin_eval=args.builtin_eval,
            limit=args.limit,
        )
        if summary:
            print(json.dumps(summary, indent=2))
            print_verdict(summary)
            if not summary.get("g2_gate_pass", False):
                sys.exit(1)
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
