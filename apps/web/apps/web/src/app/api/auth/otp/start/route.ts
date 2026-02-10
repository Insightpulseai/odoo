import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

export async function POST(req: Request) {
  const { email } = await req.json();
  if (!email) return NextResponse.json({ error: "email required" }, { status: 400 });

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
  const supabase = createClient(url, anon, { auth: { persistSession: false } });

  // Starts OTP email (same API as magic link, but user enters token instead of clicking)
  const { error } = await supabase.auth.signInWithOtp({
    email,
    options: { shouldCreateUser: true },
  });

  if (error) return NextResponse.json({ error: error.message }, { status: 400 });
  return NextResponse.json({ ok: true });
}
