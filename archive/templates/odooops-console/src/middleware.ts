// src/middleware.ts
import { NextResponse, type NextRequest } from "next/server";
import { createSupabaseMiddlewareClient } from "@/lib/supabase/middleware";

export async function middleware(req: NextRequest) {
  const { supabase, res } = createSupabaseMiddlewareClient(req);

  // Refresh session if needed (cookie-based)
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const isAppRoute = req.nextUrl.pathname.startsWith("/app");

  if (isAppRoute && !user) {
    const url = req.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("next", req.nextUrl.pathname);
    return NextResponse.redirect(url);
  }

  return res;
}

export const config = {
  matcher: ["/app/:path*"],
};
