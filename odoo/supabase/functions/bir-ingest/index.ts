// Odoo Copilot — BIR Document Ingestion Edge Function
// Accepts PDF/text, chunks, embeds, stores in kb schema with BIR metadata

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const CHUNK_SIZE = 512;
const CHUNK_OVERLAP = 64;

interface BirDocMeta {
  form_number?: string;
  tax_type?: string;
  effective_date?: string;
  issuance_number?: string;
  title: string;
}

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const embeddingApiKey = Deno.env.get("EMBEDDING_API_KEY");

  const supabase = createClient(supabaseUrl, supabaseKey);

  const { content, metadata } = (await req.json()) as {
    content: string;
    metadata: BirDocMeta;
  };

  if (!content || !metadata?.title) {
    return new Response(
      JSON.stringify({ error: "content and metadata.title required" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  // Chunk the content with overlap
  const chunks = chunkText(content, CHUNK_SIZE, CHUNK_OVERLAP);

  // Generate embeddings for each chunk
  const embeddings = await generateEmbeddings(chunks, embeddingApiKey);

  // Store in kb schema
  const records = chunks.map((chunk, i) => ({
    content: chunk,
    embedding: embeddings[i],
    source_type: "bir",
    metadata: {
      ...metadata,
      chunk_index: i,
      total_chunks: chunks.length,
    },
  }));

  const { data, error } = await supabase
    .from("kb.documents")
    .insert(records);

  if (error) {
    return new Response(
      JSON.stringify({ error: "insert_failed", detail: error.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }

  return new Response(
    JSON.stringify({
      status: "ingested",
      title: metadata.title,
      chunks: chunks.length,
    }),
    { headers: { "Content-Type": "application/json" } }
  );
});

function chunkText(text: string, size: number, overlap: number): string[] {
  const words = text.split(/\s+/);
  const chunks: string[] = [];
  let start = 0;

  while (start < words.length) {
    const end = Math.min(start + size, words.length);
    chunks.push(words.slice(start, end).join(" "));
    start += size - overlap;
    if (start >= words.length) break;
  }

  return chunks;
}

async function generateEmbeddings(
  chunks: string[],
  apiKey: string | undefined
): Promise<number[][]> {
  if (!apiKey) {
    // Return zero vectors as placeholder when no API key
    return chunks.map(() => new Array(1536).fill(0));
  }

  const response = await fetch("https://api.openai.com/v1/embeddings", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: "text-embedding-3-small",
      input: chunks,
      dimensions: 1536,
    }),
  });

  const data = await response.json();
  return data.data.map((d: { embedding: number[] }) => d.embedding);
}
