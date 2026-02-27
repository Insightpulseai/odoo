"""
IPAI AI Copilot — Main controller.

Endpoints:
  POST /ipai/copilot/chat         — conversational AI with tool execution
  POST /ipai/copilot/execute_tools — confirmed tool execution after user approval
  GET  /ipai/copilot/insights     — fetch proactive insights for current user
  GET  /ipai/copilot/tools        — list registered tools (for UI display only)

Architecture:
  Request → context_injection() → bridge_payload() → IPAI bridge (Gemini function calling)
         → tool_dispatch() [if AI requested tool] → confirmation_required()
         → execute_tool() → return result to AI → final response

Bridge payload includes:
  - system_prompt: role + tool descriptions
  - context: current_model, record_id, user_name, company, active_ids
  - conversation_history: from ipai.copilot.session
  - tools: list of available tool declarations (Gemini function calling format)
  - message: user's current message

Error codes (same pattern as ipai_ai_widget):
  BRIDGE_URL_NOT_CONFIGURED  — ir.config_parameter missing
  AI_KEY_NOT_CONFIGURED      — 503 from bridge
  BRIDGE_TIMEOUT             — 30s timeout
  TOOL_EXECUTION_FAILED      — tool raised exception
  ACCESS_DENIED              — user lacks permission for tool action
  MESSAGE_REQUIRED           — empty prompt
"""

import json
import logging
import requests
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)
TIMEOUT = 30
SYSTEM_PROMPT = """You are IPAI Copilot, an intelligent business assistant embedded in Odoo ERP.
You have access to tools that let you search, read, create, and update Odoo records.
Always be concise and business-focused. When you need to take an action, use the appropriate tool.
For write operations (create, update, confirm), always summarize what you will do and ask for confirmation.
Current context is provided in the user message. Use it to give relevant, specific answers.
Respond in the same language as the user's message."""


