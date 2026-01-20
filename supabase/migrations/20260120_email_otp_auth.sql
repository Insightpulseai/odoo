-- Email OTP Authentication Schema
-- Purpose: Passwordless email OTP login (no magic links)
-- Security: Time-limited OTPs with rate limiting

-- Create auth schema if not exists
CREATE SCHEMA IF NOT EXISTS auth_otp;

-- OTP Storage Table
CREATE TABLE IF NOT EXISTS auth_otp.email_otps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL,
    otp_code TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '10 minutes'),
    verified_at TIMESTAMPTZ,
    attempts INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 3,
    ip_address INET,
    user_agent TEXT,
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_email_otps_email ON auth_otp.email_otps(email);
CREATE INDEX IF NOT EXISTS idx_email_otps_created_at ON auth_otp.email_otps(created_at);
CREATE INDEX IF NOT EXISTS idx_email_otps_expires_at ON auth_otp.email_otps(expires_at);

-- Rate Limiting Table
CREATE TABLE IF NOT EXISTS auth_otp.rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL,
    request_count INT NOT NULL DEFAULT 1,
    window_start TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    window_end TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '1 hour'),
    blocked_until TIMESTAMPTZ,
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX IF NOT EXISTS idx_rate_limits_email ON auth_otp.rate_limits(email);
CREATE INDEX IF NOT EXISTS idx_rate_limits_window_end ON auth_otp.rate_limits(window_end);

-- Audit Log Table
CREATE TABLE IF NOT EXISTS auth_otp.audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL,
    action TEXT NOT NULL, -- 'request_otp', 'verify_otp', 'rate_limited', 'invalid_otp'
    success BOOLEAN NOT NULL,
    ip_address INET,
    user_agent TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_email ON auth_otp.audit_log(email);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON auth_otp.audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON auth_otp.audit_log(action);

-- Cleanup Function: Delete expired OTPs (runs daily)
CREATE OR REPLACE FUNCTION auth_otp.cleanup_expired_otps()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    DELETE FROM auth_otp.email_otps
    WHERE expires_at < NOW() - INTERVAL '1 day';

    DELETE FROM auth_otp.rate_limits
    WHERE window_end < NOW() - INTERVAL '1 day';

    DELETE FROM auth_otp.audit_log
    WHERE created_at < NOW() - INTERVAL '30 days';
END;
$$;

