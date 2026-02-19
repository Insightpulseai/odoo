import { createClient } from "@/lib/supabase/server";

interface MetricDataPoint {
  timestamp: string;
  value: number;
}

interface Metric {
  key: string;
  label: string;
  current: string;
  data: MetricDataPoint[];
  unit: string;
}

function formatTime(ts: string): string {
  const date = new Date(ts);
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

export default async function BuildMonitorPage({
  params,
}: {
  params: Promise<{ projectId: string; buildId: string }>;
}) {
  const { projectId } = await params;

  const supabase = createClient();

  // Fetch metrics for the last hour
  const metricKeys = ["cpu_pct", "mem_mb", "p95_ms", "req_rate"];
  const metricConfigs = {
    cpu_pct: { label: "CPU Usage", unit: "%" },
    mem_mb: { label: "Memory Usage", unit: "MB" },
    p95_ms: { label: "Response Time (P95)", unit: "ms" },
    req_rate: { label: "Requests/Min", unit: "req/min" },
  };

  const metricsPromises = metricKeys.map((metricKey) =>
    supabase
      .rpc("ops.project_metrics", {
        p_project_id: projectId,
        p_metric: metricKey,
        p_hours: 1,
      })
      .then((res) => ({
        key: metricKey,
        data: res.data || [],
        error: res.error,
      }))
  );

  const metricsResults = await Promise.all(metricsPromises);

  // Check for errors
  const firstError = metricsResults.find((r) => r.error);
  if (firstError?.error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Performance Monitor</h2>
        </div>
        <div className="rounded-md bg-red-50 p-4">
          <h3 className="text-sm font-medium text-red-800">
            Error loading metrics
          </h3>
          <p className="mt-2 text-sm text-red-700">
            {firstError.error.message}
          </p>
        </div>
      </div>
    );
  }

  const metrics: Metric[] = metricsResults.map((result) => {
    const config =
      metricConfigs[result.key as keyof typeof metricConfigs];
    const data = result.data.map((d: any) => ({
      timestamp: formatTime(d.ts),
      value: Number(d.value),
    }));
    const current = data.length > 0 ? data[0].value : 0;

    return {
      key: result.key,
      label: config.label,
      current: `${current.toFixed(1)} ${config.unit}`,
      unit: config.unit,
      data: data.reverse(), // Oldest to newest for chart
    };
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Performance Monitor</h2>
        <div className="flex gap-2">
          <select className="px-3 py-1.5 text-sm border border-gray-300 rounded">
            <option>Last 5 minutes</option>
            <option>Last hour</option>
            <option>Last 24 hours</option>
          </select>
          <button className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50">
            Refresh
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-6">
        {metrics.map((metric) => (
          <div
            key={metric.key}
            className="bg-white border border-gray-200 rounded-lg p-4"
          >
            {/* Metric Header */}
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-700">
                {metric.label}
              </h3>
              <span className="text-2xl font-bold text-gray-900">
                {metric.current}
              </span>
            </div>

            {/* Simple Chart Visualization */}
            <div className="space-y-2">
              <div className="flex items-end gap-1 h-32">
                {metric.data.map((point, idx) => {
                  const maxValue = Math.max(...metric.data.map((d) => d.value));
                  const heightPercent = (point.value / maxValue) * 100;

                  return (
                    <div
                      key={idx}
                      className="flex-1 bg-blue-500 rounded-t transition-all hover:bg-blue-600"
                      style={{ height: `${heightPercent}%` }}
                      title={`${point.timestamp}: ${point.value}${metric.unit}`}
                    />
                  );
                })}
              </div>

              {/* Time Labels */}
              <div className="flex justify-between text-xs text-gray-500">
                {metric.data.map((point, idx) => (
                  <span key={idx}>{point.timestamp}</span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Additional Metrics Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
          <h3 className="text-sm font-semibold">Health Metrics</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {[
            { label: "Database Connections", value: "12 / 100", status: "healthy" },
            { label: "Cache Hit Rate", value: "94.2%", status: "healthy" },
            { label: "Error Rate", value: "0.01%", status: "healthy" },
            { label: "Uptime", value: "99.98%", status: "healthy" },
          ].map((item, idx) => (
            <div key={idx} className="px-4 py-3 flex items-center justify-between">
              <span className="text-sm text-gray-700">{item.label}</span>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{item.value}</span>
                <span className="w-2 h-2 bg-green-500 rounded-full" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
