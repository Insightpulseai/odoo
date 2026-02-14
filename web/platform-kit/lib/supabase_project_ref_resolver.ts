export function resolveSupabaseProjectRef(): string {
  const envRef = process.env.NEXT_PUBLIC_SUPABASE_PROJECT_REF;
  if (envRef && envRef.trim()) return envRef.trim();

  if (typeof window !== "undefined") {
    const q = new URLSearchParams(window.location.search);
    const urlRef = q.get("ref");
    if (urlRef && urlRef.trim()) return urlRef.trim();
  }

  throw new Error(
    "No Supabase project ref found. Set NEXT_PUBLIC_SUPABASE_PROJECT_REF or pass ?ref=<project_ref>.",
  );
}
