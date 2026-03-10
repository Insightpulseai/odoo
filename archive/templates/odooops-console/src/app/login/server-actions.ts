// src/app/login/server-actions.ts
"use server";

import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";

export async function loginAction(formData: FormData) {
  const email = String(formData.get("email") || "").trim();
  const password = String(formData.get("password") || "");
  const next = String(formData.get("next") || "/app");

  if (!email || !password) {
    redirect(`/login?next=${encodeURIComponent(next)}`);
  }

  const supabase = createSupabaseServerClient();
  const { error } = await supabase.auth.signInWithPassword({ email, password });

  if (error) {
    // keep it simple; you can add error messaging later
    redirect(`/login?next=${encodeURIComponent(next)}`);
  }

  redirect(next);
}
