import { useState, useEffect } from "react";
import { AppShell } from "./components/AppShell";
import { CommandBar } from "./components/CommandBar";
import { RunbookCard } from "./components/RunbookCard";
import { LogViewer } from "./components/LogViewer";
import { SetupBanner } from "./components/SetupBanner";
import { IntentBar } from "./components/IntentBar";
import { RunbookTemplateCard } from "./components/RunbookTemplateCard";
import { SpecKitPanel } from "./components/SpecKitPanel";
import { RunLogViewerEnhanced } from "./components/RunLogViewerEnhanced";
import { Runboard } from "./components/Runboard";
import { DatabaseSetup } from "./components/DatabaseSetup";
import { planFromPrompt } from "../core";
import type { RunbookPlan, RunEvent, Artifact } from "../core/types";
import { createRun, subscribeToRunEvents, getRunEvents, getRunArtifacts } from "../lib/runs";
import { supabase, isSupabaseConfigured } from "../lib/supabase";
import { toast } from "sonner";

interface Message {
  role: "user" | "assistant";
  content: string;
  plan?: RunbookPlan;
}

interface RunTemplate {
  id: string;
  slug: string;
  title: string;
  description: string;
  template_yaml: string;
}

interface Run {
  id: string;
  created_at: string;
  env: string;
  kind: string;
  status: string;
  plan: any;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<"chat" | "templates" | "runs" | "spec" | "runboard">("chat");
  const [templates, setTemplates] = useState<RunTemplate[]>([]);
  const [runs, setRuns] = useState<Run[]>([]);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [needsDatabaseSetup, setNeedsDatabaseSetup] = useState(false);
  const [checkingDatabase, setCheckingDatabase] = useState(true);

