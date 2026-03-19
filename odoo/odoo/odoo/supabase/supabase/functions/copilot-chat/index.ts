// supabase/functions/copilot-chat/index.ts
// Deno Edge Function for Copilot chat - calls LLM with record context
// Deploy: supabase functions deploy copilot-chat --project-ref YOUR_PROJECT_REF

import { Hono } from "https://deno.land/x/hono@v4.4.7/mod.ts";

// Types mirrored from frontend
type CopilotRole = "user" | "assistant" | "system";

interface CopilotMessage {
  id: string;
  role: CopilotRole;
  content: string;
  createdAt: string;
}

interface CopilotProfile {
  id: string;
  name: string;
  slug: string;
  targetModel: string;
  modelLabel?: string;
}

interface CopilotRecordSummaryField {
  key: string;
  label: string;
  value: string | number | null;
}

interface CopilotRecordSummary {
  id: number | string;
  model: string;
  displayName: string;
  icon?: string;
  fields: CopilotRecordSummaryField[];
}

interface CopilotRequestBody {
  profile: CopilotProfile;
  record: CopilotRecordSummary;
  messages: CopilotMessage[];
  input: string;
  options?: { fromActionId?: string };
}

// Map Copilot roles to LLM API roles
function mapRole(role: CopilotRole): "user" | "assistant" | "system" {
  if (role === "system") return "system";
  if (role === "assistant") return "assistant";
  return "user";
}

// Build a structured system prompt using profile + record context
function buildSystemPrompt(
  profile: CopilotProfile,
  record: CopilotRecordSummary
): string {
  const fieldsText = record.fields
    .map((f) => `${f.label}: ${f.value ?? "—"}`)
    .join("\n");

  return [
    `You are a Copilot embedded in an Odoo CE + OCA 18 system, acting as a thin AI layer on top of existing models.`,
    `Profile: ${profile.name} (${profile.slug})`,
    `Target model: ${profile.targetModel}`,
    ``,
    `You are currently focused on a single record:`,
    `Model: ${record.model}`,
    `Display name: ${record.displayName}`,
    `Fields:`,
    fieldsText,
    ``,
    `Guidelines:`,
    `- Answer in clear, concise bullet points.`,
    `- Explain decisions and risks in plain language.`,
    `- If suggesting actions, format them as a checklist.`,
    `- Never assume you can change the system directly; you only suggest.`,
    `- Use markdown formatting for better readability.`,
  ].join("\n");
}

// Call OpenAI-compatible LLM API
async function callOpenAILLM(body: CopilotRequestBody): Promise<string> {
  const apiKey = Deno.env.get("OPENAI_API_KEY");
  if (!apiKey) {
    throw new Error("OPENAI_API_KEY is not configured in environment");
  }

  const systemPrompt = buildSystemPrompt(body.profile, body.record);

  const messages = [
    { role: "system" as const, content: systemPrompt },
    ...body.messages.map((m) => ({
      role: mapRole(m.role),
      content: m.content,
    })),
    {
      role: "user" as const,
      content: body.input,
    },
  ];

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      messages,
      temperature: 0.2,
      max_tokens: 1024,
    }),
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`OpenAI error: ${response.status} - ${errText}`);
  }

  const data = await response.json();
  const reply =
    data.choices?.[0]?.message?.content ??
    "I could not generate a response for this query.";

  return reply;
}

// Call Anthropic Claude API (alternative to OpenAI)
async function callAnthropicLLM(body: CopilotRequestBody): Promise<string> {
  const apiKey = Deno.env.get("ANTHROPIC_API_KEY");
  if (!apiKey) {
    throw new Error("ANTHROPIC_API_KEY is not configured in environment");
  }

  const systemPrompt = buildSystemPrompt(body.profile, body.record);

  // Build messages for Claude format
  const messages = [
    ...body.messages.map((m) => ({
      role: m.role === "assistant" ? "assistant" : "user",
      content: m.content,
    })),
    {
      role: "user" as const,
      content: body.input,
    },
  ];

  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "claude-3-haiku-20240307",
      max_tokens: 1024,
      system: systemPrompt,
      messages,
    }),
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`Anthropic error: ${response.status} - ${errText}`);
  }

  const data = await response.json();
  const reply =
    data.content?.[0]?.text ??
    "I could not generate a response for this query.";

  return reply;
}

// Select LLM provider based on environment or request
async function callLLMWithCopilotContext(
  body: CopilotRequestBody
): Promise<string> {
  // Check for Anthropic key first (preferred for Claude-labeled profiles)
  const anthropicKey = Deno.env.get("ANTHROPIC_API_KEY");
  const openaiKey = Deno.env.get("OPENAI_API_KEY");

  // Use Claude if profile says "Claude" and we have Anthropic key
  if (
    body.profile.modelLabel?.toLowerCase().includes("claude") &&
    anthropicKey
  ) {
    return callAnthropicLLM(body);
  }

  // Otherwise use OpenAI if available
  if (openaiKey) {
    return callOpenAILLM(body);
  }

  // Fallback: check if Anthropic is available
  if (anthropicKey) {
    return callAnthropicLLM(body);
  }

  throw new Error(
    "No LLM API key configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY."
  );
}

const app = new Hono();

// CORS preflight
app.options("*", (c) => {
  return c.text("", 204, {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
  });
});

// Main chat endpoint
app.post("/", async (c) => {
  try {
    const body = (await c.req.json()) as CopilotRequestBody;

    // Validate required fields
    if (!body?.profile || !body?.record || !body?.input) {
      return c.json({ error: "Missing required fields: profile, record, input" }, 400);
    }

    const reply = await callLLMWithCopilotContext(body);

    return c.json(
      { reply },
      200,
      {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
      }
    );
  } catch (err) {
    console.error("copilot-chat error:", err);
    return c.json(
      {
        error: "Copilot backend error",
        detail: err instanceof Error ? err.message : String(err),
      },
      500,
      {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
      }
    );
  }
});

// Health check
app.get("/health", (c) => {
  return c.json({ status: "ok", service: "copilot-chat" });
});

Deno.serve(app.fetch);
