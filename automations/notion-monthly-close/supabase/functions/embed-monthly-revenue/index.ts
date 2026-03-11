// =============================================================================
// Edge Function: embed-monthly-revenue
// Generates AI summaries and embeddings for monthly revenue insights
//
// Dependencies:
//   - SUPABASE_URL (env)
//   - SUPABASE_SERVICE_ROLE_KEY (env)
//   - OPENAI_API_KEY (env)
//
// Trigger: HTTP POST or pg_cron via net.http_post
// =============================================================================

import { createClient } from "npm:@supabase/supabase-js@2.48.0";
import OpenAI from "npm:openai@4.73.0";

// Environment variables
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const OPENAI_API_KEY = Deno.env.get("OPENAI_API_KEY")!;

// Initialize clients
const supabase = createClient(SUPABASE_URL, SERVICE_ROLE);
const openai = new OpenAI({ apiKey: OPENAI_API_KEY });

// Configuration
const BATCH_SIZE = 50;
const EMBEDDING_MODEL = "text-embedding-3-small";
const SUMMARY_MODEL = "gpt-4o-mini";

interface MonthlyRevenueRow {
  id: number;
  company_id: number;
  month: string;
  revenue: string;
}

interface EmbeddingUpdate {
  id: number;
  summary: string;
  embedding: number[];
  last_embedded_at: string;
}

/**
 * Generate a concise financial summary for a revenue record
 */
async function generateSummary(row: MonthlyRevenueRow): Promise<string> {
  const prompt = `You are a financial analyst.
Create a one-sentence, plain-English summary of this metric. Focus on the revenue amount and time period.
Be concise and factual, no extra commentary.

company_id: ${row.company_id}
month: ${row.month}
revenue: ${row.revenue}`;

  const response = await openai.chat.completions.create({
    model: SUMMARY_MODEL,
    messages: [
      { role: "system", content: "You write concise financial summaries." },
      { role: "user", content: prompt },
    ],
    max_tokens: 80,
    temperature: 0.2,
  });

  return response.choices[0].message.content?.trim() ?? "";
}

/**
 * Generate embedding vector for text
 */
async function generateEmbedding(text: string): Promise<number[]> {
  const response = await openai.embeddings.create({
    model: EMBEDDING_MODEL,
    input: text,
  });

  return response.data[0].embedding;
}

/**
 * Process a batch of rows: generate summaries and embeddings
 */
async function processBatch(rows: MonthlyRevenueRow[]): Promise<EmbeddingUpdate[]> {
  const updates: EmbeddingUpdate[] = [];

  for (const row of rows) {
    try {
      // Generate summary
      const summary = await generateSummary(row);

      // Generate embedding from summary
      const embedding = await generateEmbedding(summary);

      updates.push({
        id: row.id,
        summary,
        embedding,
        last_embedded_at: new Date().toISOString(),
      });
    } catch (error) {
      console.error(`Error processing row ${row.id}:`, error);
      // Continue with other rows even if one fails
    }
  }

  return updates;
}

/**
 * Main handler
 */
Deno.serve(async (req) => {
  // Validate environment
  if (!SUPABASE_URL || !SERVICE_ROLE || !OPENAI_API_KEY) {
    return new Response(
      JSON.stringify({ error: "Missing required environment variables" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }

  try {
    // Only accept POST requests (for security)
    if (req.method !== "POST") {
      return new Response(
        JSON.stringify({ error: "Method not allowed" }),
        { status: 405, headers: { "Content-Type": "application/json" } }
      );
    }

    // Parse optional parameters from request body
    let batchSize = BATCH_SIZE;
    try {
      const body = await req.json();
      if (body?.batchSize && typeof body.batchSize === "number") {
        batchSize = Math.min(body.batchSize, 100); // Cap at 100
      }
    } catch {
      // Empty body is fine, use defaults
    }

    // Fetch rows that need embedding
    const { data: rows, error: selectError } = await supabase
      .schema("ai")
      .from("monthly_revenue_insights")
      .select("id, company_id, month, revenue")
      .is("embedding", null)
      .limit(batchSize);

    if (selectError) {
      console.error("Select error:", selectError);
      return new Response(
        JSON.stringify({ error: selectError.message }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }

    // Check if there's work to do
    if (!rows || rows.length === 0) {
      return new Response(
        JSON.stringify({
          status: "noop",
          message: "No rows require embedding",
          count: 0,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    }

    // Process batch: generate summaries and embeddings
    const updates = await processBatch(rows);

    if (updates.length === 0) {
      return new Response(
        JSON.stringify({
          status: "error",
          message: "Failed to process any rows",
          attempted: rows.length,
        }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }

    // Upsert updates back to database
    const { error: upsertError } = await supabase
      .schema("ai")
      .from("monthly_revenue_insights")
      .upsert(updates);

    if (upsertError) {
      console.error("Upsert error:", upsertError);
      return new Response(
        JSON.stringify({ error: upsertError.message }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }

    // Success response
    return new Response(
      JSON.stringify({
        status: "ok",
        message: `Successfully embedded ${updates.length} rows`,
        count: updates.length,
        attempted: rows.length,
      }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Unhandled error:", error);
    return new Response(
      JSON.stringify({
        error: "Internal server error",
        details: error instanceof Error ? error.message : String(error),
      }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
});
