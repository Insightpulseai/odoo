import { useState } from "react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Alert, AlertDescription } from "./ui/alert";
import { CheckCircle2, AlertCircle, Copy, ExternalLink, Loader2 } from "lucide-react";

const SETUP_SQL = `-- ============================================================
-- Ops Control Room - Complete Database Setup
-- Single file to create all tables, indexes, policies, and functions
-- Run this in Supabase SQL Editor
-- ============================================================

-- ============================================================
-- SESSIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS public.sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_by uuid NULL,
  title text NOT NULL DEFAULT 'Session',
  intent text NOT NULL DEFAULT '',
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','archived')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- ============================================================
-- RUNS
-- ============================================================

CREATE TABLE IF NOT EXISTS public.runs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  created_by uuid NULL,
  env text NOT NULL CHECK (env IN ('prod','staging','dev')),
  kind text NOT NULL CHECK (kind IN ('deploy','healthcheck','spec','incident','schema_sync')),
  plan jsonb NULL,
  intent text NOT NULL DEFAULT '',
  template_id uuid NULL,
  input jsonb NOT NULL DEFAULT '{}'::jsonb,
  status text NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','running','success','error','canceled')),
  started_at timestamptz NULL,
  finished_at timestamptz NULL,
  error_message text NULL,
  -- Parallel execution columns
  session_id uuid NULL REFERENCES public.sessions(id) ON DELETE SET NULL,
  lane text NOT NULL DEFAULT 'A',
  priority int NOT NULL DEFAULT 100,
  claimed_by text NULL,
  claimed_at timestamptz NULL,
  heartbeat_at timestamptz NULL,
  canceled_at timestamptz NULL
);

-- ============================================================
-- RUN EVENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS public.run_events (
  id bigserial PRIMARY KEY,
  run_id uuid NOT NULL REFERENCES public.runs(id) ON DELETE CASCADE,
  ts timestamptz NOT NULL DEFAULT now(),
  level text NOT NULL CHECK (level IN ('debug','info','warn','error','success')),
  source text NOT NULL,
  message text NOT NULL,
  data jsonb NULL
);

-- ============================================================
-- ARTIFACTS
-- ============================================================

CREATE TABLE IF NOT EXISTS public.artifacts (
  id bigserial PRIMARY KEY,
  run_id uuid NOT NULL REFERENCES public.runs(id) ON DELETE CASCADE,
  created_at timestamptz NOT NULL DEFAULT now(),
  kind text NOT NULL CHECK (kind IN ('link','diff','file')),
  title text NOT NULL,
  value text NOT NULL
);

-- ============================================================
-- RUN TEMPLATES
-- ============================================================

CREATE TABLE IF NOT EXISTS public.run_templates (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug text NOT NULL UNIQUE,
  title text NOT NULL,
  description text NOT NULL DEFAULT '',
  template_yaml text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- ============================================================
-- SPEC DOCS
-- ============================================================

CREATE TABLE IF NOT EXISTS public.spec_docs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug text NOT NULL UNIQUE,
  title text NOT NULL,
  content text NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- ============================================================
-- RUN STEPS
-- ============================================================

DO $$ BEGIN
  CREATE TYPE public.step_status AS ENUM ('queued','running','succeeded','failed','canceled');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS public.run_steps (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id uuid NOT NULL REFERENCES public.runs(id) ON DELETE CASCADE,
  idx int NOT NULL,
  step_id text NOT NULL,
  title text NOT NULL,
  kind text NOT NULL DEFAULT 'system',
  tool text NULL,
  action text NULL,
  args jsonb NOT NULL DEFAULT '{}'::jsonb,
  status public.step_status NOT NULL DEFAULT 'queued',
  started_at timestamptz NULL,
  finished_at timestamptz NULL,
  error text NULL
);

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_runs_created_at ON public.runs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_runs_status ON public.runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_created_by ON public.runs(created_by);
CREATE INDEX IF NOT EXISTS idx_runs_session_idx ON public.runs(session_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_runs_claim_idx ON public.runs(status, priority, created_at);

CREATE INDEX IF NOT EXISTS idx_run_events_run_id ON public.run_events(run_id);
CREATE INDEX IF NOT EXISTS idx_run_events_ts ON public.run_events(ts);

CREATE INDEX IF NOT EXISTS idx_artifacts_run_id ON public.artifacts(run_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_run_steps_unique ON public.run_steps(run_id, idx);
CREATE INDEX IF NOT EXISTS idx_run_steps_run_idx ON public.run_steps(run_id, idx);

-- ============================================================
-- TRIGGERS
-- ============================================================

CREATE OR REPLACE FUNCTION public.touch_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  new.updated_at = now();
  RETURN new;
END $$;

DROP TRIGGER IF EXISTS trg_sessions_updated_at ON public.sessions;
CREATE TRIGGER trg_sessions_updated_at
BEFORE UPDATE ON public.sessions
FOR EACH ROW EXECUTE FUNCTION public.touch_updated_at();

DROP TRIGGER IF EXISTS trg_runs_updated_at ON public.runs;
CREATE TRIGGER trg_runs_updated_at
BEFORE UPDATE ON public.runs
FOR EACH ROW EXECUTE FUNCTION public.touch_updated_at();

-- ============================================================
-- RLS POLICIES
-- ============================================================

ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.run_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.run_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.spec_docs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.run_steps ENABLE ROW LEVEL SECURITY;

-- Sessions policies (anon access for prototyping)
DROP POLICY IF EXISTS sessions_select_anon ON public.sessions;
CREATE POLICY sessions_select_anon ON public.sessions
FOR SELECT TO anon USING (true);

DROP POLICY IF EXISTS sessions_insert_anon ON public.sessions;
CREATE POLICY sessions_insert_anon ON public.sessions
FOR INSERT TO anon WITH CHECK (true);

DROP POLICY IF EXISTS sessions_update_anon ON public.sessions;
CREATE POLICY sessions_update_anon ON public.sessions
FOR UPDATE TO anon USING (true) WITH CHECK (true);

-- Runs policies (anon access for prototyping)
DROP POLICY IF EXISTS runs_select_anon ON public.runs;
CREATE POLICY runs_select_anon ON public.runs
FOR SELECT TO anon USING (true);

DROP POLICY IF EXISTS runs_insert_anon ON public.runs;
CREATE POLICY runs_insert_anon ON public.runs
FOR INSERT TO anon WITH CHECK (true);

DROP POLICY IF EXISTS runs_update_anon ON public.runs;
CREATE POLICY runs_update_anon ON public.runs
FOR UPDATE TO anon USING (true) WITH CHECK (true);

-- Events policies (anon access for prototyping)
DROP POLICY IF EXISTS events_select_anon ON public.run_events;
CREATE POLICY events_select_anon ON public.run_events
FOR SELECT TO anon USING (true);

DROP POLICY IF EXISTS events_insert_anon ON public.run_events;
CREATE POLICY events_insert_anon ON public.run_events
FOR INSERT TO anon WITH CHECK (true);

-- Artifacts policies (anon access for prototyping)
DROP POLICY IF EXISTS artifacts_select_anon ON public.artifacts;
CREATE POLICY artifacts_select_anon ON public.artifacts
FOR SELECT TO anon USING (true);

DROP POLICY IF EXISTS artifacts_insert_anon ON public.artifacts;
CREATE POLICY artifacts_insert_anon ON public.artifacts
FOR INSERT TO anon WITH CHECK (true);

-- Run steps policies (anon access for prototyping)
DROP POLICY IF EXISTS steps_select_anon ON public.run_steps;
CREATE POLICY steps_select_anon ON public.run_steps
FOR SELECT TO anon USING (true);

DROP POLICY IF EXISTS steps_insert_anon ON public.run_steps;
CREATE POLICY steps_insert_anon ON public.run_steps
FOR INSERT TO anon WITH CHECK (true);

-- Templates policies (anon access for prototyping)
DROP POLICY IF EXISTS templates_select_anon ON public.run_templates;
CREATE POLICY templates_select_anon ON public.run_templates
FOR SELECT TO anon USING (true);

DROP POLICY IF EXISTS templates_insert_anon ON public.run_templates;
CREATE POLICY templates_insert_anon ON public.run_templates
FOR INSERT TO anon WITH CHECK (true);

DROP POLICY IF EXISTS templates_update_anon ON public.run_templates;
CREATE POLICY templates_update_anon ON public.run_templates
FOR UPDATE TO anon USING (true) WITH CHECK (true);

-- Spec docs policies (anon access for prototyping)
DROP POLICY IF EXISTS spec_select_anon ON public.spec_docs;
CREATE POLICY spec_select_anon ON public.spec_docs
FOR SELECT TO anon USING (true);

DROP POLICY IF EXISTS spec_insert_anon ON public.spec_docs;
CREATE POLICY spec_insert_anon ON public.spec_docs
FOR INSERT TO anon WITH CHECK (true);

DROP POLICY IF EXISTS spec_update_anon ON public.spec_docs;
CREATE POLICY spec_update_anon ON public.spec_docs
FOR UPDATE TO anon USING (true) WITH CHECK (true);

-- ============================================================
-- REALTIME PUBLICATION
-- ============================================================

DROP PUBLICATION IF EXISTS supabase_realtime CASCADE;
CREATE PUBLICATION supabase_realtime;

ALTER PUBLICATION supabase_realtime ADD TABLE public.sessions;
ALTER PUBLICATION supabase_realtime ADD TABLE public.runs;
ALTER PUBLICATION supabase_realtime ADD TABLE public.run_events;
ALTER PUBLICATION supabase_realtime ADD TABLE public.artifacts;
ALTER PUBLICATION supabase_realtime ADD TABLE public.run_steps;

-- ============================================================
-- FUNCTIONS
-- ============================================================

-- Claim runs function
CREATE OR REPLACE FUNCTION public.claim_runs(p_worker text, p_limit int DEFAULT 1)
RETURNS SETOF public.runs
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  RETURN QUERY
  WITH cte AS (
    SELECT id
    FROM public.runs
    WHERE status = 'queued'
      AND (canceled_at IS NULL)
      AND (claimed_at IS NULL OR claimed_at < now() - interval '5 minutes')
    ORDER BY priority ASC, created_at ASC
    FOR UPDATE SKIP LOCKED
    LIMIT p_limit
  )
  UPDATE public.runs r
  SET status = 'running',
      claimed_by = p_worker,
      claimed_at = now(),
      heartbeat_at = now(),
      updated_at = now()
  FROM cte
  WHERE r.id = cte.id
  RETURNING r.*;
END $$;

-- Heartbeat function
CREATE OR REPLACE FUNCTION public.heartbeat_run(p_run_id uuid, p_worker text)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  UPDATE public.runs
  SET heartbeat_at = now(),
      claimed_by = p_worker
  WHERE id = p_run_id AND status = 'running';
END $$;

-- Cancel run function
CREATE OR REPLACE FUNCTION public.cancel_run(p_run_id uuid)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  UPDATE public.runs
  SET status = 'canceled',
      canceled_at = now(),
      updated_at = now()
  WHERE id = p_run_id;
END $$;

-- Enqueue run function
CREATE OR REPLACE FUNCTION public.enqueue_run(
  p_env text,
  p_kind text,
  p_plan jsonb
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_run_id uuid;
BEGIN
  INSERT INTO public.runs (created_by, env, kind, plan, status)
  VALUES (NULL, p_env, p_kind, p_plan, 'queued')
  RETURNING id INTO v_run_id;
  
  RETURN v_run_id;
END;
$$;

-- Complete run function
CREATE OR REPLACE FUNCTION public.complete_run(
  p_run_id uuid,
  p_status text,
  p_error_message text DEFAULT NULL
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  UPDATE public.runs
  SET 
    status = p_status,
    finished_at = now(),
    error_message = p_error_message
  WHERE id = p_run_id;
END;
$$;

-- Grant execute permissions to anon for prototyping
GRANT EXECUTE ON FUNCTION public.claim_runs(text, int) TO anon;
GRANT EXECUTE ON FUNCTION public.heartbeat_run(uuid, text) TO anon;
GRANT EXECUTE ON FUNCTION public.cancel_run(uuid) TO anon;
GRANT EXECUTE ON FUNCTION public.enqueue_run(text, text, jsonb) TO anon;
GRANT EXECUTE ON FUNCTION public.complete_run(uuid, text, text) TO anon;`;

