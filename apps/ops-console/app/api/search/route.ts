import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!supabaseUrl || !anonKey) {
    return NextResponse.json({ error: "Supabase env not configured" }, { status: 500 });
  }

  let body: { query?: string; limit?: number };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!body.query?.trim()) {
    return NextResponse.json({ results: [] });
  }

  // Proxy to ops-search-query Edge Function
  const fnUrl = `${supabaseUrl}/functions/v1/ops-search-query`;
  const fnRes = await fetch(fnUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${anonKey}`,
    },
    body: JSON.stringify({ query: body.query, limit: body.limit ?? 20 }),
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
