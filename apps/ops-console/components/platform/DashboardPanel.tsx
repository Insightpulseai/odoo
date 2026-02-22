import { useOpsDeployments } from "@/hooks/use-ops-deployments";
import { useOpsRuns } from "@/hooks/use-ops-runs";
import { ago, statusColor, statusIcon } from "@/lib/mock-data";
import { PlatformCard, Stat, Badge } from "./Visuals";

export const DashboardPanel = () => {
  const { data: deployments, isLoading: loadingDeploys } = useOpsDeployments(4);
  const { data: runs, isLoading: loadingRuns } = useOpsRuns(10);

  const syncRuns = runs?.filter(r => r.kind === 'resync') || [];
  const syncErrors = syncRuns.filter((s) => s.status === "failed").length;

  const buildsToday = deployments?.filter(d =>
    new Date(d.created_at).toDateString() === new Date().toDateString()
  ).length || 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* Status bar */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "10px 16px",
          background: "#0d1f0d",
          border: "1px solid #166534",
          borderRadius: 8,
        }}
      >
        <span
          style={{
            width: 8,
            height: 8,
            borderRadius: "50%",
            background: "#22c55e",
            boxShadow: "0 0 8px #22c55e",
          }}
        />
        <span style={{ fontSize: 12, color: "#86efac", fontWeight: 600 }}>
          Production Online
        </span>
        <span
          style={{
            fontSize: 11,
            color: "#4ade80",
            marginLeft: "auto",
            fontFamily: "'JetBrains Mono', monospace",
          }}
        >
          erp.insightpulseai.com
        </span>
      </div>

      {/* Stats row */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 12,
        }}
      >
        <PlatformCard
          title=""
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 16,
          }}
        >
          <Stat label="BUILDS TODAY" value={String(buildsToday)} sub="across all envs" />
        </PlatformCard>
        <PlatformCard
          title=""
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 16,
          }}
        >
          <Stat
            label="RECORDS SYNCED"
            value="Coming Soon"
            sub="Wiring to ops.sync_checkpoints"
            color="#60a5fa"
          />
        </PlatformCard>
        <PlatformCard
          title=""
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 16,
          }}
        >
          <Stat
            label="FAILED RUNS"
            value={String(runs?.filter(r => r.status === 'failed').length || 0)}
            sub={syncErrors > 0 ? `${syncErrors} sync failure(s)` : "all clear"}
            color={syncErrors > 0 ? "#ef4444" : "#22c55e"}
          />
        </PlatformCard>
        <PlatformCard
          title=""
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 16,
          }}
        >
          <Stat
            label="OCA MODULES"
            value="Hydrating"
            sub="Syncing with ops.module_versions"
            color="#a78bfa"
          />
        </PlatformCard>
      </div>

      {/* Two column layout */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        {/* Recent builds */}
        <PlatformCard title="Recent Builds" subtitle="Git push → deploy pipeline">
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {loadingDeploys ? (
              <div style={{ padding: 10, fontSize: 11, color: "#52525b" }}>Loading SSOT state...</div>
            ) : deployments?.map((b) => (
              <div
                key={b.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "8px 10px",
                  background: "#0a0a0b",
                  borderRadius: 6,
                  border: "1px solid #1a1a1e",
                }}
              >
                <span
                  style={{
                    color: statusColor(b.status),
                    fontSize: 14,
                    width: 18,
                    textAlign: "center",
                  }}
                >
                  {statusIcon(b.status)}
                </span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: 11,
                      color: "#e4e4e7",
                      fontFamily: "'JetBrains Mono', monospace",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {b.commit_message || "No commit message"}
                  </div>
                  <div style={{ fontSize: 10, color: "#52525b", marginTop: 2 }}>
                    {b.branch} · <span style={{ color: "#71717a" }}>{b.commit_sha?.slice(0, 7)}</span> · {ago(b.created_at)}
                  </div>
                </div>
                <Badge color={statusColor(b.status)}>{b.status}</Badge>
              </div>
            ))}
            {!loadingDeploys && (!deployments || deployments.length === 0) && (
              <div style={{ padding: 10, fontSize: 11, color: "#52525b" }}>No deployments found.</div>
            )}
          </div>
        </PlatformCard>

        {/* Sync status */}
        <PlatformCard title="Sync Pipeline" subtitle="Odoo SOR → Supabase SSOT">
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {loadingRuns ? (
              <div style={{ padding: 10, fontSize: 11, color: "#52525b" }}>Monitoring pipeline...</div>
            ) : syncRuns.map((s) => (
              <div
                key={s.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "8px 10px",
                  background: "#0a0a0b",
                  borderRadius: 6,
                  border: "1px solid #1a1a1e",
                }}
              >
                <span
                  style={{
                    color: statusColor(s.status),
                    fontSize: 14,
                    width: 18,
                    textAlign: "center",
                  }}
                >
                  {statusIcon(s.status)}
                </span>
                <div style={{ flex: 1 }}>
                  <div
                    style={{
                      fontSize: 11,
                      color: "#e4e4e7",
                      fontFamily: "'JetBrains Mono', monospace",
                    }}
                  >
                    {s.environment?.slug?.toUpperCase()} Sync
                  </div>
                  <div style={{ fontSize: 10, color: "#52525b", marginTop: 2 }}>
                    Task ID: {s.id.slice(0, 8)} · {ago(s.created_at)}
                  </div>
                </div>
                {s.error_message && (
                  <span
                    style={{
                      fontSize: 10,
                      color: "#ef4444",
                      maxWidth: 120,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {s.error_message}
                  </span>
                )}
                <Badge color={statusColor(s.status)}>{s.status}</Badge>
              </div>
            ))}
            {!loadingRuns && syncRuns.length === 0 && (
              <div style={{ padding: 10, fontSize: 11, color: "#52525b" }}>No sync activity recorded.</div>
            )}
          </div>
        </PlatformCard>
      </div>
    </div>
  );
};
