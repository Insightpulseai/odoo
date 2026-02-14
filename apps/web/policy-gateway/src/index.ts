/**
 * Dataverse Enterprise Console - Policy Gateway Server
 * Portfolio Initiative: PORT-2026-012
 * Controls: CTRL-POLICY-001, CTRL-CAPABILITY-001, CTRL-MODEL-001
 *
 * Express middleware server for policy enforcement
 * Replicates Cursor Enterprise control plane patterns
 */

import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import { createClient } from '@supabase/supabase-js';
import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';

import { enforcePolicies } from './enforcement.js';
import { getOrgModelPolicies, setModelPolicy, deleteModelPolicy, getModelUsageStats } from './models.js';
import { getBotCapabilities, attestCapability, revokeCapability, getCapabilityStatusSummary } from './capabilities.js';
import {
  getRecentPolicyDecisions,
  getPolicyMetrics,
  getBlockedRequests,
  exportPolicyDecisionsToCSV
} from './audit.js';
import { EnforcementRequest, PolicyContext } from './types.js';

dotenv.config();

// ============================================================================
// CONFIGURATION
// ============================================================================

const PORT = process.env.POLICY_GATEWAY_PORT || 3000;
const SUPABASE_URL = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
  console.error('ERROR: Missing Supabase configuration');
  console.error('Required: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY');
  process.exit(1);
}

// ============================================================================
// SUPABASE CLIENT
// ============================================================================

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
});

