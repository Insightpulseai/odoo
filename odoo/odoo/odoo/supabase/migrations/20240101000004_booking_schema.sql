-- Appointments/Booking Schema
-- Replaces: Odoo Appointments (Enterprise)

-- Calendars (availability schedules)
CREATE TABLE IF NOT EXISTS booking_calendars (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES auth.users(id),
    timezone TEXT DEFAULT 'UTC',
    default_duration INT DEFAULT 30, -- minutes
    buffer_before INT DEFAULT 0, -- minutes before appointment
    buffer_after INT DEFAULT 0, -- minutes after appointment
    min_notice INT DEFAULT 60, -- minimum minutes in advance
    max_future_days INT DEFAULT 60, -- how far in advance can book
    is_active BOOLEAN DEFAULT true,
    booking_page_settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Availability slots (when bookings are possible)
CREATE TABLE IF NOT EXISTS booking_availability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    calendar_id UUID REFERENCES booking_calendars(id) ON DELETE CASCADE,
    day_of_week INT CHECK (day_of_week BETWEEN 0 AND 6), -- 0=Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Blocked times (exceptions to availability)
CREATE TABLE IF NOT EXISTS booking_blocked (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    calendar_id UUID REFERENCES booking_calendars(id) ON DELETE CASCADE,
    start_at TIMESTAMPTZ NOT NULL,
    end_at TIMESTAMPTZ NOT NULL,
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Appointment types (different meeting types)
CREATE TABLE IF NOT EXISTS booking_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    calendar_id UUID REFERENCES booking_calendars(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    description TEXT,
    duration INT NOT NULL, -- minutes
    color TEXT DEFAULT '#3b82f6',
    location_type TEXT DEFAULT 'video' CHECK (location_type IN ('video', 'phone', 'in_person', 'custom')),
    location_details TEXT,
    price DECIMAL(10,2),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(calendar_id, slug)
);

-- Appointments (booked meetings)
CREATE TABLE IF NOT EXISTS booking_appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    calendar_id UUID REFERENCES booking_calendars(id) ON DELETE CASCADE,
    type_id UUID REFERENCES booking_types(id),
    start_at TIMESTAMPTZ NOT NULL,
    end_at TIMESTAMPTZ NOT NULL,
    timezone TEXT NOT NULL,
    status TEXT DEFAULT 'confirmed' CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed', 'no_show')),
    -- Attendee info
    attendee_name TEXT NOT NULL,
    attendee_email TEXT NOT NULL,
    attendee_phone TEXT,
    attendee_user_id UUID REFERENCES auth.users(id),
    -- Meeting details
    location TEXT,
    meeting_link TEXT,
    notes TEXT,
    -- Cancellation
    cancelled_at TIMESTAMPTZ,
    cancelled_by TEXT, -- 'host' or 'attendee'
    cancellation_reason TEXT,
    -- Tokens
    confirmation_token TEXT UNIQUE DEFAULT encode(gen_random_bytes(16), 'hex'),
    reschedule_token TEXT UNIQUE DEFAULT encode(gen_random_bytes(16), 'hex'),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Reminders (scheduled notifications)
CREATE TABLE IF NOT EXISTS booking_reminders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    appointment_id UUID REFERENCES booking_appointments(id) ON DELETE CASCADE,
    reminder_type TEXT NOT NULL CHECK (reminder_type IN ('email', 'sms')),
    send_at TIMESTAMPTZ NOT NULL,
    sent_at TIMESTAMPTZ,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Audit log
CREATE TABLE IF NOT EXISTS booking_audit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type TEXT NOT NULL CHECK (entity_type IN ('calendar', 'appointment', 'availability')),
    entity_id UUID NOT NULL,
    action TEXT NOT NULL,
    actor_email TEXT,
    metadata JSONB,
    timestamp TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_booking_availability_calendar ON booking_availability(calendar_id);
CREATE INDEX idx_booking_appointments_calendar ON booking_appointments(calendar_id);
CREATE INDEX idx_booking_appointments_start ON booking_appointments(start_at);
CREATE INDEX idx_booking_appointments_status ON booking_appointments(status);
CREATE INDEX idx_booking_appointments_email ON booking_appointments(attendee_email);
CREATE INDEX idx_booking_reminders_send ON booking_reminders(send_at) WHERE status = 'pending';

-- Row Level Security
ALTER TABLE booking_calendars ENABLE ROW LEVEL SECURITY;
ALTER TABLE booking_appointments ENABLE ROW LEVEL SECURITY;
