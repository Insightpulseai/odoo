import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { PolicyFile } from "./policy.js";
import { OdooClient } from "./odoo-client.js";
import { CmsGateway } from "./cms-gateway.js";

type AuthorizeResult =
  | { ok: true }
  | { ok: false; error: string; errorDescription: string };

export interface ToolDeps {
  policy: PolicyFile;
  odoo: OdooClient;
  authorize: (ctx: unknown, requiredScope: string) => Promise<AuthorizeResult>;
}

export function registerOdooTools(server: McpServer, deps: ToolDeps) {
  const cms = new CmsGateway(deps.odoo);
  const odoo = deps.odoo;

  // ─── CONTACTS ───────────────────────────────────────────────────────

  server.tool(
    "odoo_search_partners",
    "Search contacts and companies in Odoo by name, email, or phone.",
    { query: z.string(), limit: z.number().min(1).max(25).optional() },
    async (args) => {
      const records = await odoo.searchRead("res.partner", {
        domain: ["|", "|", ["name", "ilike", args.query], ["email", "ilike", args.query], ["phone", "ilike", args.query]],
        fields: ["id", "name", "email", "phone", "mobile", "company_name", "city", "country_id"],
        limit: args.limit ?? 10,
        order: "name asc",
      });
      return { content: [{ type: "text", text: JSON.stringify({ count: (records as any[]).length, records }) }] };
    },
  );

  server.tool(
    "odoo_get_partner",
    "Get detailed information about an Odoo contact by ID.",
    { partner_id: z.number() },
    async (args) => {
      const records = await odoo.read("res.partner", [args.partner_id], [
        "id", "name", "email", "phone", "mobile", "street", "city", "country_id",
        "company_name", "function", "website", "comment", "credit_limit",
      ]);
      return { content: [{ type: "text", text: JSON.stringify(records) }] };
    },
  );

  // ─── CRM / PIPELINE ────────────────────────────────────────────────

  server.tool(
    "odoo_list_opportunities",
    "List CRM leads and opportunities, optionally filtered by stage or salesperson.",
    { stage: z.string().optional(), user: z.string().optional(), limit: z.number().min(1).max(50).optional() },
    async (args) => {
      const domain: unknown[] = [["type", "=", "opportunity"]];
      if (args.stage) domain.push(["stage_id.name", "ilike", args.stage]);
      if (args.user) domain.push(["user_id.name", "ilike", args.user]);

      const records = await odoo.searchRead("crm.lead", {
        domain,
        fields: ["id", "name", "partner_id", "expected_revenue", "stage_id", "probability", "user_id"],
        limit: args.limit ?? 25,
        order: "expected_revenue desc",
      });
      return { content: [{ type: "text", text: JSON.stringify({ count: (records as any[]).length, records }) }] };
    },
  );

  server.tool(
    "odoo_get_opportunity",
    "Get detailed information about a CRM lead or opportunity by ID.",
    { lead_id: z.number() },
    async (args) => {
      const records = await odoo.read("crm.lead", [args.lead_id], [
        "id", "name", "partner_id", "email_from", "phone", "expected_revenue",
        "probability", "stage_id", "user_id", "description", "date_deadline",
      ]);
      return { content: [{ type: "text", text: JSON.stringify(records) }] };
    },
  );

  // ─── SALES ──────────────────────────────────────────────────────────

  server.tool(
    "odoo_search_sale_orders",
    "Search Odoo sale orders by customer name or order reference.",
    { query: z.string(), limit: z.number().min(1).max(25).optional() },
    async (args) => {
      const records = await odoo.searchRead("sale.order", {
        domain: ["|", ["name", "ilike", args.query], ["partner_id.name", "ilike", args.query]],
        fields: ["id", "name", "partner_id", "amount_total", "state", "date_order"],
        limit: args.limit ?? 10,
        order: "id desc",
      });
      return { content: [{ type: "text", text: JSON.stringify({ count: (records as any[]).length, records }) }] };
    },
  );

  server.tool(
    "odoo_get_sale_order",
    "Get detailed information about a sale order including line items.",
    { order_id: z.number() },
    async (args) => {
      const records = await odoo.read("sale.order", [args.order_id], [
        "id", "name", "partner_id", "amount_total", "amount_untaxed", "amount_tax",
        "state", "date_order", "validity_date", "order_line", "note",
      ]);
      return { content: [{ type: "text", text: JSON.stringify(records) }] };
    },
  );

  // ─── FINANCE ────────────────────────────────────────────────────────

  server.tool(
    "odoo_list_overdue_invoices",
    "List customer invoices that are overdue.",
    { partner_name: z.string().optional(), limit: z.number().min(1).max(50).optional() },
    async (args) => {
      const domain: unknown[] = [
        ["move_type", "=", "out_invoice"],
        ["payment_state", "!=", "paid"],
        ["invoice_date_due", "<", new Date().toISOString().slice(0, 10)],
      ];
      if (args.partner_name) domain.push(["partner_id.name", "ilike", args.partner_name]);

      const records = await odoo.searchRead("account.move", {
        domain,
        fields: ["id", "name", "partner_id", "amount_total", "amount_residual", "invoice_date_due", "payment_state"],
        limit: args.limit ?? 25,
        order: "invoice_date_due asc",
      });
      return { content: [{ type: "text", text: JSON.stringify({ count: (records as any[]).length, records }) }] };
    },
  );

  server.tool(
    "odoo_get_invoice",
    "Get detailed information about an invoice by ID.",
    { invoice_id: z.number() },
    async (args) => {
      const records = await odoo.read("account.move", [args.invoice_id], [
        "id", "name", "partner_id", "amount_total", "amount_residual", "amount_untaxed",
        "invoice_date", "invoice_date_due", "payment_state", "state", "ref",
      ]);
      return { content: [{ type: "text", text: JSON.stringify(records) }] };
    },
  );

  // ─── PROJECTS ───────────────────────────────────────────────────────

  server.tool(
    "odoo_search_projects",
    "Search projects by name or customer.",
    { query: z.string().optional(), limit: z.number().min(1).max(25).optional() },
    async (args) => {
      const domain: unknown[] = args.query ? ["|", ["name", "ilike", args.query], ["partner_id.name", "ilike", args.query]] : [];

      const records = await odoo.searchRead("project.project", {
        domain,
        fields: ["id", "name", "partner_id", "task_count", "date_start", "date"],
        limit: args.limit ?? 25,
        order: "name asc",
      });
      return { content: [{ type: "text", text: JSON.stringify({ count: (records as any[]).length, records }) }] };
    },
  );

  server.tool(
    "odoo_list_project_tasks",
    "List tasks for a project, optionally filtered by stage or assignee.",
    { project_id: z.number().optional(), stage: z.string().optional(), assignee: z.string().optional(), limit: z.number().min(1).max(50).optional() },
    async (args) => {
      const domain: unknown[] = [];
      if (args.project_id) domain.push(["project_id", "=", args.project_id]);
      if (args.stage) domain.push(["stage_id.name", "ilike", args.stage]);
      if (args.assignee) domain.push(["user_ids.name", "ilike", args.assignee]);

      const records = await odoo.searchRead("project.task", {
        domain,
        fields: ["id", "name", "project_id", "user_ids", "stage_id", "date_deadline", "priority", "kanban_state"],
        limit: args.limit ?? 25,
        order: "priority desc, date_deadline asc",
      });
      return { content: [{ type: "text", text: JSON.stringify({ count: (records as any[]).length, records }) }] };
    },
  );

  // ─── INVENTORY ──────────────────────────────────────────────────────

  server.tool(
    "odoo_get_product_availability",
    "Check product stock availability by name or SKU.",
    { query: z.string(), limit: z.number().min(1).max(25).optional() },
    async (args) => {
      const records = await odoo.searchRead("product.product", {
        domain: ["|", ["name", "ilike", args.query], ["default_code", "ilike", args.query]],
        fields: ["id", "name", "default_code", "qty_available", "virtual_available", "uom_id"],
        limit: args.limit ?? 10,
      });
      return { content: [{ type: "text", text: JSON.stringify({ count: (records as any[]).length, records }) }] };
    },
  );

  // ─── COLLABORATION (writes) ─────────────────────────────────────────

  server.tool(
    "odoo_create_activity",
    "Create a follow-up activity on any Odoo record.",
    {
      model: z.string().describe("Odoo model name, e.g. crm.lead, sale.order, project.task"),
      record_id: z.number(),
      summary: z.string(),
      note: z.string().optional(),
      date_deadline: z.string().optional().describe("YYYY-MM-DD format"),
    },
    async (args) => {
      const vals: Record<string, unknown> = {
        res_model: args.model,
        res_id: args.record_id,
        summary: args.summary,
        note: args.note ?? "",
        date_deadline: args.date_deadline ?? new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10),
        activity_type_id: 4, // To-Do (default)
      };
      const result = await odoo.call("mail.activity", "create", vals);
      return { content: [{ type: "text", text: `Activity created: ${args.summary}` }] };
    },
  );

  server.tool(
    "odoo_post_note",
    "Post a note to an Odoo record's chatter.",
    {
      model: z.string().describe("Odoo model name, e.g. res.partner, sale.order"),
      record_id: z.number(),
      body: z.string(),
    },
    async (args) => {
      const result = await odoo.call(args.model, "message_post", {
        ids: [args.record_id],
        body: args.body,
        message_type: "comment",
        subtype_xmlid: "mail.mt_note",
      });
      return { content: [{ type: "text", text: `Note posted to ${args.model} #${args.record_id}.` }] };
    },
  );

  // ─── CMS ────────────────────────────────────────────────────────────

  server.tool(
    "odoo_cms_list_pages",
    "List website pages from Odoo CMS.",
    { query: z.string().optional(), limit: z.number().min(1).max(50).optional() },
    async (args) => {
      const records = await cms.listPages(args.query, undefined, args.limit ?? 25);
      return { content: [{ type: "text", text: JSON.stringify({ count: (records as any[]).length, records }) }] };
    },
  );

  server.tool(
    "odoo_cms_get_page_seo",
    "Get SEO metadata for a CMS page.",
    { page_id: z.number() },
    async (args) => {
      const records = await cms.getPageSeo(args.page_id);
      return { content: [{ type: "text", text: JSON.stringify(records) }] };
    },
  );

  server.tool(
    "odoo_cms_update_page_content",
    "Update the editable content of an Odoo CMS page draft.",
    { page_id: z.number(), html: z.string() },
    async (args) => {
      await cms.updatePageContent(args.page_id, args.html);
      return { content: [{ type: "text", text: `Updated page ${args.page_id}.` }] };
    },
  );

  server.tool(
    "odoo_cms_publish_page",
    "Publish an Odoo CMS page.",
    { page_id: z.number() },
    async (args) => {
      await cms.publishPage(args.page_id);
      return { content: [{ type: "text", text: `Published page ${args.page_id}.` }] };
    },
  );

  server.tool(
    "odoo_cms_unpublish_page",
    "Unpublish an Odoo CMS page.",
    { page_id: z.number() },
    async (args) => {
      await cms.unpublishPage(args.page_id);
      return { content: [{ type: "text", text: `Unpublished page ${args.page_id}.` }] };
    },
  );

  // ─── ADMIN / HEALTH ─────────────────────────────────────────────────

  server.tool(
    "odoo_health_check",
    "Check Odoo connector and ERP reachability.",
    {},
    async () => {
      const health = await odoo.ping();
      return {
        content: [{
          type: "text",
          text: health.ok
            ? `Odoo reachable${health.version ? ` (v${health.version})` : ""}.`
            : "Odoo unreachable.",
        }],
      };
    },
  );
}
