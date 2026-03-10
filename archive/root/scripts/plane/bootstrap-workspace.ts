#!/usr/bin/env tsx
/**
 * Plane Workspace Bootstrap Script
 *
 * Automates Plane workspace setup for OKR tracking with Odoo integration
 * Portfolio Initiative: PORT-2026-011
 * Evidence: EVID-20260212-006
 *
 * Usage:
 *   pnpm --filter scripts tsx scripts/plane/bootstrap-workspace.ts
 *   PLANE_API_KEY=xxx PLANE_WORKSPACE_SLUG=xxx tsx scripts/plane/bootstrap-workspace.ts
 */

import { createClient } from '@supabase/supabase-js';
import * as fs from 'fs';
import * as path from 'path';

// Configuration
const PLANE_API_URL = process.env.PLANE_API_URL || 'https://api.plane.so';
const PLANE_API_KEY = process.env.PLANE_API_KEY;
const PLANE_WORKSPACE_SLUG = process.env.PLANE_WORKSPACE_SLUG || 'insightpulseai-okr';
const SUPABASE_URL = process.env.SUPABASE_URL || 'https://spdtwktxdalcfigzeqrz.supabase.co';
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const EVIDENCE_DIR = path.join(__dirname, '../../docs/evidence/20260212-2000/plane-bootstrap');

// Types
interface PlaneWorkspace {
    id: string;
    slug: string;
    name: string;
    created_at: string;
}

interface PlaneProject {
    id: string;
    name: string;
    identifier: string;
    workspace: string;
}

interface PlaneIssue {
    id: string;
    name: string;
    project: string;
    state: string;
}

interface PlaneCustomField {
    id: string;
    name: string;
    type: string;
    options?: string[];
}

// Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY!, {
    auth: { persistSession: false }
});

/**
 * Make authenticated Plane API request
 */
