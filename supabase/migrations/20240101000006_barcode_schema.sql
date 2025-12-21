-- Barcode Scanner Schema
-- Replaces: Odoo Barcode (Enterprise)

-- Scan sessions (batch operations)
CREATE TABLE IF NOT EXISTS barcode_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    operation_type TEXT NOT NULL CHECK (operation_type IN ('receive', 'pick', 'transfer', 'inventory', 'pack')),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'cancelled')),
    source_location TEXT,
    destination_location TEXT,
    reference TEXT, -- PO number, SO number, etc.
    started_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ,
    notes TEXT
);

-- Scans (individual barcode scans)
CREATE TABLE IF NOT EXISTS barcode_scans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES barcode_sessions(id) ON DELETE CASCADE,
    barcode TEXT NOT NULL,
    barcode_type TEXT DEFAULT 'product' CHECK (barcode_type IN ('product', 'location', 'lot', 'serial', 'package')),
    product_id TEXT, -- Odoo product ID
    product_name TEXT,
    quantity DECIMAL(10,3) DEFAULT 1,
    uom TEXT DEFAULT 'unit',
    lot_number TEXT,
    serial_number TEXT,
    location_code TEXT,
    scan_result TEXT DEFAULT 'success' CHECK (scan_result IN ('success', 'not_found', 'wrong_location', 'error')),
    error_message TEXT,
    scanned_at TIMESTAMPTZ DEFAULT now()
);

-- Operations (completed inventory moves)
CREATE TABLE IF NOT EXISTS barcode_operations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES barcode_sessions(id),
    operation_type TEXT NOT NULL,
    product_id TEXT NOT NULL,
    product_name TEXT,
    quantity DECIMAL(10,3) NOT NULL,
    uom TEXT DEFAULT 'unit',
    source_location TEXT,
    destination_location TEXT,
    lot_number TEXT,
    serial_number TEXT,
    odoo_move_id INT, -- Link to Odoo stock.move
    synced_at TIMESTAMPTZ,
    sync_status TEXT DEFAULT 'pending' CHECK (sync_status IN ('pending', 'synced', 'failed')),
    sync_error TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Offline queue (for sync when offline)
CREATE TABLE IF NOT EXISTS barcode_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    device_id TEXT,
    operation_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    status TEXT DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'synced', 'failed')),
    attempts INT DEFAULT 0,
    last_attempt TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    synced_at TIMESTAMPTZ
);

-- Locations cache (for offline lookup)
CREATE TABLE IF NOT EXISTS barcode_locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    odoo_id INT UNIQUE,
    barcode TEXT UNIQUE,
    name TEXT NOT NULL,
    complete_name TEXT, -- Full path
    location_type TEXT,
    parent_id INT,
    is_active BOOLEAN DEFAULT true,
    synced_at TIMESTAMPTZ DEFAULT now()
);

-- Products cache (for offline lookup)
CREATE TABLE IF NOT EXISTS barcode_products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    odoo_id INT UNIQUE,
    barcode TEXT,
    default_code TEXT, -- Internal reference
    name TEXT NOT NULL,
    uom TEXT DEFAULT 'unit',
    tracking TEXT DEFAULT 'none' CHECK (tracking IN ('none', 'lot', 'serial')),
    image_url TEXT,
    is_active BOOLEAN DEFAULT true,
    synced_at TIMESTAMPTZ DEFAULT now()
);

-- Audit log
CREATE TABLE IF NOT EXISTS barcode_audit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES barcode_sessions(id),
    action TEXT NOT NULL,
    details JSONB,
    user_id UUID REFERENCES auth.users(id),
    timestamp TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_barcode_sessions_user ON barcode_sessions(user_id);
CREATE INDEX idx_barcode_sessions_status ON barcode_sessions(status);
CREATE INDEX idx_barcode_scans_session ON barcode_scans(session_id);
CREATE INDEX idx_barcode_scans_barcode ON barcode_scans(barcode);
CREATE INDEX idx_barcode_operations_sync ON barcode_operations(sync_status);
CREATE INDEX idx_barcode_queue_status ON barcode_queue(status);
CREATE INDEX idx_barcode_products_barcode ON barcode_products(barcode);
CREATE INDEX idx_barcode_products_code ON barcode_products(default_code);
CREATE INDEX idx_barcode_locations_barcode ON barcode_locations(barcode);

-- Row Level Security
ALTER TABLE barcode_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE barcode_scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE barcode_operations ENABLE ROW LEVEL SECURITY;
