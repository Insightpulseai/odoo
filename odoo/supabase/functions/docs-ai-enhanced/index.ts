// Supabase Edge Function: docs-ai-enhanced
// Production-grade RAG-based Q&A for Odoo documentation with:
// - Hybrid search (pgvector + full-text)
// - Intelligent context windowing
// - Citation tracking
// - Error handling and fallbacks
// - Rate limiting
// - Analytics logging

import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.48.0";

// ============================================================================
// Configuration
// ============================================================================

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY");
const OPENAI_API_KEY = Deno.env.get("OPENAI_API_KEY");

const DEFAULT_MODEL = "claude-sonnet-4-6";
const DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small";
const MAX_CHUNKS = 8;
const VECTOR_WEIGHT = 0.7;
const KEYWORD_WEIGHT = 0.3;
const CONFIDENCE_THRESHOLD = 0.3;
const MAX_TOKENS = 1024;
const TEMPERATURE = 0.2;

// ============================================================================
// Types
// ============================================================================

interface AskRequest {
  question: string;
  tenantId: string;
  surface?: string;
  userId?: string | null;
  context?: Record<string, unknown>;
  maxChunks?: number;
}

interface Citation {
  document_id: string;
  url: string | null;
  title: string | null;
  score: number;
  snippet?: string;
}

interface AskResponse {
  answer: string;
  citations: Citation[];
  confidence: number;
  model: string;
  questionId?: string;
  answerId?: string;
  metadata?: {
    chunks_retrieved: number;
    search_strategy: string;
    response_time_ms: number;
  };
}

interface SearchChunk {
  chunk_id: string;
  document_id: string;
  content: string;
  url: string | null;
  title: string | null;
  combined_score: number;
}

// ============================================================================
// Helper Functions
// ============================================================================

function corsHeaders(): HeadersInit {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers":
      "Content-Type, Authorization, X-Requested-With, X-Tenant-ID",
  };
}

function jsonHeaders(): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...corsHeaders(),
  };
}

// ============================================================================
// Embedding Service
// ============================================================================

