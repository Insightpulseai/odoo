-- Migration: OdooOps Control Plane Schema - Remote Procedure Calls
-- Purpose: Add RPCs for run management, event logging, backups, and restores

-- Queue a new run for execution
CREATE OR REPLACE FUNCTION ops.queue_run(
    p_project_id TEXT,
    p_env TEXT,
    p_git_sha TEXT,
    p_git_ref TEXT,
    p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    run_id TEXT,
    status TEXT,
    queued_at TIMESTAMPTZ
) AS $$
DECLARE
    v_run_id TEXT;
    v_env_id TEXT;
BEGIN
    -- Validate project exists
    IF NOT EXISTS (SELECT 1 FROM ops.projects WHERE project_id = p_project_id) THEN
        RAISE EXCEPTION 'Project % does not exist', p_project_id;
    END IF;

    -- Get environment ID
    SELECT env_id INTO v_env_id
    FROM ops.environments
    WHERE project_id = p_project_id AND env_type = p_env;

    IF v_env_id IS NULL THEN
        RAISE EXCEPTION 'Environment % not found for project %', p_env, p_project_id;
    END IF;

    -- Generate run ID
    v_run_id := 'run-' || gen_random_uuid()::text;

    -- Insert run
    INSERT INTO ops.runs (
        run_id,
        project_id,
        env_id,
        git_sha,
        git_ref,
        status,
        metadata
    ) VALUES (
        v_run_id,
        p_project_id,
        v_env_id,
        p_git_sha,
        p_git_ref,
        'queued',
        p_metadata
    );

    -- Log event
    INSERT INTO ops.run_events (run_id, level, message, payload)
    VALUES (v_run_id, 'info', 'Run queued', jsonb_build_object(
        'git_sha', p_git_sha,
        'git_ref', p_git_ref,
        'env', p_env
    ));

    -- Return run details
    RETURN QUERY
    SELECT r.run_id, r.status, r.queued_at
    FROM ops.runs r
    WHERE r.run_id = v_run_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION ops.queue_run IS 'Queue a new build/deploy run for execution';

-- Claim next queued run for execution
CREATE OR REPLACE FUNCTION ops.claim_next_run(
    p_worker_id TEXT
)
RETURNS TABLE (
    run_id TEXT,
    project_id TEXT,
    env_id TEXT,
    git_sha TEXT,
    git_ref TEXT,
    metadata JSONB
) AS $$
DECLARE
    v_run_id TEXT;
BEGIN
    -- Find and claim next queued run (with row-level locking)
    SELECT r.run_id INTO v_run_id
    FROM ops.runs r
    WHERE r.status = 'queued'
    ORDER BY r.queued_at
    LIMIT 1
    FOR UPDATE SKIP LOCKED;

    IF v_run_id IS NULL THEN
        RETURN;
    END IF;

    -- Claim the run
    UPDATE ops.runs
    SET status = 'claimed',
        claimed_by = p_worker_id,
        started_at = NOW(),
        updated_at = NOW()
    WHERE ops.runs.run_id = v_run_id;

    -- Log event
    INSERT INTO ops.run_events (run_id, level, message, payload)
    VALUES (v_run_id, 'info', 'Run claimed by worker', jsonb_build_object(
        'worker_id', p_worker_id
    ));

    -- Return claimed run
    RETURN QUERY
    SELECT r.run_id, r.project_id, r.env_id, r.git_sha, r.git_ref, r.metadata
    FROM ops.runs r
    WHERE r.run_id = v_run_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION ops.claim_next_run IS 'Claim next queued run for worker execution';

-- Append event to run log
CREATE OR REPLACE FUNCTION ops.append_event(
    p_run_id TEXT,
    p_level TEXT,
    p_message TEXT,
    p_payload JSONB DEFAULT '{}'::jsonb
)
RETURNS TEXT AS $$
DECLARE
    v_event_id TEXT;
BEGIN
    -- Validate run exists
    IF NOT EXISTS (SELECT 1 FROM ops.runs WHERE run_id = p_run_id) THEN
        RAISE EXCEPTION 'Run % does not exist', p_run_id;
    END IF;

    -- Validate level
    IF p_level NOT IN ('debug', 'info', 'warn', 'error') THEN
        RAISE EXCEPTION 'Invalid log level: %', p_level;
    END IF;

    -- Insert event
    INSERT INTO ops.run_events (run_id, level, message, payload)
    VALUES (p_run_id, p_level, p_message, p_payload)
    RETURNING event_id INTO v_event_id;

    -- Update run status to 'running' if still 'claimed'
    UPDATE ops.runs
    SET status = 'running',
        updated_at = NOW()
    WHERE run_id = p_run_id
      AND status = 'claimed';

    RETURN v_event_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION ops.append_event IS 'Append log event to run execution';

