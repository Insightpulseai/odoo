"""
index_corpus.py — Seed AI Search (srch-ipai-dev) with the PrismaLab RAG corpus.

Populates the index with:
  1. The two registered research skills (doing-meta-analysis-r, prisma2020-flow-diagram)
     — pulled straight from agents/skills/research/*/SKILL.md
  2. PRISMA 2020 checklist (Haddaway 2022 citation)
  3. Cochrane Handbook chapter headings (public ToC)
  4. Harrer et al. (2021) meta-analysis chapter list (public ToC)

Embeddings via Foundry-hosted text-embedding-3-large (keyless).

Idempotent: drops + recreates the index each run.

Usage:
  python scripts/index_corpus.py \
    --search-endpoint https://srch-ipai-dev.search.windows.net \
    --foundry-endpoint https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot

Prerequisites:
  pip install azure-search-documents azure-identity azure-ai-inference
  az login
  Azure AI User role on Foundry + Search Service Contributor on srch-ipai-dev
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import textwrap
from pathlib import Path
from typing import List

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchAlgorithmMetric,
    VectorSearchProfile,
)

INDEX_NAME = "prismalab-rag-v1"
EMBEDDING_MODEL = "text-embedding-3-small"  # deployed on ipai-copilot-resource
EMBEDDING_DIM = 1536  # text-embedding-3-small
CHUNK_SIZE_CHARS = 1800  # generous for methodology docs


def _embed(client, text: str) -> List[float]:
    resp = client.embeddings.create(input=[text], model=EMBEDDING_MODEL)
    return resp.data[0].embedding


def _chunk(text: str, size: int = CHUNK_SIZE_CHARS) -> List[str]:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, buf = [], ""
    for p in paras:
        if len(buf) + len(p) + 2 <= size:
            buf = (buf + "\n\n" + p) if buf else p
        else:
            if buf:
                chunks.append(buf)
            buf = p
    if buf:
        chunks.append(buf)
    return chunks or [text]


def _doc_id(source: str, chunk_idx: int) -> str:
    h = hashlib.sha1(f"{source}:{chunk_idx}".encode()).hexdigest()[:16]
    return f"{source.replace('/', '_').replace('.', '_')}_{chunk_idx}_{h}"


def _build_index(index_client: SearchIndexClient) -> None:
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name="title", type=SearchFieldDataType.String, sortable=True, filterable=True),
        SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
        SimpleField(name="source", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="url", type=SearchFieldDataType.String, filterable=False),
        SimpleField(name="citation", type=SearchFieldDataType.String, filterable=False),
        SearchField(
            name="contentVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=EMBEDDING_DIM,
            vector_search_profile_name="hnsw-profile",
        ),
    ]

    vector_search = VectorSearch(
        profiles=[VectorSearchProfile(name="hnsw-profile", algorithm_configuration_name="hnsw-config")],
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-config",
                parameters=HnswParameters(metric=VectorSearchAlgorithmMetric.COSINE),
            )
        ],
    )

    idx = SearchIndex(name=INDEX_NAME, fields=fields, vector_search=vector_search)
    # Drop + recreate (idempotent)
    try:
        index_client.delete_index(INDEX_NAME)
        print(f"  dropped existing index {INDEX_NAME}")
    except Exception:
        pass
    index_client.create_index(idx)
    print(f"  created index {INDEX_NAME}")


def _load_skill_docs(skills_dir: Path) -> List[dict]:
    docs = []
    for skill_md in skills_dir.glob("*/SKILL.md"):
        text = skill_md.read_text()
        docs.append({
            "title": f"Skill: {skill_md.parent.name}",
            "content": text,
            "source": f"agents/skills/research/{skill_md.parent.name}",
            "url": "",
            "citation": "IPAI Research Skills — registry v1.7 (2026-04-12)",
        })
    return docs


def _builtin_docs() -> List[dict]:
    return [
        {
            "title": "PRISMA 2020 Statement — core principles",
            "content": textwrap.dedent("""
            PRISMA 2020 is an evidence-based minimum set of items for reporting in systematic reviews.
            The flow diagram has four phases: Identification, Screening, Eligibility, and Included.

            The two-arm layout is used for new systematic reviews with database + register searches.
            The three-arm layout adds a "Previous studies" arm (for updates) and an "Other methods" arm
            (for studies identified outside database searches, e.g. citation tracking, hand-searching).

            Core counts for the two-arm diagram:
              - Records identified: from databases + registers
              - Duplicates removed: subtract before screening
              - Records screened by title/abstract (with excluded count)
              - Full-texts assessed for eligibility (with excluded count + reasons)
              - Studies included in the review

            When I² exceeds 75%, heterogeneity is considered substantial and should be investigated
            via subgroup analysis, meta-regression, or narrative synthesis rather than pooled.

            Citation: Haddaway NR, Page MJ, Pritchard CC, McGuinness LA (2022). PRISMA2020: An R package
            and Shiny app for producing PRISMA 2020-compliant flow diagrams. Campbell Systematic Reviews,
            18, e1230. https://doi.org/10.1002/cl2.1230
            """).strip(),
            "source": "builtin/prisma2020",
            "url": "https://www.prisma-statement.org/",
            "citation": "Haddaway et al. (2022) Campbell Systematic Reviews 18:e1230",
        },
        {
            "title": "Cochrane Handbook — evidence synthesis principles",
            "content": textwrap.dedent("""
            The Cochrane Handbook for Systematic Reviews of Interventions codifies methodology for
            evidence synthesis. Key chapters relevant to PrismaLab users:

              - Chapter 4: Searching for studies (PRESS peer-review guidelines)
              - Chapter 5: Collecting data (dual independent extraction)
              - Chapter 7: Considering bias and conflicts of interest (RoB 2 tool for RCTs)
              - Chapter 10: Analysing data and undertaking meta-analyses
              - Chapter 12: Synthesising and presenting findings using other methods (narrative)
              - Chapter 14: Completing 'Summary of findings' tables and GRADE assessments
              - Chapter 15: Interpreting results and drawing conclusions

            For observational studies, ROBINS-I replaces RoB 2. For diagnostic test accuracy,
            use QUADAS-2.

            For the Philippines context (PrismaLab R&D, BIR entity -00002), Cochrane Philippines
            is hosted by the University of the Philippines Manila.
            """).strip(),
            "source": "builtin/cochrane-handbook",
            "url": "https://training.cochrane.org/handbook",
            "citation": "Higgins JPT, Thomas J, Chandler J, et al. (eds.). Cochrane Handbook v6.5",
        },
        {
            "title": "Doing Meta-Analysis in R — pipeline summary",
            "content": textwrap.dedent("""
            Harrer et al. (2021) provides the canonical R-based meta-analysis pipeline:

              1. Effect size calculation via metafor::escalc() — SMD, OR, HR, RR
              2. Pooling via meta::metagen/metabin/metacont/metacor — default REML random-effects
              3. Heterogeneity — tau-squared, I-squared, prediction interval (always report)
              4. Forest + funnel plots — meta::forest(), funnel()
              5. Subgroup analysis — update.meta(subgroup=) when I-squared > 50%
              6. Meta-regression — metafor::rma() with moderators
              7. Publication bias — Egger's test (metabias), trim-and-fill (trimfill),
                 PET-PEESE, p-curve (dmetar::pcurve)
              8. Network meta-analysis (NMA) — netmeta::netmeta(), SUCRA via netrank()
              9. Bayesian meta-analysis — brms::brm(bf(yi | se(sei) ~ 1 + (1|study)))
             10. Risk of Bias (RoB 2) plots via robvis

            High heterogeneity (I-squared > 75%) should trigger subgroup or meta-regression
            before or instead of pooled estimates.

            Citation: Harrer M, Cuijpers P, Furukawa TA, Ebert DD (2021). Doing Meta-Analysis with R:
            A Hands-On Guide. Chapman & Hall/CRC Press. ISBN 978-0-367-61007-4.
            """).strip(),
            "source": "builtin/harrer-meta-analysis",
            "url": "https://bookdown.org/MathiasHarrer/Doing_Meta_Analysis_in_R/",
            "citation": "Harrer et al. (2021). Doing Meta-Analysis with R.",
        },
        {
            "title": "Review types — taxonomy",
            "content": textwrap.dedent("""
            Common evidence synthesis review types:

              - Systematic review — exhaustive search, risk-of-bias assessment, meta-analysis optional.
                Reporting: PRISMA 2020. Typical duration: 6–18 months, team 3–5.
              - Rapid review — accelerated systematic review (3–6 months) with scope trade-offs.
                Reporting: PRISMA-RR or full PRISMA 2020 with rapid-review statement.
              - Scoping review — maps the literature on a broad topic; no formal risk-of-bias.
                Reporting: PRISMA-ScR. Typical duration: 3–9 months.
              - Living review — continuously updated synthesis on a high-velocity topic.
              - Umbrella review (overview of reviews) — synthesis of existing systematic reviews.
              - Realist review — explores "what works, for whom, in what contexts, why."
                Reporting: RAMESES.
              - Mixed-methods systematic review — combines qualitative + quantitative evidence.
                Reporting: JBI convergent integrated or segregated approach.
              - Meta-analysis (quantitative synthesis) — statistical pooling inside a systematic review.
              - Network meta-analysis (NMA) — pools direct and indirect comparisons across interventions.

            Diagnostic test accuracy reviews use QUADAS-2; economic evaluation reviews use CHEC/Drummond;
            qualitative syntheses use ENTREQ.
            """).strip(),
            "source": "builtin/review-taxonomy",
            "url": "https://synthesismanual.jbi.global/",
            "citation": "JBI Manual for Evidence Synthesis (2024); Munn et al. 2018 BMC Med Res Methodol",
        },
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--search-endpoint", required=True)
    ap.add_argument("--foundry-endpoint", required=True, help="e.g. https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot")
    ap.add_argument("--skills-dir", default=None, help="Path to agents/skills/research/")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    skills_dir = Path(args.skills_dir) if args.skills_dir else repo_root / "agents" / "skills" / "research"
    if not skills_dir.exists():
        print(f"[ERROR] skills dir not found: {skills_dir}", file=sys.stderr)
        return 2

    cred = DefaultAzureCredential()

    # 1) Index
    idx_client = SearchIndexClient(endpoint=args.search_endpoint, credential=cred)
    print(f"[1/4] Creating index {INDEX_NAME} at {args.search_endpoint}")
    _build_index(idx_client)

    # 2) Embeddings client (Azure OpenAI-compatible endpoint, Entra auth, no keys)
    try:
        from openai import AzureOpenAI
        from azure.identity import get_bearer_token_provider
    except ImportError:
        print("pip install openai azure-identity", file=sys.stderr)
        return 3

    token_provider = get_bearer_token_provider(
        cred, "https://cognitiveservices.azure.com/.default"
    )
    emb_client = AzureOpenAI(
        azure_endpoint="https://ipai-copilot-resource.openai.azure.com",
        azure_ad_token_provider=token_provider,
        api_version="2024-10-21",
    )

    # 3) Gather docs
    print(f"[2/4] Loading docs")
    docs = _load_skill_docs(skills_dir) + _builtin_docs()
    print(f"  loaded {len(docs)} source docs")

    # 4) Chunk + embed + upload
    print(f"[3/4] Chunking + embedding")
    search_client = SearchClient(endpoint=args.search_endpoint, index_name=INDEX_NAME, credential=cred)
    batch = []
    for d in docs:
        chunks = _chunk(d["content"])
        for i, ch in enumerate(chunks):
            emb = _embed(emb_client, ch)
            batch.append({
                "id": _doc_id(d["source"], i),
                "title": d["title"],
                "content": ch,
                "source": d["source"],
                "url": d["url"],
                "citation": d["citation"],
                "contentVector": emb,
            })

    print(f"[4/4] Uploading {len(batch)} chunks")
    # Batch in 100s
    for i in range(0, len(batch), 100):
        result = search_client.upload_documents(documents=batch[i:i+100])
        succeeded = sum(1 for r in result if r.succeeded)
        print(f"  batch {i//100 + 1}: {succeeded}/{len(result)} succeeded")

    print(f"\n✓ Index {INDEX_NAME} ready with {len(batch)} chunks from {len(docs)} sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
