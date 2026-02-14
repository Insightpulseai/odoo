import { useEffect, useState } from "react";

type Output = {
  message?: string;
  server_time?: string;
  [key: string]: unknown;
};

export function App() {
  const [output, setOutput] = useState<Output>(
    () => (window.openai?.toolOutput as Output) ?? {}
  );
  const [busy, setBusy] = useState(false);

  // Sync if host re-renders with new toolOutput
  useEffect(() => {
    const id = window.setInterval(() => {
      const next = (window.openai?.toolOutput as Output) ?? {};
      setOutput(next);
    }, 300);
    return () => window.clearInterval(id);
  }, []);

  async function ping() {
    if (!window.openai?.callTool) return;
    setBusy(true);
    try {
      const res = (await window.openai.callTool("ipai_ping", {})) as {
        structuredContent?: Output;
      };
      setOutput(res?.structuredContent ?? res ?? {});
      await window.openai.sendFollowUpMessage?.({
        prompt: "Ping received. Widget updated.",
      });
    } finally {
      setBusy(false);
    }
  }

  function toggleTheme() {
    document.documentElement.classList.toggle("ipai-theme-light");
  }

  return (
    <div className="p-3">
      <div className="rounded-ipai border border-ipai-border bg-ipai-surface shadow-ipai">
        <div className="p-4 space-y-3">
          <div className="text-ipai-text font-semibold">
            IPAI ChatGPT App Widget
          </div>
          <div className="text-ipai-muted">
            {output?.message ?? "No tool output yet."}
          </div>
          {output?.server_time && (
            <div className="text-ipai-faint text-sm">
              server_time: {output.server_time}
            </div>
          )}
          <div className="flex gap-2 pt-2">
            <button
              disabled={busy || !window.openai?.callTool}
              onClick={ping}
              className="rounded-ipai-sm bg-ipai-primary text-black font-semibold px-4 py-2 disabled:opacity-50 hover:bg-ipai-primary2 transition-colors"
            >
              {busy ? "Pinging..." : "Ping server"}
            </button>
            <button
              onClick={toggleTheme}
              className="rounded-ipai-sm border border-ipai-border-strong bg-ipai-surface2 text-ipai-text px-4 py-2 hover:bg-ipai-border transition-colors"
            >
              Toggle light
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
