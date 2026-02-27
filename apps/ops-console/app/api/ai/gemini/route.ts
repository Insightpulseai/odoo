/**
 * POST /api/ai/gemini
 *
 * Ops Console AI route — Google Gemini text generation endpoint.
 *
 * Request:  POST { "prompt": string }
 * Response: { "text": string, "model": string, "trace_id": string }
 *
 * Errors:
 *   400 — prompt missing or empty
 *   503 — GEMINI_API_KEY not set
 *   500 — Gemini API error
 *
 * @see platform/ai/providers/gemini.ts
 * @see docs/architecture/AI_PROVIDER_BRIDGE.md
 */

import { NextResponse } from "next/server";
import { generateText } from "../../../../../../platform/ai/providers/gemini";

export const maxDuration = 60; // Vercel function timeout (seconds)

export async function POST(req: Request): Promise<NextResponse> {
  let prompt: string;
  try {
    const body = (await req.json()) as { prompt?: string };
    prompt = body.prompt?.trim() ?? "";
  } catch {
    return NextResponse.json(
      { error: "Invalid JSON body" },
      { status: 400 }
    );
  }

  if (!prompt) {
    return NextResponse.json(
      { error: "prompt is required and must not be empty" },
      { status: 400 }
    );
  }

  // Explicit 503 for missing API key — fail fast before any external call
  if (!process.env.GEMINI_API_KEY) {
    return NextResponse.json(
      { error: "GEMINI_API_KEY_MISSING", hint: "Set GEMINI_API_KEY in Vercel env vars" },
      { status: 503 }
    );
  }

  try {
    const result = await generateText(prompt);
    return NextResponse.json(result);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    console.error("[/api/ai/gemini] Error:", message);
    return NextResponse.json(
      { error: message },
      { status: 500 }
    );
  }
}
