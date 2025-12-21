-- Field Service Management Schema
-- Replaces: Odoo Field Service (Enterprise)

-- Technicians
CREATE TABLE IF NOT EXISTS fsm_technicians (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    status TEXT DEFAULT 'available' CHECK (status IN ('available', 'busy', 'offline', 'on_break')),
    current_location JSONB, -- {lat, lng, updated_at}
    home_location JSONB, -- {lat, lng, address}
    work_hours JSONB DEFAULT '{"start": "09:00", "end": "17:00"}',
    max_jobs_per_day INT DEFAULT 8,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Skills
CREATE TABLE IF NOT EXISTS fsm_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Technician skills (many-to-many)
CREATE TABLE IF NOT EXISTS fsm_technician_skills (
    technician_id UUID REFERENCES fsm_technicians(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES fsm_skills(id) ON DELETE CASCADE,
    proficiency INT DEFAULT 3 CHECK (proficiency BETWEEN 1 AND 5),
    certified_at DATE,
    expires_at DATE,
    PRIMARY KEY (technician_id, skill_id)
);

-- Jobs (service requests)
CREATE TABLE IF NOT EXISTS fsm_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reference TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    job_type TEXT DEFAULT 'standard' CHECK (job_type IN ('standard', 'emergency', 'maintenance', 'installation', 'inspection')),
    priority INT DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    status TEXT DEFAULT 'new' CHECK (status IN (
        'new', 'assigned', 'dispatched', 'in_transit', 'on_site',
        'in_progress', 'paused', 'completed', 'cancelled'
    )),
    -- Customer info
    customer_name TEXT NOT NULL,
    customer_email TEXT,
    customer_phone TEXT,
    customer_address TEXT NOT NULL,
    customer_location JSONB, -- {lat, lng}
    -- Scheduling
    scheduled_start TIMESTAMPTZ,
    scheduled_end TIMESTAMPTZ,
    actual_start TIMESTAMPTZ,
    actual_end TIMESTAMPTZ,
    estimated_duration INT DEFAULT 60, -- minutes
    -- Assignment
    technician_id UUID REFERENCES fsm_technicians(id),
    assigned_at TIMESTAMPTZ,
    -- Required skills
    required_skills UUID[] DEFAULT '{}',
    -- Parts and billing
    parts_used JSONB DEFAULT '[]',
    labor_hours DECIMAL(5,2),
    total_cost DECIMAL(10,2),
    -- Notes
    internal_notes TEXT,
    customer_notes TEXT,
    completion_notes TEXT,
    -- Photos
    photos JSONB DEFAULT '[]', -- [{url, caption, taken_at}]
    -- Signature
    signature_data TEXT, -- Base64 customer signature
    signed_at TIMESTAMPTZ,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Routes (optimized job sequences)
CREATE TABLE IF NOT EXISTS fsm_routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    technician_id UUID REFERENCES fsm_technicians(id) ON DELETE CASCADE,
    route_date DATE NOT NULL,
    job_sequence UUID[] NOT NULL, -- Ordered list of job IDs
    total_distance DECIMAL(10,2), -- km
    total_duration INT, -- minutes
    optimized_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(technician_id, route_date)
);

-- Check-ins (technician location updates)
CREATE TABLE IF NOT EXISTS fsm_checkins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES fsm_jobs(id) ON DELETE CASCADE,
    technician_id UUID REFERENCES fsm_technicians(id),
    checkin_type TEXT NOT NULL CHECK (checkin_type IN ('arrive', 'start', 'pause', 'resume', 'complete', 'depart')),
    location JSONB, -- {lat, lng}
    notes TEXT,
    timestamp TIMESTAMPTZ DEFAULT now()
);

-- Audit log
CREATE TABLE IF NOT EXISTS fsm_audit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type TEXT NOT NULL CHECK (entity_type IN ('job', 'technician', 'route')),
    entity_id UUID NOT NULL,
    action TEXT NOT NULL,
    changed_by UUID REFERENCES auth.users(id),
    change_summary JSONB,
    timestamp TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_fsm_jobs_status ON fsm_jobs(status);
CREATE INDEX idx_fsm_jobs_technician ON fsm_jobs(technician_id);
CREATE INDEX idx_fsm_jobs_scheduled ON fsm_jobs(scheduled_start);
CREATE INDEX idx_fsm_technicians_status ON fsm_technicians(status);
CREATE INDEX idx_fsm_routes_date ON fsm_routes(route_date);
CREATE INDEX idx_fsm_checkins_job ON fsm_checkins(job_id);

-- Row Level Security
ALTER TABLE fsm_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE fsm_technicians ENABLE ROW LEVEL SECURITY;

-- Generate job reference
CREATE OR REPLACE FUNCTION generate_job_reference()
RETURNS TRIGGER AS $$
BEGIN
    NEW.reference := 'FSM-' || to_char(now(), 'YYYYMMDD') || '-' ||
                     lpad(nextval('fsm_job_seq')::text, 4, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE SEQUENCE IF NOT EXISTS fsm_job_seq START 1;

CREATE TRIGGER fsm_job_reference_trigger
BEFORE INSERT ON fsm_jobs
FOR EACH ROW EXECUTE FUNCTION generate_job_reference();
