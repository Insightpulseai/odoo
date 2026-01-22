export type Env = "prod" | "staging" | "dev";
export type RunbookKind = "deploy" | "healthcheck" | "spec" | "incident" | "schema_sync";

export type Risk = { 
  level: "info" | "warn" | "block"; 
  code: string; 
  message: string; 
};

export type Integration = "Supabase" | "Vercel" | "GitHub" | "DigitalOcean" | "Kubernetes";

export type RunbookInputField =
  | { key: "env"; label: "Environment"; type: "select"; options: Env[]; value?: Env }
  | { key: "repo"; label: "Repo"; type: "text"; value?: string }
  | { key: "target"; label: "Target"; type: "text"; value?: string }
  | { key: "notes"; label: "Notes"; type: "text"; value?: string }
  | { key: "branch"; label: "Branch"; type: "text"; value?: string }
  | { key: "runMigrations"; label: "Run migrations"; type: "boolean"; value?: boolean };

export type RunbookPlan = {
  id: string;
  kind: RunbookKind;
  title: string;
  summary: string;
  inputs: RunbookInputField[];
  risks: Risk[];
  integrations: Integration[];
};

export type RunEvent = {
  ts: string;
  level: "debug" | "info" | "warn" | "error" | "success";
  source: Integration | "System";
  message: string;
  data?: Record<string, unknown>;
};

export type Artifact = {
  kind: "link" | "diff" | "file";
  title: string;
  value: string; // url, diff text, file path/id
};

export type ExecutionResult = {
  events: RunEvent[];
  artifacts: Artifact[];
  status: "running" | "completed" | "failed";
};
