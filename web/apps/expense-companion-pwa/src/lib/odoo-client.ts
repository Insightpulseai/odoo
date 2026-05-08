import axios, { AxiosInstance } from 'axios';

export interface OdooSession {
  uid: number;
  session_id: string;
  username: string;
  db: string;
  context: Record<string, unknown>;
}

class OdooClient {
  private axios: AxiosInstance;

  constructor() {
    this.axios = axios.create({
      baseURL: '/api/odoo',
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true,
    });
  }

  async getSessionInfo(): Promise<OdooSession | null> {
    const response = await this.axios.post('/web/session/get_session_info', {
      jsonrpc: '2.0',
      method: 'call',
      params: {},
    });

    if (response.data?.result?.uid) {
      return response.data.result as OdooSession;
    }

    return null;
  }

  async searchRead(
    model: string,
    domain: unknown[],
    fields: string[],
    options: { limit?: number; offset?: number; order?: string } = {}
  ): Promise<Record<string, unknown>[]> {
    const response = await this.axios.post('/web/dataset/call_kw', {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        model,
        method: 'search_read',
        args: [domain],
        kwargs: { fields, ...options },
      },
    });

    if (response.data?.error) {
      throw new Error(String(response.data.error?.data?.message ?? 'Odoo search_read failed'));
    }

    return response.data?.result ?? [];
  }
}

let odooClient: OdooClient | null = null;

export function getOdooClient() {
  if (!odooClient) {
    odooClient = new OdooClient();
  }

  return odooClient;
}
