import { OdooClient } from "./odoo-client.js";

/**
 * CMS Gateway — isolates DB-specific Odoo CMS model/method mapping.
 *
 * All CMS write methods are CANDIDATE mappings until validated against
 * the target Odoo database /doc page. Do not treat these as production-
 * verified until that validation is complete.
 */
export class CmsGateway {
  constructor(private readonly odoo: OdooClient) {}

  async listPages(query?: string, websiteId?: number, limit = 25) {
    return this.odoo.searchRead<Array<Record<string, unknown>>>("website.page", {
      domain: query ? [["name", "ilike", query]] : [],
      fields: ["id", "name", "url", "is_published"],
      limit,
      context: websiteId ? { website_id: websiteId } : {},
    });
  }

  async getPage(pageId: number) {
    return this.odoo.read<Array<Record<string, unknown>>>(
      "website.page",
      [pageId],
      ["id", "name", "url", "is_published", "arch_db"],
    );
  }

  async getPageSeo(pageId: number) {
    return this.odoo.read<Array<Record<string, unknown>>>(
      "website.page",
      [pageId],
      ["website_meta_title", "website_meta_description", "website_meta_keywords", "seo_name"],
    );
  }

  async updatePageContent(pageId: number, html: string) {
    // TODO: validate against target DB /doc — arch_db is a candidate field
    return this.odoo.call("website.page", "write", {
      ids: [pageId],
      vals: { arch_db: html },
    });
  }

  async publishPage(pageId: number) {
    // TODO: validate against target DB /doc — is_published is a candidate field
    return this.odoo.call("website.page", "write", {
      ids: [pageId],
      vals: { is_published: true },
    });
  }

  async unpublishPage(pageId: number) {
    return this.odoo.call("website.page", "write", {
      ids: [pageId],
      vals: { is_published: false },
    });
  }
}
