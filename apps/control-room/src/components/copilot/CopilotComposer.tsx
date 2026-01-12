'use client';

import { FormEvent, useState, KeyboardEvent } from "react";

interface Props {
  onSend: (value: string) => void;
  disabled?: boolean;
}

export function CopilotComposer({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!value.trim() || disabled) return;
    onSend(value.trim());
    setValue("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!value.trim() || disabled) return;
      onSend(value.trim());
      setValue("");
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-surface-700 bg-surface-800/95 px-3 pt-2 pb-3"
    >
      <div className="rounded-2xl border border-surface-600 bg-surface-700/80 px-3 py-2 focus-within:border-primary-500 focus-within:ring-1 focus-within:ring-primary-500 transition-all">
        <textarea
          rows={2}
          className="w-full resize-none bg-transparent text-sm text-white outline-none placeholder:text-surface-400"
          placeholder="Ask about this record..."
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
        />
        <div className="mt-1.5 flex items-center justify-between text-[0.65rem] text-surface-400">
          <span>Enter to send - Shift+Enter for new line</span>
          <button
            type="submit"
            disabled={disabled || !value.trim()}
            className="inline-flex items-center rounded-full bg-primary-500 px-3 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-primary-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </form>
  );
}
