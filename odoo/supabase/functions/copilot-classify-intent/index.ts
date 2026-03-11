// Odoo Copilot — Intent Classification Edge Function
// Classifies user messages as informational | navigational | transactional

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const INTENT_SYSTEM_PROMPT = `You are an intent classifier for an ERP copilot.
Classify the user message into exactly one category:
- "informational": questions about data, policies, regulations, how-to
- "navigational": requests to open, go to, show, or find a specific record/page
- "transactional": requests to create, update, approve, confirm, or execute an action

Respond with ONLY the category name, nothing else.`;

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  const { message } = await req.json();
  if (!message) {
    return new Response(JSON.stringify({ error: "message required" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const llmApiKey = Deno.env.get("LLM_API_KEY");
  const llmEndpoint = Deno.env.get("LLM_ENDPOINT") || "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent";

  if (!llmApiKey) {
    return new Response(
      JSON.stringify({ error: "LLM_API_KEY not configured" }),
      { status: 503, headers: { "Content-Type": "application/json" } }
    );
  }

  try {
    const response = await fetch(`${llmEndpoint}?key=${llmApiKey}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [
          { role: "user", parts: [{ text: `${INTENT_SYSTEM_PROMPT}\n\nUser message: ${message}` }] }
        ],
        generationConfig: { temperature: 0, maxOutputTokens: 20 },
      }),
    });

    const data = await response.json();
    const rawIntent = data?.candidates?.[0]?.content?.parts?.[0]?.text?.trim().toLowerCase() || "informational";

    const validIntents = ["informational", "navigational", "transactional"];
    const intent = validIntents.includes(rawIntent) ? rawIntent : "informational";

    return new Response(
      JSON.stringify({ intent, raw: rawIntent }),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (err) {
    return new Response(
      JSON.stringify({ error: "classification_failed", detail: String(err) }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
});