async function planeRequest<T>(
    method: string,
    endpoint: string,
    body?: any
): Promise<T> {
    const url = `${PLANE_API_URL}${endpoint}`;
    const headers = {
        'Authorization': `Bearer ${PLANE_API_KEY}`,
        'Content-Type': 'application/json'
    };

    const response = await fetch(url, {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Plane API error (${response.status}): ${errorText}`);
    }

    return response.json();
}

/**
 * Check if workspace exists
 */
async function workspaceExists(slug: string): Promise<PlaneWorkspace | null> {
    try {
        const workspace = await planeRequest<PlaneWorkspace>(
            'GET',
            `/api/v1/workspaces/${slug}/`
        );
        return workspace;
    } catch (error) {
        if (error instanceof Error && error.message.includes('404')) {
            return null;
        }
        throw error;
    }
}

/**
 * Create Plane workspace
 */
async function createWorkspace(name: string, slug: string): Promise<PlaneWorkspace> {
    console.log(`[INFO] Creating workspace: ${name} (${slug})`);

    const workspace = await planeRequest<PlaneWorkspace>(
        'POST',
        '/api/v1/workspaces/',
        {
            name,
            slug,
            organization_size: '1-10',
            url: 'https://erp.insightpulseai.com'
        }
    );

    console.log(`[SUCCESS] Workspace created: ${workspace.id}`);
    return workspace;
}

/**
 * Create OKR project
 */
async function createOKRProject(workspaceSlug: string): Promise<PlaneProject> {
    console.log(`[INFO] Creating OKR project in workspace: ${workspaceSlug}`);

    const project = await planeRequest<PlaneProject>(
        'POST',
        `/api/v1/workspaces/${workspaceSlug}/projects/`,
        {
            name: 'OKRs - Q1 2026',
            identifier: 'OKR',
            description: 'Objectives and Key Results tracking for Q1 2026',
            network: 0, // Private project
            project_lead: null // Set later
        }
    );

    console.log(`[SUCCESS] OKR project created: ${project.id}`);
    return project;
}

/**
 * Create custom fields for OKR tracking
 */
async function createOKRCustomFields(
    workspaceSlug: string,
    projectId: string
): Promise<PlaneCustomField[]> {
    console.log(`[INFO] Creating OKR custom fields for project: ${projectId}`);

    const fields: PlaneCustomField[] = [];

    // Custom field 1: OKR Type (Objective vs Key Result)
    const okrType = await planeRequest<PlaneCustomField>(
        'POST',
        `/api/v1/workspaces/${workspaceSlug}/projects/${projectId}/custom-fields/`,
        {
            name: 'OKR Type',
            type: 'select',
            options: ['Objective', 'Key Result']
        }
    );
    fields.push(okrType);
    console.log(`[SUCCESS] Created custom field: OKR Type`);

    // Custom field 2: Target Value
    const targetValue = await planeRequest<PlaneCustomField>(
        'POST',
        `/api/v1/workspaces/${workspaceSlug}/projects/${projectId}/custom-fields/`,
        {
            name: 'Target Value',
            type: 'number'
        }
    );
    fields.push(targetValue);
    console.log(`[SUCCESS] Created custom field: Target Value`);

    // Custom field 3: Current Value
    const currentValue = await planeRequest<PlaneCustomField>(
        'POST',
        `/api/v1/workspaces/${workspaceSlug}/projects/${projectId}/custom-fields/`,
        {
            name: 'Current Value',
            type: 'number'
        }
    );
    fields.push(currentValue);
    console.log(`[SUCCESS] Created custom field: Current Value`);

    // Custom field 4: Progress Percentage
    const progress = await planeRequest<PlaneCustomField>(
        'POST',
        `/api/v1/workspaces/${workspaceSlug}/projects/${projectId}/custom-fields/`,
        {
            name: 'Progress %',
            type: 'number'
        }
    );
    fields.push(progress);
    console.log(`[SUCCESS] Created custom field: Progress %`);

    return fields;
}

/**
 * Create example OKRs (Q1 2026)
 */
async function seedExampleOKRs(
    workspaceSlug: string,
    projectId: string
): Promise<PlaneIssue[]> {
    console.log(`[INFO] Seeding example OKRs for Q1 2026`);

    const issues: PlaneIssue[] = [];

    // Objective 1: Revenue Growth
    const objective1 = await planeRequest<PlaneIssue>(
        'POST',
        `/api/v1/workspaces/${workspaceSlug}/projects/${projectId}/issues/`,
        {
            name: 'Achieve 30% Revenue Growth in Q1 2026',
            description: 'Drive revenue growth through client acquisition and upselling',
            priority: 'high',
            state: 'backlog',
            custom_fields: {
                'OKR Type': 'Objective',
                'Target Value': 30,
                'Current Value': 0,
                'Progress %': 0
            }
        }
    );
    issues.push(objective1);

    // Key Result 1.1
    const kr1_1 = await planeRequest<PlaneIssue>(
        'POST',
        `/api/v1/workspaces/${workspaceSlug}/projects/${projectId}/issues/`,
        {
            name: 'Acquire 10 new enterprise clients',
            description: 'Target Fortune 500 companies for Odoo implementation projects',
            priority: 'high',
            state: 'backlog',
            parent: objective1.id,
            custom_fields: {
                'OKR Type': 'Key Result',
                'Target Value': 10,
                'Current Value': 0,
                'Progress %': 0
            }
        }
    );
    issues.push(kr1_1);

    // Key Result 1.2
    const kr1_2 = await planeRequest<PlaneIssue>(
        'POST',
        `/api/v1/workspaces/${workspaceSlug}/projects/${projectId}/issues/`,
        {
            name: 'Upsell 5 existing clients to premium tier',
            description: 'Upgrade clients from basic to premium Odoo support packages',
            priority: 'high',
            state: 'backlog',
            parent: objective1.id,
            custom_fields: {
                'OKR Type': 'Key Result',
                'Target Value': 5,
                'Current Value': 0,
                'Progress %': 0
            }
        }
    );
    issues.push(kr1_2);

    // Objective 2: Product Quality
    const objective2 = await planeRequest<PlaneIssue>(
        'POST',
        `/api/v1/workspaces/${workspaceSlug}/projects/${projectId}/issues/`,
        {
            name: 'Achieve 95% Customer Satisfaction Score',
            description: 'Improve product quality and customer support responsiveness',
            priority: 'high',
            state: 'backlog',
            custom_fields: {
                'OKR Type': 'Objective',
                'Target Value': 95,
                'Current Value': 0,
                'Progress %': 0
            }
        }
    );
    issues.push(objective2);

    // Key Result 2.1
    const kr2_1 = await planeRequest<PlaneIssue>(
        'POST',
        `/api/v1/workspaces/${workspaceSlug}/projects/${projectId}/issues/`,
        {
            name: 'Reduce average ticket resolution time to <4 hours',
            description: 'Improve support team efficiency and tooling',
            priority: 'medium',
            state: 'backlog',
            parent: objective2.id,
            custom_fields: {
                'OKR Type': 'Key Result',
                'Target Value': 4,
                'Current Value': 0,
                'Progress %': 0
            }
        }
    );
    issues.push(kr2_1);

    console.log(`[SUCCESS] Seeded ${issues.length} example OKRs`);
    return issues;
}

/**
 * Sync workspace to Supabase
 */
async function syncToSupabase(
    workspace: PlaneWorkspace,
    project: PlaneProject,
    issues: PlaneIssue[]
) {
    console.log(`[INFO] Syncing workspace to Supabase...`);

    // Upsert workspace
    const { error: workspaceError } = await supabase
        .from('plane.workspaces')
        .upsert({
            id: workspace.id,
            slug: workspace.slug,
            name: workspace.name,
            created_at: workspace.created_at
        }, { onConflict: 'id' });

    if (workspaceError) {
        console.error(`[ERROR] Failed to sync workspace:`, workspaceError);
    } else {
        console.log(`[SUCCESS] Workspace synced to Supabase`);
    }

    // Upsert project
    const { error: projectError } = await supabase
        .from('plane.projects')
        .upsert({
            id: project.id,
            name: project.name,
            identifier: project.identifier,
            workspace_id: workspace.id
        }, { onConflict: 'id' });

    if (projectError) {
        console.error(`[ERROR] Failed to sync project:`, projectError);
    } else {
        console.log(`[SUCCESS] Project synced to Supabase`);
    }

    // Upsert issues
    const issueRecords = issues.map(issue => ({
        id: issue.id,
        name: issue.name,
        project_id: project.id,
        state: issue.state
    }));

    const { error: issuesError } = await supabase
        .from('plane.issues')
        .upsert(issueRecords, { onConflict: 'id' });

    if (issuesError) {
        console.error(`[ERROR] Failed to sync issues:`, issuesError);
    } else {
        console.log(`[SUCCESS] ${issues.length} issues synced to Supabase`);
    }
}

/**
 * Write evidence log
 */
function writeEvidenceLog(data: any) {
    if (!fs.existsSync(EVIDENCE_DIR)) {
        fs.mkdirSync(EVIDENCE_DIR, { recursive: true });
    }

    const logPath = path.join(EVIDENCE_DIR, `bootstrap-log-${Date.now()}.json`);
    fs.writeFileSync(logPath, JSON.stringify(data, null, 2));
    console.log(`[INFO] Evidence log written: ${logPath}`);
}

/**
 * Main execution
 */
async function main() {
    console.log('================================================');
    console.log('Plane Workspace Bootstrap');
    console.log('================================================');
    console.log(`Workspace Slug: ${PLANE_WORKSPACE_SLUG}`);
    console.log('');

    // Validate environment
    if (!PLANE_API_KEY) {
        console.error('[ERROR] PLANE_API_KEY environment variable not set');
        process.exit(1);
    }

    if (!SUPABASE_SERVICE_ROLE_KEY) {
        console.error('[ERROR] SUPABASE_SERVICE_ROLE_KEY environment variable not set');
        process.exit(1);
    }

    const results: any = {
        workspace_slug: PLANE_WORKSPACE_SLUG,
        started_at: new Date().toISOString(),
        steps: []
    };

    try {
        // Step 1: Check if workspace exists
        console.log('[Step 1] Checking if workspace exists...');
        let workspace = await workspaceExists(PLANE_WORKSPACE_SLUG);

        if (workspace) {
            console.log(`[INFO] Workspace already exists: ${workspace.id}`);
            results.steps.push({ step: 1, action: 'check_workspace', status: 'exists', workspace_id: workspace.id });
        } else {
            // Create workspace
            workspace = await createWorkspace('InsightPulse AI - OKRs', PLANE_WORKSPACE_SLUG);
            results.steps.push({ step: 1, action: 'create_workspace', status: 'created', workspace_id: workspace.id });
        }

        // Step 2: Create OKR project
        console.log('[Step 2] Creating OKR project...');
        const project = await createOKRProject(workspace.slug);
        results.steps.push({ step: 2, action: 'create_project', status: 'created', project_id: project.id });

        // Step 3: Create custom fields
        console.log('[Step 3] Creating OKR custom fields...');
        const customFields = await createOKRCustomFields(workspace.slug, project.id);
        results.steps.push({ step: 3, action: 'create_custom_fields', status: 'created', fields_count: customFields.length });

        // Step 4: Seed example OKRs
        console.log('[Step 4] Seeding example OKRs...');
        const issues = await seedExampleOKRs(workspace.slug, project.id);
        results.steps.push({ step: 4, action: 'seed_okrs', status: 'created', issues_count: issues.length });

        // Step 5: Sync to Supabase
        console.log('[Step 5] Syncing to Supabase...');
        await syncToSupabase(workspace, project, issues);
        results.steps.push({ step: 5, action: 'sync_supabase', status: 'synced' });

        results.completed_at = new Date().toISOString();
        results.status = 'success';

        console.log('');
        console.log('================================================');
        console.log('✅ Bootstrap Complete');
        console.log('================================================');
        console.log(`Workspace: ${workspace.name} (${workspace.slug})`);
        console.log(`Project: ${project.name} (${project.identifier})`);
        console.log(`OKRs Created: ${issues.length}`);
        console.log('');

    } catch (error) {
        console.error('[ERROR] Bootstrap failed:', error);
        results.completed_at = new Date().toISOString();
        results.status = 'failed';
        results.error = error instanceof Error ? error.message : String(error);
        process.exit(1);
    } finally {
        writeEvidenceLog(results);
    }
}

// Execute
main().catch(error => {
    console.error('[FATAL]', error);
    process.exit(1);
});
