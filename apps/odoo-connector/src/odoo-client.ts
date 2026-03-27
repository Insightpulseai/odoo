export interface OdooClientConfig {
  baseUrl: string;
  apiKey: string;
  database?: string;
  userAgent?: string;
}

export interface SearchReadParams {
  domain?: unknown[];
  fields?: string[];
  limit?: number;
  order?: string;
  context?: Record<string, unknown>;
}

export class OdooClient {
  constructor(private readonly config: OdooClientConfig) {}

  async call<TResponse>(
    model: string,
    method: string,
    body: Record<string, unknown>,
  ): Promise<TResponse> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "Authorization": `bearer ${this.config.apiKey}`,
      "User-Agent": this.config.userAgent ?? "odoo-connector/1.0",
    };

    if (this.config.database) {
      headers["X-Odoo-Database"] = this.config.database;
    }

    const url = `${this.config.baseUrl.replace(/\/$/, "")}/json/2/${model}/${method}`;
    const res = await fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Odoo JSON-2 error ${res.status}: ${text}`);
    }

    return (await res.json()) as TResponse;
  }

  async searchRead<TResponse>(
    model: string,
    params: SearchReadParams,
  ): Promise<TResponse> {
    return this.call<TResponse>(model, "search_read", params);
  }

  async read<TResponse>(
    model: string,
    ids: number[],
    fields: string[],
    context?: Record<string, unknown>,
  ): Promise<TResponse> {
    return this.call<TResponse>(model, "read", {
      ids,
      fields,
      context: context ?? {},
    });
  }

  async ping(): Promise<{ version?: string; ok: boolean }> {
    const url = `${this.config.baseUrl.replace(/\/$/, "")}/web/version`;
    const res = await fetch(url, {
      method: "GET",
      headers: {
        "Authorization": `bearer ${this.config.apiKey}`,
        "User-Agent": this.config.userAgent ?? "odoo-connector/1.0",
      },
    });

    if (!res.ok) {
      return { ok: false };
    }

    const body = (await res.json()) as { version?: string };
    return { ok: true, version: body.version };
  }
}
