import { useState, useEffect } from "react";
import { supabase } from "../../lib/supabase";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Badge } from "./ui/badge";
import { Play, X, Eye, Loader2, Activity } from "lucide-react";

interface Run {
  id: string;
  intent: string;
  status: string;
  created_at: string;
  claimed_by: string | null;
  heartbeat_at: string | null;
}

interface RunLaneProps {
  lane: string;
  sessionId: string;
  onRunInLane: (intent: string) => void;
  onCancelRun: (runId: string) => void;
  onViewRun?: (runId: string) => void;
}

export function RunLane({ lane, sessionId, onRunInLane, onCancelRun, onViewRun }: RunLaneProps) {
  const [runs, setRuns] = useState<Run[]>([]);
  const [newIntent, setNewIntent] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadRuns();
  }, [sessionId, lane]);

  // Subscribe to run changes for this lane
  useEffect(() => {
    const channel = supabase
      .channel(`lane-${lane}-${sessionId}`)
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "runs",
          filter: `session_id=eq.${sessionId}`,
        },
        () => {
          loadRuns();
        }
      )
      .subscribe();

    return () => {
      channel.unsubscribe();
    };
  }, [sessionId, lane]);

  async function loadRuns() {
    const { data, error } = await supabase
      .from("runs")
      .select("id, intent, status, created_at, claimed_by, heartbeat_at")
      .eq("session_id", sessionId)
      .eq("lane", lane)
      .order("created_at", { ascending: false })
      .limit(10);

    if (error) {
      console.error("Error loading runs:", error);
      return;
    }

    setRuns(data || []);
  }

  async function handleRun() {
    if (!newIntent.trim()) return;
    
    setLoading(true);
    try {
      await onRunInLane(newIntent);
      setNewIntent("");
    } finally {
      setLoading(false);
    }
  }

  const activeRun = runs.find((r) => r.status === "running" || r.status === "queued");
  const isAlive = activeRun?.heartbeat_at
    ? new Date().getTime() - new Date(activeRun.heartbeat_at).getTime() < 10000
    : false;

  return (
    <div className="bg-white border rounded-xl p-4 flex flex-col h-[600px]">
      {/* Lane Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
            {lane}
          </div>
          <div className="font-semibold">Lane {lane}</div>
        </div>
        {activeRun && (
          <Badge variant={isAlive ? "default" : "secondary"}>
            {activeRun.status === "running" && isAlive ? (
              <Activity className="w-3 h-3 mr-1 animate-pulse" />
            ) : (
              <Loader2 className="w-3 h-3 mr-1 animate-spin" />
            )}
            {activeRun.status}
          </Badge>
        )}
      </div>

      {/* Intent Input */}
      <div className="mb-4">
        <div className="flex gap-2">
          <Input
            placeholder={`Run in lane ${lane}...`}
            value={newIntent}
            onChange={(e) => setNewIntent(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleRun()}
            className="flex-1 text-sm"
            disabled={loading}
          />
          <Button size="sm" onClick={handleRun} disabled={loading || !newIntent.trim()}>
            <Play className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Runs List */}
      <div className="flex-1 overflow-y-auto space-y-2">
        {runs.length === 0 && (
          <div className="text-center py-8 opacity-50">
            <p className="text-sm">No runs yet</p>
            <p className="text-xs mt-1">Start a run above</p>
          </div>
        )}

        {runs.map((run) => {
          const isActive = run.status === "running" || run.status === "queued";
          const runIsAlive = run.heartbeat_at
            ? new Date().getTime() - new Date(run.heartbeat_at).getTime() < 10000
            : false;

          return (
            <div
              key={run.id}
              className={`p-3 rounded-lg border text-sm ${
                isActive ? "bg-blue-50 border-blue-200" : "bg-gray-50 border-gray-200"
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{run.intent}</div>
                  <div className="text-xs opacity-60 mt-1">
                    {new Date(run.created_at).toLocaleTimeString()}
                    {run.claimed_by && ` • ${run.claimed_by}`}
                  </div>
                </div>
                <div className="flex gap-1">
                  {onViewRun && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onViewRun(run.id)}
                      className="h-7 w-7 p-0"
                    >
                      <Eye className="w-3.5 h-3.5" />
                    </Button>
                  )}
                  {isActive && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onCancelRun(run.id)}
                      className="h-7 w-7 p-0 text-red-600 hover:text-red-700"
                    >
                      <X className="w-3.5 h-3.5" />
                    </Button>
                  )}
                </div>
              </div>

              {/* Status indicator */}
              <div className="mt-2">
                <Badge
                  variant={
                    run.status === "succeeded"
                      ? "default"
                      : run.status === "failed"
                      ? "destructive"
                      : run.status === "canceled"
                      ? "secondary"
                      : "outline"
                  }
                  className="text-xs"
                >
                  {run.status === "running" && runIsAlive && (
                    <Activity className="w-2.5 h-2.5 mr-1 animate-pulse" />
                  )}
                  {run.status}
                </Badge>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}