-- Rate Limiting Check Function
CREATE OR REPLACE FUNCTION auth_otp.check_rate_limit(
    p_email TEXT,
    p_max_requests INT DEFAULT 5,
    p_window_minutes INT DEFAULT 60
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_rate_limit auth_otp.rate_limits;
    v_blocked_until TIMESTAMPTZ;
BEGIN
    -- Check if email is currently blocked
    SELECT blocked_until INTO v_blocked_until
    FROM auth_otp.rate_limits
    WHERE email = p_email
      AND blocked_until > NOW()
    ORDER BY blocked_until DESC
    LIMIT 1;

    IF FOUND THEN
        RETURN jsonb_build_object(
            'allowed', false,
            'reason', 'rate_limited',
            'blocked_until', v_blocked_until,
            'retry_after_seconds', EXTRACT(EPOCH FROM (v_blocked_until - NOW()))::int
        );
    END IF;

    -- Get or create rate limit record
    SELECT * INTO v_rate_limit
    FROM auth_otp.rate_limits
    WHERE email = p_email
      AND window_end > NOW()
    ORDER BY window_start DESC
    LIMIT 1;

    IF NOT FOUND THEN
        -- Create new rate limit window
        INSERT INTO auth_otp.rate_limits (email, request_count, window_start, window_end)
        VALUES (
            p_email,
            1,
            NOW(),
            NOW() + (p_window_minutes || ' minutes')::INTERVAL
        );

        RETURN jsonb_build_object(
            'allowed', true,
            'requests_remaining', p_max_requests - 1
        );
    END IF;

    -- Check if limit exceeded
    IF v_rate_limit.request_count >= p_max_requests THEN
        -- Block for 1 hour
        UPDATE auth_otp.rate_limits
        SET blocked_until = NOW() + INTERVAL '1 hour'
        WHERE id = v_rate_limit.id;

        RETURN jsonb_build_object(
            'allowed', false,
            'reason', 'rate_limit_exceeded',
            'blocked_until', NOW() + INTERVAL '1 hour',
            'retry_after_seconds', 3600
        );
    END IF;

    -- Increment request count
    UPDATE auth_otp.rate_limits
    SET request_count = request_count + 1
    WHERE id = v_rate_limit.id;

    RETURN jsonb_build_object(
        'allowed', true,
        'requests_remaining', p_max_requests - v_rate_limit.request_count - 1
    );
END;
$$;

-- Generate OTP Function
CREATE OR REPLACE FUNCTION auth_otp.generate_otp_code()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_otp TEXT;
BEGIN
    -- Generate 6-digit numeric OTP
    v_otp := LPAD(FLOOR(RANDOM() * 1000000)::TEXT, 6, '0');
    RETURN v_otp;
END;
$$;

-- Request OTP Function
CREATE OR REPLACE FUNCTION auth_otp.request_otp(
    p_email TEXT,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_rate_check JSONB;
    v_otp_code TEXT;
    v_otp_id UUID;
BEGIN
    -- Normalize email
    p_email := LOWER(TRIM(p_email));

    -- Check rate limit
    v_rate_check := auth_otp.check_rate_limit(p_email);

    IF NOT (v_rate_check->>'allowed')::BOOLEAN THEN
        -- Log rate limit hit
        INSERT INTO auth_otp.audit_log (email, action, success, ip_address, user_agent, metadata)
        VALUES (p_email, 'rate_limited', false, p_ip_address, p_user_agent, v_rate_check);

        RETURN v_rate_check;
    END IF;

    -- Invalidate any existing OTPs for this email
    UPDATE auth_otp.email_otps
    SET verified_at = NOW()
    WHERE email = p_email
      AND verified_at IS NULL
      AND expires_at > NOW();

    -- Generate new OTP
    v_otp_code := auth_otp.generate_otp_code();

    -- Store OTP
    INSERT INTO auth_otp.email_otps (email, otp_code, ip_address, user_agent)
    VALUES (p_email, v_otp_code, p_ip_address, p_user_agent)
    RETURNING id INTO v_otp_id;

    -- Log successful OTP request
    INSERT INTO auth_otp.audit_log (email, action, success, ip_address, user_agent, metadata)
    VALUES (p_email, 'request_otp', true, p_ip_address, p_user_agent, jsonb_build_object('otp_id', v_otp_id));

    RETURN jsonb_build_object(
        'success', true,
        'otp_id', v_otp_id,
        'otp_code', v_otp_code,
        'expires_at', NOW() + INTERVAL '10 minutes',
        'requests_remaining', v_rate_check->'requests_remaining'
    );
END;
$$;

-- Verify OTP Function
CREATE OR REPLACE FUNCTION auth_otp.verify_otp(
    p_email TEXT,
    p_otp_code TEXT,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_otp_record auth_otp.email_otps;
    v_user_id UUID;
BEGIN
    -- Normalize inputs
    p_email := LOWER(TRIM(p_email));
    p_otp_code := TRIM(p_otp_code);

    -- Find latest unverified OTP for this email
    SELECT * INTO v_otp_record
    FROM auth_otp.email_otps
    WHERE email = p_email
      AND verified_at IS NULL
      AND expires_at > NOW()
    ORDER BY created_at DESC
    LIMIT 1;

    IF NOT FOUND THEN
        -- Log invalid OTP attempt
        INSERT INTO auth_otp.audit_log (email, action, success, ip_address, user_agent, metadata)
        VALUES (p_email, 'verify_otp', false, p_ip_address, p_user_agent, jsonb_build_object('reason', 'no_active_otp'));

        RETURN jsonb_build_object(
            'success', false,
            'error', 'invalid_otp',
            'message', 'No active OTP found. Please request a new one.'
        );
    END IF;

    -- Check if max attempts exceeded
    IF v_otp_record.attempts >= v_otp_record.max_attempts THEN
        -- Invalidate OTP
        UPDATE auth_otp.email_otps
        SET verified_at = NOW()
        WHERE id = v_otp_record.id;

        -- Log max attempts exceeded
        INSERT INTO auth_otp.audit_log (email, action, success, ip_address, user_agent, metadata)
        VALUES (p_email, 'verify_otp', false, p_ip_address, p_user_agent, jsonb_build_object('reason', 'max_attempts_exceeded'));

        RETURN jsonb_build_object(
            'success', false,
            'error', 'max_attempts_exceeded',
            'message', 'Maximum verification attempts exceeded. Please request a new OTP.'
        );
    END IF;

    -- Increment attempt counter
    UPDATE auth_otp.email_otps
    SET attempts = attempts + 1
    WHERE id = v_otp_record.id;

    -- Verify OTP code
    IF v_otp_record.otp_code != p_otp_code THEN
        -- Log failed verification
        INSERT INTO auth_otp.audit_log (email, action, success, ip_address, user_agent, metadata)
        VALUES (p_email, 'verify_otp', false, p_ip_address, p_user_agent, jsonb_build_object('reason', 'invalid_code', 'attempts', v_otp_record.attempts + 1));

        RETURN jsonb_build_object(
            'success', false,
            'error', 'invalid_code',
            'message', 'Invalid OTP code.',
            'attempts_remaining', v_otp_record.max_attempts - v_otp_record.attempts - 1
        );
    END IF;

    -- Mark OTP as verified
    UPDATE auth_otp.email_otps
    SET verified_at = NOW()
    WHERE id = v_otp_record.id;

    -- Get or create user in auth.users
    SELECT id INTO v_user_id
    FROM auth.users
    WHERE email = p_email;

    IF NOT FOUND THEN
        -- Create new user (Supabase will handle this via signUp)
        -- For now, just return success and let Edge Function handle user creation
        v_user_id := NULL;
    END IF;

    -- Log successful verification
    INSERT INTO auth_otp.audit_log (email, action, success, ip_address, user_agent, metadata)
    VALUES (p_email, 'verify_otp', true, p_ip_address, p_user_agent, jsonb_build_object('otp_id', v_otp_record.id, 'user_id', v_user_id));

    RETURN jsonb_build_object(
        'success', true,
        'email', p_email,
        'user_id', v_user_id,
        'verified_at', NOW()
    );
END;
$$;

-- RLS Policies (service role only)
ALTER TABLE auth_otp.email_otps ENABLE ROW LEVEL SECURITY;
ALTER TABLE auth_otp.rate_limits ENABLE ROW LEVEL SECURITY;
ALTER TABLE auth_otp.audit_log ENABLE ROW LEVEL SECURITY;

-- Service role full access
CREATE POLICY service_role_all ON auth_otp.email_otps FOR ALL TO service_role USING (true);
CREATE POLICY service_role_all ON auth_otp.rate_limits FOR ALL TO service_role USING (true);
CREATE POLICY service_role_all ON auth_otp.audit_log FOR ALL TO service_role USING (true);

-- Grant permissions
GRANT USAGE ON SCHEMA auth_otp TO service_role;
GRANT ALL ON ALL TABLES IN SCHEMA auth_otp TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA auth_otp TO service_role;

-- Seed rate limit for testing (optional)
-- INSERT INTO auth_otp.rate_limits (email, request_count, window_start, window_end)
-- VALUES ('test@example.com', 0, NOW(), NOW() + INTERVAL '1 hour');

COMMENT ON SCHEMA auth_otp IS 'Email OTP authentication system - passwordless login';
COMMENT ON TABLE auth_otp.email_otps IS 'Stores time-limited OTP codes for email verification';
COMMENT ON TABLE auth_otp.rate_limits IS 'Rate limiting per email address (5 requests/hour)';
COMMENT ON TABLE auth_otp.audit_log IS 'Audit trail for all OTP operations';
COMMENT ON FUNCTION auth_otp.request_otp IS 'Generate and store OTP code for email (returns OTP for Edge Function to send via Mailgun)';
COMMENT ON FUNCTION auth_otp.verify_otp IS 'Verify OTP code and return success/failure';
COMMENT ON FUNCTION auth_otp.check_rate_limit IS 'Check if email is rate limited (5 requests/hour, 1 hour block on exceed)';
