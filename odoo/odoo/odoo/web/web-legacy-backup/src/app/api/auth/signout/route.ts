import { createServerClient } from "@/lib/supabase";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export async function POST() {
  try {
    const cookieStore = cookies();
    const sessionCookie = cookieStore.get("sb-session");

    if (!sessionCookie) {
      return NextResponse.json({ success: true });
    }

    const supabase = createServerClient();

    // Sign out from Supabase
    const { error } = await supabase.auth.signOut();

    if (error) {
      console.error("Sign out error:", error);
      return NextResponse.json(
        { error: "Failed to sign out" },
        { status: 500 }
      );
    }

    // Clear session cookie
    const response = NextResponse.json({ success: true });
    response.cookies.delete("sb-session");

    return response;
  } catch (error) {
    console.error("Auth signout error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
