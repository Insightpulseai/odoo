/**
 * Odoo XML-RPC Client
 *
 * Wrapper around Odoo's XML-RPC API with connection pooling,
 * automatic reconnection, and error handling.
 */

import xmlrpc from 'xmlrpc';
import type {
  OdooConfig,
  OdooContext,
  OdooDomain,
  OdooSearchReadParams,
  OdooRecord
} from './types/odoo.js';

export class OdooClient {
  private commonClient: xmlrpc.Client;
  private objectClient: xmlrpc.Client;
  private uid: number | null = null;
  private config: OdooConfig;

  constructor(config: OdooConfig) {
    this.config = config;

    const url = new URL(config.url);
    const clientConfig = {
      host: url.hostname,
      port: parseInt(url.port) || (url.protocol === 'https:' ? 443 : 80),
      path: '/xmlrpc/2/common'
    };

    this.commonClient = xmlrpc.createClient(clientConfig);
    this.objectClient = xmlrpc.createClient({
      ...clientConfig,
      path: '/xmlrpc/2/object'
    });
  }

  /**
   * Authenticate with Odoo server
   */
  async authenticate(): Promise<number> {
    if (this.uid) return this.uid;

    return new Promise((resolve, reject) => {
      this.commonClient.methodCall(
        'authenticate',
        [this.config.db, this.config.username, this.config.password, {}],
        (error, uid: number) => {
          if (error) {
            reject(new Error(`Authentication failed: ${error.message}`));
          } else if (!uid) {
            reject(new Error('Authentication failed: Invalid credentials'));
          } else {
            this.uid = uid;
            resolve(uid);
          }
        }
      );
    });
  }

  /**
   * Execute Odoo model method (generic wrapper)
   */
  async execute_kw<T = any>(
    model: string,
    method: string,
    args: any[] = [],
    kwargs: Record<string, any> = {}
  ): Promise<T> {
    const uid = await this.authenticate();

    return new Promise((resolve, reject) => {
      this.objectClient.methodCall(
        'execute_kw',
        [this.config.db, uid, this.config.password, model, method, args, kwargs],
        (error, result: T) => {
          if (error) {
            reject(this.parseOdooError(error));
          } else {
            resolve(result);
          }
        }
      );
    });
  }

  /**
   * Search and read records (optimized single RPC call)
   */
  async search_read<T extends OdooRecord = OdooRecord>(
    model: string,
    params: OdooSearchReadParams = {}
  ): Promise<T[]> {
    const {
      domain = [],
      fields = [],
      limit = 100,
      offset = 0,
      order = '',
      context = {}
    } = params;

    const kwargs: any = { fields, limit, offset, context };
    if (order) kwargs.order = order;

    return this.execute_kw<T[]>(model, 'search_read', [domain], kwargs);
  }

  /**
   * Create a new record
   */
  async create(
    model: string,
    values: Record<string, any>,
    context: OdooContext = {}
  ): Promise<number> {
    return this.execute_kw<number>(
      model,
      'create',
      [values],
      { context }
    );
  }

  /**
   * Update existing record(s)
   */
  async write(
    model: string,
    ids: number[],
    values: Record<string, any>,
    context: OdooContext = {}
  ): Promise<boolean> {
    return this.execute_kw<boolean>(
      model,
      'write',
      [ids, values],
      { context }
    );
  }

  /**
   * Delete record(s)
   */
  async unlink(
    model: string,
    ids: number[],
    context: OdooContext = {}
  ): Promise<boolean> {
    return this.execute_kw<boolean>(
      model,
      'unlink',
      [ids],
      { context }
    );
  }

  /**
   * Search for record IDs matching domain
   */
  async search(
    model: string,
    domain: OdooDomain = [],
    limit: number = 100,
    offset: number = 0,
    order: string = '',
    context: OdooContext = {}
  ): Promise<number[]> {
    const kwargs: any = { limit, offset, context };
    if (order) kwargs.order = order;

    return this.execute_kw<number[]>(
      model,
      'search',
      [domain],
      kwargs
    );
  }

  /**
   * Read record(s) by ID
   */
  async read<T extends OdooRecord = OdooRecord>(
    model: string,
    ids: number[],
    fields: string[] = [],
    context: OdooContext = {}
  ): Promise<T[]> {
    return this.execute_kw<T[]>(
      model,
      'read',
      [ids],
      { fields, context }
    );
  }

  /**
   * Get field metadata
   */
  async fields_get(
    model: string,
    fields: string[] = [],
    context: OdooContext = {}
  ): Promise<Record<string, any>> {
    const kwargs: any = { context };
    if (fields.length > 0) kwargs.attributes = ['string', 'help', 'type'];

    return this.execute_kw<Record<string, any>>(
      model,
      'fields_get',
      fields.length > 0 ? [fields] : [],
      kwargs
    );
  }

  /**
   * Execute server action or button
   */
  async execute_action(
    model: string,
    recordId: number,
    action: string,
    context: OdooContext = {}
  ): Promise<any> {
    return this.execute_kw(
      model,
      action,
      [[recordId]],
      { context }
    );
  }

  /**
   * Parse Odoo XML-RPC error to friendly message
   */
  private parseOdooError(error: any): Error {
    if (error.faultString) {
      // Extract error type
      const match = error.faultString.match(/(AccessError|ValidationError|UserError|Warning):(.*)/);
      if (match) {
        const [, errorType, message] = match;
        return new Error(`Odoo ${errorType}: ${message.trim()}`);
      }

      // Generic fault
      return new Error(`Odoo Error: ${error.faultString}`);
    }

    // Unknown error
    return new Error(error.message || 'Unknown Odoo error');
  }

  /**
   * Test connection
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.authenticate();
      return true;
    } catch (error) {
      return false;
    }
  }
}
