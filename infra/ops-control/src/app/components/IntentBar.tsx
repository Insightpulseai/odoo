import { useState } from "react";

interface IntentBarProps {
  onSubmit: (intent: string) => void;
  busy?: boolean;
}

export function IntentBar({ onSubmit, busy }: IntentBarProps) {
  const [intent, setIntent] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = intent.trim();
    if (trimmed && !busy) {
      setIntent("");
      onSubmit(trimmed);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 items-center p-4 border rounded-2xl bg-white shadow-sm">
      <input
        className="flex-1 px-4 py-2 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder='Type intent, e.g. "fix vercel env var missing SUPABASE_SERVICE_ROLE"'
        value={intent}
        onChange={(e) => setIntent(e.target.value)}
        disabled={busy}
      />
      <button
        type="submit"
        className="px-6 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        disabled={busy || !intent.trim()}
      >
        {busy ? "Running..." : "Run"}
      </button>
    </form>
  );
}
