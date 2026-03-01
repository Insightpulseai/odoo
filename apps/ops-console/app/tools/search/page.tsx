"use client";

import { useState, useCallback } from "react";
import { createClient } from "@supabase/supabase-js";

// Browser Supabase client — reads session cookies set by Supabase Auth.
// We create it lazily so it only runs in the browser (this is a Client Component).
function getBrowserClient() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { auth: { persistSession: true } }
  );
}

interface SearchResult {
  type: "initiative" | "run" | "finding";
  id: string;
  title: string;
  status: string | null;
  link: string;
}

const TYPE_ICON: Record<string, string> = {
  initiative: "🎯",
  run:        "⚙️",
  finding:    "⚠️",
};

const TYPE_LABEL: Record<string, string> = {
  initiative: "Initiative",
  run:        "Run",
  finding:    "Finding",
};

export default function SearchPage() {
  const [query, setQuery]     = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError]     = useState<string | null>(null);

  const doSearch = useCallback(
    async (q: string) => {
      if (!q.trim()) return;
      setLoading(true);
      setError(null);
      try {
        // Get current user session for auth forwarding (uses @supabase/supabase-js)
        const supabase = getBrowserClient();
        const { data: { session } } = await supabase.auth.getSession();
        const authHeader = session?.access_token
          ? `Bearer ${session.access_token}`
          : undefined;

        const headers: Record<string, string> = { "Content-Type": "application/json" };
        if (authHeader) headers["Authorization"] = authHeader;

        const res = await fetch("/api/search", {
          method: "POST",
          headers,
          body: JSON.stringify({ query: q.trim(), limit: 30 }),
        });

        if (res.status === 401) {
          setError("Sign in to search.");
          return;
        }
        if (!res.ok) throw new Error(`Search failed: ${res.status}`);

        const { results: r } = await res.json();
        setResults(r ?? []);
        setSearched(true);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Search error");
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return (
    <div className="p-6 space-y-4 max-w-2xl">
      <h1 className="text-xl font-semibold text-gray-900">Ops Search</h1>
      <p className="text-sm text-gray-500">
        Search across initiatives, agent runs, and convergence findings.
      </p>

      <form
        onSubmit={(e) => { e.preventDefault(); doSearch(query); }}
        className="flex gap-2"
      >
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search runs, specs, findings…"
          className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "…" : "Search"}
        </button>
      </form>

      {error && (
        <div className="text-sm text-red-600 bg-red-50 rounded border border-red-200 px-3 py-2">
          {error}
        </div>
      )}

      {searched && results.length === 0 && !loading && (
        <p className="text-sm text-gray-400">No results for &ldquo;{query}&rdquo;</p>
      )}

      {results.length > 0 && (
        <ul className="space-y-2">
          {results.map((r) => (
            <li key={`${r.type}-${r.id}`}>
              <a
                href={r.link}
                className="flex items-start gap-3 p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-colors"
              >
                <span className="text-lg leading-none mt-0.5">
                  {TYPE_ICON[r.type] ?? "📄"}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="font-medium text-sm text-gray-900 truncate">
                    {r.title}
                  </div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-xs text-gray-400">{TYPE_LABEL[r.type]}</span>
                    {r.status && (
                      <span className="text-xs text-gray-500">· {r.status}</span>
                    )}
                  </div>
                </div>
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
