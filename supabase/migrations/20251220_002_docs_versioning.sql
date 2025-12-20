-- =============================================================================
-- DOCS PLATFORM: VERSIONING EXTENSIONS
-- =============================================================================
-- Adds version lineage tracking to existing RAG document tables
-- Supports release channels, breaking changes, and deprecation trails
-- =============================================================================

-- =============================================================================
-- EXTEND RAG.DOCUMENT_VERSIONS (if exists)
-- =============================================================================

-- Add versioning columns if rag.document_versions exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'rag' AND table_name = 'document_versions'
    ) THEN
        -- Add release_channel if not exists
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'rag'
            AND table_name = 'document_versions'
            AND column_name = 'release_channel'
        ) THEN
            ALTER TABLE rag.document_versions
            ADD COLUMN release_channel TEXT DEFAULT 'stable';

            ALTER TABLE rag.document_versions
            ADD CONSTRAINT check_release_channel
            CHECK (release_channel IN ('edge', 'stable', 'lts', 'deprecated'));
        END IF;

        -- Add is_breaking if not exists
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'rag'
            AND table_name = 'document_versions'
            AND column_name = 'is_breaking'
        ) THEN
            ALTER TABLE rag.document_versions
            ADD COLUMN is_breaking BOOLEAN DEFAULT false;
        END IF;

        -- Add is_deprecated if not exists
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'rag'
            AND table_name = 'document_versions'
            AND column_name = 'is_deprecated'
        ) THEN
            ALTER TABLE rag.document_versions
            ADD COLUMN is_deprecated BOOLEAN DEFAULT false;
        END IF;

        -- Add successor_id if not exists
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'rag'
            AND table_name = 'document_versions'
            AND column_name = 'successor_id'
        ) THEN
            ALTER TABLE rag.document_versions
            ADD COLUMN successor_id UUID REFERENCES rag.document_versions(id);
        END IF;

        RAISE NOTICE 'Extended rag.document_versions with versioning columns';
    ELSE
        RAISE NOTICE 'rag.document_versions does not exist, skipping extension';
    END IF;
END;
$$;

-- =============================================================================
-- VERSION HISTORY VIEW
-- =============================================================================

CREATE OR REPLACE VIEW docs.v_version_lineage AS
WITH RECURSIVE lineage AS (
    -- Base case: documents without successors
    SELECT
        dm.doc_id,
        dm.doc_id as root_id,
        dm.version,
        dm.release_channel,
        dm.is_deprecated,
        dm.successor_id,
        1 as generation,
        ARRAY[dm.doc_id] as version_path
    FROM docs.doc_metadata dm
    WHERE dm.successor_id IS NULL

    UNION ALL

    -- Recursive case: find predecessors
    SELECT
        dm.doc_id,
        l.root_id,
        dm.version,
        dm.release_channel,
        dm.is_deprecated,
        dm.successor_id,
        l.generation + 1,
        dm.doc_id || l.version_path
    FROM docs.doc_metadata dm
    JOIN lineage l ON dm.successor_id = l.doc_id
    WHERE NOT dm.doc_id = ANY(l.version_path)  -- Prevent cycles
)
SELECT * FROM lineage;

-- =============================================================================
-- DEPRECATION HELPER FUNCTIONS
-- =============================================================================

