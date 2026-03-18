-- Phase 6: Agent Orchestration Schema
-- Create tables for agent definitions and flows before seeding

CREATE TABLE IF NOT EXISTS agent_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    input_schema JSONB DEFAULT '{}'::jsonb,
    output_schema JSONB DEFAULT '{}'::jsonb,
    prompt_template TEXT,
    model TEXT DEFAULT 'default',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_flows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    flow JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_agent_definitions_name ON agent_definitions(name);
CREATE INDEX IF NOT EXISTS idx_agent_flows_name ON agent_flows(name);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_agent_definitions_updated_at BEFORE UPDATE ON agent_definitions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_flows_updated_at BEFORE UPDATE ON agent_flows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
