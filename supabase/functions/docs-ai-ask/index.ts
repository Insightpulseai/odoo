// Supabase Edge Function: docs-ai-ask
// RAG-based Q&A endpoint for InsightPulse Docs AI

import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.48.0";

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

// LLM Configuration
const OPENAI_API_KEY = Deno.env.get("OPENAI_API_KEY");
const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY");
const DEFAULT_MODEL = Deno.env.get("DOCS_AI_MODEL") || "gpt-4o-mini";
const DEFAULT_EMBEDDING_MODEL = Deno.env.get("DOCS_AI_EMBEDDING_MODEL") || "text-embedding-3-small";

const supabase = createClient(supabaseUrl, supabaseServiceKey);

type AskRequest = {
  question: string;
  tenantId: string;
  surface?: string;
  userId?: string | null;
  context?: Record<string, unknown>;
  sourceFilter?: string[];
  maxChunks?: number;
};

type Citation = {
  document_id: string;
  url: string | null;
  title: string | null;
  score: number;
};

type AskResponse = {
  answer: string;
  citations: Citation[];
  confidence: number;
  questionId?: string;
  answerId?: string;
};

serve(async (req) => {
  // CORS handling
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: corsHeaders(),
    });
  }

  if (req.method !== "POST") {
    return new Response(
      JSON.stringify({ error: "Method not allowed" }),
      { status: 405, headers: jsonHeaders() }
    );
  }

  try {
    const body = (await req.json()) as AskRequest;
    const question = body.question?.trim();
    const tenantId = body.tenantId;
    const surface = body.surface ?? "docs";
    const userId = body.userId ?? null;
    const ctx = body.context ?? {};
    const maxChunks = body.maxChunks ?? 8;

    if (!question || !tenantId) {
      return new Response(
        JSON.stringify({ error: "Missing question or tenantId" }),
        { status: 400, headers: jsonHeaders() }
      );
    }

    // 1) Log the question
    const { data: questionRow, error: qError } = await supabase.rpc(
      "docs_ai_log_question",
      {
        p_tenant_id: tenantId,
        p_user_id: userId,
        p_surface: surface,
        p_question: question,
        p_context: ctx,
      }
    );

    if (qError) {
      console.error("Error logging question:", qError);
    }

    const questionId = questionRow as string | null;

    // 2) Embed the question
    const queryEmbedding = await embedText(question);

    // 3) Hybrid search via RPC
    const { data: matches, error: matchError } = await supabase.rpc(
      "docs_ai_hybrid_search",
      {
        match_tenant_id: tenantId,
        query_text: question,
        query_embedding: queryEmbedding,
        match_count: maxChunks,
        vector_weight: 0.7,
        keyword_weight: 0.3,
      }
    );

    if (matchError) {
      console.error("Hybrid search error:", matchError);
      throw matchError;
    }

    const chunks: {
      chunk_id: string;
      document_id: string;
      content: string;
      url: string | null;
      title: string | null;
      combined_score: number;
    }[] = matches ?? [];

    // 4) Generate answer from chunks
    const { answer, confidence } = await generateAnswer(question, chunks, ctx);

    // 5) Build citations
    const citations: Citation[] = chunks.map((c) => ({
      document_id: c.document_id,
      url: c.url,
      title: c.title,
      score: c.combined_score,
    }));

    // 6) Log the answer
    let answerId: string | null = null;
    if (questionId) {
      const { data: answerRow, error: aError } = await supabase.rpc(
        "docs_ai_log_answer",
        {
          p_question_id: questionId,
          p_tenant_id: tenantId,
          p_answer: answer,
          p_citations: citations,
          p_confidence: confidence,
          p_model: DEFAULT_MODEL,
          p_surface: surface,
        }
      );

      if (aError) {
        console.error("Error logging answer:", aError);
      }
      answerId = answerRow as string | null;
    }

    const response: AskResponse = {
      answer,
      citations,
      confidence,
      questionId: questionId ?? undefined,
      answerId: answerId ?? undefined,
    };

    return new Response(JSON.stringify(response), {
      status: 200,
      headers: jsonHeaders(),
    });
  } catch (err) {
    console.error("docs-ai-ask error:", err);
    return new Response(
      JSON.stringify({ error: "Internal error", details: String(err) }),
      { status: 500, headers: jsonHeaders() }
    );
  }
});

