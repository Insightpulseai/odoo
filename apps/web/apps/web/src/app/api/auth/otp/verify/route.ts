import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { createClient } from "@supabase/supabase-js";

export async function POST(req: Request) {
  const { email, token } = await req.json();
  if (!email || !token) {
    return NextResponse.json({ error: "email and token required" }, { status: 400 });
  }

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
  const supabase = createClient(url, anon);

  // Email OTP verification
  const { data, error } = await supabase.auth.verifyOtp({
    email,
    token,
    type: "email",
  });

  if (error) return NextResponse.json({ error: error.message }, { status: 400 });

  // Align with /api/auth/callback cookie strategy
  const cookieStore = await cookies();
  if (data.session?.access_token) {
    cookieStore.set("sb-access-token", data.session.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: data.session.expires_in,
      path: "/",
    });
  }
  if (data.session?.refresh_token) {
    cookieStore.set("sb-refresh-token", data.session.refresh_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 30, // 30 days
      path: "/",
    });
  }

  return NextResponse.json({ ok: true, user: data.user });
}
