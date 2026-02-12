import { createClient } from "@/lib/supabase/server";

interface ServiceStatus {
  name: string;
  status: "healthy" | "warning" | "critical";
  responseTime: string;
  uptime: string;
}

function formatRelativeTime(date: string | null): string {
  if (!date) return "Never";
  const ms = Date.now() - new Date(date).getTime();
  const minutes = Math.floor(ms / 60000);
  const hours = Math.floor(ms / 3600000);
  const days = Math.floor(ms / 86400000);

  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return "Just now";
}

export default async function ProjectMonitorPage({
  params,
}: {
  params: { projectId: string };
}) {
  const supabase = createClient();

  // Fetch monitoring data for all branches
  const { data: monitoringData, error: monitoringError } = await supabase
    .from("ops.monitoring")
    .select("*")
    .eq("project_id", params.projectId);

  if (monitoringError) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">System Monitor</h1>
        </div>
        <div className="rounded-md bg-red-50 p-4">
          <h3 className="text-sm font-medium text-red-800">
            Error loading monitoring data
          </h3>
          <p className="mt-2 text-sm text-red-700">
            {monitoringError.message}
          </p>
        </div>
      </div>
    );
  }

  // Calculate overall status
  const overallStatus =
    monitoringData && monitoringData.length > 0
      ? monitoringData.some((m: any) => m.status === "critical")
        ? "critical"
        : monitoringData.some((m: any) => m.status === "warning")
        ? "warning"
        : "healthy"
      : "unknown";

  // Get production branch monitoring if exists
  const productionMonitoring = monitoringData?.find(
    (m: any) => m.branch_id
  );

  // Build services array from monitoring data
  const services: ServiceStatus[] = monitoringData?.map((m: any) => ({
    name: `Branch: ${m.branch_id.substring(0, 8)}`,
    status: m.status,
    responseTime: m.request_rate
      ? `${Math.round(1000 / m.request_rate)}ms`
      : "—",
    uptime: "—",
  })) || [];

  // Get recent advisories as "incidents"
  const { data: recentIncidents, error: incidentsError } = await supabase
    .from("ops.advisories")
    .select("*")
    .eq("project_id", params.projectId)
    .order("created_at", { ascending: false })
    .limit(5);

  const statusColors = {
    healthy: { bg: "bg-green-100", text: "text-green-800", dot: "bg-green-500" },
    warning: {
      bg: "bg-yellow-100",
      text: "text-yellow-800",
      dot: "bg-yellow-500",
    },
    critical: { bg: "bg-red-100", text: "text-red-800", dot: "bg-red-500" },
    unknown: { bg: "bg-gray-100", text: "text-gray-800", dot: "bg-gray-500" },
  };

  const severityColors = {
    warning: "text-yellow-600",
    critical: "text-red-600",
    info: "text-blue-600",
  };

  // Fetch recent metrics for system metrics section
  const { data: cpuMetrics } = await supabase.rpc("ops.project_metrics", {
    p_project_id: params.projectId,
    p_metric: "cpu_pct",
    p_hours: 1,
  });

  const { data: memMetrics } = await supabase.rpc("ops.project_metrics", {
    p_project_id: params.projectId,
    p_metric: "mem_mb",
    p_hours: 1,
  });

  const { data: reqMetrics } = await supabase.rpc("ops.project_metrics", {
    p_project_id: params.projectId,
    p_metric: "req_rate",
    p_hours: 1,
  });

  const avgCpu =
    cpuMetrics && cpuMetrics.length > 0
      ? (
          cpuMetrics.reduce((sum: number, m: any) => sum + Number(m.value), 0) /
          cpuMetrics.length
        ).toFixed(1)
      : "0";

  const avgMem =
    memMetrics && memMetrics.length > 0
      ? Math.round(
          memMetrics.reduce((sum: number, m: any) => sum + Number(m.value), 0) /
            memMetrics.length
        )
      : 0;

  const avgReq =
    reqMetrics && reqMetrics.length > 0
      ? Math.round(
          reqMetrics.reduce((sum: number, m: any) => sum + Number(m.value), 0) /
            reqMetrics.length
        )
      : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">System Monitor</h1>
        <p className="text-sm text-gray-600 mt-1">
          Real-time health and performance monitoring
        </p>
      </div>

      {/* Overall Status */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center gap-3">
          <div
            className={`w-12 h-12 ${statusColors[overallStatus].bg} rounded-full flex items-center justify-center`}
          >
            <div
              className={`w-6 h-6 ${statusColors[overallStatus].dot} rounded-full ${
                overallStatus === "healthy" ? "animate-pulse" : ""
              }`}
            />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {overallStatus === "healthy"
                ? "All Systems Operational"
                : overallStatus === "warning"
                ? "Systems Degraded"
                : overallStatus === "critical"
                ? "Systems Critical"
                : "Status Unknown"}
            </h2>
            <p className="text-sm text-gray-600">
              Last checked: {new Date().toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* Service Status */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-semibold">Service Status</h2>
        </div>

        <div className="divide-y divide-gray-200">
          {services.length > 0 ? (
            services.map((service) => {
              const colors = statusColors[service.status];
              return (
                <div
                  key={service.name}
                  className="px-6 py-4 flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 ${colors.dot} rounded-full`} />
                    <span className="font-medium text-gray-900">
                      {service.name}
                    </span>
                  </div>

                  <div className="flex items-center gap-6 text-sm">
                    <div>
                      <span className="text-gray-500">Response:</span>{" "}
                      <span className="font-medium">{service.responseTime}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Uptime:</span>{" "}
                      <span className="font-medium">{service.uptime}</span>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${colors.bg} ${colors.text}`}
                    >
                      {service.status}
                    </span>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="px-6 py-4 text-center text-sm text-gray-500">
              No monitoring data available
            </div>
          )}
        </div>
      </div>

      {/* Recent Incidents */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-semibold">Recent Incidents</h2>
        </div>

        <div className="divide-y divide-gray-200">
          {recentIncidents && recentIncidents.length > 0 ? (
            recentIncidents.map((incident: any) => (
              <div key={incident.id} className="px-6 py-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium text-gray-900">
                        {incident.title}
                      </h3>
                      <span
                        className={`text-xs font-medium ${
                          severityColors[
                            incident.severity as keyof typeof severityColors
                          ]
                        }`}
                      >
                        {incident.severity.toUpperCase()}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                      <span>{formatRelativeTime(incident.created_at)}</span>
                      <span>{incident.category}</span>
                    </div>
                    <p className="mt-1 text-sm text-gray-700">
                      {incident.recommendation}
                    </p>
                  </div>
                  {incident.status === "resolved" && (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      ✓ Resolved
                    </span>
                  )}
                  {incident.status === "snoozed" && (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      ⏸ Snoozed
                    </span>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="px-6 py-4 text-center text-sm text-gray-500">
              No recent incidents
            </div>
          )}
        </div>
      </div>

      {/* System Metrics */}
      <div className="grid grid-cols-3 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="text-sm text-gray-600 mb-2">Avg CPU Usage</div>
          <div className="flex items-end justify-between">
            <div className="text-3xl font-bold text-gray-900">{avgCpu}%</div>
          </div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="text-sm text-gray-600 mb-2">Avg Memory</div>
          <div className="flex items-end justify-between">
            <div className="text-3xl font-bold text-gray-900">{avgMem} MB</div>
          </div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="text-sm text-gray-600 mb-2">Requests/Min</div>
          <div className="flex items-end justify-between">
            <div className="text-3xl font-bold text-gray-900">{avgReq}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
