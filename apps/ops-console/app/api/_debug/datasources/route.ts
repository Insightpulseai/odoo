// apps/ops-console/app/api/_debug/datasources/route.ts
import { NextResponse } from "next/server";
import { getAttestation } from "@/lib/datasource/runtime";

export const dynamic = "force-dynamic";

export async function GET() {
  const attestation = getAttestation();

  return NextResponse.json(attestation, {
    headers: {
      "Cache-Control": "no-store, max-age=0",
    },
  });
}
