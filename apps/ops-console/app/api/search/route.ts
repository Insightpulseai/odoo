import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

/**
 * POST /api/search
 * Proxies to ops-search-query Edge Function.
 * Forwards the caller's Supabase session token (authenticated users only).
 * Body: { query: string, sources?: string[], limit?: number }
 */
export async function POST(req: NextRequest) {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  if (!supabaseUrl) {
    return NextResponse.json({ error: "Supabase env not configured" }, { status: 500 });
  }

  // Forward the user's Supabase JWT from the request
  const authHeader = req.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) {
    return NextResponse.json(
      { error: "Authentication required" },
      { status: 401 }
    );
  }

  let body: { query?: string; sources?: string[]; limit?: number };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!body.query?.trim()) {
    return NextResponse.json({ results: [] });
  }

  const fnUrl = `${supabaseUrl}/functions/v1/ops-search-query`;
  const fnRes = await fetch(fnUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: authHeader,  // Forward user JWT — Edge Function validates it
    },
    body: JSON.stringify({
      query: body.query,
      sources: body.sources,
      limit: body.limit ?? 20,
    }),
  });

  if (!fnRes.ok) {
    const text = await fnRes.text().catch(() => "");
    return NextResponse.json(
      { error: `Search function error: ${fnRes.status}`, detail: text },
      { status: 502 }
    );
  }

  const data = await fnRes.json();
  return NextResponse.json(data);
}
