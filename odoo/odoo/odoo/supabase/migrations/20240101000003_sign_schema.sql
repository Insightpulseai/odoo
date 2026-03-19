-- E-Signature Schema
-- Replaces: Odoo Sign (Enterprise)

-- Documents (files to be signed)
CREATE TABLE IF NOT EXISTS sign_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    file_path TEXT NOT NULL, -- Storage path
    file_type TEXT NOT NULL CHECK (file_type IN ('pdf', 'docx', 'doc')),
    file_size INT,
    page_count INT DEFAULT 1,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'pending', 'partially_signed', 'completed', 'expired', 'cancelled')),
    created_by UUID REFERENCES auth.users(id),
    expires_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Signature requests (who needs to sign)
CREATE TABLE IF NOT EXISTS sign_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES sign_documents(id) ON DELETE CASCADE,
    signer_email TEXT NOT NULL,
    signer_name TEXT,
    signer_user_id UUID REFERENCES auth.users(id),
    role TEXT DEFAULT 'signer' CHECK (role IN ('signer', 'approver', 'cc')),
    signing_order INT DEFAULT 1,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'viewed', 'signed', 'declined', 'expired')),
    access_token TEXT UNIQUE DEFAULT encode(gen_random_bytes(32), 'hex'),
    reminder_sent_at TIMESTAMPTZ,
    viewed_at TIMESTAMPTZ,
    signed_at TIMESTAMPTZ,
    declined_at TIMESTAMPTZ,
    decline_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Signature placements (where to sign)
CREATE TABLE IF NOT EXISTS sign_placements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES sign_documents(id) ON DELETE CASCADE,
    request_id UUID REFERENCES sign_requests(id) ON DELETE CASCADE,
    placement_type TEXT NOT NULL CHECK (placement_type IN ('signature', 'initial', 'date', 'text', 'checkbox')),
    page_number INT NOT NULL DEFAULT 1,
    x_position DECIMAL NOT NULL, -- Percentage from left
    y_position DECIMAL NOT NULL, -- Percentage from top
    width DECIMAL DEFAULT 20,
    height DECIMAL DEFAULT 5,
    required BOOLEAN DEFAULT true,
    value TEXT, -- Filled value after signing
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Signatures (actual signature data)
CREATE TABLE IF NOT EXISTS sign_signatures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID REFERENCES sign_requests(id) ON DELETE CASCADE,
    placement_id UUID REFERENCES sign_placements(id) ON DELETE CASCADE,
    signature_type TEXT NOT NULL CHECK (signature_type IN ('draw', 'type', 'upload')),
    signature_data TEXT NOT NULL, -- Base64 image or typed name
    ip_address INET,
    user_agent TEXT,
    signed_at TIMESTAMPTZ DEFAULT now()
);

-- Audit log
CREATE TABLE IF NOT EXISTS sign_audit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES sign_documents(id) ON DELETE CASCADE,
    request_id UUID REFERENCES sign_requests(id),
    action TEXT NOT NULL CHECK (action IN (
        'created', 'sent', 'viewed', 'signed', 'declined',
        'reminded', 'expired', 'cancelled', 'completed', 'downloaded'
    )),
    actor_email TEXT,
    actor_user_id UUID REFERENCES auth.users(id),
    ip_address INET,
    metadata JSONB,
    timestamp TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_sign_requests_document ON sign_requests(document_id);
CREATE INDEX idx_sign_requests_email ON sign_requests(signer_email);
CREATE INDEX idx_sign_requests_token ON sign_requests(access_token);
CREATE INDEX idx_sign_placements_document ON sign_placements(document_id);
CREATE INDEX idx_sign_audit_document ON sign_audit(document_id);

-- Row Level Security
ALTER TABLE sign_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE sign_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE sign_signatures ENABLE ROW LEVEL SECURITY;