  // Chat state
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Welcome to the Ops Control Room. Try commands like:\n• Deploy prod\n• Check prod status\n• Generate spec for user dashboard\n• Fix production error\n• Run schema sync",
    },
  ]);

  const [currentEvents, setCurrentEvents] = useState<RunEvent[]>([]);
  const [currentArtifacts, setCurrentArtifacts] = useState<Artifact[]>([]);
  const [showLogViewer, setShowLogViewer] = useState(false);
  const [currentPlanTitle, setCurrentPlanTitle] = useState("");
  const [currentRunId, setCurrentRunId] = useState<string | null>(null);

  // Check if database is set up
  useEffect(() => {
    if (isSupabaseConfigured) {
      checkDatabaseSetup();
    }
  }, []);

  async function checkDatabaseSetup() {
    try {
      setCheckingDatabase(true);
      // Try to query the runs table
      const { error } = await supabase
        .from("runs")
        .select("id")
        .limit(1);

      if (error) {
        // If error code is PGRST205, it means table doesn't exist
        if (error.code === "PGRST205" || error.message.includes("Could not find the table")) {
          setNeedsDatabaseSetup(true);
        } else {
          console.error("Database check error:", error);
        }
      } else {
        setNeedsDatabaseSetup(false);
      }
    } catch (error) {
      console.error("Error checking database setup:", error);
    } finally {
      setCheckingDatabase(false);
    }
  }

  // Load templates and runs
  useEffect(() => {
    if (isSupabaseConfigured && !needsDatabaseSetup) {
      loadTemplates();
      loadRuns();
    }
  }, [needsDatabaseSetup]);

  async function loadTemplates() {
    try {
      const { data, error } = await supabase
        .from("run_templates")
        .select("*")
        .order("created_at", { ascending: false });

      if (error) throw error;
      setTemplates(data || []);
    } catch (error) {
      console.error("Error loading templates:", error);
    }
  }

  async function loadRuns() {
    try {
      const { data, error } = await supabase
        .from("runs")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(25);

      if (error) throw error;
      setRuns(data || []);
    } catch (error) {
      console.error("Error loading runs:", error);
    }
  }

  // Subscribe to realtime events when a run is active
  useEffect(() => {
    if (!currentRunId) return;

    const unsubscribe = subscribeToRunEvents(
      currentRunId,
      (event) => {
        setCurrentEvents((prev) => [...prev, event]);
      },
      (artifact) => {
        setCurrentArtifacts((prev) => [...prev, artifact]);
      },
      (status) => {
        if (status === "success") {
          toast.success("Runbook completed successfully");
        } else if (status === "error") {
          toast.error("Runbook execution failed");
        }
      }
    );

    return () => {
      unsubscribe();
    };
  }, [currentRunId]);

  const handleCommand = (command: string) => {
    // Add user message
    setMessages((prev) => [...prev, { role: "user", content: command }]);

    // Parse command to runbook plan
    const plan = planFromPrompt(command);

    // Add assistant message with plan
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `I've detected a **${plan.kind}** task. Review the details below and click **Run** to execute, or **Edit** to modify parameters.`,
          plan,
        },
      ]);
    }, 500);
  };

  const handleIntentSubmit = async (intent: string) => {
    setBusy(true);
    try {
      // For now, use the existing planFromPrompt
      const plan = planFromPrompt(intent);
      
      // Create run in Supabase
      const runId = await createRun(plan);

      // Trigger executor
      const { error } = await supabase.functions.invoke("ops-executor", {
        body: { run_id: runId },
      });

      if (error) throw error;

      // Show logs
      setActiveRunId(runId);
      toast.success("Runbook enqueued");

      // Refresh runs list
      await loadRuns();
    } catch (error) {
      console.error("Error running intent:", error);
      toast.error(error instanceof Error ? error.message : "Failed to run intent");
    } finally {
      setBusy(false);
    }
  };

  const handleRunPlan = async (plan: RunbookPlan) => {
    try {
      // Create run in Supabase
      const runId = await createRun(plan);

      // Set up UI for log viewing
      setCurrentPlanTitle(plan.title);
      setCurrentRunId(runId);
      setCurrentEvents([]);
      setCurrentArtifacts([]);
      setShowLogViewer(true);

      toast.success("Runbook enqueued for execution");

      // Trigger executor
      const { error } = await supabase.functions.invoke("ops-executor", {
        body: { run_id: runId },
      });

      if (error) {
        console.error("Executor error:", error);
      }

      // Optionally fetch existing events
      const existingEvents = await getRunEvents(runId);
      const existingArtifacts = await getRunArtifacts(runId);

      if (existingEvents.length > 0) {
        setCurrentEvents(existingEvents);
      }
      if (existingArtifacts.length > 0) {
        setCurrentArtifacts(existingArtifacts);
      }

      // Refresh runs list
      await loadRuns();
    } catch (error) {
      console.error("Error creating run:", error);
      toast.error(error instanceof Error ? error.message : "Failed to create run");
    }
  };

  const handleRunTemplate = async (templateId: string) => {
    setBusy(true);
    try {
      const template = templates.find((t) => t.id === templateId);
      if (!template) throw new Error("Template not found");

      // Create a simple plan from template
      const plan: RunbookPlan = {
        id: Math.random().toString(36).substring(7),
        kind: "deploy", // TODO: parse from template
        env: "prod",
        title: template.title,
        summary: template.description,
        inputs: [],
        risks: [],
        integrations: [],
      };

      const runId = await createRun(plan);

      // Trigger executor
      const { error } = await supabase.functions.invoke("ops-executor", {
        body: { run_id: runId },
      });

      if (error) throw error;

      setActiveRunId(runId);
      toast.success("Template runbook started");

      await loadRuns();
    } catch (error) {
      console.error("Error running template:", error);
      toast.error(error instanceof Error ? error.message : "Failed to run template");
    } finally {
      setBusy(false);
    }
  };

  const handleEditPlan = (plan: RunbookPlan) => {
    const inputsStr = plan.inputs.map((i) => `${i.label}: ${i.value}`).join(", ");
    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: `Edit mode for "${plan.title}". Current settings: ${inputsStr}.\n\nWhat would you like to change? (Note: Edit mode is a demo placeholder - in production, this would open an interactive form.)`,
      },
    ]);
  };

  const handleCloseLogViewer = () => {
    setShowLogViewer(false);
    setCurrentRunId(null);
  };

  if (!isSupabaseConfigured) {
    return (
      <AppShell>
        <SetupBanner />
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-md text-center">
            <div className="text-xl font-semibold mb-2">Supabase Not Configured</div>
            <div className="opacity-70">
              Please configure your Supabase credentials to use the Ops Control Room.
            </div>
          </div>
        </div>
      </AppShell>
    );
  }

  // Show loading state while checking database
  if (checkingDatabase) {
    return (
      <AppShell>
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-md text-center">
            <div className="text-xl font-semibold mb-2">Checking Database...</div>
            <div className="opacity-70">
              Verifying database setup
            </div>
          </div>
        </div>
      </AppShell>
    );
  }

  // Show database setup wizard if tables don't exist
  if (needsDatabaseSetup) {
    const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || "";
    return (
      <AppShell>
        <div className="flex-1 overflow-y-auto bg-gray-50">
          <DatabaseSetup 
            supabaseUrl={supabaseUrl}
            onComplete={() => {
              setNeedsDatabaseSetup(false);
              checkDatabaseSetup();
            }}
          />
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="flex-1 overflow-hidden flex flex-col">
        <SetupBanner />

        {/* Tab Navigation */}
        <div className="flex gap-2 px-6 pt-6 border-b">
          <button
            className={`px-4 py-2 rounded-t-lg transition-colors ${
              activeTab === "chat"
                ? "bg-white border border-b-0 font-semibold"
                : "opacity-70 hover:opacity-100"
            }`}
            onClick={() => setActiveTab("chat")}
          >
            Chat
          </button>
          <button
            className={`px-4 py-2 rounded-t-lg transition-colors ${
              activeTab === "templates"
                ? "bg-white border border-b-0 font-semibold"
                : "opacity-70 hover:opacity-100"
            }`}
            onClick={() => setActiveTab("templates")}
          >
            Templates
          </button>
          <button
            className={`px-4 py-2 rounded-t-lg transition-colors ${
              activeTab === "runs"
                ? "bg-white border border-b-0 font-semibold"
                : "opacity-70 hover:opacity-100"
            }`}
            onClick={() => setActiveTab("runs")}
          >
            Runs
          </button>
          <button
            className={`px-4 py-2 rounded-t-lg transition-colors ${
              activeTab === "spec"
                ? "bg-white border border-b-0 font-semibold"
                : "opacity-70 hover:opacity-100"
            }`}
            onClick={() => setActiveTab("spec")}
          >
            Spec Kit
          </button>
          <button
            className={`px-4 py-2 rounded-t-lg transition-colors ${
              activeTab === "runboard"
                ? "bg-white border border-b-0 font-semibold"
                : "opacity-70 hover:opacity-100"
            }`}
            onClick={() => setActiveTab("runboard")}
          >
            Runboard
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === "chat" && (
          <div className="flex-1 overflow-y-auto px-6 py-6">
            <div className="max-w-4xl mx-auto space-y-6">
              {messages.map((message, idx) => (
                <div
                  key={idx}
                  className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-2xl ${
                      message.role === "user" ? "bg-blue-600 text-white" : "bg-white"
                    } rounded-2xl px-5 py-3 shadow-sm`}
                  >
                    <p className="whitespace-pre-line">{message.content}</p>
                    {message.plan && (
                      <div className="mt-4">
                        <RunbookCard
                          plan={message.plan}
                          onRun={handleRunPlan}
                          onEdit={handleEditPlan}
                        />
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "templates" && (
          <div className="flex-1 overflow-y-auto px-6 py-6">
            <div className="max-w-4xl mx-auto">
              <div className="mb-4">
                <IntentBar onSubmit={handleIntentSubmit} busy={busy} />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                {templates.length === 0 && (
                  <div className="col-span-2 text-center py-12 opacity-70">
                    No templates found. Run the migration to seed templates.
                  </div>
                )}
                {templates.map((t) => (
                  <RunbookTemplateCard
                    key={t.id}
                    template={t}
                    onRun={handleRunTemplate}
                    onEdit={() => toast.info("Template editing coming soon")}
                  />
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === "runs" && (
          <div className="flex-1 overflow-y-auto px-6 py-6">
            <div className="max-w-4xl mx-auto space-y-2">
              <div className="font-semibold mb-3">Recent Runs</div>
              {runs.length === 0 && (
                <div className="text-center py-12 opacity-70">
                  No runs yet. Create a run from Templates or Chat.
                </div>
              )}
              {runs.map((r) => (
                <button
                  key={r.id}
                  className="w-full text-left p-4 border rounded-xl hover:shadow-md transition-shadow bg-white"
                  onClick={() => setActiveRunId(r.id)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{r.plan?.title || r.kind}</div>
                      <div className="text-xs opacity-60 mt-1">
                        {new Date(r.created_at).toLocaleString()} • {r.env} • {r.kind}
                      </div>
                    </div>
                    <div
                      className={`text-xs px-2 py-1 rounded ${
                        r.status === "success"
                          ? "bg-green-100 text-green-700"
                          : r.status === "error"
                          ? "bg-red-100 text-red-700"
                          : r.status === "running"
                          ? "bg-blue-100 text-blue-700"
                          : "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {r.status}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {activeTab === "spec" && (
          <div className="flex-1 overflow-y-auto px-6 py-6">
            <SpecKitPanel />
          </div>
        )}

        {activeTab === "runboard" && (
          <Runboard onViewRun={setActiveRunId} />
        )}

        {/* Command bar only shown in chat tab */}
        {activeTab === "chat" && <CommandBar onSubmit={handleCommand} />}
      </div>

      {/* Old log viewer for chat flow */}
      {showLogViewer && (
        <LogViewer
          title={currentPlanTitle}
          events={currentEvents}
          artifacts={currentArtifacts}
          onClose={handleCloseLogViewer}
        />
      )}

      {/* New enhanced log viewer for templates/runs */}
      {activeRunId && activeTab !== "chat" && (
        <RunLogViewerEnhanced runId={activeRunId} onClose={() => setActiveRunId(null)} />
      )}
    </AppShell>
  );
}