# Storage Multipart Upload Pattern

## Purpose
Artifact and evidence upload pattern using Supabase Storage with multipart form data handling and row-level bucket policies.

## Folder Layout
```
supabase/functions/upload-artifact/
├── index.ts                 # Upload handler
├── .env.example             # Required env vars
└── README.md                # Upload documentation
```

## Required Environment Variables
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Anonymous key for RLS-enforced uploads (user context)
- `SUPABASE_SERVICE_ROLE_KEY`: Service role key for worker uploads (optional)

## Minimal Code Skeleton

**User-context upload (RLS-enforced):**
```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseAnonKey = Deno.env.get('SUPABASE_ANON_KEY')!

serve(async (req) => {
  try {
    // Extract user JWT
    const authHeader = req.headers.get('Authorization')
    if (!authHeader) {
      return new Response('Unauthorized', { status: 401 })
    }

    // Initialize Supabase client with user context
    const supabase = createClient(supabaseUrl, supabaseAnonKey, {
      global: {
        headers: { Authorization: authHeader }
      }
    })

    // Verify user session
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    if (authError || !user) {
      return new Response('Invalid token', { status: 401 })
    }

    // Parse multipart form data
    const formData = await req.formData()
    const file = formData.get('file') as File

    if (!file) {
      return new Response('No file provided', { status: 400 })
    }

    // Generate file path with user scoping
    const fileName = `${user.id}/${Date.now()}-${file.name}`
    const bucketName = 'artifacts' // or 'evidence', 'exports', etc.

    // Upload to Supabase Storage (RLS bucket policy enforces user access)
    const { data, error } = await supabase.storage
      .from(bucketName)
      .upload(fileName, file, {
        cacheControl: '3600',
        upsert: false,
        contentType: file.type
      })

    if (error) throw error

    // Create metadata record in database
    await supabase.from('ops.artifacts').insert({
      artifact_id: crypto.randomUUID(),
      user_id: user.id,
      bucket: bucketName,
      path: data.path,
      file_name: file.name,
      file_size: file.size,
      mime_type: file.type,
      created_at: new Date().toISOString()
    })

    // Get public URL (if bucket is public) or signed URL
    const { data: { publicUrl } } = supabase.storage
      .from(bucketName)
      .getPublicUrl(data.path)

    return new Response(
      JSON.stringify({
        success: true,
        path: data.path,
        url: publicUrl
      }),
      { headers: { "Content-Type": "application/json" }, status: 200 }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { headers: { "Content-Type": "application/json" }, status: 500 }
    )
  }
})
```

**Storage bucket RLS policy example:**
```sql
-- Enable RLS on artifacts bucket
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only upload to their own folder
CREATE POLICY "Users can upload to own folder"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'artifacts' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy: Users can read own files
CREATE POLICY "Users can read own files"
ON storage.objects
FOR SELECT
TO authenticated
USING (
  bucket_id = 'artifacts' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy: Service role can access all files (for workers)
CREATE POLICY "Service role full access"
ON storage.objects
FOR ALL
TO service_role
USING (bucket_id = 'artifacts');
```

## Failure Modes
- **File too large**: Set size limits in bucket policy; return 413 if exceeded
- **Invalid file type**: Validate MIME type before upload; reject dangerous types
- **Storage quota exceeded**: Handle quota errors gracefully; notify user
- **Upload timeout**: Large files may timeout; use resumable uploads for >10MB files

## SSOT/SOR Boundary Notes
- **Artifacts only**: Storage is for SSOT artifacts/evidence/exports, NEVER for Odoo SOR documents
- **Provenance required**: Every uploaded file must have metadata record in `ops.artifacts` with source system
- **RLS enforcement**: Bucket policies must enforce user-scoped access; no public write access
- **SOR attachments**: Odoo attachments remain in Odoo; Supabase stores only pointers/hashes if mirroring needed
- **Audit trail**: All uploads must be logged in `ops.artifacts` with user_id, timestamp, file metadata
- **No sensitive SOR data**: Never upload ledger documents, financial records, or PII without encryption
