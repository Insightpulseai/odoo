/**
 * Odoo XML-RPC / JSON-RPC Client
 * Decoupled frontend integration with Odoo CE 18 backend
 */

import axios, { AxiosInstance } from 'axios';

export interface OdooConfig {
  baseURL: string;
  database: string;
  username?: string;
  password?: string;
}

export interface OdooSession {
  uid: number;
  session_id: string;
  username: string;
  db: string;
  context: Record<string, any>;
}

export class OdooClient {
  private axios: AxiosInstance;
  private config: OdooConfig;
  private session: OdooSession | null = null;

  constructor(config: OdooConfig) {
    this.config = config;
    this.axios = axios.create({
      baseURL: config.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // Send cookies for session management
    });
  }

  /**
   * Authenticate with Odoo backend
   */
  async authenticate(username?: string, password?: string): Promise<OdooSession> {
    const user = username || this.config.username;
    const pass = password || this.config.password;

    if (!user || !pass) {
      throw new Error('Username and password required');
    }

    const response = await this.axios.post('/web/session/authenticate', {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        db: this.config.database,
        login: user,
        password: pass,
      },
    });

    if (response.data.error) {
      throw new Error(response.data.error.data.message);
    }

    this.session = response.data.result;
    return this.session;
  }

  /**
   * Get current session info
   */
  async getSessionInfo(): Promise<OdooSession | null> {
    const response = await this.axios.post('/web/session/get_session_info', {
      jsonrpc: '2.0',
      method: 'call',
      params: {},
    });

    if (response.data.result && response.data.result.uid) {
      this.session = response.data.result;
      return this.session;
    }

    return null;
  }

  /**
   * Logout from Odoo
   */
  async logout(): Promise<void> {
    await this.axios.post('/web/session/destroy', {
      jsonrpc: '2.0',
      method: 'call',
      params: {},
    });
    this.session = null;
  }

  /**
   * Call Odoo model method via JSON-RPC
   */
  async call(
    model: string,
    method: string,
    args: any[] = [],
    kwargs: Record<string, any> = {}
  ): Promise<any> {
    if (!this.session) {
      throw new Error('Not authenticated. Call authenticate() first.');
    }

    const response = await this.axios.post('/web/dataset/call_kw', {
      jsonrpc: '2.0',
      method: 'call',
      params: {
        model,
        method,
        args,
        kwargs,
      },
    });

    if (response.data.error) {
      throw new Error(response.data.error.data.message);
    }

    return response.data.result;
  }

  /**
   * Search records
   */
  async search(
    model: string,
    domain: any[] = [],
    options: { limit?: number; offset?: number; order?: string } = {}
  ): Promise<number[]> {
    return this.call(model, 'search', [domain], options);
  }

  /**
   * Read records
   */
  async read(
    model: string,
    ids: number[],
    fields: string[] = []
  ): Promise<any[]> {
    return this.call(model, 'read', [ids], { fields });
  }

  /**
   * Search and read records
   */
  async searchRead(
    model: string,
    domain: any[] = [],
    fields: string[] = [],
    options: { limit?: number; offset?: number; order?: string } = {}
  ): Promise<any[]> {
    return this.call(model, 'search_read', [domain], { fields, ...options });
  }

  /**
   * Create record
   */
  async create(model: string, values: Record<string, any>): Promise<number> {
    return this.call(model, 'create', [values]);
  }

  /**
   * Update record(s)
   */
  async write(
    model: string,
    ids: number[],
    values: Record<string, any>
  ): Promise<boolean> {
    return this.call(model, 'write', [ids, values]);
  }

  /**
   * Delete record(s)
   */
  async unlink(model: string, ids: number[]): Promise<boolean> {
    return this.call(model, 'unlink', [ids]);
  }

  /**
   * Get fields definition for a model
   */
  async fieldsGet(model: string): Promise<any> {
    return this.call(model, 'fields_get', []);
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.session !== null && this.session.uid !== undefined;
  }

  /**
   * Get current user ID
   */
  getUserId(): number | null {
    return this.session?.uid || null;
  }
}

// Singleton instance
let odooClient: OdooClient | null = null;

export function getOdooClient(): OdooClient {
  if (!odooClient) {
    odooClient = new OdooClient({
      baseURL: process.env.NEXT_PUBLIC_ODOO_URL || 'http://localhost:8069',
      database: process.env.NEXT_PUBLIC_ODOO_DB || 'odoo_dev',
    });
  }
  return odooClient;
}
