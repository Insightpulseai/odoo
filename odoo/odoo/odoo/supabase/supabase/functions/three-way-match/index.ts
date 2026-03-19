// =============================================================================
// THREE-WAY MATCH - Gap Handler Edge Function
// =============================================================================
// Capability: ap.invoice.three_way_match
// Handler: assertions.three_way_match
// Description: Assertion store (PO/GR/INV) + tolerance checks
// =============================================================================

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

interface LineItem {
  product_id: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  total: number;
}

interface Document {
  id: string;
  number: string;
  date: string;
  vendor_id: string;
  lines: LineItem[];
  total: number;
}

interface MatchRequest {
  tenant_id: string;
  purchase_order: Document;
  goods_receipt?: Document;
  invoice: Document;
  tolerance_percent?: number;
  tolerance_amount?: number;
}

interface MatchAssertion {
  assertion_type: "quantity" | "price" | "total" | "vendor";
  product_id?: string;
  expected: number | string;
  actual: number | string;
  variance: number;
  variance_percent: number;
  within_tolerance: boolean;
  message: string;
}

interface MatchResult {
  ok: boolean;
  match_status: "full_match" | "partial_match" | "mismatch" | "pending_gr";
  assertions: MatchAssertion[];
  summary: {
    po_total: number;
    gr_total: number | null;
    inv_total: number;
    total_variance: number;
    total_variance_percent: number;
  };
  work_item_created?: string;
}

function calculateVariance(expected: number, actual: number): { variance: number; percent: number } {
  const variance = actual - expected;
  const percent = expected !== 0 ? (variance / expected) * 100 : 0;
  return { variance, percent: Math.round(percent * 100) / 100 };
}

function matchDocuments(
  po: Document,
  gr: Document | undefined,
  inv: Document,
  tolerancePercent: number,
  toleranceAmount: number
): MatchAssertion[] {
  const assertions: MatchAssertion[] = [];

  // Vendor match
  if (po.vendor_id !== inv.vendor_id) {
    assertions.push({
      assertion_type: "vendor",
      expected: po.vendor_id,
      actual: inv.vendor_id,
      variance: 0,
      variance_percent: 0,
      within_tolerance: false,
      message: `Vendor mismatch: PO vendor ${po.vendor_id} ≠ Invoice vendor ${inv.vendor_id}`,
    });
  }

  // Total match (PO vs Invoice)
  const totalVariance = calculateVariance(po.total, inv.total);
  const totalWithinTolerance =
    Math.abs(totalVariance.percent) <= tolerancePercent ||
    Math.abs(totalVariance.variance) <= toleranceAmount;

  assertions.push({
    assertion_type: "total",
    expected: po.total,
    actual: inv.total,
    variance: totalVariance.variance,
    variance_percent: totalVariance.percent,
    within_tolerance: totalWithinTolerance,
    message: totalWithinTolerance
      ? `Total within tolerance: PO ${po.total} ≈ INV ${inv.total} (${totalVariance.percent}%)`
      : `Total mismatch: PO ${po.total} ≠ INV ${inv.total} (${totalVariance.percent}% variance)`,
  });

  // Line-by-line matching
  for (const poLine of po.lines) {
    const invLine = inv.lines.find((l) => l.product_id === poLine.product_id);

    if (!invLine) {
      assertions.push({
        assertion_type: "quantity",
        product_id: poLine.product_id,
        expected: poLine.quantity,
        actual: 0,
        variance: -poLine.quantity,
        variance_percent: -100,
        within_tolerance: false,
        message: `Product ${poLine.product_name} on PO but not on Invoice`,
      });
      continue;
    }

    // Quantity match
    const qtyVariance = calculateVariance(poLine.quantity, invLine.quantity);
    const qtyWithinTolerance =
      Math.abs(qtyVariance.percent) <= tolerancePercent ||
      Math.abs(qtyVariance.variance) <= 1; // Allow 1 unit variance

    assertions.push({
      assertion_type: "quantity",
      product_id: poLine.product_id,
      expected: poLine.quantity,
      actual: invLine.quantity,
      variance: qtyVariance.variance,
      variance_percent: qtyVariance.percent,
      within_tolerance: qtyWithinTolerance,
      message: qtyWithinTolerance
        ? `Quantity OK for ${poLine.product_name}`
        : `Quantity mismatch for ${poLine.product_name}: PO ${poLine.quantity} ≠ INV ${invLine.quantity}`,
    });

    // Price match
    const priceVariance = calculateVariance(poLine.unit_price, invLine.unit_price);
    const priceWithinTolerance =
      Math.abs(priceVariance.percent) <= tolerancePercent ||
      Math.abs(priceVariance.variance) <= toleranceAmount;

    assertions.push({
      assertion_type: "price",
      product_id: poLine.product_id,
      expected: poLine.unit_price,
      actual: invLine.unit_price,
      variance: priceVariance.variance,
      variance_percent: priceVariance.percent,
      within_tolerance: priceWithinTolerance,
      message: priceWithinTolerance
        ? `Price OK for ${poLine.product_name}`
        : `Price mismatch for ${poLine.product_name}: PO ${poLine.unit_price} ≠ INV ${invLine.unit_price}`,
    });
  }

  // Check for invoice lines not on PO
  for (const invLine of inv.lines) {
    const poLine = po.lines.find((l) => l.product_id === invLine.product_id);
    if (!poLine) {
      assertions.push({
        assertion_type: "quantity",
        product_id: invLine.product_id,
        expected: 0,
        actual: invLine.quantity,
        variance: invLine.quantity,
        variance_percent: 100,
        within_tolerance: false,
        message: `Product ${invLine.product_name} on Invoice but not on PO (unauthorized)`,
      });
    }
  }

  // GR matching (if provided)
  if (gr) {
    const grTotalVariance = calculateVariance(gr.total, inv.total);
    const grWithinTolerance =
      Math.abs(grTotalVariance.percent) <= tolerancePercent ||
      Math.abs(grTotalVariance.variance) <= toleranceAmount;

    assertions.push({
      assertion_type: "total",
      expected: gr.total,
      actual: inv.total,
      variance: grTotalVariance.variance,
      variance_percent: grTotalVariance.percent,
      within_tolerance: grWithinTolerance,
      message: grWithinTolerance
        ? `GR-Invoice total match: GR ${gr.total} ≈ INV ${inv.total}`
        : `GR-Invoice mismatch: GR ${gr.total} ≠ INV ${inv.total}`,
    });
  }

  return assertions;
}