-- Finish run with final status
CREATE OR REPLACE FUNCTION ops.finish_run(
    p_run_id TEXT,
    p_status TEXT,
    p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS BOOLEAN AS $$
BEGIN
    -- Validate run exists
    IF NOT EXISTS (SELECT 1 FROM ops.runs WHERE run_id = p_run_id) THEN
        RAISE EXCEPTION 'Run % does not exist', p_run_id;
    END IF;

    -- Validate status
    IF p_status NOT IN ('success', 'failed', 'cancelled') THEN
        RAISE EXCEPTION 'Invalid final status: %', p_status;
    END IF;

    -- Update run
    UPDATE ops.runs
    SET status = p_status,
        finished_at = NOW(),
        updated_at = NOW(),
        metadata = ops.runs.metadata || p_metadata
    WHERE run_id = p_run_id;

    -- Log event
    INSERT INTO ops.run_events (run_id, level, message, payload)
    VALUES (
        p_run_id,
        CASE WHEN p_status = 'success' THEN 'info' ELSE 'error' END,
        'Run finished: ' || p_status,
        p_metadata
    );

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION ops.finish_run IS 'Mark run as complete with final status';

-- Create backup for project environment
CREATE OR REPLACE FUNCTION ops.create_backup(
    p_project_id TEXT,
    p_env TEXT,
    p_backup_type TEXT DEFAULT 'manual',
    p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    backup_id TEXT,
    created_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ
) AS $$
DECLARE
    v_backup_id TEXT;
    v_env_id TEXT;
BEGIN
    -- Validate project exists
    IF NOT EXISTS (SELECT 1 FROM ops.projects WHERE project_id = p_project_id) THEN
        RAISE EXCEPTION 'Project % does not exist', p_project_id;
    END IF;

    -- Get environment ID
    SELECT env_id INTO v_env_id
    FROM ops.environments
    WHERE project_id = p_project_id AND env_type = p_env;

    IF v_env_id IS NULL THEN
        RAISE EXCEPTION 'Environment % not found for project %', p_env, p_project_id;
    END IF;

    -- Validate backup type
    IF p_backup_type NOT IN ('daily', 'weekly', 'monthly', 'manual') THEN
        RAISE EXCEPTION 'Invalid backup type: %', p_backup_type;
    END IF;

    -- Generate backup ID
    v_backup_id := 'bak-' || gen_random_uuid()::text;

    -- Insert backup record (trigger will set expiration)
    INSERT INTO ops.backups (
        backup_id,
        project_id,
        env_id,
        backup_type,
        db_dump_path,
        metadata
    ) VALUES (
        v_backup_id,
        p_project_id,
        v_env_id,
        p_backup_type,
        'pending',  -- Will be updated by backup worker
        p_metadata
    );

    -- Return backup details
    RETURN QUERY
    SELECT b.backup_id, b.created_at, b.expires_at
    FROM ops.backups b
    WHERE b.backup_id = v_backup_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION ops.create_backup IS 'Create backup record for project environment';

-- Restore backup to target environment
CREATE OR REPLACE FUNCTION ops.restore_backup(
    p_backup_id TEXT,
    p_target_env_id TEXT,
    p_requested_by TEXT,
    p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    restore_id TEXT,
    status TEXT,
    created_at TIMESTAMPTZ
) AS $$
DECLARE
    v_restore_id TEXT;
    v_backup_exists BOOLEAN;
    v_env_exists BOOLEAN;
    v_env_type TEXT;
    v_project_id TEXT;
BEGIN
    -- Validate backup exists
    SELECT EXISTS (SELECT 1 FROM ops.backups WHERE backup_id = p_backup_id)
    INTO v_backup_exists;

    IF NOT v_backup_exists THEN
        RAISE EXCEPTION 'Backup % does not exist', p_backup_id;
    END IF;

    -- Validate target environment exists and get type
    SELECT EXISTS (SELECT 1 FROM ops.environments WHERE env_id = p_target_env_id),
           env_type,
           project_id
    INTO v_env_exists, v_env_type, v_project_id
    FROM ops.environments
    WHERE env_id = p_target_env_id;

    IF NOT v_env_exists THEN
        RAISE EXCEPTION 'Target environment % does not exist', p_target_env_id;
    END IF;

    -- Generate restore ID
    v_restore_id := 'rst-' || gen_random_uuid()::text;

    -- Determine initial status (prod requires approval)
    INSERT INTO ops.restores (
        restore_id,
        backup_id,
        target_env_id,
        status,
        requested_by,
        metadata
    ) VALUES (
        v_restore_id,
        p_backup_id,
        p_target_env_id,
        CASE WHEN v_env_type = 'prod' THEN 'pending' ELSE 'approved' END,
        p_requested_by,
        p_metadata
    );

    -- Create approval record if production
    IF v_env_type = 'prod' THEN
        INSERT INTO ops.approvals (
            approval_type,
            resource_id,
            requested_by,
            status,
            metadata
        ) VALUES (
            'restore_prod',
            v_restore_id,
            p_requested_by,
            'pending',
            jsonb_build_object(
                'backup_id', p_backup_id,
                'target_env_id', p_target_env_id,
                'project_id', v_project_id
            )
        );
    END IF;

    -- Return restore details
    RETURN QUERY
    SELECT r.restore_id, r.status, r.created_at
    FROM ops.restores r
    WHERE r.restore_id = v_restore_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION ops.restore_backup IS 'Restore backup to target environment with approval workflow';

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION ops.queue_run TO authenticated;
GRANT EXECUTE ON FUNCTION ops.claim_next_run TO authenticated;
GRANT EXECUTE ON FUNCTION ops.append_event TO authenticated;
GRANT EXECUTE ON FUNCTION ops.finish_run TO authenticated;
GRANT EXECUTE ON FUNCTION ops.create_backup TO authenticated;
GRANT EXECUTE ON FUNCTION ops.restore_backup TO authenticated;
