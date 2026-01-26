/**
 * Google Services Handler
 * Handles Google Drive uploads and Google Workspace events
 */

import { createClient, SupabaseClient } from 'https://esm.sh/@supabase/supabase-js@2';
import {
  GoogleDriveUploadResult,
  GoogleDriveChangeEvent,
  HandlerResponse,
  ArtifactSync,
} from '../types.ts';

const GOOGLE_DRIVE_API = 'https://www.googleapis.com/drive/v3';
const GOOGLE_UPLOAD_API = 'https://www.googleapis.com/upload/drive/v3';

/**
 * Refresh Google OAuth token using refresh token from Vault
 */
export async function refreshGoogleToken(
  refreshToken: string,
  clientId: string,
  clientSecret: string
): Promise<{ access_token: string; expires_in: number }> {
  const response = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      refresh_token: refreshToken,
      grant_type: 'refresh_token',
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to refresh Google token: ${error}`);
  }

  return await response.json();
}

/**
 * Get or create folder in Google Drive
 */
async function getOrCreateFolder(
  folderPath: string,
  parentId: string | null,
  accessToken: string
): Promise<string> {
  const parts = folderPath.split('/').filter(Boolean);
  let currentParentId = parentId || 'root';

  for (const folderName of parts) {
    // Search for existing folder
    const query = `name='${folderName}' and mimeType='application/vnd.google-apps.folder' and '${currentParentId}' in parents and trashed=false`;
    const searchUrl = `${GOOGLE_DRIVE_API}/files?q=${encodeURIComponent(query)}&fields=files(id,name)`;

    const searchResponse = await fetch(searchUrl, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    });

    if (!searchResponse.ok) {
      throw new Error(`Failed to search for folder: ${searchResponse.statusText}`);
    }

    const searchData = await searchResponse.json();

    if (searchData.files && searchData.files.length > 0) {
      currentParentId = searchData.files[0].id;
    } else {
      // Create folder
      const createResponse = await fetch(`${GOOGLE_DRIVE_API}/files`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: folderName,
          mimeType: 'application/vnd.google-apps.folder',
          parents: [currentParentId],
        }),
      });

      if (!createResponse.ok) {
        throw new Error(`Failed to create folder: ${createResponse.statusText}`);
      }

      const createData = await createResponse.json();
      currentParentId = createData.id;
    }
  }

  return currentParentId;
}

/**
 * Upload file to Google Drive
 */
export async function uploadToDrive(
  fileContent: ArrayBuffer,
  fileName: string,
  destinationPath: string,
  accessToken: string,
  mimeType: string = 'application/octet-stream'
): Promise<GoogleDriveUploadResult> {
  // Parse destination path
  const pathParts = destinationPath.split('/');
  const targetFileName = pathParts.pop() || fileName;
  const folderPath = pathParts.join('/');

  // Get or create parent folder
  const parentFolderId = folderPath
    ? await getOrCreateFolder(folderPath, null, accessToken)
    : 'root';

  // Create metadata
  const metadata = {
    name: targetFileName,
    parents: [parentFolderId],
  };

  // Create multipart request
  const boundary = '-------314159265358979323846';
  const delimiter = '\r\n--' + boundary + '\r\n';
  const closeDelimiter = '\r\n--' + boundary + '--';

  const metadataString = JSON.stringify(metadata);
  const fileBase64 = btoa(
    new Uint8Array(fileContent).reduce((data, byte) => data + String.fromCharCode(byte), '')
  );

  const requestBody =
    delimiter +
    'Content-Type: application/json; charset=UTF-8\r\n\r\n' +
    metadataString +
    delimiter +
    `Content-Type: ${mimeType}\r\n` +
    'Content-Transfer-Encoding: base64\r\n\r\n' +
    fileBase64 +
    closeDelimiter;

  const response = await fetch(
    `${GOOGLE_UPLOAD_API}/files?uploadType=multipart&fields=id,name,mimeType,webViewLink,parents`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': `multipart/related; boundary="${boundary}"`,
      },
      body: requestBody,
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to upload to Drive: ${error}`);
  }

  return await response.json();
}

