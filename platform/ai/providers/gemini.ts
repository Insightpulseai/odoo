/**
 * Gemini AI Provider
 *
 * Bridge module for Google Gemini API integration.
 * Consumed by: apps/ops-console/app/api/ai/gemini/route.ts
 *
 * Required env var: GEMINI_API_KEY
 * Model: gemini-2.0-flash-preview (or GEMINI_MODEL override)
 *
 * @see docs/architecture/AI_PROVIDER_BRIDGE.md
 * @see ssot/secrets/registry.yaml (gemini_api_key entry)
 */

const DEFAULT_MODEL = "gemini-2.0-flash-preview";

export interface GeminiTextResult {
  provider: string;
  text: string;
  model: string;
  trace_id: string;
  usage?: {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
  };
}

/**
 * Generate text using the Gemini API.
 *
 * @param prompt - The text prompt to send to Gemini
 * @returns GeminiTextResult with generated text, model name, and trace ID
 * @throws Error if GEMINI_API_KEY is not set or if the API call fails
 */
export async function generateText(prompt: string): Promise<GeminiTextResult> {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error(
      "GEMINI_API_KEY environment variable is not set. " +
        "Add it to Vercel environment variables or your local .env.local file."
    );
  }

  const model = process.env.GEMINI_MODEL ?? DEFAULT_MODEL;

  // Use the Gemini REST API directly to avoid requiring @google/genai in platform/
  // This keeps the platform/ layer dependency-free.
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      contents: [
        {
          parts: [{ text: prompt }],
        },
      ],
    }),
  });

  if (!response.ok) {
    const errorBody = await response.text().catch(() => "unknown error");
    throw new Error(
      `Gemini API error: ${response.status} ${response.statusText} — ${errorBody}`
    );
  }

  const data = (await response.json()) as {
    candidates?: Array<{
      content?: { parts?: Array<{ text?: string }> };
    }>;
  };

  const text =
    data.candidates?.[0]?.content?.parts?.[0]?.text ??
    "No content returned from Gemini API";

  // Extract usage metadata if available (Gemini returns usageMetadata)
  const usageMeta = (data as any).usageMetadata;
  const usage = usageMeta
    ? {
        prompt_tokens: usageMeta.promptTokenCount,
        completion_tokens: usageMeta.candidatesTokenCount,
        total_tokens: usageMeta.totalTokenCount,
      }
    : undefined;

  return {
    provider: "gemini",
    text,
    model,
    trace_id: crypto.randomUUID(),
    ...(usage && { usage }),
  };
}
