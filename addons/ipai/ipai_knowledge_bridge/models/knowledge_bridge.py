import json
import logging
import os
import time

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

GROUNDING_SYSTEM_PROMPT = """You are a knowledge assistant. Answer the user's question using ONLY the provided source chunks.

Rules:
- Cite sources by [N] where N is the chunk number.
- If no source chunk answers the question, say: "I cannot find this in the registered knowledge sources."
- Do not speculate or infer beyond what the sources state.
- Keep answers concise and factual."""


class KnowledgeBridge(models.AbstractModel):
    _name = "ipai.knowledge.bridge"
    _description = "Knowledge Bridge (Azure AI Search + OpenAI)"

    @api.model
    def query(self, source_code, question, caller_uid=None, caller_surface="direct",
              context_data=None):
        """Query a knowledge source and return a cited answer.

        Returns:
            dict: {answer, citations, confidence, abstained, log_id, error}
        """
        start_ms = int(time.time() * 1000)
        source = self.env["ipai.knowledge.source"].search(
            [("code", "=", source_code), ("state", "=", "active")],
            limit=1,
        )
        if not source:
            return {
                "answer": "",
                "citations": [],
                "confidence": 0.0,
                "abstained": True,
                "log_id": False,
                "error": f"No active source found for code '{source_code}'",
            }

        try:
            search_results = self._call_azure_search(source, question)
        except Exception as e:
            _logger.error("Azure Search call failed: %s", e)
            log = self._create_log(
                source, question, caller_uid, caller_surface,
                error_message=str(e)[:200],
                latency_ms=int(time.time() * 1000) - start_ms,
            )
            return {
                "answer": "",
                "citations": [],
                "confidence": 0.0,
                "abstained": True,
                "log_id": log.id,
                "error": str(e)[:200],
            }

        top_score = max(
            (r.get("@search.rerankerScore", r.get("@search.score", 0))
             for r in search_results),
            default=0,
        )
        # Normalize score to 0-1 range (reranker scores are 0-4)
        top_confidence = min(top_score / 4.0, 1.0) if top_score > 0 else 0.0

        if (top_confidence < source.confidence_threshold
                and source.abstain_below_threshold):
            log = self._create_log(
                source, question, caller_uid, caller_surface,
                top_confidence=top_confidence,
                was_abstained=True,
                latency_ms=int(time.time() * 1000) - start_ms,
            )
            return {
                "answer": "I cannot find a confident answer in the registered knowledge sources.",
                "citations": [],
                "confidence": top_confidence,
                "abstained": True,
                "log_id": log.id,
                "error": False,
            }

        try:
            gen_result = self._call_azure_openai(question, search_results)
        except Exception as e:
            _logger.error("Azure OpenAI call failed: %s", e)
            log = self._create_log(
                source, question, caller_uid, caller_surface,
                top_confidence=top_confidence,
                error_message=str(e)[:200],
                latency_ms=int(time.time() * 1000) - start_ms,
            )
            return {
                "answer": "",
                "citations": [],
                "confidence": top_confidence,
                "abstained": True,
                "log_id": log.id,
                "error": str(e)[:200],
            }

        citations = self._build_citations(search_results, source)
        latency = int(time.time() * 1000) - start_ms

        log = self._create_log(
            source, question, caller_uid, caller_surface,
            answer_text=gen_result.get("answer", ""),
            citations_json=json.dumps(citations),
            top_confidence=top_confidence,
            answer_confidence=top_confidence,
            model_used=gen_result.get("model", ""),
            latency_ms=latency,
        )

        # Create citation records
        Citation = self.env["ipai.knowledge.citation"]
        for i, c in enumerate(citations):
            Citation.create({
                "query_log_id": log.id,
                "rank": i + 1,
                "document_title": c.get("title", ""),
                "document_url": c.get("url", ""),
                "section_heading": c.get("section", ""),
                "chunk_text": c.get("content", ""),
                "score": c.get("score", 0),
                "source_id": source.id,
            })

        return {
            "answer": gen_result.get("answer", ""),
            "citations": citations,
            "confidence": top_confidence,
            "abstained": False,
            "log_id": log.id,
            "error": False,
        }

    @api.model
    def list_sources(self, consumer_tag=None):
        domain = [("state", "=", "active")]
        if consumer_tag:
            domain.append(("consumer_tag", "=", consumer_tag))
        sources = self.env["ipai.knowledge.source"].search(domain)
        return [{"code": s.code, "name": s.name, "type": s.source_type}
                for s in sources]

    def _call_azure_search(self, source, question):
        import requests

        endpoint = self._resolve_search_endpoint()
        api_key = self._resolve_search_key()
        if not endpoint or not api_key:
            raise ValueError("Azure AI Search endpoint or key not configured")

        url = (
            f"{endpoint.rstrip('/')}/indexes/{source.azure_index_name}"
            f"/docs/search?api-version=2024-05-01-preview"
        )
        payload = {
            "search": question,
            "queryType": "semantic",
            "semanticConfiguration": source.azure_semantic_config or "default",
            "captions": "extractive",
            "answers": "extractive",
            "top": source.max_results or 5,
            "select": "id,title,content,section,url,source",
        }
        resp = requests.post(
            url,
            json=payload,
            headers={"api-key": api_key, "Content-Type": "application/json"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("value", [])

    def _call_azure_openai(self, question, chunks):
        import requests

        endpoint = self._resolve_openai_endpoint()
        deployment = self._resolve_openai_deployment()
        api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        if not endpoint or not deployment:
            raise ValueError("Azure OpenAI endpoint or deployment not configured")

        numbered_chunks = "\n\n".join(
            f"[{i+1}] {c.get('title', 'Untitled')}: {c.get('content', '')[:500]}"
            for i, c in enumerate(chunks)
        )
        url = (
            f"{endpoint.rstrip('/')}/openai/deployments/{deployment}"
            f"/chat/completions?api-version=2024-02-01"
        )
        payload = {
            "messages": [
                {"role": "system", "content": GROUNDING_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"{question}\n\nSOURCES:\n{numbered_chunks}",
                },
            ],
            "temperature": 0.0,
            "max_tokens": 800,
        }
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["api-key"] = api_key

        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        choice = data.get("choices", [{}])[0]
        return {
            "answer": choice.get("message", {}).get("content", ""),
            "model": data.get("model", deployment),
        }

    def _build_citations(self, search_results, source):
        citations = []
        for r in search_results:
            citations.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "section": r.get("section", ""),
                "content": r.get("content", "")[:500],
                "score": r.get("@search.rerankerScore",
                              r.get("@search.score", 0)),
            })
        return citations

    def _check_index_health(self, source):
        import requests

        endpoint = self._resolve_search_endpoint()
        api_key = self._resolve_search_key()
        if not endpoint or not api_key:
            source.write({"index_health": "error"})
            return

        url = (
            f"{endpoint.rstrip('/')}/indexes/{source.azure_index_name}"
            f"/stats?api-version=2024-05-01-preview"
        )
        try:
            resp = requests.get(
                url,
                headers={"api-key": api_key},
                timeout=15,
            )
            resp.raise_for_status()
            stats = resp.json()
            source.write({
                "doc_count_estimate": stats.get("documentCount", 0),
                "index_health": "healthy",
                "last_indexed_at": fields.Datetime.now(),
            })
        except Exception as e:
            _logger.warning("Index health check failed for %s: %s",
                            source.code, e)
            source.write({"index_health": "error"})

    def _resolve_search_endpoint(self):
        return self.env["ir.config_parameter"].sudo().get_param(
            "ipai_knowledge.azure_search_endpoint", ""
        )

    def _resolve_search_key(self):
        return os.getenv("AZURE_SEARCH_API_KEY", "")

    def _resolve_openai_endpoint(self):
        return self.env["ir.config_parameter"].sudo().get_param(
            "ipai_knowledge.azure_openai_endpoint", ""
        )

    def _resolve_openai_deployment(self):
        return self.env["ir.config_parameter"].sudo().get_param(
            "ipai_knowledge.azure_openai_deployment", ""
        )

    def _create_log(self, source, question, caller_uid, caller_surface,
                    answer_text="", citations_json="", top_confidence=0,
                    answer_confidence=0, was_abstained=False, model_used="",
                    latency_ms=0, error_message=""):
        return self.env["ipai.knowledge.query.log"].sudo().create({
            "source_id": source.id,
            "query_text": question,
            "answer_text": answer_text,
            "citations_json": citations_json,
            "top_confidence": top_confidence,
            "answer_confidence": answer_confidence,
            "was_abstained": was_abstained,
            "model_used": model_used,
            "latency_ms": latency_ms,
            "caller_uid": caller_uid or self.env.uid,
            "caller_surface": caller_surface,
            "error_message": error_message,
        })
