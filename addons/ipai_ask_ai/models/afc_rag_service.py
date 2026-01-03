# -*- coding: utf-8 -*-
"""
AFC RAG Service Integration

Integrates the AFC Close Manager RAG system (document chunks + embeddings)
with the Odoo AI assistant for intelligent financial compliance queries.
"""

import json
import logging
import os
from typing import List, Dict, Any, Optional

import psycopg2
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AfcRagService(models.AbstractModel):
    """
    AFC RAG (Retrieval-Augmented Generation) Service

    Provides semantic search capabilities over the AFC knowledge base
    using pgvector embeddings stored in Supabase.
    """
    _name = "afc.rag.service"
    _description = "AFC RAG Service"

    @api.model
    def semantic_search(self, query: str, top_k: int = 5, company_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Perform semantic search over AFC document chunks.

        Args:
            query: User's natural language question
            top_k: Number of top results to return (default 5)
            company_id: Optional company filter for multi-tenant isolation

        Returns:
            List[Dict]: Top matching document chunks with similarity scores
        """
        # Get database connection parameters
        db_config = self._get_supabase_connection()

        try:
            # Generate query embedding (requires external API call)
            query_embedding = self._generate_embedding(query)

            # Execute vector similarity search
            results = self._execute_vector_search(
                db_config,
                query_embedding,
                top_k,
                company_id
            )

            _logger.info(
                "AFC RAG search for '%s' returned %d results",
                query[:50],
                len(results)
            )

            return results

        except Exception as e:
            _logger.exception("AFC RAG semantic search failed: %s", str(e))
            return []

    @api.model
    def query_knowledge_base(self, question: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Query the AFC knowledge base and return enriched response.

        Args:
            question: User's question about AFC/BIR compliance
            context: Optional context (company_id, employee_code, etc.)

        Returns:
            Dict with:
                - answer: AI-generated response
                - sources: List of source document chunks
                - confidence: Confidence score (0-1)
        """
        context = context or {}
        company_id = context.get("company_id") or self.env.company.id

        # 1. Retrieve relevant document chunks
        chunks = self.semantic_search(question, top_k=5, company_id=company_id)

        if not chunks:
            return {
                "answer": _("I don't have enough information about that topic in my knowledge base."),
                "sources": [],
                "confidence": 0.0,
            }

        # 2. Build context from retrieved chunks
        knowledge_context = self._build_context_from_chunks(chunks)

        # 3. Generate answer using retrieved context
        # Note: This requires integration with Claude/OpenAI API
        answer = self._generate_answer(question, knowledge_context, context)

        # 4. Calculate confidence based on similarity scores
        avg_similarity = sum(c.get("similarity", 0) for c in chunks) / len(chunks)
        confidence = min(avg_similarity, 1.0)

        return {
            "answer": answer,
            "sources": [
                {
                    "content": c.get("content", "")[:200] + "...",
                    "source": c.get("source", "Unknown"),
                    "similarity": c.get("similarity", 0),
                }
                for c in chunks
            ],
            "confidence": confidence,
        }

    @api.model
    def _get_supabase_connection(self) -> Dict[str, str]:
        """Get Supabase database connection parameters from environment."""
        # Try to get from Odoo config parameters first
        ICP = self.env["ir.config_parameter"].sudo()

        db_host = ICP.get_param("afc.supabase.db_host") or os.getenv("POSTGRES_HOST")
        db_name = ICP.get_param("afc.supabase.db_name") or os.getenv("POSTGRES_DATABASE", "postgres")
        db_user = ICP.get_param("afc.supabase.db_user") or os.getenv("POSTGRES_USER", "postgres")
        db_password = ICP.get_param("afc.supabase.db_password") or os.getenv("POSTGRES_PASSWORD")
        db_port = ICP.get_param("afc.supabase.db_port") or os.getenv("POSTGRES_PORT", "5432")

        if not all([db_host, db_password]):
            raise UserError(_(
                "AFC RAG service not configured. "
                "Please set Supabase connection parameters in System Parameters "
                "or environment variables."
            ))

        return {
            "host": db_host,
            "database": db_name,
            "user": db_user,
            "password": db_password,
            "port": db_port,
        }

    @api.model
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for text.

        Args:
            text: Input text to embed

        Returns:
            List[float]: 1536-dimensional embedding vector

        Note:
            This requires OpenAI API integration.
            For now, returns placeholder. Implement actual embedding generation.
        """
        # TODO: Integrate with OpenAI text-embedding-3-large
        # or use local embedding model

        # Placeholder: Return zero vector (this will not work for actual search)
        _logger.warning(
            "AFC RAG using placeholder embeddings. "
            "Integrate OpenAI API for actual semantic search."
        )
        return [0.0] * 1536

    @api.model
    def _execute_vector_search(
        self,
        db_config: Dict[str, str],
        query_embedding: List[float],
        top_k: int,
        company_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute pgvector similarity search in Supabase.

        Args:
            db_config: Database connection parameters
            query_embedding: Query embedding vector
            top_k: Number of results to return
            company_id: Optional company filter

        Returns:
            List[Dict]: Matching chunks with similarity scores
        """
        conn = None
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            # Build SQL query with vector similarity
            # Note: Uses cosine similarity via <=> operator in pgvector
            query = """
                SELECT
                    dc.id,
                    dc.content,
                    dc.source,
                    dc.metadata,
                    ce.embedding <=> %s::vector AS similarity
                FROM afc.document_chunks dc
                JOIN afc.chunk_embeddings ce ON ce.chunk_id = dc.id
                WHERE 1=1
            """
            params = [str(query_embedding)]

            # Add company filter if provided
            if company_id:
                query += " AND (dc.metadata->>'company_id')::int = %s"
                params.append(company_id)

            query += """
                ORDER BY similarity ASC
                LIMIT %s
            """
            params.append(top_k)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "content": row[1],
                    "source": row[2],
                    "metadata": row[3],
                    "similarity": float(row[4]),
                })

            return results

        except Exception as e:
            _logger.exception("Vector search execution failed: %s", str(e))
            return []
        finally:
            if conn:
                conn.close()

    @api.model
    def _build_context_from_chunks(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Build context string from retrieved document chunks.

        Args:
            chunks: List of document chunks with content and metadata

        Returns:
            str: Formatted context for LLM prompt
        """
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.get("source", "Unknown")
            content = chunk.get("content", "")
            context_parts.append(f"[Source {i}: {source}]\n{content}\n")

        return "\n---\n".join(context_parts)

    @api.model
    def _generate_answer(
        self,
        question: str,
        knowledge_context: str,
        user_context: Dict[str, Any]
    ) -> str:
        """
        Generate answer using retrieved knowledge and LLM.

        Args:
            question: User's question
            knowledge_context: Retrieved document chunks
            user_context: User/company context

        Returns:
            str: AI-generated answer

        Note:
            This requires Claude/OpenAI API integration.
            For now, returns knowledge context directly.
        """
        # TODO: Integrate with Claude 3.5 Sonnet or GPT-4
        # Use prompt template:
        # System: "You are an AFC finance close assistant expert in Philippine BIR compliance..."
        # Context: {knowledge_context}
        # Question: {question}

        # Placeholder: Return formatted knowledge context
        return _(
            "Based on the AFC knowledge base:\n\n"
            "{context}\n\n"
            "To answer your question more precisely, "
            "please integrate Claude/OpenAI API for answer generation."
        ).format(context=knowledge_context[:500])

    @api.model
    def health_check(self) -> Dict[str, Any]:
        """
        Check AFC RAG service health.

        Returns:
            Dict with:
                - status: 'ok' or 'error'
                - chunk_count: Number of document chunks
                - embedding_count: Number of embeddings
                - message: Status message
        """
        try:
            db_config = self._get_supabase_connection()
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            # Count chunks and embeddings
            cursor.execute("SELECT COUNT(*) FROM afc.document_chunks")
            chunk_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM afc.chunk_embeddings")
            embedding_count = cursor.fetchone()[0]

            conn.close()

            return {
                "status": "ok",
                "chunk_count": chunk_count,
                "embedding_count": embedding_count,
                "message": _(
                    "AFC RAG service healthy. "
                    "{chunks} chunks with {embeddings} embeddings available."
                ).format(chunks=chunk_count, embeddings=embedding_count),
            }

        except Exception as e:
            _logger.exception("AFC RAG health check failed: %s", str(e))
            return {
                "status": "error",
                "chunk_count": 0,
                "embedding_count": 0,
                "message": _("AFC RAG service unavailable: {error}").format(error=str(e)),
            }
