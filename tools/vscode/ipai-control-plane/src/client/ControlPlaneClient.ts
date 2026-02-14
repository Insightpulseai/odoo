import axios, { AxiosInstance } from 'axios';

export interface Project {
  id: string;
  repo_root: string;
  environments: Environment[];
  spec_bundles: string[];
}

export interface Environment {
  name: string;
  db_name: string;
  odoo_version: string;
  modules_installed: string[];
  schema_hash: string;
  last_deploy: string;
  health: 'healthy' | 'degraded' | 'failed' | 'unknown';
  pending_migrations: Migration[];
}

export interface Migration {
  id: string;
  description: string;
  version: string;
}

export interface ValidationResult {
  validator: string;
  status: 'pass' | 'warn' | 'fail';
  issues: ValidationIssue[];
  fixes?: QuickFix[];
}

export interface ValidationIssue {
  file: string;
  line?: number;
  column?: number;
  severity: 'error' | 'warning' | 'info';
  message: string;
  rule: string;
}

export interface QuickFix {
  label: string;
  diff: string;
}

export interface EvidenceBundle {
  timestamp: string;
  operation: string;
  target_env: string;
  path: string;
  status: 'pending' | 'success' | 'failed';
}

export interface OperationPlan {
  op_id: string;
  status: string;
  diffs: OperationDiff[];
  checks: ValidationCheck[];
}

export interface OperationDiff {
  type: string;
  path: string;
  summary: string;
  patch: string;
  safe: boolean;
}

export interface ValidationCheck {
  id: string;
  status: 'pass' | 'warn' | 'fail';
  severity: 'error' | 'warning' | 'info';
  message: string;
  file?: string;
  line?: number;
}

export interface OperationExecution {
  op_id: string;
  bundle_id: string;
  status: string;
}

export interface OperationStatus {
  op_id: string;
  status: string;
  bundle_id?: string;
  created_at: string;
  updated_at?: string;
  type: string;
}

export class ControlPlaneClient {
  private http: AxiosInstance;

  constructor(baseURL: string) {
    this.http = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.http.get('/health');
      return response.status === 200;
    } catch {
      return false;
    }
  }

  async getProjects(): Promise<Project[]> {
    const response = await this.http.get('/api/projects');
    return response.data;
  }

  async getEnvironments(projectId: string): Promise<Environment[]> {
    const response = await this.http.get(`/api/projects/${projectId}/environments`);
    return response.data;
  }

  async getEnvironmentStatus(projectId: string, envName: string): Promise<Environment> {
    const response = await this.http.get(`/api/projects/${projectId}/environments/${envName}/status`);
    return response.data;
  }

  async validateManifest(filePath: string): Promise<ValidationResult> {
    const response = await this.http.post('/api/validate/manifest', { file_path: filePath });
    return response.data;
  }

  async validateXml(filePath: string): Promise<ValidationResult> {
    const response = await this.http.post('/api/validate/xml', { file_path: filePath });
    return response.data;
  }

  async validateSecurity(modulePath: string): Promise<ValidationResult> {
    const response = await this.http.post('/api/validate/security', { module_path: modulePath });
    return response.data;
  }

  async validateAll(projectId: string): Promise<ValidationResult[]> {
    const response = await this.http.post('/api/validate/all', { project_id: projectId });
    return response.data;
  }

  async installModules(projectId: string, environment: string, modules: string[]): Promise<any> {
    const response = await this.http.post('/api/operations/install-modules', {
      project_id: projectId,
      environment,
      modules
    });
    return response.data;
  }

  async previewInstall(projectId: string, environment: string, modules: string[]): Promise<any> {
    const response = await this.http.post('/api/operations/install-modules/preview', {
      project_id: projectId,
      environment,
      modules
    });
    return response.data;
  }

  async getEvidenceBundles(projectId: string): Promise<EvidenceBundle[]> {
    const response = await this.http.get(`/api/evidence/${projectId}`);
    return response.data;
  }

  async getEvidenceBundle(bundleId: string): Promise<EvidenceBundle> {
    const response = await this.http.get(`/api/evidence/bundle/${bundleId}`);
    return response.data;
  }

  async aiGeneratePatch(context: any): Promise<any> {
    const response = await this.http.post('/api/ai/generate-patch', context);
    return response.data;
  }

  async aiExplainDrift(drift: any): Promise<any> {
    const response = await this.http.post('/api/ai/explain-drift', drift);
    return response.data;
  }

  // V1 API Methods (SaaS-grade operations)

  async planOperation(type: string, params: any): Promise<OperationPlan> {
    const response = await this.http.post('/v1/ops/plan', {
      type,
      ...params
    });
    return response.data;
  }

  async executeOperation(opId: string): Promise<OperationExecution> {
    const response = await this.http.post('/v1/ops/execute', {
      op_id: opId
    });
    return response.data;
  }

  async getOperationStatus(opId: string): Promise<OperationStatus> {
    const response = await this.http.get(`/v1/ops/${opId}`);
    return response.data;
  }

  async getEvidenceBundleV1(bundleId: string): Promise<EvidenceBundle> {
    const response = await this.http.get(`/v1/evidence/${bundleId}`);
    return response.data;
  }
}
