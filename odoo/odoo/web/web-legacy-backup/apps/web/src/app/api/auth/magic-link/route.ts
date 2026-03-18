import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

export async function POST(req: Request) {
  const { email, redirectTo } = await req.json();

  if (!email) return NextResponse.json({ error: "email required" }, { status: 400 });

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
  const supabase = createClient(url, anon, { auth: { persistSession: false } });

  // redirectTo MUST be an allowed redirect URL in Supabase Auth settings
  const emailRedirectTo =
    redirectTo ||
    `${process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3002"}/api/auth/callback`;

  const { error } = await supabase.auth.signInWithOtp({
    email,
    options: {
      emailRedirectTo,
      shouldCreateUser: true,
    },
  });

  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  return NextResponse.json({ ok: true });
}
