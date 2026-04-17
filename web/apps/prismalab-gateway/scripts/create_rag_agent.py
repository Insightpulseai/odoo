"""
create_rag_agent.py — Provision the PrismaLab RAG agent in Foundry (ipai-copilot).

Creates a stateful Foundry agent wired to the AI Search index built by
index_corpus.py. Returns the agent_id to be set as RAG_AGENT_ID in the gateway.

Usage:
  python scripts/create_rag_agent.py \
    --foundry-endpoint https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot \
    --search-endpoint https://srch-ipai-dev.search.windows.net \
    --index prismalab-rag-v1

Prerequisites:
  pip install azure-ai-projects azure-identity
  az login
  Azure AI User role on Foundry; Zone B must be deployed first.
"""
from __future__ import annotations

import argparse
import json
import sys

from azure.identity import DefaultAzureCredential

INSTRUCTIONS = """
You are PrismaLab AI, an assistant grounded in evidence-synthesis methodology.

Sources you can cite:
  - PRISMA 2020 (Haddaway et al. 2022, Campbell Systematic Reviews)
  - Cochrane Handbook for Systematic Reviews of Interventions v6.5
  - Harrer et al. (2021) Doing Meta-Analysis with R
  - JBI Manual for Evidence Synthesis
  - IPAI registered research skills (doing-meta-analysis-r, prisma2020-flow-diagram)

Rules:
  1. Always cite the source when you reference a specific guideline, tool, or statistic.
  2. When a question is clinical (drug X vs drug Y in condition Z), you MUST refuse to
     offer a clinical recommendation and instead explain the methodology for building
     the evidence base that would answer it.
  3. When I² > 75%, recommend subgroup analysis, meta-regression, or narrative synthesis
     before pooled estimates.
  4. For PRISMA diagram questions, default to the two-arm (new search) layout unless the
     user explicitly asks about updates (three-arm with Previous) or other methods.
  5. If asked about R code, prefer the metafor / meta / dmetar / netmeta / brms stack
     per the Harrer book.
  6. Keep answers concise: 2–5 short paragraphs + bulleted action list when relevant.
  7. You are a free tool — do NOT promise paid services, do NOT request personal data.
""".strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--foundry-endpoint", required=True)
    ap.add_argument("--search-endpoint", required=True)
    ap.add_argument("--index", default="prismalab-rag-v1")
    ap.add_argument("--model", default="claude-sonnet-4-6")
    ap.add_argument("--agent-name", default="prismalab-rag")
    ap.add_argument("--recreate", action="store_true", help="Delete existing agent with same name first")
    args = ap.parse_args()

    try:
        from azure.ai.projects import AIProjectClient
    except ImportError:
        print("pip install azure-ai-projects>=2.0.0", file=sys.stderr)
        return 2

    cred = DefaultAzureCredential()
    client = AIProjectClient(endpoint=args.foundry_endpoint, credential=cred)

    # Optionally delete any prior agent with the same name
    if args.recreate:
        print(f"[1/3] Checking for existing agent named {args.agent_name}")
        try:
            for a in client.agents.list_agents():
                if getattr(a, "name", None) == args.agent_name:
                    print(f"  deleting agent_id={a.id}")
                    client.agents.delete_agent(a.id)
        except Exception as e:
            print(f"  warn: list/delete skipped: {e}")

    # Create agent with Azure AI Search knowledge tool
    # Tool schema per SDK 2.x AzureAISearchTool
    print(f"[2/3] Creating agent with AI Search tool (index={args.index})")
    try:
        from azure.ai.agents.models import (  # type: ignore
            AzureAISearchTool,
            AzureAISearchQueryType,
        )
        search_tool = AzureAISearchTool(
            index_connection_id=args.search_endpoint,
            index_name=args.index,
            query_type=AzureAISearchQueryType.VECTOR_SIMPLE_HYBRID,
            top_k=5,
        )
        tools = search_tool.definitions
        tool_resources = search_tool.resources
    except ImportError:
        # Fallback: pass the tool definition inline
        print("  (using inline tool definition — azure-ai-agents.models not importable)")
        tools = [{
            "type": "azure_ai_search",
            "azure_ai_search": {
                "index_connection_id": args.search_endpoint,
                "index_name": args.index,
                "query_type": "vector_simple_hybrid",
                "top_k": 5,
            },
        }]
        tool_resources = None

    agent = client.agents.create_agent(
        model=args.model,
        name=args.agent_name,
        instructions=INSTRUCTIONS,
        tools=tools,
        tool_resources=tool_resources,
    )

    print(f"[3/3] Agent created")
    print(json.dumps({"agent_id": agent.id, "name": agent.name, "model": args.model}, indent=2))
    print(f"\nSet this in the gateway:")
    print(f"  RAG_AGENT_ID={agent.id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