-- Mark a document as deprecated with successor
CREATE OR REPLACE FUNCTION docs.deprecate_document(
    p_doc_id UUID,
    p_successor_id UUID,
    p_reason TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
BEGIN
    -- Validate successor exists and is not deprecated
    IF NOT EXISTS (
        SELECT 1 FROM docs.doc_metadata
        WHERE doc_id = p_successor_id AND is_deprecated = false
    ) THEN
        RAISE EXCEPTION 'Successor document % does not exist or is deprecated', p_successor_id;
    END IF;

    -- Mark as deprecated
    UPDATE docs.doc_metadata
    SET
        is_deprecated = true,
        release_channel = 'deprecated',
        successor_id = p_successor_id,
        updated_at = now()
    WHERE doc_id = p_doc_id;

    -- Add relationship
    INSERT INTO docs.related_docs (source_id, target_id, relationship, weight)
    VALUES (p_successor_id, p_doc_id, 'supersedes', 1.0)
    ON CONFLICT (source_id, target_id, relationship) DO NOTHING;

    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- Get current (non-deprecated) version of a document
CREATE OR REPLACE FUNCTION docs.get_current_version(p_doc_id UUID)
RETURNS UUID AS $$
DECLARE
    v_current UUID := p_doc_id;
    v_successor UUID;
    v_depth INTEGER := 0;
BEGIN
    LOOP
        SELECT successor_id INTO v_successor
        FROM docs.doc_metadata
        WHERE doc_id = v_current;

        EXIT WHEN v_successor IS NULL;

        v_current := v_successor;
        v_depth := v_depth + 1;

        -- Safety limit to prevent infinite loops
        IF v_depth > 100 THEN
            RAISE EXCEPTION 'Circular successor reference detected for document %', p_doc_id;
        END IF;
    END LOOP;

    RETURN v_current;
END;
$$ LANGUAGE plpgsql STABLE;

-- =============================================================================
-- RELEASE CHANNEL TRANSITIONS
-- =============================================================================

-- Promote a document through release channels
CREATE OR REPLACE FUNCTION docs.promote_release_channel(
    p_doc_id UUID,
    p_target_channel TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_channel TEXT;
BEGIN
    SELECT release_channel INTO v_current_channel
    FROM docs.doc_metadata
    WHERE doc_id = p_doc_id;

    IF v_current_channel IS NULL THEN
        RAISE EXCEPTION 'Document % not found', p_doc_id;
    END IF;

    -- Validate promotion path: edge -> stable -> lts
    IF p_target_channel = 'stable' AND v_current_channel != 'edge' THEN
        RAISE EXCEPTION 'Can only promote to stable from edge';
    ELSIF p_target_channel = 'lts' AND v_current_channel != 'stable' THEN
        RAISE EXCEPTION 'Can only promote to lts from stable';
    ELSIF p_target_channel = 'edge' THEN
        RAISE EXCEPTION 'Cannot demote to edge';
    END IF;

    UPDATE docs.doc_metadata
    SET
        release_channel = p_target_channel,
        updated_at = now()
    WHERE doc_id = p_doc_id;

    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- BREAKING CHANGE NOTIFICATIONS
-- =============================================================================

-- Table to track breaking change acknowledgments
CREATE TABLE IF NOT EXISTS docs.breaking_change_acks (
    doc_id UUID NOT NULL,
    user_id TEXT NOT NULL,
    acknowledged_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (doc_id, user_id)
);

-- Get unacknowledged breaking changes for a user
CREATE OR REPLACE FUNCTION docs.get_breaking_changes(
    p_user_id TEXT,
    p_product TEXT DEFAULT NULL
)
RETURNS TABLE(
    doc_id UUID,
    product TEXT,
    version TEXT,
    release_channel TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        dm.doc_id,
        dm.product,
        dm.version,
        dm.release_channel
    FROM docs.doc_metadata dm
    WHERE dm.is_breaking = true
      AND dm.is_deprecated = false
      AND (p_product IS NULL OR dm.product = p_product)
      AND NOT EXISTS (
          SELECT 1 FROM docs.breaking_change_acks bca
          WHERE bca.doc_id = dm.doc_id AND bca.user_id = p_user_id
      )
    ORDER BY dm.updated_at DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- =============================================================================
-- VERSION DIFF SUPPORT
-- =============================================================================

-- Store version diffs for changelog generation
CREATE TABLE IF NOT EXISTS docs.version_diffs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_doc_id UUID NOT NULL,
    target_doc_id UUID NOT NULL,
    diff_type TEXT NOT NULL,
    diff_summary TEXT,
    diff_details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT valid_diff_type CHECK (diff_type IN (
        'content', 'metadata', 'taxonomy', 'breaking'
    ))
);

CREATE INDEX idx_version_diffs_source ON docs.version_diffs(source_doc_id);
CREATE INDEX idx_version_diffs_target ON docs.version_diffs(target_doc_id);

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Docs versioning schema created';
END;
$$;
