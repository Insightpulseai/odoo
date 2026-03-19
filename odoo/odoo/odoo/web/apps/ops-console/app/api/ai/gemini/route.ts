/**
 * POST /api/ai/gemini
 *
 * Ops Console AI route — Google Gemini text generation via Vercel AI Gateway.
 * @see https://vercel.com/docs/ai-gateway
 *
 * Request:  POST { "prompt": string }
 * Response: { "text": string, "model": string, "trace_id": string }
 *
 * Env vars:
 *   GEMINI_API_KEY          — Google AI Studio key
 *   VERCEL_AI_GATEWAY_URL   — (optional) AI Gateway base URL
 *
 * Errors:
 *   400 — prompt missing or empty
 *   503 — GEMINI_API_KEY not set
 *   500 — API error
 */

import { NextResponse } from "next/server";
import OpenAI from "openai";

const DEFAULT_MODEL = process.env.GEMINI_MODEL ?? "gemini-2.0-flash";
const GOOGLE_OPENAI_BASE = "https://generativelanguage.googleapis.com/v1beta/openai";

export const maxDuration = 60;

export async function POST(req: Request): Promise<NextResponse> {
  let prompt: string;
  try {
    const body = (await req.json()) as { prompt?: string };
    prompt = body.prompt?.trim() ?? "";
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  if (!prompt) {
    return NextResponse.json(
      { error: "prompt is required and must not be empty" },
      { status: 400 }
    );
  }

  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    return NextResponse.json(
      { error: "GEMINI_API_KEY_MISSING", hint: "Set GEMINI_API_KEY in Vercel env vars" },
      { status: 503 }
    );
  }

  try {
    const baseURL = process.env.VERCEL_AI_GATEWAY_URL ?? GOOGLE_OPENAI_BASE;
    const client = new OpenAI({ apiKey, baseURL });

    const traceId =
      typeof crypto !== "undefined" && crypto.randomUUID
        ? crypto.randomUUID()
        : `trace-${Date.now()}-${Math.random().toString(36).slice(2)}`;

    const completion = await client.chat.completions.create({
      model: DEFAULT_MODEL,
      messages: [{ role: "user", content: prompt }],
    });

    const text = completion.choices[0]?.message?.content ?? "";

    return NextResponse.json({
      provider: "google",
      text,
      model: DEFAULT_MODEL,
      trace_id: traceId,
      usage: completion.usage
        ? {
            prompt_tokens: completion.usage.prompt_tokens,
            completion_tokens: completion.usage.completion_tokens,
            total_tokens: completion.usage.total_tokens,
          }
        : undefined,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    console.error("[/api/ai/gemini] Error:", message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
