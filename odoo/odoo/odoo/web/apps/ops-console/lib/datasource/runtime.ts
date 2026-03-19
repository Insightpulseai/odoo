// apps/ops-console/lib/datasource/runtime.ts

export type DataSourceMode = "live" | "mock";

export interface DataAttestation {
  mode: DataSourceMode;
  envName: string;
  buildSha: string;
  supabaseUrl: string;
  supabaseProjectRef: string;
  odooBaseUrl: string;
}

const getMode = (): DataSourceMode => {
  // Explicitly check for '1' or 'true' to enable mocks
  if (process.env.NEXT_PUBLIC_USE_MOCKS === "1" || process.env.NEXT_PUBLIC_USE_MOCKS === "true") {
    return "mock";
  }
  return "live";
};

const getEnvName = () => process.env.NEXT_PUBLIC_APP_ENV || process.env.NODE_ENV || "development";
const getBuildSha = () => process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA || "local-dev";

export const runtime = {
  mode: getMode(),
  envName: getEnvName(),
  buildSha: getBuildSha(),
  supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL || "",
  supabaseProjectRef: process.env.NEXT_PUBLIC_SUPABASE_PROJECT_REF || "",
  odooBaseUrl: process.env.NEXT_PUBLIC_ODOO_BASE_URL || "https://erp.insightpulseai.com",
};

/**
 * Hard fail if mock mode is active in production environments.
 */
export const assertLive = () => {
  const isProduction = runtime.envName === "production" || runtime.envName === "prod" || process.env.NODE_ENV === "production";

  if (isProduction && runtime.mode === "mock") {
    console.error("CRITICAL: Mock mode active in production environment.");
    throw new Error("SECURITY_FAILURE: Data source must be 'live' in production.");
  }
};

export const getAttestation = (): DataAttestation => ({
  mode: runtime.mode,
  envName: runtime.envName,
  buildSha: runtime.buildSha,
  supabaseUrl: runtime.supabaseUrl.replace(/^https?:\/\//, ""), // Sanitize URL for UI
  supabaseProjectRef: runtime.supabaseProjectRef,
  odooBaseUrl: runtime.odooBaseUrl.replace(/^https?:\/\//, ""),
});
