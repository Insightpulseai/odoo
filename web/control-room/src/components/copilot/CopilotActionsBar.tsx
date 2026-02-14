'use client';

import { CopilotActionTemplate } from "./types";

interface Props {
  actions: CopilotActionTemplate[];
  onSelect: (prompt: string, options?: { fromActionId?: string }) => void;
}

export function CopilotActionsBar({ actions, onSelect }: Props) {
  if (!actions?.length) return null;

  return (
    <div className="px-4 pb-2 pt-1 border-t border-surface-700 bg-surface-800/90">
      <div className="mb-1 flex items-center justify-between">
        <span className="text-[0.7rem] uppercase tracking-[0.12em] text-surface-400">
          Quick actions
        </span>
      </div>
      <div className="flex flex-wrap gap-2">
        {actions.map((a) => (
          <button
            key={a.id}
            type="button"
            onClick={() => onSelect(a.prompt, { fromActionId: a.id })}
            className="inline-flex items-center rounded-full bg-surface-700 px-3 py-1.5 text-xs font-medium text-surface-200 hover:bg-surface-600 active:bg-surface-500 transition-colors border border-surface-600"
          >
            {a.label}
          </button>
        ))}
      </div>
    </div>
  );
}
