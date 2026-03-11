// Alias for compatibility - delegates to src/lib/supabase/server
import { createSupabaseServerClient } from "@/lib/supabase/server";

export { createSupabaseServerClient };
export const createClient = createSupabaseServerClient;
