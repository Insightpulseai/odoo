/**
 * POST /api/ai/gemini/tools
 *
 * Next.js App Router API route for Gemini function calling.
 * Used by ipai_ai_copilot Odoo addon for tool-capable AI requests.
 *
 * Required environment variable:
 *   GEMINI_API_KEY — Google AI Studio API key (stored in Vercel env vars)
 *
 * Error responses:
 *   400 — missing required field (message)
 *   503 — GEMINI_API_KEY not configured
 *   500 — unexpected error
 *
 * Success responses:
 *   200 { text, provider, model, trace_id }           — plain text response
 *   200 { tool_calls, provider, model, trace_id }     — AI wants to call tools
 */
import { NextResponse } from "next/server";
import {
    generateWithTools,
    type CopilotPayload,
} from "@/../../platform/ai/providers/gemini_tools";

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

    // Validate required field
    if (!payload.message || !String(payload.message).trim()) {
        return NextResponse.json(
            { error: "MESSAGE_REQUIRED", message: "message field is required and must be non-empty" },
            { status: 400 }
        );
    }

    try {
        const result = await generateWithTools(payload);
        return NextResponse.json(result);
    } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);

        if (message.includes("GEMINI_API_KEY")) {
            return NextResponse.json(
                {
                    error: "AI_KEY_NOT_CONFIGURED",
                    message: "GEMINI_API_KEY is not set in the deployment environment",
                },
                { status: 503 }
            );
        }

        // Log unexpected errors (visible in Vercel function logs)
        console.error("[/api/ai/gemini/tools] Unexpected error:", message);
        return NextResponse.json(
            { error: "INTERNAL_ERROR", message },
            { status: 500 }
        );
    }
}

/**
 * Vercel function configuration.
 * maxDuration 60 = Pro tier max (allows time for complex Gemini Pro responses).
 */
export const config = {
    maxDuration: 60,
};
