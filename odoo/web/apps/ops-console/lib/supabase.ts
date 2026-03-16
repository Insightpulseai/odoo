// apps/ops-console/lib/supabase.ts
import { createClient } from "@supabase/supabase-js";

import { runtime } from "./datasource/runtime";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn("Supabase credentials missing in environment variables.");
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  db: {
    schema: "ops",
  },
  global: {
    headers: {
      "x-datasource-mode": runtime.mode,
      "x-odooops-client": runtime.buildSha,
    },
  },
});
