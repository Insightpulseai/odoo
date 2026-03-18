/**
 * IPAI BIR Tax Compute Engine
 *
 * INPUT:  Signed webhook from Odoo (posted account.move.line batch)
 * PROCESS: Resolve ATC → compute EWT → risk-score → write findings
 * OUTPUT:  ops.tax_findings + ops.tax_runs + audit.tax_events
 *
 * Owner: Supabase (computation state)
 * SOR:   Odoo (posted moves — never written back)
 * Auth:  HMAC-SHA256 signed (X-Odoo-Signature header)
 */

import { createClient } from "jsr:@supabase/supabase-js@2";

interface OdooMoveLine {
  move_id: number;
  move_name: string;
  move_line_id: number;
  posting_date: string;
  partner_id: number;
  partner_name: string;
  partner_tin?: string;
  payee_type: "individual" | "corporate";
  income_type: string;
  gross_income_band?: string;
  is_vat_registered?: boolean;
  is_top_wha?: boolean;
  base_amount: number;
  posted_ewt?: number;
}

interface TaxComputePayload {
  odoo_db: "odoo" | "odoo_staging" | "odoo_dev";
  tenant_id: string;
  company_id: number;
  period_start: string;
  period_end: string;
  move_lines: OdooMoveLine[];
  tax_run_id?: string;
}

const RISK_THRESHOLDS = { low: 0.01, medium: 0.05, high: 0.10, critical: 0.20 };

async function verifySignature(body: string, sig: string | null, secret: string): Promise<boolean> {
  if (!sig) return false;
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const expected = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(body));
  const hex = Array.from(new Uint8Array(expected)).map(b => b.toString(16).padStart(2, "0")).join("");
  return hex === sig;
}

function scoreRisk(computed: number, posted: number, resolved: boolean, tin?: string) {
  if (!resolved) return { risk_level: "critical" as const, risk_reason: "ATC unresolved" };
  if (computed > 0 && posted === 0) return { risk_level: "critical" as const, risk_reason: `EWT ₱${computed.toFixed(2)} required, ₱0 posted` };
  if (!tin && computed > 500) return { risk_level: "high" as const, risk_reason: "Missing TIN" };
  const ratio = computed > 0 ? Math.abs(computed - posted) / computed : 0;
  if (ratio > RISK_THRESHOLDS.critical) return { risk_level: "critical" as const, risk_reason: `Delta ${(ratio*100).toFixed(1)}%` };
  if (ratio > RISK_THRESHOLDS.high) return { risk_level: "high" as const, risk_reason: `Delta ${(ratio*100).toFixed(1)}%` };
  if (ratio > RISK_THRESHOLDS.medium) return { risk_level: "medium" as const, risk_reason: `Delta ${(ratio*100).toFixed(1)}%` };
  if (ratio > RISK_THRESHOLDS.low) return { risk_level: "low" as const, risk_reason: `Delta ${(ratio*100).toFixed(1)}%` };
  return { risk_level: "ok" as const, risk_reason: undefined };
}

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") return new Response("Method Not Allowed", { status: 405 });

  const rawBody = await req.text();
  const sig = req.headers.get("X-Odoo-Signature");
  if (!(await verifySignature(rawBody, sig, Deno.env.get("ODOO_WEBHOOK_SECRET") ?? ""))) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: { "Content-Type": "application/json" } });
  }

  let payload: TaxComputePayload;
  try { payload = JSON.parse(rawBody); } catch { return new Response(JSON.stringify({ error: "Invalid JSON" }), { status: 400 }); }

  const { odoo_db, tenant_id, company_id, period_start, period_end, move_lines } = payload;
  if (!odoo_db || !tenant_id || !move_lines?.length) {
    return new Response(JSON.stringify({ error: "Missing required fields" }), { status: 400 });
  }

  const supabase = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });

  // Create tax_run
  const { data: taxRun, error: runErr } = await supabase
    .from("ops.tax_runs")
    .insert({ tenant_id, odoo_db, period_start, period_end, company_id, status: "running", total_docs: move_lines.length, started_at: new Date().toISOString() })
    .select("id").single();

  if (runErr || !taxRun) return new Response(JSON.stringify({ error: "Failed to create tax run" }), { status: 500 });
  const taxRunId = taxRun.id;

  // Process lines
  const findings: Record<string, unknown>[] = [];
  let totalBase = 0, totalEwt = 0, flagged = 0;

  for (const line of move_lines) {
    const { data: atcData } = await supabase.rpc("resolve_atc", {
      p_payee_type: line.payee_type, p_income_type: line.income_type,
      p_gross_income_band: line.gross_income_band ?? "any",
      p_is_vat_registered: line.is_vat_registered ?? null,
      p_is_top_wha: line.is_top_wha ?? false, p_amount: line.base_amount,
    });

    const atc = (atcData as { atc_code: string; current_rate: number }[])?.[0];
    const rate = atc?.current_rate ?? null;
    const ewt = rate !== null ? Math.round(line.base_amount * rate * 100) / 100 : null;
    const posted = line.posted_ewt ?? 0;
    const { risk_level, risk_reason } = scoreRisk(ewt ?? 0, posted, !!atc, line.partner_tin);
    const review = ["high", "critical"].includes(risk_level);
    if (review) flagged++;
    totalBase += line.base_amount;
    totalEwt += ewt ?? 0;

    findings.push({
      tax_run_id: taxRunId, tenant_id, odoo_db,
      move_id: line.move_id, move_name: line.move_name, move_line_id: line.move_line_id,
      posting_date: line.posting_date, partner_id: line.partner_id, partner_name: line.partner_name,
      partner_tin: line.partner_tin, payee_type: line.payee_type, income_type: line.income_type,
      atc_code: atc?.atc_code, base_amount: line.base_amount,
      computed_rate: rate, computed_ewt: ewt, posted_ewt: posted,
      risk_level, risk_reason, requires_review: review, bir_form_eligible: ["2307", "1601-EQ"],
    });
  }

  // Batch insert
  for (let i = 0; i < findings.length; i += 200) {
    await supabase.from("ops.tax_findings").insert(findings.slice(i, i + 200));
  }

  // Update run
  await supabase.from("ops.tax_runs").update({
    status: "completed", docs_processed: move_lines.length, docs_flagged: flagged,
    total_base: totalBase, total_ewt: totalEwt, completed_at: new Date().toISOString(),
  }).eq("id", taxRunId);

  // Audit
  await supabase.from("audit.tax_events").insert({
    tenant_id, event_type: "tax_run_completed", source: "tax-compute", tax_run_id: taxRunId, odoo_db,
    payload: { docs: move_lines.length, flagged, total_base: totalBase, total_ewt: totalEwt },
  });

  return new Response(JSON.stringify({
    tax_run_id: taxRunId, docs: move_lines.length, flagged, total_base: totalBase, total_ewt: totalEwt,
    next: flagged > 0 ? `Review ${flagged} flagged items` : "Generate 2307 forms",
  }), { status: 200, headers: { "Content-Type": "application/json" } });
});
