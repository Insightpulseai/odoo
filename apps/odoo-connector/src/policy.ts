import fs from "node:fs";
import path from "node:path";
import YAML from "yaml";

export type ToolMode = "read" | "write";

export interface PolicyTool {
  title: string;
  description: string;
  feature_group: string;
  scope: string;
  mode: ToolMode;
  read_only: boolean;
  destructive?: boolean;
  idempotent?: boolean;
  input_schema: Record<string, unknown>;
  wrapper: string;
}

export interface PolicyFile {
  version: number;
  oauth: {
    resource_metadata_url: string;
  };
  feature_groups: Record<string, { label: string }>;
  tools: Record<string, PolicyTool>;
}

export function loadPolicy(policyPath?: string): PolicyFile {
  const resolved =
    policyPath ??
    path.resolve(process.cwd(), "apps/odoo-connector/config/odoo-policy.yaml");

  const raw = fs.readFileSync(resolved, "utf8");
  const parsed = YAML.parse(raw) as PolicyFile;

  if (!parsed?.oauth?.resource_metadata_url) {
    throw new Error("Policy missing oauth.resource_metadata_url");
  }

  return parsed;
}

export function getToolOrThrow(policy: PolicyFile, toolName: string): PolicyTool {
  const tool = policy.tools[toolName];
  if (!tool) {
    throw new Error(`Unknown tool in policy: ${toolName}`);
  }
  return tool;
}

export function buildSecuritySchemes(scope: string, readOnly: boolean) {
  if (readOnly) {
    return [
      { type: "noauth" as const },
      { type: "oauth2" as const, scopes: [scope] },
    ];
  }

  return [{ type: "oauth2" as const, scopes: [scope] }];
}

export function buildAnnotations(tool: PolicyTool) {
  if (tool.mode === "read") {
    return { readOnlyHint: true };
  }

  return {
    destructiveHint: Boolean(tool.destructive),
    idempotentHint: Boolean(tool.idempotent),
  };
}
