'use client';

import { useCallback, useEffect, useState } from "react";
import {
  CopilotActionTemplate,
  CopilotMessage,
  CopilotProfile,
  CopilotRecordSummary,
  CopilotSendOptions,
  CopilotSessionState,
} from "../types";

function nowIso() {
  return new Date().toISOString();
}

function randomId(prefix: string) {
  return `${prefix}_${Math.random().toString(36).slice(2, 10)}`;
}

// Configurable API endpoint - supports Next.js API routes, Supabase Edge, or custom backends
// Set via environment variable:
// - Next.js: NEXT_PUBLIC_COPILOT_ENDPOINT
// - Vite: VITE_COPILOT_ENDPOINT
// - Default: /api/copilot/chat (local Next.js API route)
const COPILOT_API_ENDPOINT =
  process.env.NEXT_PUBLIC_COPILOT_ENDPOINT || "/api/copilot/chat";

async function callCopilotApi(params: {
  profile: CopilotProfile;
  record: CopilotRecordSummary;
  messages: CopilotMessage[];
  input: string;
  options?: CopilotSendOptions;
}): Promise<{ reply: string }> {
  const res = await fetch(COPILOT_API_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Copilot API error: ${res.status}`);
  }

  return res.json();
}

export function useCopilotSession(
  profile: CopilotProfile,
  record: CopilotRecordSummary
): {
  state: CopilotSessionState;
  sendMessage: (content: string, options?: CopilotSendOptions) => Promise<void>;
  reset: () => void;
} {
  const [state, setState] = useState<CopilotSessionState>({
    messages: [],
    actions: [],
    isLoading: false,
    error: null,
  });

  // Seed default action templates based on profile
  useEffect(() => {
    const baseActions: CopilotActionTemplate[] = [
      {
        id: "summarize_record",
        label: "Summarize this record",
        description: "Short overview of what matters here.",
        prompt: "Summarize this record in 5 bullet points, focusing on decisions and risks.",
      },
      {
        id: "explain_numbers",
        label: "Explain the numbers",
        description: "Explain key figures and anomalies.",
        prompt:
          "Explain the key numbers in this record, highlight anomalies, and flag anything that needs attention.",
      },
      {
        id: "draft_email",
        label: "Draft email",
        description: "Draft a client / stakeholder email.",
        prompt:
          "Draft a clear, professional email summarizing this record to a non-technical stakeholder.",
      },
      {
        id: "next_steps",
        label: "Suggest next steps",
        description: "Actionable checklist.",
        prompt:
          "Propose a concrete next-steps checklist to move this record forward, including owners and timelines.",
      },
    ];

    setState((prev) => ({
      ...prev,
      actions: baseActions,
    }));
  }, [profile.slug]);

  const reset = useCallback(() => {
    setState((prev) => ({
      ...prev,
      messages: [],
      error: null,
    }));
  }, []);

  const sendMessage = useCallback(
    async (content: string, options?: CopilotSendOptions) => {
      if (!content.trim()) return;

      const userMessage: CopilotMessage = {
        id: randomId("msg_user"),
        role: "user",
        content,
        createdAt: nowIso(),
      };

      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, userMessage],
        isLoading: true,
        error: null,
      }));

      try {
        const currentMessages = state.messages;
        const { reply } = await callCopilotApi({
          profile,
          record,
          messages: [...currentMessages, userMessage],
          input: content,
          options,
        });

        const assistantMessage: CopilotMessage = {
          id: randomId("msg_ai"),
          role: "assistant",
          content: reply,
          createdAt: nowIso(),
          meta: {
            actionLabel: options?.fromActionId,
          },
        };

        setState((prev) => ({
          ...prev,
          messages: [...prev.messages, assistantMessage],
          isLoading: false,
        }));
      } catch (err: unknown) {
        const errorMessage = err instanceof Error ? err.message : "Unexpected Copilot error";
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: errorMessage,
        }));
      }
    },
    [profile, record, state.messages]
  );

  return { state, sendMessage, reset };
}