serve(async (req: Request) => {
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  };

  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_ANON_KEY") ?? "",
      {
        global: {
          headers: { Authorization: req.headers.get("Authorization")! },
        },
      }
    );

    const body: MatchRequest = await req.json();
    const {
      tenant_id,
      purchase_order,
      goods_receipt,
      invoice,
      tolerance_percent = 2,
      tolerance_amount = 10,
    } = body;

    // Run matching assertions
    const assertions = matchDocuments(
      purchase_order,
      goods_receipt,
      invoice,
      tolerance_percent,
      tolerance_amount
    );

    // Determine match status
    const failedAssertions = assertions.filter((a) => !a.within_tolerance);
    const hasVendorMismatch = failedAssertions.some((a) => a.assertion_type === "vendor");
    const hasPriceMismatch = failedAssertions.some((a) => a.assertion_type === "price");

    let matchStatus: MatchResult["match_status"];
    if (failedAssertions.length === 0) {
      matchStatus = "full_match";
    } else if (!goods_receipt) {
      matchStatus = "pending_gr";
    } else if (hasVendorMismatch || failedAssertions.length > 3) {
      matchStatus = "mismatch";
    } else {
      matchStatus = "partial_match";
    }

    // Calculate summary
    const summary = {
      po_total: purchase_order.total,
      gr_total: goods_receipt?.total ?? null,
      inv_total: invoice.total,
      total_variance: invoice.total - purchase_order.total,
      total_variance_percent: calculateVariance(purchase_order.total, invoice.total).percent,
    };

    const result: MatchResult = {
      ok: matchStatus === "full_match",
      match_status: matchStatus,
      assertions,
      summary,
    };

    // Create work item for mismatches
    if (matchStatus === "mismatch" || matchStatus === "partial_match") {
      const { data: workItem } = await supabaseClient
        .from("run.work_items")
        .insert({
          tenant_id,
          node_id: null, // Will be set by process engine
          title: `3-Way Match Dispute: PO ${purchase_order.number} / INV ${invoice.number}`,
          payload: {
            purchase_order_id: purchase_order.id,
            invoice_id: invoice.id,
            goods_receipt_id: goods_receipt?.id,
            failed_assertions: failedAssertions,
            summary,
          },
          status: "pending",
        })
        .select("id")
        .single();

      if (workItem) {
        result.work_item_created = workItem.id;
      }
    }

    // Log to audit trail
    await supabaseClient.from("runtime.audit_log").insert({
      tenant_id,
      action: "three_way_match",
      resource_type: "invoice",
      resource_id: invoice.id,
      details: {
        po_number: purchase_order.number,
        inv_number: invoice.number,
        gr_number: goods_receipt?.number,
        match_status: matchStatus,
        assertion_count: assertions.length,
        failed_count: failedAssertions.length,
      },
    });

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 200,
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 400,
    });
  }
});
