"use client";

import { useEffect, useState } from "react";

interface Initiative {
  initiative_id: string;
  name: string;
  owner: string | null;
  status: string;
  spec_slug: string | null;
  target_date: string | null;
}

interface Rollup {
  initiative_id: string;
  blocking_findings: number;
  merged_prs_30d: number;
  computed_at: string;
}

const STATUS_BADGE: Record<string, string> = {
  active: "bg-green-100 text-green-800",
  "on-hold": "bg-yellow-100 text-yellow-800",
  completed: "bg-blue-100 text-blue-800",
  cancelled: "bg-gray-100 text-gray-600",
};

export default function PPMPage() {
  const [initiatives, setInitiatives] = useState<Initiative[]>([]);
  const [rollups, setRollups] = useState<Record<string, Rollup>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [initRes, rollupRes] = await Promise.all([
          fetch("/api/ppm/initiatives"),
          fetch("/api/ppm/rollups"),
        ]);
        if (!initRes.ok) throw new Error(`initiatives: ${initRes.status}`);
        const { data: inits } = await initRes.json();
        const { data: rolls } = await rollupRes.json();

        setInitiatives(inits ?? []);

        // Index rollups by initiative_id (latest per initiative)
        const map: Record<string, Rollup> = {};
        for (const r of rolls ?? []) {
          if (!map[r.initiative_id] || r.computed_at > map[r.initiative_id].computed_at) {
            map[r.initiative_id] = r;
          }
        }
        setRollups(map);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Load failed");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="p-6 text-sm text-gray-500 animate-pulse">Loading portfolio...</div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-sm text-red-600 bg-red-50 rounded border border-red-200">
        {error}
      </div>
    );
  }

  if (initiatives.length === 0) {
    return (
      <div className="p-6 text-sm text-gray-500">
        No initiatives yet.{" "}
        <span className="font-mono text-gray-400">
          Run ops-ppm-rollup to sync ssot/ppm/portfolio.yaml.
        </span>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-900">Portfolio</h1>
        <span className="text-xs text-gray-400">{initiatives.length} initiatives</span>
      </div>

      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wider">
            <tr>
              <th className="px-4 py-3 text-left">ID</th>
              <th className="px-4 py-3 text-left">Name</th>
              <th className="px-4 py-3 text-left">Status</th>
              <th className="px-4 py-3 text-left">Owner</th>
              <th className="px-4 py-3 text-right">Blockers</th>
              <th className="px-4 py-3 text-right">PRs (30d)</th>
              <th className="px-4 py-3 text-left">Target</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {initiatives.map((i) => {
              const r = rollups[i.initiative_id];
              return (
                <tr key={i.initiative_id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-gray-500 text-xs">
                    {i.initiative_id}
                  </td>
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {i.spec_slug ? (
                      <a
                        href={`https://github.com/Insightpulseai/odoo/tree/main/spec/${i.spec_slug}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:underline text-blue-700"
                      >
                        {i.name}
                      </a>
                    ) : (
                      i.name
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                        STATUS_BADGE[i.status] ?? "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {i.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-600 text-xs">{i.owner ?? "—"}</td>
                  <td className="px-4 py-3 text-right">
                    {r ? (
                      r.blocking_findings > 0 ? (
                        <span className="text-red-600 font-semibold">
                          ⚠️ {r.blocking_findings}
                        </span>
                      ) : (
                        <span className="text-gray-400">0</span>
                      )
                    ) : (
                      <span className="text-gray-300">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-600">
                    {r?.merged_prs_30d ?? "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs">
                    {i.target_date ?? "—"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
