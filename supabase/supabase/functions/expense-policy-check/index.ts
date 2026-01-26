// =============================================================================
// EXPENSE POLICY CHECK - Gap Handler Edge Function
// =============================================================================
// Capability: travel.expense.policy
// Handler: policy.expense_rules
// Description: Per diem, category limits, receipt requirements engine
// =============================================================================

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

interface ExpenseLine {
  id: string;
  category: string;
  amount: number;
  currency: string;
  date: string;
  has_receipt: boolean;
  merchant?: string;
  description?: string;
}

interface PolicyRule {
  rule_type: "per_diem" | "category_limit" | "receipt_required" | "merchant_block";
  category?: string;
  limit_amount?: number;
  limit_currency?: string;
  receipt_threshold?: number;
  blocked_merchants?: string[];
  message: string;
}

interface PolicyCheckRequest {
  tenant_id: string;
  employee_id: string;
  expense_lines: ExpenseLine[];
  trip_destination?: string;
  trip_dates?: { start: string; end: string };
}

interface PolicyViolation {
  line_id: string;
  rule_type: string;
  severity: "warning" | "error" | "block";
  message: string;
  auto_fixable: boolean;
  suggested_fix?: string;
}

interface PolicyCheckResponse {
  ok: boolean;
  violations: PolicyViolation[];
  summary: {
    total_lines: number;
    passed: number;
    warnings: number;
    errors: number;
    blocked: number;
  };
  auto_approved: boolean;
}

// Default policy rules (should be loaded from DB per tenant)
const DEFAULT_RULES: PolicyRule[] = [
  {
    rule_type: "receipt_required",
    receipt_threshold: 25,
    message: "Receipt required for expenses over $25",
  },
  {
    rule_type: "category_limit",
    category: "meals",
    limit_amount: 75,
    limit_currency: "USD",
    message: "Meal expenses limited to $75 per day",
  },
  {
    rule_type: "category_limit",
    category: "lodging",
    limit_amount: 250,
    limit_currency: "USD",
    message: "Lodging expenses limited to $250 per night",
  },
  {
    rule_type: "per_diem",
    limit_amount: 100,
    limit_currency: "USD",
    message: "Per diem limit is $100/day for this destination",
  },
];

async function loadPolicyRules(
  supabase: ReturnType<typeof createClient>,
  tenantId: string
): Promise<PolicyRule[]> {
  // TODO: Load from gold.capability_map or dedicated policy table
  // For now, return default rules
  return DEFAULT_RULES;
}

function checkExpenseLine(
  line: ExpenseLine,
  rules: PolicyRule[]
): PolicyViolation[] {
  const violations: PolicyViolation[] = [];

  for (const rule of rules) {
    switch (rule.rule_type) {
      case "receipt_required":
        if (
          line.amount > (rule.receipt_threshold || 25) &&
          !line.has_receipt
        ) {
          violations.push({
            line_id: line.id,
            rule_type: "receipt_required",
            severity: "error",
            message: rule.message,
            auto_fixable: false,
            suggested_fix: "Upload receipt image",
          });
        }
        break;

      case "category_limit":
        if (
          line.category === rule.category &&
          line.amount > (rule.limit_amount || 0)
        ) {
          violations.push({
            line_id: line.id,
            rule_type: "category_limit",
            severity: "warning",
            message: `${rule.message} (actual: ${line.amount} ${line.currency})`,
            auto_fixable: false,
            suggested_fix: "Request manager exception or split expense",
          });
        }
        break;

      case "merchant_block":
        if (
          rule.blocked_merchants &&
          line.merchant &&
          rule.blocked_merchants.some((m) =>
            line.merchant!.toLowerCase().includes(m.toLowerCase())
          )
        ) {
          violations.push({
            line_id: line.id,
            rule_type: "merchant_block",
            severity: "block",
            message: `Merchant "${line.merchant}" is blocked by company policy`,
            auto_fixable: false,
          });
        }
        break;
    }
  }

  return violations;
}

serve(async (req: Request) => {
  // CORS headers
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

    const body: PolicyCheckRequest = await req.json();
    const { tenant_id, employee_id, expense_lines, trip_destination, trip_dates } = body;

    // Load policy rules for tenant
    const rules = await loadPolicyRules(supabaseClient, tenant_id);

    // Check each expense line
    const allViolations: PolicyViolation[] = [];
    for (const line of expense_lines) {
      const lineViolations = checkExpenseLine(line, rules);
      allViolations.push(...lineViolations);
    }

    // Calculate summary
    const warnings = allViolations.filter((v) => v.severity === "warning").length;
    const errors = allViolations.filter((v) => v.severity === "error").length;
    const blocked = allViolations.filter((v) => v.severity === "block").length;
    const passed = expense_lines.length - new Set(allViolations.map((v) => v.line_id)).size;

    const response: PolicyCheckResponse = {
      ok: blocked === 0 && errors === 0,
      violations: allViolations,
      summary: {
        total_lines: expense_lines.length,
        passed,
        warnings,
        errors,
        blocked,
      },
      auto_approved: allViolations.length === 0,
    };

    // Log to audit trail
    await supabaseClient.from("runtime.audit_log").insert({
      tenant_id,
      action: "expense_policy_check",
      resource_type: "expense_report",
      details: {
        employee_id,
        line_count: expense_lines.length,
        violation_count: allViolations.length,
        auto_approved: response.auto_approved,
      },
    });

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
