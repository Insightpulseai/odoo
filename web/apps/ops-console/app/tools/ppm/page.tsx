// Server Component — fetches directly from Supabase via service role.
// The internal API routes (/api/ppm/*) are NOT called from the browser;
// they exist for CI and server-to-server callers only.
import { createClient } from "@supabase/supabase-js";

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
  active:    "bg-green-100 text-green-800",
  "on-hold": "bg-yellow-100 text-yellow-800",
  completed: "bg-blue-100 text-blue-800",
  cancelled: "bg-gray-100 text-gray-600",
};

async function getData(): Promise<{
  initiatives: Initiative[];
  rollupMap: Record<string, Rollup>;
  error: string | null;
}> {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const serviceKey  = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!supabaseUrl || !serviceKey) {
    return { initiatives: [], rollupMap: {}, error: "Supabase env not configured" };
  }

  const supabase = createClient(supabaseUrl, serviceKey, {
    auth: { persistSession: false },
  });

  const [initResult, rollupResult] = await Promise.all([
    supabase
      .schema("ops")
      .from("ppm_initiatives")
      .select("initiative_id, name, owner, status, spec_slug, target_date")
      .order("status")
      .order("initiative_id"),
    supabase
      .schema("ops")
      .from("ppm_status_rollups")
      .select("initiative_id, blocking_findings, merged_prs_30d, computed_at")
      .order("computed_at", { ascending: false })
      .limit(500),
  ]);

  if (initResult.error) {
    return { initiatives: [], rollupMap: {}, error: initResult.error.message };
  }

  // Latest rollup per initiative
  const rollupMap: Record<string, Rollup> = {};
  for (const r of rollupResult.data ?? []) {
    if (!rollupMap[r.initiative_id] || r.computed_at > rollupMap[r.initiative_id].computed_at) {
      rollupMap[r.initiative_id] = r;
    }
  }

  return { initiatives: (initResult.data as Initiative[]) ?? [], rollupMap, error: null };
}

export default async function PPMPage() {
  const { initiatives, rollupMap, error } = await getData();

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
              const r = rollupMap[i.initiative_id];
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
                    {r
                      ? r.blocking_findings > 0
                        ? <span className="text-red-600 font-semibold">⚠️ {r.blocking_findings}</span>
                        : <span className="text-gray-400">0</span>
                      : <span className="text-gray-300">—</span>}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-600">
                    {r?.merged_prs_30d ?? "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{i.target_date ?? "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
