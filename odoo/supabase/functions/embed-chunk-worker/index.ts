import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

// Simplified queue worker invoked via webhook or cron
serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
    const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
    const openAIApiKey = Deno.env.get("OPENAI_API_KEY");

    if (!openAIApiKey) throw new Error("Missing OPENAI_API_KEY");

    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // Get payload (expected from a DB webhook on kb_chunks insert)
    const payload = await req.json();
    const chunkId = payload.record?.id;
    const textContent = payload.record?.text_content;

    if (!chunkId || !textContent) {
      return new Response("Missing chunk dat", { status: 400 });
    }

    // Call OpenAI
    const response = await fetch("https://api.openai.com/v1/embeddings", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${openAIApiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        input: textContent,
        model: "text-embedding-3-small",
      }),
    });

    const result = await response.json();
    if (result.error) throw new Error(result.error.message);

    const embedding = result.data[0].embedding;

    // Save Embedding
    const { error } = await supabase.from("kb_embeddings").insert({
      chunk_id: chunkId,
      embedding: embedding,
      model: "text-embedding-3-small",
    });

    if (error) throw error;

    return new Response(
      JSON.stringify({ status: "success", chunk_id: chunkId }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
        status: 200,
      },
    );
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 500,
    });
  }
});