// =========================================
// Helper Functions
// =========================================

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
      input: text,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Embedding API error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  return data.data[0].embedding;
}

async function generateAnswer(
  question: string,
  chunks: {
    content: string;
    url: string | null;
    title: string | null;
    combined_score: number;
  }[],
  context: Record<string, unknown>
): Promise<{ answer: string; confidence: number }> {
  if (chunks.length === 0) {
    return {
      answer:
        "I couldn't find relevant documentation to answer your question. Please try rephrasing or check our docs directly.",
      confidence: 0,
    };
  }

  // Build context from chunks
  const chunkContext = chunks
    .map((c, i) => {
      const source = c.title ? `[${c.title}](${c.url})` : c.url || "Unknown source";
      return `### Source ${i + 1}: ${source}\n${c.content}`;
    })
    .join("\n\n---\n\n");

  const systemPrompt = `You are InsightPulse Docs AI, a technical documentation assistant. Your role is to answer questions about InsightPulse products accurately and helpfully.

CRITICAL RULES:
1. ONLY answer based on the provided documentation context
2. ALWAYS cite your sources with [Source N] references
3. If the documentation doesn't contain enough information, say so clearly
4. Provide code examples when relevant
5. Be concise but thorough
6. Use markdown formatting for readability

Current page context: ${JSON.stringify(context)}`;

  const userPrompt = `Based on the following documentation, answer this question:

**Question:** ${question}

---

**Documentation Context:**

${chunkContext}

---

Please provide a clear, accurate answer with source citations.`;

  // Try OpenAI first, fall back to Anthropic
  if (OPENAI_API_KEY) {
    return await generateWithOpenAI(systemPrompt, userPrompt, chunks);
  } else if (ANTHROPIC_API_KEY) {
    return await generateWithAnthropic(systemPrompt, userPrompt, chunks);
  } else {
    throw new Error("No LLM API key configured (OPENAI_API_KEY or ANTHROPIC_API_KEY)");
  }
}

async function generateWithOpenAI(
  systemPrompt: string,
  userPrompt: string,
  chunks: { combined_score: number }[]
): Promise<{ answer: string; confidence: number }> {
  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${OPENAI_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: DEFAULT_MODEL,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt },
      ],
      temperature: 0.3,
      max_tokens: 1024,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`OpenAI API error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  const answer = data.choices[0]?.message?.content || "Unable to generate answer.";

  // Estimate confidence based on retrieval scores
  const avgScore = chunks.reduce((sum, c) => sum + c.combined_score, 0) / chunks.length;
  const confidence = Math.min(0.95, Math.max(0.1, avgScore));

  return { answer, confidence };
}

async function generateWithAnthropic(
  systemPrompt: string,
  userPrompt: string,
  chunks: { combined_score: number }[]
): Promise<{ answer: string; confidence: number }> {
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": ANTHROPIC_API_KEY!,
      "Content-Type": "application/json",
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: "claude-3-5-sonnet-20241022",
      max_tokens: 1024,
      system: systemPrompt,
      messages: [{ role: "user", content: userPrompt }],
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Anthropic API error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  const answer =
    data.content[0]?.type === "text"
      ? data.content[0].text
      : "Unable to generate answer.";

  // Estimate confidence based on retrieval scores
  const avgScore = chunks.reduce((sum, c) => sum + c.combined_score, 0) / chunks.length;
  const confidence = Math.min(0.95, Math.max(0.1, avgScore));

  return { answer, confidence };
}
