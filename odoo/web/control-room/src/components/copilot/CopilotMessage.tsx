'use client';

import { CopilotMessage } from "./types";
import clsx from "clsx";

interface Props {
  message: CopilotMessage;
  isLast: boolean;
}

export function CopilotMessageBubble({ message, isLast }: Props) {
  const isUser = message.role === "user";

  const baseClasses = clsx(
    "max-w-[80%] rounded-2xl px-3.5 py-2.5 text-sm shadow-sm border transition-all"
  );

  const userClasses = clsx(
    "ml-auto bg-primary-500/20 border-primary-500/40 text-white rounded-br-sm"
  );

  const aiClasses = clsx(
    "mr-auto bg-surface-700 border-surface-600 text-white rounded-bl-sm"
  );

  return (
    <div className={clsx("flex w-full", isUser ? "justify-end" : "justify-start")}>
      <div className={clsx(baseClasses, isUser ? userClasses : aiClasses)}>
        {!isUser && (
          <div className="mb-1 text-[0.65rem] uppercase tracking-[0.08em] text-primary-400">
            Copilot
          </div>
        )}
        <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
        <div className="mt-1.5 flex items-center justify-between text-[0.65rem] text-surface-400">
          <span>
            {new Date(message.createdAt).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
        </div>
      </div>
    </div>
  );
}
