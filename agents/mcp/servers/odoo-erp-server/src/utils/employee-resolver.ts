/**
 * Employee Code Resolver
 *
 * Maps employee codes (RIM, CKVC, etc.) to Odoo user IDs with caching.
 * Critical for multi-employee context switching in BIR workflows.
 */

import type { OdooClient } from '../odoo-client.js';
import type { EmployeeMapping } from '../types/odoo.js';
import { EMPLOYEE_DIRECTORY } from '../types/odoo.js';

export class EmployeeResolver {
  private cache = new Map<string, EmployeeMapping>();
  private cacheTTL = 5 * 60 * 1000; // 5 minutes
  private cacheTimestamps = new Map<string, number>();

  constructor(private odoo: OdooClient) {}

  /**
   * Resolve employee code to full mapping
   */
  async resolve(employeeCode: string): Promise<EmployeeMapping> {
    // Normalize code
    const code = employeeCode.toUpperCase().trim();

    // Check cache first
    const cached = this.getFromCache(code);
    if (cached) return cached;

    // Validate code exists in directory
    const directoryEntry = EMPLOYEE_DIRECTORY[code];
    if (!directoryEntry) {
      throw new Error(
        `Invalid employee code: ${code}\n` +
        `Valid codes: ${Object.keys(EMPLOYEE_DIRECTORY).join(', ')}`
      );
    }

    // Query Odoo for user_id and agency assignments
    try {
      const employees = await this.odoo.search_read<any>('ipai.employee_code', {
        domain: [['code', '=', code]],
        fields: ['code', 'user_id', 'agency_ids', 'active'],
        limit: 1
      });

      if (!employees.length) {
        throw new Error(
          `Employee code ${code} not found in Odoo.\n` +
          `Add to ipai.employee_code model:\n` +
          `  Code: ${code}\n` +
          `  User: ${directoryEntry.user_name}\n` +
          `  Email: ${directoryEntry.email}`
        );
      }

      const employee = employees[0];

      if (!employee.active) {
        throw new Error(`Employee code ${code} is inactive`);
      }

      const mapping: EmployeeMapping = {
        code: employee.code,
        user_id: employee.user_id[0],
        user_name: employee.user_id[1] || directoryEntry.user_name,
        email: directoryEntry.email,
        role: directoryEntry.role,
        agency_ids: employee.agency_ids || []
      };

      // Update cache
      this.cache.set(code, mapping);
      this.cacheTimestamps.set(code, Date.now());

      return mapping;
    } catch (error) {
      // If Odoo query fails, return minimal mapping from directory
      console.warn(`Failed to query Odoo for employee ${code}:`, error);

      // Return partial mapping (will fail on operations requiring user_id)
      const partialMapping: EmployeeMapping = {
        ...directoryEntry,
        user_id: 0, // Invalid - will need manual resolution
        agency_ids: []
      };

      return partialMapping;
    }
  }

  /**
   * Resolve multiple employee codes in parallel
   */
  async resolveMany(employeeCodes: string[]): Promise<EmployeeMapping[]> {
    return Promise.all(employeeCodes.map(code => this.resolve(code)));
  }

  /**
   * Get all valid employee codes
   */
  getValidCodes(): string[] {
    return Object.keys(EMPLOYEE_DIRECTORY);
  }

  /**
   * Validate employee code without querying Odoo
   */
  isValidCode(employeeCode: string): boolean {
    const code = employeeCode.toUpperCase().trim();
    return code in EMPLOYEE_DIRECTORY;
  }

  /**
   * Clear cache (for testing or forced refresh)
   */
  clearCache(employeeCode?: string): void {
    if (employeeCode) {
      const code = employeeCode.toUpperCase().trim();
      this.cache.delete(code);
      this.cacheTimestamps.delete(code);
    } else {
      this.cache.clear();
      this.cacheTimestamps.clear();
    }
  }

  /**
   * Get employee info from cache
   */
  private getFromCache(employeeCode: string): EmployeeMapping | null {
    const timestamp = this.cacheTimestamps.get(employeeCode);
    if (!timestamp || Date.now() - timestamp > this.cacheTTL) {
      this.cache.delete(employeeCode);
      this.cacheTimestamps.delete(employeeCode);
      return null;
    }
    return this.cache.get(employeeCode) || null;
  }

  /**
   * Get employee directory for display
   */
  getDirectory(): Array<{
    code: string;
    name: string;
    email: string;
    role: string;
  }> {
    return Object.values(EMPLOYEE_DIRECTORY).map(emp => ({
      code: emp.code,
      name: emp.user_name,
      email: emp.email,
      role: emp.role
    }));
  }
}
