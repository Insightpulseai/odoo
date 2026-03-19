/**
 * Gemini bridge with function calling (tool use) support.
 *
 * Used by ipai_ai_copilot when tool_declarations are provided in the payload.
 *
 * Endpoint: POST /api/ai/gemini/tools
 *
 * Payload:
 *   {
 *     system_prompt?: string
 *     context?: string
 *     history?: { role: string; content: string }[]
 *     message: string
 *     tools?: GeminiToolDeclaration[]
 *   }
 *
 * Response (plain text):
 *   { text: string; provider: string; model: string; trace_id: string }
 *
 * Response (tool call):
 *   { tool_calls: { name: string; args: Record<string, unknown> }[]; provider: string; model: string; trace_id: string }
 *
 * Model routing:
 *   - Tools present → gemini-1.5-pro-latest (better function calling)
 *   - No tools → gemini-2.0-flash-preview (cost-optimised)
 */

import {
    GoogleGenerativeAI,
    FunctionCallingMode,
    type Content,
    type Part,
} from "@google/generative-ai";

/** Cost-optimised model for simple queries */
const MODEL_FAST = "gemini-2.0-flash-preview";

/** Full capability model for tool-heavy / complex queries */
const MODEL_PRO = "gemini-1.5-pro-latest";

// ── Type definitions ──────────────────────────────────────────────────────────

export interface CopilotPayload {
    system_prompt?: string;
    context?: string;
    history?: { role: string; content: string }[];
    message: string;
    tools?: Record<string, unknown>[];
}

export interface CopilotResponse {
    text?: string;
    tool_calls?: { name: string; args: Record<string, unknown> }[];
    provider: string;
    model: string;
    trace_id: string;
}

// ── Main function ─────────────────────────────────────────────────────────────

/**
 * Generate a response using Gemini, with optional function calling support.
 *
 * @param payload - The copilot request payload
 * @returns A CopilotResponse with either text or tool_calls
 * @throws Error if GEMINI_API_KEY is not set
 */
export async function generateWithTools(payload: CopilotPayload): Promise<CopilotResponse> {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
        throw new Error("GEMINI_API_KEY not configured");
    }

    const genAI = new GoogleGenerativeAI(apiKey);
    const hasTools = Array.isArray(payload.tools) && payload.tools.length > 0;

    // Select model based on whether tools are involved
    const modelId = hasTools ? MODEL_PRO : MODEL_FAST;

    // Generate a unique trace ID for this request
    const traceId =
        typeof crypto !== "undefined" && crypto.randomUUID
            ? crypto.randomUUID()
            : `trace-${Date.now()}-${Math.random().toString(36).slice(2)}`;

    // Build system instruction from system_prompt + context
    const systemParts: string[] = [];
    if (payload.system_prompt) {
        systemParts.push(payload.system_prompt);
    }
    if (payload.context) {
        systemParts.push(`\nCurrent context: ${payload.context}`);
    }
    const systemInstruction = systemParts.join("\n").trim() || undefined;

    // Build model configuration
    const modelConfig: Parameters<typeof genAI.getGenerativeModel>[0] = {
        model: modelId,
        ...(systemInstruction ? { systemInstruction } : {}),
        ...(hasTools
            ? {
                  tools: [{ functionDeclarations: payload.tools as any[] }],
                  toolConfig: {
                      functionCallingConfig: {
                          mode: FunctionCallingMode.AUTO,
                      },
                  },
              }
            : {}),
    };

    const model = genAI.getGenerativeModel(modelConfig);

    // Build conversation history in Gemini Content format
    const history: Content[] = (payload.history || []).map((h) => ({
        role: h.role === "user" ? "user" : "model",
        parts: [{ text: h.content }] as Part[],
    }));

    // Start chat with history
    const chat = model.startChat({ history });

    // Send the current user message
    const result = await chat.sendMessage(payload.message);
    const response = result.response;

    // Check for function calls in the response
    const candidates = response.candidates ?? [];
    const parts: Part[] = (candidates[0]?.content?.parts ?? []) as Part[];

    const functionCalls = parts
        .filter((p): p is Part & { functionCall: { name: string; args: Record<string, unknown> } } =>
            "functionCall" in p && p.functionCall !== undefined
        )
        .map((p) => ({
            name: p.functionCall.name,
            args: (p.functionCall.args as Record<string, unknown>) || {},
        }));

    if (functionCalls.length > 0) {
        return {
            tool_calls: functionCalls,
            provider: "google",
            model: modelId,
            trace_id: traceId,
        };
    }

    // Plain text response
    return {
        text: response.text(),
        provider: "google",
        model: modelId,
        trace_id: traceId,
    };
}
