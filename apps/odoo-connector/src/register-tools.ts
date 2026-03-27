import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import {
  PolicyFile,
  buildAnnotations,
  buildSecuritySchemes,
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
    isError: true,
    content: [{ type: "text", text: `Authentication required: ${errorDescription}` }],
    _meta: {
      "mcp/www_authenticate": [
        `Bearer resource_metadata="${resourceMetadataUrl}", error="${error}", error_description="${errorDescription}"`,
      ],
    },
  };
}

export function registerOdooTools(server: McpServer, deps: ToolDeps) {
  const cms = new CmsGateway(deps.odoo);

  registerSearchSaleOrders(server, deps);
  registerListOverdueInvoices(server, deps);
  registerCmsListPages(server, deps, cms);
  registerCmsUpdatePageContent(server, deps, cms);
  registerCmsPublishPage(server, deps, cms);
  registerHealthCheck(server, deps);
}

function registerSearchSaleOrders(server: McpServer, deps: ToolDeps) {
  const toolName = "odoo_search_sale_orders";
  const tool = getToolOrThrow(deps.policy, toolName);

  server.registerTool(
    toolName,
    {
      title: tool.title,
      description: tool.description,
      inputSchema: tool.input_schema,
      annotations: buildAnnotations(tool),
      _meta: {
        securitySchemes: buildSecuritySchemes(tool.scope, tool.read_only),
        "openai/toolInvocation/invoking": "Searching sale orders\u2026",
        "openai/toolInvocation/invoked": "Sale orders ready",
      },
    },
    async (args: any, ctx: unknown) => {
      const authz = await deps.authorize(ctx, tool.scope);
      if (!authz.ok) {
        return authError(
          deps.policy.oauth.resource_metadata_url,
          authz.error,
          authz.errorDescription,
        );
      }

      const records = await deps.odoo.searchRead<Array<Record<string, unknown>>>(
        "sale.order",
        {
          domain: [
            "|",
            ["name", "ilike", args.query],
            ["partner_id.name", "ilike", args.query],
          ],
          fields: ["id", "name", "partner_id", "amount_total", "state"],
          limit: args.limit ?? 10,
          order: "id desc",
        },
      );

      return {
        structuredContent: { count: records.length, records },
        content: [{ type: "text", text: `Found ${records.length} sale order(s).` }],
        _meta: { source: "odoo", wrapper: tool.wrapper },
      };
    },
  );
}

function registerListOverdueInvoices(server: McpServer, deps: ToolDeps) {
  const toolName = "odoo_list_overdue_invoices";
  const tool = getToolOrThrow(deps.policy, toolName);

  server.registerTool(
    toolName,
    {
      title: tool.title,
      description: tool.description,
      inputSchema: tool.input_schema,
      annotations: buildAnnotations(tool),
      _meta: {
        securitySchemes: buildSecuritySchemes(tool.scope, tool.read_only),
        "openai/toolInvocation/invoking": "Loading overdue invoices\u2026",
        "openai/toolInvocation/invoked": "Invoices ready",
      },
    },
    async (args: any, ctx: unknown) => {
      const authz = await deps.authorize(ctx, tool.scope);
      if (!authz.ok) {
        return authError(deps.policy.oauth.resource_metadata_url, authz.error, authz.errorDescription);
      }

      const domain: unknown[] = [
        ["move_type", "=", "out_invoice"],
        ["payment_state", "!=", "paid"],
        ["invoice_date_due", "<", new Date().toISOString().slice(0, 10)],
      ];

      if (args.partner_name) {
        domain.push(["partner_id.name", "ilike", args.partner_name]);
      }

      const records = await deps.odoo.searchRead<Array<Record<string, unknown>>>(
        "account.move",
        {
          domain,
          fields: ["id", "name", "partner_id", "amount_residual", "invoice_date_due", "payment_state"],
          limit: args.limit ?? 25,
          order: "invoice_date_due asc",
        },
      );

      return {
        structuredContent: { count: records.length, records },
        content: [{ type: "text", text: `Found ${records.length} overdue invoice(s).` }],
      };
    },
  );
}

