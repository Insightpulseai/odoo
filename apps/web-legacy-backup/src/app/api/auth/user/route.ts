import { createServerClient } from "@/lib/supabase";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export async function GET() {
  try {
    const cookieStore = cookies();
    const sessionCookie = cookieStore.get("sb-session");

    if (!sessionCookie) {
      return NextResponse.json({ user: null }, { status: 401 });
    }

    const supabase = createServerClient();

    // Get user from session token
    const { data: { user }, error } = await supabase.auth.getUser(sessionCookie.value);

    if (error || !user) {
      return NextResponse.json({ user: null }, { status: 401 });
    }

    return NextResponse.json({
      user: {
        id: user.id,
        email: user.email,
        created_at: user.created_at,
      },
    });
  } catch (error) {
    console.error("Auth user error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
