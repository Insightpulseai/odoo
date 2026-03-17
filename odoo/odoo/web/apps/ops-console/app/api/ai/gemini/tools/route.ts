/**
 * POST /api/ai/gemini/tools
 *
 * Gemini function calling via Vercel AI Gateway (OpenAI-compatible API).
 * @see https://vercel.com/docs/ai-gateway
 *
 * Uses the `openai` SDK pointed at either:
 *   - VERCEL_AI_GATEWAY_URL  (if set) — routes through Vercel AI Gateway
 *   - Google's OpenAI-compatible endpoint (fallback)
 *
 * Required env vars:
 *   GEMINI_API_KEY           — Google AI Studio key
 *   VERCEL_AI_GATEWAY_URL    — (optional) Vercel AI Gateway base URL
 *
 * Success responses:
 *   200 { text, provider, model, trace_id }
 *   200 { tool_calls, provider, model, trace_id }
 */

import { NextResponse } from "next/server";
import OpenAI from "openai";

const MODEL_FAST = "gemini-2.0-flash";
const MODEL_PRO = "gemini-1.5-pro-latest";

// Google's OpenAI-compatible endpoint
const GOOGLE_OPENAI_BASE = "https://generativelanguage.googleapis.com/v1beta/openai";

export interface CopilotPayload {
    system_prompt?: string;
    context?: string;
    history?: { role: string; content: string }[];
    message: string;
    tools?: Record<string, unknown>[];
}

export async function POST(req: Request): Promise<NextResponse> {
    let payload: CopilotPayload;

    try {
        payload = (await req.json()) as CopilotPayload;
    } catch {
        return NextResponse.json(
            { error: "INVALID_JSON", message: "Request body must be valid JSON" },
            { status: 400 }
        );
    }

    if (!payload.message?.trim()) {
        return NextResponse.json(
            { error: "MESSAGE_REQUIRED", message: "message field is required and must be non-empty" },
            { status: 400 }
        );
    }

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
        return NextResponse.json(
            { error: "AI_KEY_NOT_CONFIGURED", message: "GEMINI_API_KEY is not set" },
            { status: 503 }
        );
    }

    try {
        const hasTools = Array.isArray(payload.tools) && payload.tools.length > 0;
        const modelId = hasTools ? MODEL_PRO : MODEL_FAST;

        const traceId =
            typeof crypto !== "undefined" && crypto.randomUUID
                ? crypto.randomUUID()
                : `trace-${Date.now()}-${Math.random().toString(36).slice(2)}`;

        // Use AI Gateway if configured, else fall back to Google's direct endpoint
        const baseURL = process.env.VERCEL_AI_GATEWAY_URL ?? GOOGLE_OPENAI_BASE;

        const client = new OpenAI({ apiKey, baseURL });

        // Build messages
        const messages: OpenAI.ChatCompletionMessageParam[] = [];

        const systemParts: string[] = [];
        if (payload.system_prompt) systemParts.push(payload.system_prompt);
        if (payload.context) systemParts.push(`Current context: ${payload.context}`);
        if (systemParts.length > 0) {
            messages.push({ role: "system", content: systemParts.join("\n") });
        }

        for (const h of payload.history ?? []) {
            messages.push({
                role: h.role === "user" ? "user" : "assistant",
                content: h.content,
            });
        }
        messages.push({ role: "user", content: payload.message });

        // Build tool declarations
        const tools: OpenAI.ChatCompletionTool[] | undefined = hasTools
            ? payload.tools!.map((decl) => ({
                  type: "function" as const,
                  function: {
                      name: decl.name as string,
                      description: (decl.description as string) ?? "",
                      parameters: (decl.parameters as Record<string, unknown>) ?? {
                          type: "object",
                          properties: {},
                      },
                  },
              }))
            : undefined;

        const completion = await client.chat.completions.create({
            model: modelId,
            messages,
            ...(tools ? { tools, tool_choice: "auto" } : {}),
        });

        const choice = completion.choices[0];

        // Tool calls
        if (choice.message.tool_calls?.length) {
            return NextResponse.json({
                tool_calls: choice.message.tool_calls.map((tc) => ({
                    name: tc.function.name,
                    args: JSON.parse(tc.function.arguments || "{}"),
                })),
                provider: "google",
                model: modelId,
                trace_id: traceId,
            });
        }

        return NextResponse.json({
            text: choice.message.content ?? "",
            provider: "google",
            model: modelId,
            trace_id: traceId,
        });
    } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        console.error("[/api/ai/gemini/tools] Error:", message);
        return NextResponse.json({ error: "INTERNAL_ERROR", message }, { status: 500 });
    }
}

export const maxDuration = 60;