// ============================================================================
// EXPRESS APP
// ============================================================================

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Request logging
app.use((req: Request, res: Response, next: NextFunction) => {
  const requestId = req.headers['x-request-id'] || uuidv4();
  req.headers['x-request-id'] = requestId as string;
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path} | Request ID: ${requestId}`);
  next();
});

// ============================================================================
// ROUTES
// ============================================================================

// Health check
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    service: 'policy-gateway',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// ============================================================================
// POLICY ENFORCEMENT ENDPOINT
// ============================================================================

/**
 * POST /policy/enforce
 * Main policy enforcement endpoint
 * Called by MCP Coordinator before routing requests
 */
app.post('/policy/enforce', async (req: Request, res: Response) => {
  try {
    const requestData: EnforcementRequest = req.body;

    // Validate required fields
    if (!requestData.org_id || !requestData.bot_id) {
      return res.status(400).json({
        error: 'Missing required fields',
        required: ['org_id', 'bot_id']
      });
    }

    const context: PolicyContext = {
      org_id: requestData.org_id,
      bot_id: requestData.bot_id,
      request_id: requestData.request_id || (req.headers['x-request-id'] as string)
    };

    // Enforce policies
    const decision = await enforcePolicies(requestData, context, supabase);

    const statusCode = decision.allowed ? 200 : 403;
    res.status(statusCode).json(decision);
  } catch (error) {
    console.error('[PolicyGateway] Error enforcing policies:', error);
    res.status(500).json({
      error: 'Policy enforcement failed',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// ============================================================================
// MODEL GOVERNANCE ENDPOINTS
// ============================================================================

/**
 * GET /api/model-policy/:org_id
 * Get all model policies for organization
 */
app.get('/api/model-policy/:org_id', async (req: Request, res: Response) => {
  try {
    const { org_id } = req.params;
    const policies = await getOrgModelPolicies(org_id, supabase);
    res.json({ policies });
  } catch (error) {
    console.error('[ModelPolicy] Error:', error);
    res.status(500).json({ error: 'Failed to fetch model policies' });
  }
});

/**
 * POST /api/model-policy
 * Create or update model policy
 */
app.post('/api/model-policy', async (req: Request, res: Response) => {
  try {
    const { org_id, model_family, model_name, policy_type, reason } = req.body;

    if (!org_id || !model_family || !model_name || !policy_type) {
      return res.status(400).json({
        error: 'Missing required fields',
        required: ['org_id', 'model_family', 'model_name', 'policy_type']
      });
    }

    const result = await setModelPolicy(
      org_id,
      model_family,
      model_name,
      policy_type,
      reason || '',
      supabase
    );

    if (!result.success) {
      return res.status(500).json({ error: result.error });
    }

    res.json({ success: true });
  } catch (error) {
    console.error('[ModelPolicy] Error:', error);
    res.status(500).json({ error: 'Failed to set model policy' });
  }
});

/**
 * DELETE /api/model-policy/:org_id/:model_name
 * Delete model policy
 */
app.delete('/api/model-policy/:org_id/:model_name', async (req: Request, res: Response) => {
  try {
    const { org_id, model_name } = req.params;
    const result = await deleteModelPolicy(org_id, model_name, supabase);

    if (!result.success) {
      return res.status(500).json({ error: result.error });
    }

    res.json({ success: true });
  } catch (error) {
    console.error('[ModelPolicy] Error:', error);
    res.status(500).json({ error: 'Failed to delete model policy' });
  }
});

/**
 * GET /api/model-usage/:org_id
 * Get model usage statistics
 */
app.get('/api/model-usage/:org_id', async (req: Request, res: Response) => {
  try {
    const { org_id } = req.params;
    const hours = parseInt(req.query.hours as string) || 24;
    const stats = await getModelUsageStats(org_id, hours, supabase);
    res.json({ stats });
  } catch (error) {
    console.error('[ModelPolicy] Error:', error);
    res.status(500).json({ error: 'Failed to fetch model usage stats' });
  }
});

// ============================================================================
// CAPABILITY ENDPOINTS
// ============================================================================

/**
 * GET /api/capabilities/:bot_id
 * Get bot capability attestations
 */
app.get('/api/capabilities/:bot_id', async (req: Request, res: Response) => {
  try {
    const { bot_id } = req.params;
    const capabilities = await getBotCapabilities(bot_id, supabase);
    res.json({ capabilities });
  } catch (error) {
    console.error('[Capability] Error:', error);
    res.status(500).json({ error: 'Failed to fetch capabilities' });
  }
});

/**
 * POST /api/capabilities/attest
 * Attest bot capability
 */
app.post('/api/capabilities/attest', async (req: Request, res: Response) => {
  try {
    const {
      bot_id,
      capability_key,
      has_capability,
      attestation_method,
      attestation_evidence,
      validator_id,
      expiry_days
    } = req.body;

    if (!bot_id || !capability_key || has_capability === undefined || !attestation_method) {
      return res.status(400).json({
        error: 'Missing required fields',
        required: ['bot_id', 'capability_key', 'has_capability', 'attestation_method']
      });
    }

    const result = await attestCapability(
      bot_id,
      capability_key,
      has_capability,
      attestation_method,
      attestation_evidence || '',
      validator_id || 'system',
      expiry_days,
      supabase
    );

    if (!result.success) {
      return res.status(500).json({ error: result.error });
    }

    res.json({ success: true });
  } catch (error) {
    console.error('[Capability] Error:', error);
    res.status(500).json({ error: 'Failed to attest capability' });
  }
});

/**
 * GET /api/capabilities/:bot_id/summary
 * Get capability status summary
 */
app.get('/api/capabilities/:bot_id/summary', async (req: Request, res: Response) => {
  try {
    const { bot_id } = req.params;
    const summary = await getCapabilityStatusSummary(bot_id, supabase);
    res.json(summary);
  } catch (error) {
    console.error('[Capability] Error:', error);
    res.status(500).json({ error: 'Failed to fetch capability summary' });
  }
});

// ============================================================================
// AUDIT ENDPOINTS
// ============================================================================

/**
 * GET /api/audit/decisions
 * Get recent policy decisions
 */
app.get('/api/audit/decisions', async (req: Request, res: Response) => {
  try {
    const filters = {
      bot_id: req.query.bot_id as string,
      policy_type: req.query.policy_type as string,
      decision: req.query.decision as 'allow' | 'block' | 'warn',
      hours: req.query.hours ? parseInt(req.query.hours as string) : 24,
      limit: req.query.limit ? parseInt(req.query.limit as string) : 100
    };

    const decisions = await getRecentPolicyDecisions(filters, supabase);
    res.json({ decisions });
  } catch (error) {
    console.error('[Audit] Error:', error);
    res.status(500).json({ error: 'Failed to fetch policy decisions' });
  }
});

/**
 * GET /api/audit/metrics
 * Get policy decision metrics
 */
app.get('/api/audit/metrics', async (req: Request, res: Response) => {
  try {
    const hours = req.query.hours ? parseInt(req.query.hours as string) : 24;
    const metrics = await getPolicyMetrics(hours, supabase);
    res.json(metrics);
  } catch (error) {
    console.error('[Audit] Error:', error);
    res.status(500).json({ error: 'Failed to fetch metrics' });
  }
});

/**
 * GET /api/audit/violations
 * Get blocked requests
 */
app.get('/api/audit/violations', async (req: Request, res: Response) => {
  try {
    const hours = req.query.hours ? parseInt(req.query.hours as string) : 24;
    const limit = req.query.limit ? parseInt(req.query.limit as string) : 50;
    const violations = await getBlockedRequests(hours, limit, supabase);
    res.json({ violations });
  } catch (error) {
    console.error('[Audit] Error:', error);
    res.status(500).json({ error: 'Failed to fetch violations' });
  }
});

/**
 * GET /api/audit/export
 * Export policy decisions to CSV
 */
app.get('/api/audit/export', async (req: Request, res: Response) => {
  try {
    const hours = req.query.hours ? parseInt(req.query.hours as string) : 24;
    const decisions = await getRecentPolicyDecisions({ hours }, supabase);
    const csv = exportPolicyDecisionsToCSV(decisions);

    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', `attachment; filename="policy-decisions-${new Date().toISOString()}.csv"`);
    res.send(csv);
  } catch (error) {
    console.error('[Audit] Error:', error);
    res.status(500).json({ error: 'Failed to export decisions' });
  }
});

// ============================================================================
// ERROR HANDLING
// ============================================================================

app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error('[PolicyGateway] Unhandled error:', err);
  res.status(500).json({
    error: 'Internal server error',
    message: err.message
  });
});

// ============================================================================
// START SERVER
// ============================================================================

app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════════╗
║   DATAVERSE ENTERPRISE CONSOLE - POLICY GATEWAY               ║
║   Portfolio Initiative: PORT-2026-012                          ║
║   Controls: CTRL-POLICY-001, CTRL-CAPABILITY-001, CTRL-MODEL-001 ║
╚═══════════════════════════════════════════════════════════════╝

Server running on port ${PORT}
Supabase: ${SUPABASE_URL}

Endpoints:
  POST   /policy/enforce           - Main policy enforcement
  GET    /api/model-policy/:org    - Get model policies
  POST   /api/model-policy         - Set model policy
  GET    /api/capabilities/:bot    - Get bot capabilities
  POST   /api/capabilities/attest  - Attest capability
  GET    /api/audit/decisions      - Get policy decisions
  GET    /api/audit/metrics        - Get policy metrics
  GET    /api/audit/violations     - Get violations
  GET    /api/audit/export         - Export to CSV

Ready to enforce policies! 🛡️
  `);
});
