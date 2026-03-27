import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import {
  PolicyFile,
  getToolOrThrow,
} from "./policy.js";
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

function authError(resourceMetadataUrl: string, error: string, errorDescription: string) {
  return {
    isError: true as const,
    content: [{ type: "text" as const, text: `Authentication required: ${errorDescription}` }],
  };
}

export function registerOdooTools(server: McpServer, deps: ToolDeps) {
  const cms = new CmsGateway(deps.odoo);

  // Sales: search orders
  const soTool = getToolOrThrow(deps.policy, "odoo_search_sale_orders");
  server.tool(
    "odoo_search_sale_orders",
    soTool.description,
    { query: z.string(), limit: z.number().min(1).max(25).optional() },
    async (args) => {
      const records = await deps.odoo.searchRead("sale.order", {
        domain: ["|", ["name", "ilike", args.query], ["partner_id.name", "ilike", args.query]],
        fields: ["id", "name", "partner_id", "amount_total", "state"],
        limit: args.limit ?? 10,
        order: "id desc",
      });
      return { content: [{ type: "text", text: JSON.stringify({ count: (records as any[]).length, records }) }] };
    },
  );

  // Finance: overdue invoices
  const invTool = getToolOrThrow(deps.policy, "odoo_list_overdue_invoices");
  server.tool(
    "odoo_list_overdue_invoices",
    invTool.description,
    { partner_name: z.string().optional(), limit: z.number().min(1).max(50).optional() },
    async (args) => {
      const domain: unknown[] = [
        ["move_type", "=", "out_invoice"],
        ["payment_state", "!=", "paid"],
        ["invoice_date_due", "<", new Date().toISOString().slice(0, 10)],
      ];
      if (args.partner_name) domain.push(["partner_id.name", "ilike", args.partner_name]);

      const records = await deps.odoo.searchRead("account.move", {
        domain,
        fields: ["id", "name", "partner_id", "amount_residual", "invoice_date_due"],
        limit: args.limit ?? 25,
        order: "invoice_date_due asc",
      });
      return { content: [{ type: "text", text: JSON.stringify({ count: (records as any[]).length, records }) }] };
    },
  );

  // CMS: list pages
  const cmsListTool = getToolOrThrow(deps.policy, "odoo_cms_list_pages");
  server.tool(
    "odoo_cms_list_pages",
    cmsListTool.description,
    { query: z.string().optional(), website_id: z.number().optional(), limit: z.number().min(1).max(50).optional() },
    async (args) => {
      const records = await cms.listPages(args.query, args.website_id, args.limit ?? 25);
      return { content: [{ type: "text", text: JSON.stringify({ count: (records as any[]).length, records }) }] };
    },
  );

  // CMS: update page content
  const cmsUpdateTool = getToolOrThrow(deps.policy, "odoo_cms_update_page_content");
  server.tool(
    "odoo_cms_update_page_content",
    cmsUpdateTool.description,
    { page_id: z.number(), html: z.string() },
    async (args) => {
      const result = await cms.updatePageContent(args.page_id, args.html);
      return { content: [{ type: "text", text: `Updated page ${args.page_id}.` }] };
    },
  );

  // CMS: publish page
  const cmsPubTool = getToolOrThrow(deps.policy, "odoo_cms_publish_page");
  server.tool(
    "odoo_cms_publish_page",
    cmsPubTool.description,
    { page_id: z.number() },
    async (args) => {
      const result = await cms.publishPage(args.page_id);
      return { content: [{ type: "text", text: `Published page ${args.page_id}.` }] };
    },
  );

  // Health check
  const healthTool = getToolOrThrow(deps.policy, "odoo_health_check");
  server.tool(
    "odoo_health_check",
    healthTool.description,
    {},
    async () => {
      const health = await deps.odoo.ping();
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
