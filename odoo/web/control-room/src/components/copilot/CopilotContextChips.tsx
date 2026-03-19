'use client';

import { CopilotRecordSummary } from "./types";

interface Props {
  record: CopilotRecordSummary;
}

export function CopilotContextChips({ record }: Props) {
  if (!record.fields?.length) return null;

  return (
    <div className="px-4 pt-2 pb-1 border-b border-surface-700 bg-surface-800/80 backdrop-blur-sm">
      <div className="flex flex-wrap gap-1.5">
        {record.fields.slice(0, 5).map((f) => (
          <span
            key={f.key}
            className="inline-flex items-center rounded-full border border-surface-600 bg-surface-700 px-2.5 py-1 text-xs font-medium text-surface-100 shadow-sm"
          >
            <span className="mr-1 text-[0.7rem] uppercase tracking-wide text-surface-400">
              {f.label}
            </span>
            <span className="truncate max-w-[8rem]">{String(f.value ?? "—")}</span>
          </span>
        ))}
      </div>
    </div>
  );
}
