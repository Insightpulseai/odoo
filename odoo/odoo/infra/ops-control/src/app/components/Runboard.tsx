import { useState, useEffect } from "react";
import { Session, listSessions, createSession, listRuns, createRun, cancelRun } from "../../lib/runs";
import { supabase } from "../../lib/supabase";
import { RunLane } from "./RunLane";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { toast } from "sonner";
import { PlusCircle, Play, Archive } from "lucide-react";

interface RunboardProps {
  onViewRun?: (runId: string) => void;
}

export function Runboard({ onViewRun }: RunboardProps) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [newSessionIntent, setNewSessionIntent] = useState("");
  const [showNewSession, setShowNewSession] = useState(false);

  const LANES = ["A", "B", "C", "D"];

  useEffect(() => {
    loadSessions();
  }, []);

  // Subscribe to session changes
  useEffect(() => {
    const channel = supabase
      .channel("sessions-changes")
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "sessions",
        },
        () => {
          loadSessions();
        }
      )
      .subscribe();

    return () => {
      channel.unsubscribe();
    };
  }, []);

  async function loadSessions() {
    const data = await listSessions(25);
    setSessions(data.filter((s) => s.status === "active"));
    
    // Auto-select first session if none selected
    if (!activeSessionId && data.length > 0) {
      setActiveSessionId(data[0].id);
    }
  }

  async function handleCreateSession() {
    if (!newSessionIntent.trim()) {
      toast.error("Please enter an intent");
      return;
    }

    try {
      const session = await createSession(`Session ${sessions.length + 1}`, newSessionIntent);
      toast.success("Session created");
      setNewSessionIntent("");
      setShowNewSession(false);
      setActiveSessionId(session.id);
      await loadSessions();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to create session");
    }
  }

  async function handleRunInLane(lane: string, intent: string) {
    if (!activeSessionId) {
      toast.error("Please select a session");
      return;
    }

    try {
      const runId = await createRun({
        session_id: activeSessionId,
        lane,
        intent,
        kind: "deploy", // TODO: parse from intent
        env: "dev",
        priority: 100,
      });

      // Trigger executor
      await supabase.functions.invoke("ops-executor", {
        body: { run_id: runId, worker_id: "ui-direct" },
      });

      toast.success(`Run started in lane ${lane}`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to start run");
    }
  }

  async function handleCancelRun(runId: string) {
    try {
      await cancelRun(runId);
      toast.success("Run canceled");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to cancel run");
    }
  }

  const activeSession = sessions.find((s) => s.id === activeSessionId);

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b bg-white px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Runboard</h2>
            <p className="text-sm opacity-60 mt-1">Parallel execution lanes (Claude Code Web style)</p>
          </div>
          <div className="flex items-center gap-3">
            {/* Session selector */}
            <select
              className="px-3 py-2 border rounded-lg bg-white"
              value={activeSessionId || ""}
              onChange={(e) => setActiveSessionId(e.target.value || null)}
            >
              <option value="">Select session...</option>
              {sessions.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.title} - {s.intent.slice(0, 40)}
                </option>
              ))}
            </select>

            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowNewSession(!showNewSession)}
            >
              <PlusCircle className="w-4 h-4 mr-2" />
              New Session
            </Button>
          </div>
        </div>

        {/* New session input */}
        {showNewSession && (
          <div className="mt-4 flex gap-2">
            <Input
              placeholder="Enter session intent (e.g., Deploy prod + fix schema)"
              value={newSessionIntent}
              onChange={(e) => setNewSessionIntent(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleCreateSession()}
              className="flex-1"
            />
            <Button onClick={handleCreateSession}>
              <Play className="w-4 h-4 mr-2" />
              Create
            </Button>
          </div>
        )}

        {/* Active session info */}
        {activeSession && (
          <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="text-sm font-medium">Active: {activeSession.title}</div>
            <div className="text-xs opacity-70 mt-1">{activeSession.intent}</div>
          </div>
        )}
      </div>

      {/* Lanes Grid */}
      <div className="flex-1 overflow-auto p-6">
        {!activeSessionId ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center opacity-70">
              <Archive className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">No active session</p>
              <p className="text-sm mt-2">Create a new session to start running tasks in parallel lanes</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            {LANES.map((lane) => (
              <RunLane
                key={lane}
                lane={lane}
                sessionId={activeSessionId}
                onRunInLane={(intent) => handleRunInLane(lane, intent)}
                onCancelRun={handleCancelRun}
                onViewRun={onViewRun}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}