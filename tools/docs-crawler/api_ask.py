#!/usr/bin/env python3
"""
/api/ask endpoint - Kapa-style RAG with citations
Retrieves relevant chunks via hybrid search, generates answer with citations
"""

import json
import os
from typing import List, Dict, Optional

import requests


class DocsAPI:
    """Kapa-style docs API with hybrid retrieval + citation-first answers"""

    def __init__(
        self,
        supabase_url: str,
        supabase_service_key: str,
        openai_api_key: str,
        tenant_id: str
    ):
        self.supabase_url = supabase_url
        self.supabase_service_key = supabase_service_key
        self.openai_api_key = openai_api_key
        self.tenant_id = tenant_id

    def embed_query(self, query: str) -> List[float]:
        """Generate query embedding using OpenAI"""
        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "text-embedding-3-small",
            "input": query
        }

        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()

        return r.json()['data'][0]['embedding']

    def search_hybrid(
        self,
        query: str,
        query_embedding: List[float],
        top_k: int = 6,
        source_type: Optional[str] = None,
        visibility: str = "internal"
    ) -> List[Dict]:
        """Execute hybrid search RPC on Supabase"""
        url = f"{self.supabase_url}/rest/v1/rpc/search_hybrid"
        headers = {
            "apikey": self.supabase_service_key,
            "Authorization": f"Bearer {self.supabase_service_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "p_tenant_id": self.tenant_id,
            "p_query": query,
            "p_query_embedding": query_embedding,
            "p_top_k": top_k,
            "p_source_type": source_type,
            "p_visibility": visibility
        }

        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()

        return r.json()

    def format_citations(self, chunks: List[Dict]) -> List[Dict]:
        """Format citations in Kapa style"""
        citations = []

        for i, chunk in enumerate(chunks, 1):
            canonical_url = chunk.get('canonical_url', '')
            section_path = chunk.get('section_path', '')
            doc_version = chunk.get('doc_version', '')
            commit_sha = chunk.get('commit_sha', '')

            # Create anchor from section path
            anchor = None
            if section_path:
                anchor = '#' + section_path.lower()\
                    .replace(' ', '-')\
                    .replace('>', '')\
                    .replace('  ', '-')

            citation = {
                'id': i,
                'url': canonical_url,
                'section': section_path,
                'version': doc_version,
                'commit': commit_sha[:7] if commit_sha else None,
                'anchor': anchor,
                'score': chunk.get('score', 0.0)
            }

            citations.append(citation)

        return citations

    def generate_answer(
        self,
        query: str,
        chunks: List[Dict],
        model: str = "gpt-4o-mini"
    ) -> Dict:
        """Generate answer with GPT-4o-mini using retrieved chunks"""
        # Build context from chunks
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            section = chunk.get('section_path', 'Section')
            version = chunk.get('doc_version', 'unknown')
            content = chunk.get('content', '')

            context_parts.append(
                f"[{i}] {section} ({version})\n{content}"
            )

        context = "\n\n---\n\n".join(context_parts)

        # System prompt (Kapa-style)
        system_prompt = """You are a helpful documentation assistant for Odoo CE 18.0 and OCA modules.

Answer the user's question based ONLY on the provided context from official documentation.

Rules:
- Always cite sources using [1], [2], etc. format
- If the answer requires multiple citations, use all relevant ones
- If the context doesn't contain enough information, say "I don't have enough information in the documentation to answer that question."
- Be concise but complete
- Include code examples from the context when relevant
- Mention version numbers when discussing version-specific behavior

Format citations like: "According to the Odoo documentation [1], ..."
"""

        # User prompt
        user_prompt = f"""Context from documentation:

{context}

Question: {query}

Please provide a comprehensive answer with citations."""

        # Call OpenAI
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }

        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()

        response = r.json()
        answer_text = response['choices'][0]['message']['content']

        return {
            "answer": answer_text,
            "model": model,
            "tokens_used": response['usage']['total_tokens']
        }

    def ask(
        self,
        question: str,
        top_k: int = 6,
        source_type: Optional[str] = None,
        visibility: str = "internal"
    ) -> Dict:
        """
        Main /api/ask endpoint handler

        Returns:
        {
            "question": str,
            "answer": str,
            "citations": List[Dict],
            "confidence": float,
            "search_method": "hybrid",
            "model": str,
            "debug": Dict (optional)
        }
        """
        # 1. Embed query
        query_embedding = self.embed_query(question)

        # 2. Hybrid search
        chunks = self.search_hybrid(
            question,
            query_embedding,
            top_k=top_k,
            source_type=source_type,
            visibility=visibility
        )

        # 3. Format citations
        citations = self.format_citations(chunks)

        # 4. Generate answer
        result = self.generate_answer(question, chunks)

        # 5. Calculate confidence (avg search score)
        confidence = sum(c['score'] for c in citations) / len(citations) if citations else 0.0

        return {
            "question": question,
            "answer": result['answer'],
            "citations": citations,
            "confidence": round(confidence, 3),
            "search_method": "hybrid",
            "model": result['model'],
            "tokens_used": result['tokens_used'],
            "debug": {
                "chunks_retrieved": len(chunks),
                "top_sources": [c.get('source_type') for c in chunks[:3]]
            }
        }


def lambda_handler(event, context):
    """
    AWS Lambda / Vercel Function handler
    Expected event body:
    {
        "question": str,
        "top_k": int (optional),
        "source_type": str (optional),
        "visibility": str (optional, default "internal")
    }
    """
    # Parse request
    body = json.loads(event.get('body', '{}'))
    question = body.get('question')

    if not question:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing required field: question"})
        }

    # Get config from environment
    supabase_url = os.environ['SUPABASE_URL']
    supabase_service_key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
    openai_api_key = os.environ['OPENAI_API_KEY']
    tenant_id = os.environ['TENANT_ID']

    # Initialize API
    api = DocsAPI(supabase_url, supabase_service_key, openai_api_key, tenant_id)

    # Execute ask
    try:
        result = api.ask(
            question=question,
            top_k=body.get('top_k', 6),
            source_type=body.get('source_type'),
            visibility=body.get('visibility', 'internal')
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(result)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


# CLI testing
if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--question", required=True, help="Question to ask")
    ap.add_argument("--top-k", type=int, default=6, help="Number of chunks to retrieve")
    ap.add_argument("--source", help="Filter to specific source")
    ap.add_argument("--visibility", default="internal", help="public or internal")
    args = ap.parse_args()

    # Load from environment
    supabase_url = os.environ['SUPABASE_URL']
    supabase_service_key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
    openai_api_key = os.environ['OPENAI_API_KEY']
    tenant_id = os.environ['TENANT_ID']

    api = DocsAPI(supabase_url, supabase_service_key, openai_api_key, tenant_id)

    result = api.ask(
        question=args.question,
        top_k=args.top_k,
        source_type=args.source,
        visibility=args.visibility
    )

    print(json.dumps(result, indent=2))
