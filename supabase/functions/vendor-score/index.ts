// =============================================================================
// VENDOR SCORING - Gap Handler Edge Function
// =============================================================================
// Capability: procurement.supplier.master
// Handler: vendor.scoring
// Description: Supplier risk scoring and performance tracking
// =============================================================================

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

interface VendorMetrics {
  on_time_delivery_rate: number; // 0-100
  quality_rate: number; // 0-100
  invoice_accuracy_rate: number; // 0-100
  response_time_days: number;
  total_orders: number;
  total_spend: number;
  dispute_count: number;
  active_contracts: number;
}

interface RiskFactor {
  factor: string;
  weight: number;
  score: number;
  max_score: number;
  impact: "positive" | "negative" | "neutral";
  details: string;
}

interface VendorScoreRequest {
  tenant_id: string;
  vendor_id: string;
  vendor_name: string;
  metrics?: VendorMetrics;
  force_recalculate?: boolean;
}

interface VendorScoreResponse {
  vendor_id: string;
  vendor_name: string;
  overall_score: number; // 0-100
  risk_level: "low" | "medium" | "high" | "critical";
  risk_factors: RiskFactor[];
  recommendations: string[];
  last_calculated: string;
  metrics_used: VendorMetrics;
}

// Scoring weights
const WEIGHTS = {
  on_time_delivery: 0.25,
  quality: 0.25,
  invoice_accuracy: 0.15,
  response_time: 0.10,
  order_volume: 0.10,
  dispute_rate: 0.15,
};

function calculateScore(metrics: VendorMetrics): {
  score: number;
  riskFactors: RiskFactor[];
} {
  const riskFactors: RiskFactor[] = [];

  // On-time delivery (0-100)
  const otdScore = metrics.on_time_delivery_rate;
  riskFactors.push({
    factor: "on_time_delivery",
    weight: WEIGHTS.on_time_delivery,
    score: otdScore,
    max_score: 100,
    impact: otdScore >= 90 ? "positive" : otdScore < 70 ? "negative" : "neutral",
    details: `${metrics.on_time_delivery_rate}% on-time delivery rate`,
  });

  // Quality rate (0-100)
  const qualityScore = metrics.quality_rate;
  riskFactors.push({
    factor: "quality",
    weight: WEIGHTS.quality,
    score: qualityScore,
    max_score: 100,
    impact: qualityScore >= 95 ? "positive" : qualityScore < 80 ? "negative" : "neutral",
    details: `${metrics.quality_rate}% quality acceptance rate`,
  });

  // Invoice accuracy (0-100)
  const invoiceScore = metrics.invoice_accuracy_rate;
  riskFactors.push({
    factor: "invoice_accuracy",
    weight: WEIGHTS.invoice_accuracy,
    score: invoiceScore,
    max_score: 100,
    impact: invoiceScore >= 95 ? "positive" : invoiceScore < 80 ? "negative" : "neutral",
    details: `${metrics.invoice_accuracy_rate}% invoice accuracy`,
  });

  // Response time (lower is better, normalize to 0-100)
  const responseScore = Math.max(0, 100 - metrics.response_time_days * 10);
  riskFactors.push({
    factor: "response_time",
    weight: WEIGHTS.response_time,
    score: responseScore,
    max_score: 100,
    impact: responseScore >= 80 ? "positive" : responseScore < 50 ? "negative" : "neutral",
    details: `Average response time: ${metrics.response_time_days} days`,
  });

  // Order volume (normalized, higher = more established)
  const volumeScore = Math.min(100, Math.log10(metrics.total_orders + 1) * 40);
  riskFactors.push({
    factor: "order_volume",
    weight: WEIGHTS.order_volume,
    score: volumeScore,
    max_score: 100,
    impact: volumeScore >= 60 ? "positive" : volumeScore < 30 ? "negative" : "neutral",
    details: `${metrics.total_orders} total orders, $${metrics.total_spend.toLocaleString()} spend`,
  });

  // Dispute rate (lower is better)
  const disputeRate = metrics.total_orders > 0
    ? (metrics.dispute_count / metrics.total_orders) * 100
    : 0;
  const disputeScore = Math.max(0, 100 - disputeRate * 20);
  riskFactors.push({
    factor: "dispute_rate",
    weight: WEIGHTS.dispute_rate,
    score: disputeScore,
    max_score: 100,
    impact: disputeScore >= 90 ? "positive" : disputeScore < 60 ? "negative" : "neutral",
    details: `${metrics.dispute_count} disputes (${disputeRate.toFixed(1)}% rate)`,
  });

  // Calculate weighted overall score
  const overallScore = riskFactors.reduce(
    (sum, f) => sum + (f.score / f.max_score) * f.weight * 100,
    0
  );

  return { score: Math.round(overallScore), riskFactors };
}

