import requests
import json

token = "sbp_9aa105cc134904b74bea64212607cca42cf2d36d"
project_ref = "spdtwktxdalcfigzeqrz"

sql = """
-- Mission: Schema Alignment for Sync Pipeline
CREATE TABLE IF NOT EXISTS ops.sync_checkpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model TEXT UNIQUE NOT NULL, -- e.g. 'res.partner'
    last_odoo_id INTEGER,
    last_sync_at TIMESTAMPTZ DEFAULT now(),
    records_synced BIGINT DEFAULT 0,
    status TEXT DEFAULT 'idle' CHECK (status IN ('idle', 'running', 'error')),
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ops.sync_dlq (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model TEXT NOT NULL,
    odoo_id INTEGER NOT NULL,
    payload JSONB,
    error_message TEXT,
    attempts INTEGER DEFAULT 0,
    resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS
ALTER TABLE ops.sync_checkpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.sync_dlq ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read for all authenticated" ON ops.sync_checkpoints FOR SELECT TO authenticated USING (true);
CREATE POLICY "Enable read for all authenticated" ON ops.sync_dlq FOR SELECT TO authenticated USING (true);

CREATE POLICY "Service Role full access" ON ops.sync_checkpoints USING (auth.role() = 'service_role');
CREATE POLICY "Service Role full access" ON ops.sync_dlq USING (auth.role() = 'service_role');

-- Seed Checkpoints
INSERT INTO ops.sync_checkpoints (model, records_synced, status) VALUES
('res.partner', 1240, 'idle'),
('res.users', 42, 'idle'),
('account.move', 890, 'idle'),
('crm.lead', 315, 'idle')
ON CONFLICT (model) DO NOTHING;
"""

url = f"https://api.supabase.com/v1/projects/{project_ref}/database/query"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
payload = {"query": sql}

print(f"Applying sync schema extensions to {project_ref}...")
response = requests.post(url, headers=headers, json=payload)

if response.status_code == 201 or response.status_code == 200:
    print("Success: Sync schema applied.")
else:
    print(f"Error {response.status_code}: {response.text}")
