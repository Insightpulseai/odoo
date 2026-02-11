import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs"; // keep token handling on server
export const dynamic = "force-dynamic";

const BASE_URL = "https://api.supabase.com";

function assertToken() {
  const token = process.env.SUPABASE_MANAGEMENT_API_TOKEN;
  if (!token) {
    return {
      ok: false as const,
      error: "SUPABASE_MANAGEMENT_API_TOKEN is missing",
    };
  }
  return { ok: true as const, token };
}

async function proxy(req: NextRequest, pathParts: string[]) {
  const tok = assertToken();
  if (!tok.ok) {
    return NextResponse.json(
      { message: "Server configuration error.", detail: tok.error },
      { status: 500 },
    );
  }

  // Build upstream URL
  const upstreamUrl = new URL(`${BASE_URL}/${pathParts.join("/")}`);
  // preserve query string
  req.nextUrl.searchParams.forEach((v, k) =>
    upstreamUrl.searchParams.set(k, v),
  );

  // Copy headers safely
  const headers = new Headers(req.headers);
  headers.delete("host");
  headers.delete("connection");
  headers.delete("content-length");
  headers.set("authorization", `Bearer ${tok.token}`);
  headers.set("accept", headers.get("accept") ?? "application/json");

  // Forward body for non-GET/HEAD
  const method = req.method.toUpperCase();
  const hasBody = !["GET", "HEAD"].includes(method);
  const body = hasBody ? await req.arrayBuffer() : undefined;

  const upstreamRes = await fetch(upstreamUrl.toString(), {
    method,
    headers,
    body,
    cache: "no-store",
  });

  const resHeaders = new Headers(upstreamRes.headers);
  // Avoid leaking hop-by-hop headers
  resHeaders.delete("transfer-encoding");
  resHeaders.delete("content-encoding");

  const data = await upstreamRes.arrayBuffer();
  return new NextResponse(data, {
    status: upstreamRes.status,
    headers: resHeaders,
  });
}

export async function GET(
  req: NextRequest,
  ctx: { params: { path: string[] } },
) {
  const params = await ctx.params;
  return proxy(req, params.path);
}
export async function POST(
  req: NextRequest,
  ctx: { params: { path: string[] } },
) {
  const params = await ctx.params;
  return proxy(req, params.path);
}
export async function PUT(
  req: NextRequest,
  ctx: { params: { path: string[] } },
) {
  const params = await ctx.params;
  return proxy(req, params.path);
}
export async function PATCH(
  req: NextRequest,
  ctx: { params: { path: string[] } },
) {
  const params = await ctx.params;
  return proxy(req, params.path);
}
export async function DELETE(
  req: NextRequest,
  ctx: { params: { path: string[] } },
) {
  const params = await ctx.params;
  return proxy(req, params.path);
}