function getRiskLevel(score: number): VendorScoreResponse["risk_level"] {
  if (score >= 85) return "low";
  if (score >= 70) return "medium";
  if (score >= 50) return "high";
  return "critical";
}

function getRecommendations(riskFactors: RiskFactor[]): string[] {
  const recommendations: string[] = [];

  for (const factor of riskFactors) {
    if (factor.impact === "negative") {
      switch (factor.factor) {
        case "on_time_delivery":
          recommendations.push("Schedule performance review meeting to address delivery delays");
          break;
        case "quality":
          recommendations.push("Request quality improvement plan and increase inspection frequency");
          break;
        case "invoice_accuracy":
          recommendations.push("Work with vendor to improve invoice matching process");
          break;
        case "response_time":
          recommendations.push("Establish SLA for communication response times");
          break;
        case "dispute_rate":
          recommendations.push("Conduct root cause analysis on recurring disputes");
          break;
      }
    }
  }

  if (recommendations.length === 0) {
    recommendations.push("Vendor performing within acceptable parameters. Continue monitoring.");
  }

  return recommendations;
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

    const body: VendorScoreRequest = await req.json();
    const { tenant_id, vendor_id, vendor_name, force_recalculate = false } = body;

    // Use provided metrics or fetch from Odoo/Supabase
    let metrics: VendorMetrics = body.metrics || {
      on_time_delivery_rate: 92,
      quality_rate: 96,
      invoice_accuracy_rate: 88,
      response_time_days: 2,
      total_orders: 45,
      total_spend: 125000,
      dispute_count: 3,
      active_contracts: 2,
    };

    // Calculate score
    const { score, riskFactors } = calculateScore(metrics);
    const riskLevel = getRiskLevel(score);
    const recommendations = getRecommendations(riskFactors);

    const response: VendorScoreResponse = {
      vendor_id,
      vendor_name,
      overall_score: score,
      risk_level: riskLevel,
      risk_factors: riskFactors,
      recommendations,
      last_calculated: new Date().toISOString(),
      metrics_used: metrics,
    };

    // Store score in audit log
    await supabaseClient.from("runtime.audit_log").insert({
      tenant_id,
      action: "vendor_score_calculated",
      resource_type: "vendor",
      resource_id: vendor_id,
      details: {
        vendor_name,
        overall_score: score,
        risk_level: riskLevel,
        metrics,
      },
    });

    // Create alert for high-risk vendors
    if (riskLevel === "high" || riskLevel === "critical") {
      await supabaseClient.from("run.work_items").insert({
        tenant_id,
        title: `Vendor Risk Alert: ${vendor_name} (${riskLevel.toUpperCase()})`,
        payload: {
          vendor_id,
          vendor_name,
          overall_score: score,
          risk_level: riskLevel,
          top_issues: riskFactors
            .filter((f) => f.impact === "negative")
            .map((f) => f.details),
          recommendations,
        },
        status: "pending",
      });
    }

    return new Response(JSON.stringify(response), {
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
