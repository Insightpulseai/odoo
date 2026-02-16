/**
 * Odoo XML-RPC type definitions
 */

export interface OdooConfig {
  url: string;
  db: string;
  username: string;
  password: string;
}

export interface OdooContext {
  uid?: number;
  allowed_company_ids?: number[];
  employee_code?: string;
  tz?: string;
  lang?: string;
}

export type OdooDomain = Array<
  | string
  | [string, string, any]
  | '&'
  | '|'
  | '!'
>;

export interface OdooSearchReadParams {
  domain?: OdooDomain;
  fields?: string[];
  limit?: number;
  offset?: number;
  order?: string;
  context?: OdooContext;
}

export interface OdooRecord {
  id: number;
  [key: string]: any;
}

// Employee Code Mapping (TBWA Finance SSC Directory)
export interface EmployeeMapping {
  code: string;
  user_id: number;
  user_name: string;
  email: string;
  role: 'Director' | 'Manager' | 'Supervisor' | 'Staff';
  agency_ids: number[];
}

export const EMPLOYEE_DIRECTORY: Record<string, Omit<EmployeeMapping, 'user_id' | 'agency_ids'>> = {
  'CKVC': { code: 'CKVC', user_name: 'Khalil Veracruz', email: 'khalil.veracruz@omc.com', role: 'Director' },
  'RIM': { code: 'RIM', user_name: 'Rey Meran', email: 'rey.meran@omc.com', role: 'Manager' },
  'BOM': { code: 'BOM', user_name: 'Beng Manalo', email: 'beng.manalo@omc.com', role: 'Supervisor' },
  'LAS': { code: 'LAS', user_name: 'Amor Lasaga', email: 'amor.lasaga@omc.com', role: 'Staff' },
  'RMQB': { code: 'RMQB', user_name: 'Sally Brillantes', email: 'sally.brillantes@omc.com', role: 'Staff' },
  'JMSM': { code: 'JMSM', user_name: 'Joana Maravillas', email: 'joana.maravillas@omc.com', role: 'Staff' },
  'JAP': { code: 'JAP', user_name: 'Jinky Paladin', email: 'jinky.paladin@omc.com', role: 'Staff' },
  'JPAL': { code: 'JPAL', user_name: 'Jerald Loterte', email: 'jerald.loterte@omc.com', role: 'Staff' },
  'JLI': { code: 'JLI', user_name: 'Jasmin Ignacio', email: 'jasmin.ignacio@omc.com', role: 'Staff' },
  'JRMO': { code: 'JRMO', user_name: 'Jhoee Oliva', email: 'jhoee.oliva@omc.com', role: 'Staff' },
  'CSD': { code: 'CSD', user_name: 'Cliff Dejecacion', email: 'cliff.dejecacion@omc.com', role: 'Staff' }
};

// BIR Form Types
export type BIRFormType =
  | '1600' | '1601-C' | '1601-E' | '1601-F' | '1604-CF' | '1604-E'
  | '2550M' | '2550Q' | '2551M' | '2551Q'
  | '1700' | '1701' | '1702' | '1702-RT' | '1702-EX'
  | '1706' | '1707'
  | '1800' | '1801'
  | '2200-A' | '2200-P' | '2200-T' | '2200-M' | '2200-AN'
  | '2000' | '2000-OT'
  | '0619-E' | '0619-F';

export interface BIRTaxReturn {
  id: number;
  form_type: BIRFormType;
  employee_code: string;
  agency_id: number;
  period_start: string;
  period_end: string;
  filing_deadline: string;
  status: 'draft' | 'to_review' | 'to_approve' | 'filed' | 'late';
  total_tax_due: number;
}

export interface eBIRFormsJSON {
  header: {
    formType: string;
    tin: string;
    rdoCode: string;
    taxableMonth?: string;
    taxableQuarter?: string;
    taxableYear: string;
  };
  schedules: Record<string, any>;
  attachments?: Record<string, any>;
  certification?: {
    preparedBy: string;
    preparedByTIN: string;
    preparedDate: string;
    reviewedBy?: string;
    reviewedDate?: string;
    approvedBy?: string;
    approvedDate?: string;
  };
}
