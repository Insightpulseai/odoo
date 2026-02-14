'use client';

import { CopilotProfile, CopilotRecordSummary } from "./types";
import { useCopilotSession } from "./hooks/useCopilotSession";
import { CopilotContextChips } from "./CopilotContextChips";
import { CopilotThread } from "./CopilotThread";
import { CopilotActionsBar } from "./CopilotActionsBar";
import { CopilotComposer } from "./CopilotComposer";

interface Props {
  open: boolean;
  onClose: () => void;
  profile: CopilotProfile;
  record: CopilotRecordSummary;
}

export function CopilotPanel({ open, onClose, profile, record }: Props) {
  const { state, sendMessage } = useCopilotSession(profile, record);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-40 flex justify-end bg-black/40 backdrop-blur-sm">
      <div className="h-full w-full max-w-md bg-surface-900 shadow-2xl flex flex-col border-l border-surface-700">
        {/* Header */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-surface-700 bg-surface-800/95">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-primary-500 text-xs font-semibold text-white">
              {record.icon || "AI"}
            </div>
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.16em] text-surface-400">
                {profile.name}
              </div>
              <div className="text-[0.8rem] text-surface-300">
                Based on{" "}
                <span className="font-medium text-white">
                  {record.displayName}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {profile.modelLabel && (
              <span className="rounded-full bg-surface-700 px-2 py-1 text-[0.65rem] font-medium text-surface-200 border border-surface-600">
                {profile.modelLabel}
              </span>
            )}
            <button
              type="button"
              onClick={onClose}
              className="inline-flex h-7 w-7 items-center justify-center rounded-full border border-surface-600 text-surface-400 hover:bg-surface-700 hover:text-white transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        </header>

        {/* Context pills */}
        <CopilotContextChips record={record} />

        {/* Error display */}
        {state.error && (
          <div className="px-4 py-2 bg-red-900/30 border-b border-red-700/50 text-xs text-red-300">
            {state.error}
          </div>
        )}

        {/* Conversation */}
        <CopilotThread
          messages={state.messages}
          isLoading={state.isLoading}
        />

        {/* Actions + composer */}
        <CopilotActionsBar
          actions={state.actions}
          onSelect={(prompt, opts) => {
            sendMessage(prompt, { fromActionId: opts?.fromActionId });
          }}
        />
        <CopilotComposer
          onSend={(input) => sendMessage(input)}
          disabled={state.isLoading}
        />
      </div>
    </div>
  );
}