interface DatabaseSetupProps {
  supabaseUrl?: string;
  onComplete?: () => void;
}

export function DatabaseSetup({ supabaseUrl, onComplete }: DatabaseSetupProps) {
  const [copied, setCopied] = useState(false);
  const [step, setStep] = useState<1 | 2 | 3>(1);

  // Get project ref from URL or use environment variable
  const url = supabaseUrl || import.meta.env.VITE_SUPABASE_URL || "";
  const projectRef = url.split("//")[1]?.split(".")[0] || "";
  const dashboardUrl = `https://supabase.com/dashboard/project/${projectRef}`;
  const sqlEditorUrl = `${dashboardUrl}/sql`;
  const replicationUrl = `${dashboardUrl}/database/replication`;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(SETUP_SQL);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("Failed to copy:", error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="text-center mb-8">
        <div className="text-3xl font-bold mb-2">Database Setup Required</div>
        <div className="text-lg opacity-70">
          Your database tables don't exist yet. Let's set them up in 3 easy steps.
        </div>
      </div>

      {/* Progress indicator */}
      <div className="flex justify-center gap-4 mb-8">
        {[1, 2, 3].map((num) => (
          <div
            key={num}
            className={`flex items-center gap-2 ${
              step >= num ? "opacity-100" : "opacity-40"
            }`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold ${
                step >= num
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-600"
              }`}
            >
              {num}
            </div>
            {num < 3 && <div className="w-12 h-0.5 bg-gray-300" />}
          </div>
        ))}
      </div>

      {/* Step 1: Copy SQL */}
      <Card className="p-6 mb-4">
        <div className="flex items-start gap-3 mb-4">
          <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-semibold flex-shrink-0">
            1
          </div>
          <div className="flex-1">
            <div className="font-semibold text-lg mb-2">
              Copy the Setup SQL
            </div>
            <div className="opacity-70 mb-4">
              Click the button below to copy the database setup script to your clipboard.
            </div>
            <Button
              onClick={handleCopy}
              className="w-full sm:w-auto"
              variant={copied ? "default" : "outline"}
            >
              {copied ? (
                <>
                  <CheckCircle2 className="w-4 h-4 mr-2" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4 mr-2" />
                  Copy Setup SQL
                </>
              )}
            </Button>
            {copied && (
              <div className="mt-4">
                <Alert>
                  <CheckCircle2 className="h-4 w-4" />
                  <AlertDescription>
                    SQL copied to clipboard! Now proceed to step 2.
                  </AlertDescription>
                </Alert>
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Step 2: Run in SQL Editor */}
      <Card className="p-6 mb-4">
        <div className="flex items-start gap-3 mb-4">
          <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-semibold flex-shrink-0">
            2
          </div>
          <div className="flex-1">
            <div className="font-semibold text-lg mb-2">
              Run in Supabase SQL Editor
            </div>
            <div className="opacity-70 mb-4">
              Open the SQL Editor in your Supabase dashboard and paste the SQL.
            </div>
            <ol className="list-decimal list-inside space-y-2 opacity-70 mb-4">
              <li>Click "Open SQL Editor" below</li>
              <li>Click "New query" in the SQL Editor</li>
              <li>Paste the SQL you copied (Cmd/Ctrl + V)</li>
              <li>Click "Run" (green button at bottom right)</li>
              <li>Wait for the success message</li>
            </ol>
            <a
              href={sqlEditorUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex"
            >
              <Button className="w-full sm:w-auto">
                <ExternalLink className="w-4 h-4 mr-2" />
                Open SQL Editor
              </Button>
            </a>
          </div>
        </div>
      </Card>

      {/* Step 3: Enable Realtime */}
      <Card className="p-6 mb-8">
        <div className="flex items-start gap-3 mb-4">
          <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-semibold flex-shrink-0">
            3
          </div>
          <div className="flex-1">
            <div className="font-semibold text-lg mb-2">
              Enable Realtime (Optional)
            </div>
            <div className="opacity-70 mb-4">
              Enable real-time subscriptions for live log streaming.
            </div>
            <ol className="list-decimal list-inside space-y-2 opacity-70 mb-4">
              <li>Click "Open Replication Settings" below</li>
              <li>Find "supabase_realtime" in the publications list</li>
              <li>Toggle it ON (green)</li>
            </ol>
            <a
              href={replicationUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex"
            >
              <Button variant="outline" className="w-full sm:w-auto">
                <ExternalLink className="w-4 h-4 mr-2" />
                Open Replication Settings
              </Button>
            </a>
          </div>
        </div>
      </Card>

      {/* Completion */}
      <Card className="p-6 bg-blue-50 border-blue-200">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold mb-1">After Running the SQL</div>
            <div className="opacity-70 mb-4">
              Once you see the success message in the SQL Editor, click the button below to
              refresh the app. The database errors should be gone!
            </div>
            <Button
              onClick={() => {
                if (onComplete) onComplete();
                window.location.reload();
              }}
              className="w-full sm:w-auto"
            >
              <CheckCircle2 className="w-4 h-4 mr-2" />
              I've Run the SQL - Refresh App
            </Button>
          </div>
        </div>
      </Card>

      {/* What gets created */}
      <div className="mt-8 p-6 bg-gray-50 rounded-lg">
        <div className="font-semibold mb-3">What Gets Created</div>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <div className="text-sm font-medium mb-2">Tables (7)</div>
            <ul className="text-sm opacity-70 space-y-1">
              <li>• sessions - Grouped runs</li>
              <li>• runs - Execution tasks</li>
              <li>• run_events - Log entries</li>
              <li>• artifacts - Generated outputs</li>
              <li>• run_templates - Reusable templates</li>
              <li>• spec_docs - Documentation</li>
              <li>• run_steps - Step tracking</li>
            </ul>
          </div>
          <div>
            <div className="text-sm font-medium mb-2">Features</div>
            <ul className="text-sm opacity-70 space-y-1">
              <li>• Row Level Security (RLS)</li>
              <li>• Realtime subscriptions</li>
              <li>• Atomic run claiming</li>
              <li>• Heartbeat monitoring</li>
              <li>• 5 helper functions</li>
              <li>• Performance indexes</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}