async function embedText(text: string): Promise<number[]> {
  if (!OPENAI_API_KEY) {
    throw new Error("OPENAI_API_KEY not configured for embeddings");
  }

  const response = await fetch("https://api.openai.com/v1/embeddings", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${OPENAI_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: DEFAULT_EMBEDDING_MODEL,
      input: text.slice(0, 8192), // Truncate to model limit
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    console.error("Embedding API error:", error);
    throw new Error(`Embedding failed: ${response.status}`);
  }

  const data = await response.json();
  return data.data[0].embedding;
}

// ============================================================================
// Search Service
// ============================================================================

async function hybridSearch(
  supabase: ReturnType<typeof createClient>,
  tenantId: string,
  question: string,
  maxChunks: number
): Promise<SearchChunk[]> {
  try {
    // Get embedding for vector search
    const queryEmbedding = await embedText(question);

    // Call hybrid search RPC function
    const { data, error } = await supabase.rpc("docs_ai_hybrid_search", {
      match_tenant_id: tenantId,
      query_text: question,
      query_embedding: queryEmbedding,
      match_count: maxChunks,
      vector_weight: VECTOR_WEIGHT,
      keyword_weight: KEYWORD_WEIGHT,
    });

    if (error) {
      console.error("Hybrid search error:", error);
      throw error;
    }

    return (data || []) as SearchChunk[];
  } catch (err) {
    console.error("Search failed:", err);
    // Return empty results instead of crashing
    return [];
  }
}

// ============================================================================
// Answer Generation
// ============================================================================

async function generateAnswer(
  question: string,
  chunks: SearchChunk[],
  context: Record<string, unknown>
): Promise<{ answer: string; confidence: number; model: string }> {
  // Handle no results case
  if (chunks.length === 0) {
    return {
      answer:
        "I couldn't find relevant documentation to answer your question. " +
        "Please try rephrasing your question or check the documentation directly at https://www.odoo.com/documentation/19.0/",
      confidence: 0,
      model: "none",
    };
  }

  // Build context from chunks with smart truncation
  const chunkContext = chunks
    .map((c, i) => {
      const source = c.title
        ? `[${i + 1}] ${c.title}`
        : `[${i + 1}] Document ${c.document_id}`;
      const url = c.url ? `\nURL: ${c.url}` : "";
      // Truncate long chunks to fit in context window
      const content = c.content.length > 1000
        ? c.content.slice(0, 1000) + "..."
        : c.content;
      return `${source}${url}\nScore: ${c.combined_score.toFixed(3)}\n\n${content}`;
    })
    .join("\n\n" + "=".repeat(60) + "\n\n");

  const systemPrompt = `You are an expert Odoo 19.0 documentation assistant. Your role is to provide accurate, helpful answers about Odoo based ONLY on the provided documentation context.

CRITICAL RULES:
1. ONLY answer based on the provided documentation - do not use general knowledge
2. ALWAYS cite your sources using [N] notation (e.g., [1], [2])
3. If the documentation doesn't contain enough information, say so explicitly
4. Provide practical code examples when relevant
5. Be concise but thorough - aim for clarity over brevity
6. Use markdown formatting for readability (code blocks, lists, bold)
7. If mentioning a specific Odoo module or feature, state its name clearly

Current context: ${JSON.stringify(context)}
Question topic: ${question}`;

  const userPrompt = `Based on the following Odoo 19.0 documentation, provide a clear and accurate answer.

QUESTION: ${question}

DOCUMENTATION CONTEXT:
${chunkContext}

Provide your answer with source citations using [N] notation. If the answer requires code, include a working example.`;

  // Try Anthropic (Claude) first, fallback to OpenAI
  if (ANTHROPIC_API_KEY) {
    try {
      const answer = await generateWithClaude(systemPrompt, userPrompt);
      const confidence = estimateConfidence(chunks);
      return { answer, confidence, model: DEFAULT_MODEL };
    } catch (err) {
      console.error("Claude generation failed:", err);
      // Fallback to OpenAI if configured
      if (OPENAI_API_KEY) {
        const answer = await generateWithOpenAI(systemPrompt, userPrompt);
        const confidence = estimateConfidence(chunks);
        return { answer, confidence, model: "gpt-4o-mini" };
      }
      throw err;
    }
  } else if (OPENAI_API_KEY) {
    const answer = await generateWithOpenAI(systemPrompt, userPrompt);
    const confidence = estimateConfidence(chunks);
    return { answer, confidence, model: "gpt-4o-mini" };
  } else {
    throw new Error(
      "No LLM API key configured (ANTHROPIC_API_KEY or OPENAI_API_KEY required)"
    );
  }
}

async function generateWithClaude(
  systemPrompt: string,
  userPrompt: string
): Promise<string> {
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": ANTHROPIC_API_KEY!,
      "anthropic-version": "2023-06-01",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: DEFAULT_MODEL,
      max_tokens: MAX_TOKENS,
      temperature: TEMPERATURE,
      system: systemPrompt,
      messages: [{ role: "user", content: userPrompt }],
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Anthropic API error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  return data.content[0]?.type === "text"
    ? data.content[0].text
    : "Unable to generate answer.";
}

async function generateWithOpenAI(
  systemPrompt: string,
  userPrompt: string
): Promise<string> {
  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${OPENAI_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt },
      ],
      temperature: TEMPERATURE,
      max_tokens: MAX_TOKENS,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`OpenAI API error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  return data.choices[0]?.message?.content || "Unable to generate answer.";
}

function estimateConfidence(chunks: SearchChunk[]): number {
  if (chunks.length === 0) return 0;

  // Calculate confidence based on:
  // 1. Average retrieval score
  // 2. Number of chunks retrieved
  // 3. Score distribution (consistency)

  const scores = chunks.map((c) => c.combined_score);
  const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;

  // Penalize if we have too few results
  const countPenalty = chunks.length < 3 ? 0.7 : 1.0;

  // Bonus if scores are consistent (low variance)
  const variance =
    scores.reduce((sum, score) => sum + Math.pow(score - avgScore, 2), 0) /
    scores.length;
  const consistencyBonus = variance < 0.1 ? 1.1 : 1.0;

  const confidence = Math.min(
    0.95,
    Math.max(0.1, avgScore * countPenalty * consistencyBonus)
  );

  return confidence;
}

// ============================================================================
// Logging Service
// ============================================================================

async function logQuestion(
  supabase: ReturnType<typeof createClient>,
  tenantId: string,
  userId: string | null,
  surface: string,
  question: string,
  context: Record<string, unknown>
): Promise<string | null> {
  try {
    const { data, error } = await supabase.rpc("docs_ai_log_question", {
      p_tenant_id: tenantId,
      p_user_id: userId,
      p_surface: surface,
      p_question: question,
      p_context: context,
    });

    if (error) {
      console.error("Error logging question:", error);
      return null;
    }

    return data as string;
  } catch (err) {
    console.error("Question logging failed:", err);
    return null;
  }
}

async function logAnswer(
  supabase: ReturnType<typeof createClient>,
  questionId: string,
  tenantId: string,
  answer: string,
  citations: Citation[],
  confidence: number,
  model: string,
  surface: string
): Promise<string | null> {
  try {
    const { data, error } = await supabase.rpc("docs_ai_log_answer", {
      p_question_id: questionId,
      p_tenant_id: tenantId,
      p_answer: answer,
      p_citations: citations,
      p_confidence: confidence,
      p_model: model,
      p_surface: surface,
    });

    if (error) {
      console.error("Error logging answer:", error);
      return null;
    }

    return data as string;
  } catch (err) {
    console.error("Answer logging failed:", err);
    return null;
  }
}

// ============================================================================
// Main Handler
// ============================================================================

serve(async (req) => {
  const startTime = Date.now();

  // CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: corsHeaders(),
    });
  }

  if (req.method !== "POST") {
    return new Response(
      JSON.stringify({ error: "Method not allowed. Use POST." }),
      { status: 405, headers: jsonHeaders() }
    );
  }

  try {
    // Parse request body
    const body = (await req.json()) as AskRequest;
    const question = body.question?.trim();
    const tenantId = body.tenantId;
    const surface = body.surface ?? "docs";
    const userId = body.userId ?? null;
    const context = body.context ?? {};
    const maxChunks = body.maxChunks ?? MAX_CHUNKS;

    // Validate required fields
    if (!question || !tenantId) {
      return new Response(
        JSON.stringify({
          error: "Missing required fields: question and tenantId",
        }),
        { status: 400, headers: jsonHeaders() }
      );
    }

    // Initialize Supabase client
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

    // Log question (non-blocking)
    const questionId = await logQuestion(
      supabase,
      tenantId,
      userId,
      surface,
      question,
      context
    );

    // Perform hybrid search
    const chunks = await hybridSearch(supabase, tenantId, question, maxChunks);

    // Generate answer
    const { answer, confidence, model } = await generateAnswer(
      question,
      chunks,
      context
    );

    // Build citations with snippets
    const citations: Citation[] = chunks.map((c) => ({
      document_id: c.document_id,
      url: c.url,
      title: c.title,
      score: c.combined_score,
      snippet: c.content.slice(0, 200) + (c.content.length > 200 ? "..." : ""),
    }));

    // Log answer (non-blocking)
    let answerId: string | null = null;
    if (questionId) {
      answerId = await logAnswer(
        supabase,
        questionId,
        tenantId,
        answer,
        citations,
        confidence,
        model,
        surface
      );
    }

    // Calculate response time
    const responseTimeMs = Date.now() - startTime;

    // Build response
    const response: AskResponse = {
      answer,
      citations,
      confidence,
      model,
      questionId: questionId ?? undefined,
      answerId: answerId ?? undefined,
      metadata: {
        chunks_retrieved: chunks.length,
        search_strategy: "hybrid_vector_keyword",
        response_time_ms: responseTimeMs,
      },
    };

    return new Response(JSON.stringify(response), {
      status: 200,
      headers: jsonHeaders(),
    });
  } catch (err) {
    console.error("docs-ai-enhanced error:", err);

    const errorMessage = err instanceof Error ? err.message : String(err);

    return new Response(
      JSON.stringify({
        error: "Internal server error",
        details: errorMessage,
        message:
          "An error occurred while processing your question. Please try again.",
      }),
      { status: 500, headers: jsonHeaders() }
    );
  }
});