class IpaiCopilotController(http.Controller):

    @http.route(
        "/ipai/copilot/chat",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def chat(self, message=None, session_id=None, context=None, **_kw):
        """Main conversational endpoint. Routes message through IPAI bridge with tool support."""
        if not message or not str(message).strip():
            return {"error": "MESSAGE_REQUIRED", "status": 400}

        bridge_url = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_ai_copilot.bridge_url", default="")
        )
        if not bridge_url:
            return {"error": "BRIDGE_URL_NOT_CONFIGURED", "status": 503}

        # Load or create session
        Session = request.env["ipai.copilot.session"]
        session = Session._get_or_create(session_id)

        # Get available tools (server-side only — not sent before AI evaluation)
        tools = (
            request.env["ipai.copilot.tool"]
            .sudo()
            .search([("active", "=", True)])
        )
        tool_declarations = [t._to_gemini_declaration() for t in tools]

        # Build context string
        ctx_str = _format_context(context or {})

        # Build payload for IPAI bridge
        payload = {
            "system_prompt": SYSTEM_PROMPT,
            "context": ctx_str,
            "history": session._get_history(),
            "message": str(message).strip(),
            "tools": tool_declarations,
        }

        try:
            resp = requests.post(
                bridge_url,
                json=payload,
                timeout=TIMEOUT,
                headers={"Content-Type": "application/json"},
            )
        except requests.Timeout:
            return {"error": "BRIDGE_TIMEOUT", "status": 504}
        except requests.RequestException as exc:
            _logger.error("IPAI Copilot bridge error: %s", exc)
            return {"error": "BRIDGE_ERROR", "status": 500}

        if resp.status_code == 503:
            return {"error": "AI_KEY_NOT_CONFIGURED", "status": 503}
        if not resp.ok:
            _logger.error(
                "IPAI Copilot bridge returned %s: %s", resp.status_code, resp.text[:200]
            )
            return {"error": "BRIDGE_ERROR", "status": resp.status_code}

        data = resp.json()

        # Handle tool calls — return to client for confirmation before execution
        if data.get("tool_calls"):
            tool_results_preview = []
            for tc in data["tool_calls"]:
                preview = _dispatch_tool_preview(tc["name"], tc.get("args", {}))
                tool_results_preview.append({"tool": tc["name"], "result": preview})
            # Append user message to history (assistant response pending confirmation)
            session._append(role="user", content=str(message).strip())
            return {
                "type": "tool_confirmation",
                "session_id": session.id,
                "tool_calls": data["tool_calls"],
                "tool_results_preview": tool_results_preview,
                "trace_id": data.get("trace_id", ""),
            }

        # Plain text response
        session._append(role="user", content=str(message).strip())
        session._append(role="assistant", content=data.get("text", ""))

        return {
            "type": "message",
            "session_id": session.id,
            "provider": data.get("provider", "unknown"),
            "text": data.get("text", ""),
            "model": data.get("model", ""),
            "trace_id": data.get("trace_id", ""),
        }

    @http.route(
        "/ipai/copilot/execute_tools",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def execute_tools(self, tool_calls=None, session_id=None, **_kw):
        """Execute confirmed tool calls. User must have already approved via confirmation dialog."""
        if not tool_calls:
            return {"error": "NO_TOOL_CALLS", "status": 400}

        results = []
        for tc in tool_calls:
            tool_name = tc.get("name", "")
            tool_args = tc.get("args", {})
            try:
                result = _execute_tool_confirmed(tool_name, tool_args)
                results.append({"tool": tool_name, "status": "ok", "result": result})
                # Append execution to session history if session provided
                if session_id:
                    try:
                        session = request.env["ipai.copilot.session"].browse(
                            int(session_id)
                        )
                        if session.exists() and session.user_id == request.env.user:
                            session._append(
                                role="assistant",
                                content=f"[Tool: {tool_name}] {json.dumps(result)}",
                            )
                    except Exception:
                        pass
            except PermissionError as exc:
                results.append(
                    {"tool": tool_name, "status": "error", "error": "ACCESS_DENIED", "detail": str(exc)}
                )
            except Exception as exc:
                _logger.error("Tool execution failed: %s(%s) — %s", tool_name, tool_args, exc)
                results.append(
                    {"tool": tool_name, "status": "error", "error": "TOOL_EXECUTION_FAILED", "detail": str(exc)}
                )

        return {"results": results}

    @http.route(
        "/ipai/copilot/insights",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def insights(self, **_kw):
        """Fetch proactive insights for the current user."""
        insights = request.env["ipai.copilot.insight"].search(
            [
                ("user_id", "in", [request.env.user.id, False]),
                ("dismissed", "=", False),
            ],
            order="priority desc, date desc",
            limit=10,
        )
        return [i._to_dict() for i in insights]

    @http.route(
        "/ipai/copilot/tools",
        type="json",
        auth="user",
        methods=["POST"],
        csrf=False,
    )
    def tools_list(self, **_kw):
        """List registered tools for UI display only — not for AI evaluation."""
        tools = (
            request.env["ipai.copilot.tool"].sudo().search([("active", "=", True)])
        )
        return [
            {
                "name": t.name,
                "display_name": t.display_name,
                "description": t.description,
                "category": t.category,
                "requires_confirmation": t.requires_confirmation,
            }
            for t in tools
        ]


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _format_context(ctx):
    """Format context dict into a readable string for the AI system prompt."""
    parts = []
    if ctx.get("model"):
        parts.append(f"Current model: {ctx['model']}")
    if ctx.get("record_id"):
        parts.append(f"Current record ID: {ctx['record_id']}")
    if ctx.get("active_ids"):
        parts.append(f"Selected records: {ctx['active_ids']}")
    if ctx.get("user_name"):
        parts.append(f"User: {ctx['user_name']}")
    if ctx.get("company"):
        parts.append(f"Company: {ctx['company']}")
    return " | ".join(parts) if parts else "No record context"


def _dispatch_tool_preview(name, args):
    """
    Read-only human-readable preview of what a tool WOULD do.
    Used for the confirmation dialog — never executes anything.
    """
    preview_map = {
        "search_records": lambda a: (
            f"Search {a.get('model', '?')} for \"{a.get('query', '?')}\""
        ),
        "read_record": lambda a: (
            f"Read {a.get('model', '?')} ID {a.get('record_id', '?')}"
        ),
        "navigate_to": lambda a: (
            f"Open {a.get('model', '?')} ID {a.get('record_id', '?')}"
        ),
        "create_record": lambda a: (
            f"Create new {a.get('model', '?')} with {json.dumps(a.get('values', {}))}"
        ),
        "update_record": lambda a: (
            f"Update {a.get('model', '?')} ID {a.get('record_id', '?')}: "
            f"{json.dumps(a.get('values', {}))}"
        ),
        "send_chatter_message": lambda a: (
            f"Post message in chatter: \"{a.get('message', '')}\""
        ),
        "schedule_activity": lambda a: (
            f"Schedule {a.get('activity_type', 'activity')} on {a.get('date', '?')}: "
            f"\"{a.get('summary', '')}\""
        ),
        "trigger_workflow": lambda a: (
            f"Trigger n8n workflow: {a.get('workflow_id', '?')}"
        ),
        "confirm_invoice": lambda a: (
            f"Confirm (validate) invoice ID {a.get('invoice_id', '?')}"
        ),
        "create_quotation": lambda a: (
            f"Create quotation for partner ID {a.get('partner_id', '?')}"
        ),
        "confirm_sale_order": lambda a: (
            f"Confirm sale order ID {a.get('order_id', '?')}"
        ),
        "create_payment": lambda a: (
            f"Register payment of {a.get('amount', '?')} on invoice ID {a.get('invoice_id', '?')}"
        ),
        "check_stock": lambda a: (
            f"Check stock for product ID {a.get('product_id', '?')}"
        ),
    }
    fn = preview_map.get(name, lambda a: f"Execute {name}({json.dumps(a)})")
    return fn(args)


def _execute_tool_confirmed(name, args):
    """
    Execute a confirmed tool. All write operations require prior user confirmation via UI.
    Record rules and access rights are enforced via request.env (user context).
    """
    env = request.env

    # ── Read tools (no confirmation required) ─────────────────────────────────

    if name == "search_records":
        model = args.get("model", "res.partner")
        query = args.get("query", "")
        limit = min(int(args.get("limit", 5)), 20)
        records = env[model].name_search(query, limit=limit)
        return [{"id": r[0], "name": r[1]} for r in records]

    elif name == "read_record":
        model = args.get("model")
        rec_id = int(args.get("record_id", 0))
        fields = args.get("fields", [])
        rec = env[model].browse(rec_id)
        if not rec.exists():
            return {"error": "record_not_found"}
        if fields:
            return {f: getattr(rec, f, None) for f in fields}
        return {
            "id": rec.id,
            "name": getattr(rec, "name", str(rec)),
            "display_name": getattr(rec, "display_name", str(rec)),
        }

    elif name == "get_pipeline_summary":
        leads = env["crm.lead"].search(
            [("type", "=", "opportunity"), ("active", "=", True)],
            limit=50,
        )
        by_stage = {}
        for lead in leads:
            stage = lead.stage_id.name if lead.stage_id else "Unknown"
            by_stage.setdefault(stage, {"count": 0, "amount": 0.0})
            by_stage[stage]["count"] += 1
            by_stage[stage]["amount"] += lead.expected_revenue or 0.0
        return {"pipeline": by_stage, "total_leads": len(leads)}

    elif name == "check_stock":
        product_id = int(args.get("product_id", 0))
        product = env["product.product"].browse(product_id)
        if not product.exists():
            return {"error": "product_not_found"}
        return {
            "product": product.name,
            "qty_available": product.qty_available,
            "qty_on_hand": getattr(product, "qty_on_hand", product.qty_available),
            "uom": product.uom_id.name if product.uom_id else "",
        }

    elif name == "run_aged_receivables":
        invoices = env["account.move"].search(
            [
                ("move_type", "in", ["out_invoice", "out_refund"]),
                ("state", "=", "posted"),
                ("payment_state", "not in", ["paid", "reversed"]),
            ],
            limit=20,
            order="invoice_date_due asc",
        )
        result = []
        for inv in invoices:
            result.append(
                {
                    "id": inv.id,
                    "partner": inv.partner_id.name if inv.partner_id else "",
                    "amount_residual": inv.amount_residual,
                    "date_due": inv.invoice_date_due.isoformat()
                    if inv.invoice_date_due
                    else None,
                    "currency": inv.currency_id.name if inv.currency_id else "",
                }
            )
        return {"overdue_invoices": result}

    elif name == "navigate_to":
        # Navigation is handled client-side; return action descriptor
        return {
            "action": "navigate",
            "model": args.get("model"),
            "id": args.get("record_id"),
        }

    # ── Write tools (all require confirmation via UI before reaching here) ────

    elif name == "send_chatter_message":
        model = args.get("model")
        rec_id = int(args.get("record_id", 0))
        msg = args.get("message", "")
        if not msg:
            return {"error": "message_required"}
        env[model].browse(rec_id).message_post(body=msg)
        return {"status": "sent", "model": model, "record_id": rec_id}

    elif name == "schedule_activity":
        model = args.get("model")
        rec_id = int(args.get("record_id", 0))
        summary = args.get("summary", "")
        date_deadline = args.get("date")
        act_type = env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        env[model].browse(rec_id).activity_schedule(
            activity_type_id=act_type.id if act_type else None,
            summary=summary,
            date_deadline=date_deadline,
        )
        return {"status": "scheduled", "model": model, "record_id": rec_id}

    elif name == "create_record":
        model = args.get("model")
        values = args.get("values", {})
        if not model or not values:
            return {"error": "model_and_values_required"}
        rec = env[model].create(values)
        return {"id": rec.id, "name": getattr(rec, "name", str(rec))}

    elif name == "update_record":
        model = args.get("model")
        rec_id = int(args.get("record_id", 0))
        values = args.get("values", {})
        rec = env[model].browse(rec_id)
        if not rec.exists():
            return {"error": "record_not_found"}
        rec.write(values)
        return {"status": "updated", "id": rec.id}

    elif name == "confirm_invoice":
        invoice_id = int(args.get("invoice_id", 0))
        invoice = env["account.move"].browse(invoice_id)
        if not invoice.exists():
            return {"error": "invoice_not_found"}
        invoice.action_post()
        return {"status": "confirmed", "id": invoice.id, "state": invoice.state}

    elif name == "create_payment":
        import datetime

        invoice_id = int(args.get("invoice_id", 0))
        invoice = env["account.move"].browse(invoice_id)
        if not invoice.exists():
            return {"error": "invoice_not_found"}
        payment_register = (
            env["account.payment.register"]
            .with_context(active_model="account.move", active_ids=[invoice_id])
            .create(
                {
                    "payment_date": datetime.date.today(),
                    "amount": args.get("amount") or invoice.amount_residual,
                }
            )
        )
        payment_register.action_create_payments()
        return {"status": "payment_registered", "invoice_id": invoice_id}

    elif name == "create_quotation":
        partner_id = int(args.get("partner_id", 0))
        order_lines = args.get("order_lines", [])
        vals = {
            "partner_id": partner_id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "product_id": line.get("product_id"),
                        "product_uom_qty": line.get("qty", 1),
                        "price_unit": line.get("price_unit", 0),
                    },
                )
                for line in order_lines
            ],
        }
        order = env["sale.order"].create(vals)
        return {"id": order.id, "name": order.name, "state": order.state}

    elif name == "confirm_sale_order":
        order_id = int(args.get("order_id", 0))
        order = env["sale.order"].browse(order_id)
        if not order.exists():
            return {"error": "order_not_found"}
        order.action_confirm()
        return {"status": "confirmed", "id": order.id, "state": order.state}

    elif name == "trigger_workflow":
        import hmac
        import hashlib

        wf_id = args.get("workflow_id", "")
        wf_data = args.get("data", {})

        # Allowlist check — workflow must be configured in ir.config_parameter
        webhook_url = (
            env["ir.config_parameter"]
            .sudo()
            .get_param(f"ipai_ai_copilot.n8n_webhook.{wf_id}", "")
        )
        if not webhook_url:
            return {"error": f"workflow '{wf_id}' not in allowlist"}

        # HMAC signature
        n8n_secret = (
            env["ir.config_parameter"]
            .sudo()
            .get_param("ipai_ai_copilot.n8n_secret", "")
        )
        body = json.dumps(wf_data).encode()
        headers = {"Content-Type": "application/json"}
        if n8n_secret:
            sig = hmac.new(n8n_secret.encode(), body, hashlib.sha256).hexdigest()
            headers["X-IPAI-Signature"] = f"sha256={sig}"

        r = requests.post(webhook_url, data=body, headers=headers, timeout=15)
        return {"status": "triggered", "workflow_id": wf_id, "code": r.status_code}

    else:
        raise ValueError(f"Unknown tool: {name!r}")