function registerCmsListPages(server: McpServer, deps: ToolDeps, cms: CmsGateway) {
  const toolName = "odoo_cms_list_pages";
  const tool = getToolOrThrow(deps.policy, toolName);

  server.registerTool(
    toolName,
    {
      title: tool.title,
      description: tool.description,
      inputSchema: tool.input_schema,
      annotations: buildAnnotations(tool),
      _meta: {
        securitySchemes: buildSecuritySchemes(tool.scope, tool.read_only),
        "openai/toolInvocation/invoking": "Loading CMS pages\u2026",
        "openai/toolInvocation/invoked": "CMS pages ready",
      },
    },
    async (args: any, ctx: unknown) => {
      const authz = await deps.authorize(ctx, tool.scope);
      if (!authz.ok) {
        return authError(deps.policy.oauth.resource_metadata_url, authz.error, authz.errorDescription);
      }

      const records = await cms.listPages(args.query, args.website_id, args.limit ?? 25);

      return {
        structuredContent: { count: records.length, records },
        content: [{ type: "text", text: `Found ${records.length} CMS page(s).` }],
        _meta: { wrapper: tool.wrapper, mappingStatus: "candidate-model-needs-doc-validation" },
      };
    },
  );
}

function registerCmsUpdatePageContent(server: McpServer, deps: ToolDeps, cms: CmsGateway) {
  const toolName = "odoo_cms_update_page_content";
  const tool = getToolOrThrow(deps.policy, toolName);

  server.registerTool(
    toolName,
    {
      title: tool.title,
      description: tool.description,
      inputSchema: tool.input_schema,
      annotations: buildAnnotations(tool),
      _meta: {
        securitySchemes: buildSecuritySchemes(tool.scope, tool.read_only),
        "openai/toolInvocation/invoking": "Updating CMS page\u2026",
        "openai/toolInvocation/invoked": "CMS page updated",
      },
    },
    async (args: any, ctx: unknown) => {
      const authz = await deps.authorize(ctx, tool.scope);
      if (!authz.ok) {
        return authError(deps.policy.oauth.resource_metadata_url, authz.error, authz.errorDescription);
      }

      const result = await cms.updatePageContent(args.page_id, args.html);

      return {
        structuredContent: { ok: true, result },
        content: [{ type: "text", text: `Updated page ${args.page_id}.` }],
      };
    },
  );
}

function registerCmsPublishPage(server: McpServer, deps: ToolDeps, cms: CmsGateway) {
  const toolName = "odoo_cms_publish_page";
  const tool = getToolOrThrow(deps.policy, toolName);

  server.registerTool(
    toolName,
    {
      title: tool.title,
      description: tool.description,
      inputSchema: tool.input_schema,
      annotations: buildAnnotations(tool),
      _meta: {
        securitySchemes: buildSecuritySchemes(tool.scope, tool.read_only),
        "openai/toolInvocation/invoking": "Publishing page\u2026",
        "openai/toolInvocation/invoked": "Page published",
      },
    },
    async (args: any, ctx: unknown) => {
      const authz = await deps.authorize(ctx, tool.scope);
      if (!authz.ok) {
        return authError(deps.policy.oauth.resource_metadata_url, authz.error, authz.errorDescription);
      }

      const result = await cms.publishPage(args.page_id);

      return {
        structuredContent: { ok: true, result },
        content: [{ type: "text", text: `Published page ${args.page_id}.` }],
      };
    },
  );
}

function registerHealthCheck(server: McpServer, deps: ToolDeps) {
  const toolName = "odoo_health_check";
  const tool = getToolOrThrow(deps.policy, toolName);

  server.registerTool(
    toolName,
    {
      title: tool.title,
      description: tool.description,
      inputSchema: tool.input_schema,
      annotations: buildAnnotations(tool),
      _meta: {
        securitySchemes: buildSecuritySchemes(tool.scope, tool.read_only),
        "openai/toolInvocation/invoking": "Checking Odoo health\u2026",
        "openai/toolInvocation/invoked": "Health check complete",
      },
    },
    async (_args: any, ctx: unknown) => {
      const authz = await deps.authorize(ctx, tool.scope);
      if (!authz.ok) {
        return authError(deps.policy.oauth.resource_metadata_url, authz.error, authz.errorDescription);
      }

      const health = await deps.odoo.ping();

      return {
        structuredContent: health,
        content: [{
          type: "text",
          text: health.ok
            ? `Odoo reachable${health.version ? ` on version ${health.version}` : ""}.`
            : "Odoo unreachable.",
        }],
      };
    },
  );
}
