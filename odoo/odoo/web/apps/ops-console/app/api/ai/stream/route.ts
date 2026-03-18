/**
 * POST /api/ai/stream
 *
 * Streaming chat endpoint using Vercel AI SDK streamText.
 * Routes through Vercel AI Gateway when VERCEL_AI_GATEWAY_URL is set;
 * falls back to direct Google Gemini endpoint.
 *
 * Request:  POST { "messages": CoreMessage[], "system"?: string }
 * Response: text/event-stream (Vercel AI SDK data stream format)
 *
 * Provider: ssot/providers/ai/provider.yaml
 *
 * Env vars:
 *   GEMINI_API_KEY          — Google AI Studio key (required)
 *   VERCEL_AI_GATEWAY_URL   — (optional) AI Gateway base URL; enables gateway routing
 *
 * Errors (JSON):
 *   400 — messages missing or not an array
 *   503 — { error: { code: "AI_KEY_NOT_CONFIGURED" } }
 *   500 — { error: { code: "STREAM_ERROR", message: string } }
 */

import { streamText } from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { google } from "@ai-sdk/google";

export const runtime = "edge";
export const maxDuration = 60;

const GOOGLE_OPENAI_BASE =
  "https://generativelanguage.googleapis.com/v1beta/openai";
const DEFAULT_MODEL = "gemini-2.0-flash";
const GATEWAY_MODEL = "google/gemini-2.0-flash"; // Gateway model ID format

export async function POST(req: Request): Promise<Response> {
  // Parse body
  let messages: unknown;
  let system: string | undefined;
  try {
    const body = (await req.json()) as {
      messages?: unknown;
      system?: string;
    };
    messages = body.messages;
    system = body.system?.trim() || undefined;
  } catch {
    return Response.json({ error: { code: "INVALID_JSON" } }, { status: 400 });
  }

  if (!Array.isArray(messages) || messages.length === 0) {
    return Response.json(
      { error: { code: "MESSAGES_REQUIRED", hint: "messages must be a non-empty array" } },
      { status: 400 }
    );
  }

  // Auth check
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    return Response.json(
      {
        error: {
          code: "AI_KEY_NOT_CONFIGURED",
          hint: "Set GEMINI_API_KEY in Vercel env vars",
        },
      },
      { status: 503 }
    );
  }

  try {
    const gatewayUrl = process.env.VERCEL_AI_GATEWAY_URL;

    // Select model: AI Gateway (preferred) or direct Gemini (fallback)
    const model = gatewayUrl
      ? createOpenAI({ baseURL: gatewayUrl, apiKey })(GATEWAY_MODEL)
      : google(DEFAULT_MODEL);

    const result = streamText({
      model,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      messages: messages as any,
      ...(system ? { system } : {}),
    });

    return result.toDataStreamResponse();
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    console.error("[/api/ai/stream] Error:", message);
    return Response.json(
      { error: { code: "STREAM_ERROR", message } },
      { status: 500 }
    );
  }
}
