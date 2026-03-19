import { useState, useEffect } from "react";
import { supabase } from "../../lib/supabase";
import type { RunEvent, Artifact } from "../../core/types";

interface Run {
  id: string;
  status: string;
  env: string;
  kind: string;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  error_message: string | null;
}

interface RunLogViewerEnhancedProps {
  runId: string;
  onClose: () => void;
}

export function RunLogViewerEnhanced({ runId, onClose }: RunLogViewerEnhancedProps) {
  const [events, setEvents] = useState<RunEvent[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [run, setRun] = useState<Run | null>(null);

  useEffect(() => {
    let mounted = true;

    // Load initial data
    (async () => {
      const { data: runData } = await supabase
        .from("runs")
        .select("*")
        .eq("id", runId)
        .single();

      if (mounted && runData) setRun(runData as Run);

      const { data: eventsData } = await supabase
        .from("run_events")
        .select("*")
        .eq("run_id", runId)
        .order("ts", { ascending: false })
        .limit(200);

      if (mounted && eventsData) {
        setEvents(
          eventsData.map((e: any) => ({
            id: e.id.toString(),
            timestamp: e.ts,
            level: e.level as RunEvent["level"],
            source: e.source,
            message: e.message,
            data: e.data,
          }))
        );
      }

      const { data: artifactsData } = await supabase
        .from("artifacts")
        .select("*")
        .eq("run_id", runId)
        .order("created_at", { ascending: false });

      if (mounted && artifactsData) {
        setArtifacts(
          artifactsData.map((a: any) => ({
            id: a.id.toString(),
            kind: a.kind as Artifact["kind"],
            title: a.title,
            value: a.value,
          }))
        );
      }
    })();

    // Subscribe to realtime updates
    const channel = supabase
      .channel(`run-logs-${runId}`)
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "ops",
          table: "run_events",
          filter: `run_id=eq.${runId}`,
        },
        (payload) => {
          const newEvent = payload.new as any;
          setEvents((prev) => [
            {
              id: newEvent.id.toString(),
              timestamp: newEvent.ts,
              level: newEvent.level,
              source: newEvent.source,
              message: newEvent.message,
              data: newEvent.data,
            },
            ...prev,
          ]);
        }
      )
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "ops",
          table: "artifacts",
          filter: `run_id=eq.${runId}`,
        },
        (payload) => {
          const newArtifact = payload.new as any;
          setArtifacts((prev) => [
            {
              id: newArtifact.id.toString(),
              kind: newArtifact.kind,
              title: newArtifact.title,
              value: newArtifact.value,
            },
            ...prev,
          ]);
        }
      )
      .on(
        "postgres_changes",
        {
          event: "UPDATE",
          schema: "ops",
          table: "runs",
          filter: `id=eq.${runId}`,
        },
        (payload) => {
          setRun(payload.new as Run);
        }
      )
      .subscribe();

    return () => {
      mounted = false;
      supabase.removeChannel(channel);
    };
  }, [runId]);

  const getLevelColor = (level: string) => {
    switch (level) {
      case "success":
        return "text-green-600 bg-green-50";
      case "error":
        return "text-red-600 bg-red-50";
      case "warn":
        return "text-yellow-600 bg-yellow-50";
      case "debug":
        return "text-gray-600 bg-gray-50";
      default:
        return "text-blue-600 bg-blue-50";
    }
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      queued: "bg-gray-100 text-gray-700",
      running: "bg-blue-100 text-blue-700",
      success: "bg-green-100 text-green-700",
      error: "bg-red-100 text-red-700",
    };
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${colors[status as keyof typeof colors] || colors.queued}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="w-full max-w-6xl bg-white rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between p-4 border-b bg-gray-50">
          <div>
            <div className="font-semibold text-lg">Run Logs</div>
            <div className="text-sm opacity-70 mt-1">
              Run ID: {runId.substring(0, 8)}
              {run && (
                <>
                  {" • "}
                  {getStatusBadge(run.status)}
                  {" • "}
                  {run.kind}
                  {" • "}
                  {run.env}
                </>
              )}
            </div>
          </div>
          <button
            className="px-4 py-2 border rounded-lg hover:bg-gray-100 transition-colors"
            onClick={onClose}
          >
            Close
          </button>
        </div>

        <div className="flex-1 grid grid-cols-3 gap-0 overflow-hidden">
          <div className="col-span-2 p-4 border-r overflow-y-auto">
            <div className="font-semibold mb-3">Events ({events.length})</div>
            <div className="space-y-2">
              {events.length === 0 && (
                <div className="text-center py-12 opacity-70">
                  No events yet. Waiting for executor...
                </div>
              )}
              {events.map((e) => (
                <div key={e.id} className={`p-3 border rounded-xl ${getLevelColor(e.level)}`}>
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-medium">
                      [{e.level.toUpperCase()}] {e.source}
                    </div>
                    <div className="text-xs opacity-60">
                      {new Date(e.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                  <div className="text-sm mt-1">{e.message}</div>
                  {e.data && Object.keys(e.data).length > 0 && (
                    <pre className="mt-2 text-xs bg-white/50 p-2 rounded-lg overflow-auto max-h-32">
                      {JSON.stringify(e.data, null, 2)}
                    </pre>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="col-span-1 p-4 overflow-y-auto bg-gray-50">
            <div className="font-semibold mb-3">Artifacts ({artifacts.length})</div>
            <div className="space-y-2">
              {artifacts.length === 0 && (
                <div className="text-center py-12 opacity-70 text-sm">
                  No artifacts yet
                </div>
              )}
              {artifacts.map((a) => (
                <div key={a.id} className="p-3 border rounded-xl bg-white">
                  <div className="text-sm font-medium">{a.title}</div>
                  <div className="text-xs opacity-60 mb-2">{a.kind}</div>
                  {a.kind === "link" ? (
                    <a
                      className="text-sm text-blue-600 hover:underline break-all"
                      href={a.value}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {a.value}
                    </a>
                  ) : (
                    <pre className="mt-2 text-xs bg-gray-50 p-2 rounded-lg overflow-auto max-h-48">
                      {a.value}
                    </pre>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}