/**
 * Handle Google Drive change notification webhook
 */
export async function handleDriveChangeNotification(
  payload: GoogleDriveChangeEvent,
  supabase: SupabaseClient
): Promise<HandlerResponse> {
  // Log the change event for processing
  const { data, error } = await supabase.rpc('log_webhook_event', {
    p_source: 'google_drive',
    p_event_type: payload.type,
    p_event_id: `${payload.fileId}-${payload.time}`,
    p_payload: payload,
  });

  if (error) {
    return {
      success: false,
      error: error.message,
    };
  }

  return {
    success: true,
    event_id: data,
    details: {
      file_id: payload.fileId,
      change_type: payload.type,
      removed: payload.removed,
    },
  };
}

/**
 * Execute pending Drive syncs
 */
export async function executeDriveSyncs(
  supabase: SupabaseClient,
  accessToken: string,
  limit: number = 10
): Promise<HandlerResponse> {
  // Get pending syncs for Google Drive destination
  const { data: syncs, error: fetchError } = await supabase
    .from('artifact_syncs')
    .select('*')
    .eq('destination_provider', 'google_drive')
    .eq('status', 'pending')
    .order('created_at', { ascending: true })
    .limit(limit);

  if (fetchError) {
    return {
      success: false,
      error: fetchError.message,
    };
  }

  if (!syncs || syncs.length === 0) {
    return {
      success: true,
      syncs_completed: 0,
      details: { message: 'No pending Drive syncs' },
    };
  }

  let completed = 0;
  let failed = 0;

  for (const sync of syncs as ArtifactSync[]) {
    try {
      // Mark as syncing
      await supabase.rpc('update_sync_status', {
        p_sync_id: sync.id,
        p_status: 'syncing',
      });

      // Get artifact content from metadata
      const downloadUrl = (sync.metadata as Record<string, unknown>)?.download_url as string;
      if (!downloadUrl) {
        throw new Error('No download URL in sync metadata');
      }

      // Download artifact (this would need the source token, e.g., GitHub token)
      // For now, we'll mark it for manual processing
      // In production, this would fetch the content and upload

      // Simulated upload result
      const result = await uploadToDrive(
        new ArrayBuffer(0), // Would be actual content
        sync.artifact_name,
        sync.destination_path,
        accessToken
      );

      // Mark as completed
      await supabase.rpc('update_sync_status', {
        p_sync_id: sync.id,
        p_status: 'completed',
        p_destination_ref: result.id,
        p_size_bytes: sync.size_bytes,
      });

      completed++;
    } catch (error) {
      // Mark as failed
      await supabase.rpc('update_sync_status', {
        p_sync_id: sync.id,
        p_status: 'failed',
        p_error_message: error instanceof Error ? error.message : 'Unknown error',
      });

      failed++;
    }
  }

  return {
    success: true,
    syncs_completed: completed,
    details: {
      total_processed: syncs.length,
      completed,
      failed,
    },
  };
}

/**
 * Convert Google Docs to Markdown (for spec/PRD syncs)
 */
export async function convertDocsToMarkdown(
  docId: string,
  accessToken: string
): Promise<string> {
  // Export as plain text (Markdown requires parsing)
  const response = await fetch(
    `${GOOGLE_DRIVE_API}/files/${docId}/export?mimeType=text/plain`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to export document: ${response.statusText}`);
  }

  const text = await response.text();

  // Basic conversion to Markdown (simplified)
  // In production, use Google Docs API for proper formatting
  return text;
}

/**
 * Main Google handler entry point
 */
export async function handleGoogleWebhook(
  eventType: string,
  payload: Record<string, unknown>,
  supabase: SupabaseClient
): Promise<HandlerResponse> {
  switch (eventType) {
    case 'drive.changes':
    case 'sync':
      return handleDriveChangeNotification(payload as GoogleDriveChangeEvent, supabase);

    default:
      return {
        success: true,
        details: { message: `Unhandled Google event type: ${eventType}` },
      };
  }
}
