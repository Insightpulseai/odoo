-- =============================================================================
-- DRAW.IO ASSESSMENT TASKS & CERTIFICATION LEVELS
-- =============================================================================
-- Practical tasks for Draw.io skill certification at each level
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Draw.io Specific Certification Levels
-- (These extend the base certification_levels in skills schema)
-- -----------------------------------------------------------------------------

-- Note: Using skill_evaluations for certification tracking
-- Tasks are stored as JSON in skill_criteria details

-- -----------------------------------------------------------------------------
-- Assessment Tasks Table (Extends skills schema)
-- -----------------------------------------------------------------------------

-- Create assessment_tasks table if not exists
CREATE TABLE IF NOT EXISTS skills.assessment_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_key TEXT NOT NULL UNIQUE,
    skill_id UUID NOT NULL REFERENCES skills.skill_definitions(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    difficulty TEXT NOT NULL,                -- 'beginner', 'intermediate', 'advanced', 'expert'
    time_limit_minutes INT NOT NULL,
    assessment_type TEXT NOT NULL DEFAULT 'practical',  -- 'practical', 'written', 'portfolio'
    artifacts_required TEXT[] NOT NULL,
    rubric JSONB NOT NULL,
    passing_score INT NOT NULL,
    instructions_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_difficulty CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert', 'instructor'))
);

COMMENT ON TABLE skills.assessment_tasks IS 'Practical assessment tasks for skill certification';

CREATE INDEX IF NOT EXISTS idx_assessment_tasks_skill ON skills.assessment_tasks(skill_id);
CREATE INDEX IF NOT EXISTS idx_assessment_tasks_difficulty ON skills.assessment_tasks(difficulty);

-- RLS for assessment_tasks
ALTER TABLE skills.assessment_tasks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access on assessment_tasks"
    ON skills.assessment_tasks FOR ALL TO service_role USING (true);
CREATE POLICY "Authenticated users can read assessment_tasks"
    ON skills.assessment_tasks FOR SELECT TO authenticated USING (true);

-- -----------------------------------------------------------------------------
-- Beginner Level Tasks
-- -----------------------------------------------------------------------------

-- Task: Simple Flowchart
INSERT INTO skills.assessment_tasks (task_key, skill_id, name, description, difficulty, time_limit_minutes, assessment_type, artifacts_required, rubric, passing_score, instructions_url)
SELECT
    'task_drawio_beginner_001',
    id,
    'Create a Simple Flowchart',
    'Create a 5-step process flowchart using standard ISO 5807 symbols. The flowchart should represent a common business process like order fulfillment or user registration.',
    'beginner',
    30,
    'practical',
    ARRAY['.drawio XML file', 'PNG export', 'Brief description (100 words)'],
    '[
        {"criterion": "Correct shape usage", "max_score": 5, "description": "Uses appropriate flowchart symbols (terminal, process, decision, connector)"},
        {"criterion": "Proper flow direction", "max_score": 5, "description": "Flow follows logical top-to-bottom or left-to-right direction"},
        {"criterion": "Clear labeling", "max_score": 5, "description": "All shapes have clear, descriptive labels"},
        {"criterion": "Professional appearance", "max_score": 5, "description": "Clean layout with consistent spacing and alignment"}
    ]'::jsonb,
    14,
    '/tasks/beginner/simple-flowchart'
FROM skills.skill_definitions WHERE slug = 'drawio-fundamentals'
ON CONFLICT (task_key) DO NOTHING;

-- Task: Organization Chart
INSERT INTO skills.assessment_tasks (task_key, skill_id, name, description, difficulty, time_limit_minutes, assessment_type, artifacts_required, rubric, passing_score, instructions_url)
SELECT
    'task_drawio_beginner_002',
    id,
    'Design an Organization Chart',
    'Create an organizational chart with 8+ positions showing reporting structure. Include at least 3 levels of hierarchy.',
    'beginner',
    25,
    'practical',
    ARRAY['.drawio XML file', 'PNG export'],
    '[
        {"criterion": "Hierarchical structure clarity", "max_score": 5, "description": "Clear visual hierarchy showing reporting relationships"},
        {"criterion": "Alignment & spacing", "max_score": 5, "description": "Even spacing and proper alignment of elements"},
        {"criterion": "Labels completeness", "max_score": 5, "description": "All positions labeled with titles and names"}
    ]'::jsonb,
    11,
    '/tasks/beginner/org-chart'
FROM skills.skill_definitions WHERE slug = 'drawio-fundamentals'
ON CONFLICT (task_key) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Intermediate (Practitioner) Level Tasks
-- -----------------------------------------------------------------------------

-- Task: AWS Architecture Design
INSERT INTO skills.assessment_tasks (task_key, skill_id, name, description, difficulty, time_limit_minutes, assessment_type, artifacts_required, rubric, passing_score, instructions_url)
SELECT
    'task_drawio_practitioner_001',
    id,
    'Design 3-Tier AWS Architecture',
    'Design a 3-tier AWS architecture with VPC, public/private subnets, security groups, ALB, EC2/ECS, RDS, and S3. Show proper icon usage and network boundaries.',
    'intermediate',
    60,
    'practical',
    ARRAY['.drawio XML file', 'SVG export', 'Architecture description (300 words)'],
    '[
        {"criterion": "Correct AWS symbols", "max_score": 5, "description": "Uses official AWS architecture icons correctly"},
        {"criterion": "VPC/subnet design", "max_score": 5, "description": "Proper VPC structure with public/private subnets"},
        {"criterion": "Security groups", "max_score": 5, "description": "Security groups shown with correct placement"},
        {"criterion": "Documentation quality", "max_score": 5, "description": "Clear written explanation of architecture decisions"}
    ]'::jsonb,
    16,
    '/tasks/practitioner/aws-architecture'
FROM skills.skill_definitions WHERE slug = 'aws-architecture-diagramming'
ON CONFLICT (task_key) DO NOTHING;

-- Task: BPMN Process Model
INSERT INTO skills.assessment_tasks (task_key, skill_id, name, description, difficulty, time_limit_minutes, assessment_type, artifacts_required, rubric, passing_score, instructions_url)
SELECT
    'task_drawio_practitioner_002',
    id,
    'Model BPMN 2.0 Approval Process',
    'Create a BPMN 2.0 diagram for a multi-stage approval workflow with parallel gateways, subprocess, and error handling. Must include pools, lanes, and message flows.',
    'intermediate',
    75,
    'practical',
    ARRAY['.drawio XML file', 'PNG export', 'Process narrative (200 words)'],
    '[
        {"criterion": "BPMN 2.0 compliance", "max_score": 5, "description": "Correct BPMN element usage per specification"},
        {"criterion": "Gateway logic", "max_score": 5, "description": "Proper use of exclusive, parallel, inclusive gateways"},
        {"criterion": "Process completeness", "max_score": 5, "description": "All paths have proper start and end events"},
        {"criterion": "Readability", "max_score": 5, "description": "Clear organization with proper use of lanes and pools"}
    ]'::jsonb,
    16,
    '/tasks/practitioner/bpmn-approval'
FROM skills.skill_definitions WHERE slug = 'bpmn-process-modeling'
ON CONFLICT (task_key) DO NOTHING;

-- Task: UML Class Diagram
INSERT INTO skills.assessment_tasks (task_key, skill_id, name, description, difficulty, time_limit_minutes, assessment_type, artifacts_required, rubric, passing_score, instructions_url)
SELECT
    'task_drawio_practitioner_003',
    id,
    'UML Class Diagram for E-Commerce System',
    'Create a UML class diagram for an e-commerce system with at least 8 classes showing inheritance, composition, aggregation, and associations. Include methods and attributes.',
    'intermediate',
    60,
    'practical',
    ARRAY['.drawio XML file', 'PDF export', 'Design rationale (300 words)'],
    '[
        {"criterion": "UML notation accuracy", "max_score": 5, "description": "Correct UML class diagram notation"},
        {"criterion": "Relationship correctness", "max_score": 5, "description": "Proper use of inheritance, composition, aggregation"},
        {"criterion": "Design quality", "max_score": 5, "description": "Good OOP principles (SRP, DRY, etc.)"},
        {"criterion": "Clarity", "max_score": 5, "description": "Easy to read and understand"}
    ]'::jsonb,
    16,
    '/tasks/practitioner/uml-ecommerce'
FROM skills.skill_definitions WHERE slug = 'uml-diagram-design'
ON CONFLICT (task_key) DO NOTHING;

-- Task: ERD Database Design
INSERT INTO skills.assessment_tasks (task_key, skill_id, name, description, difficulty, time_limit_minutes, assessment_type, artifacts_required, rubric, passing_score, instructions_url)
SELECT
    'task_drawio_practitioner_004',
    id,
    'ERD for Multi-Tenant SaaS Application',
    'Design an ERD for a multi-tenant SaaS application with user management, subscriptions, and audit logging. Show 10+ tables with proper normalization.',
    'intermediate',
    60,
    'practical',
    ARRAY['.drawio XML file', 'PNG export', 'Schema description'],
    '[
        {"criterion": "Notation correctness", "max_score": 5, "description": "Correct Crow''s Foot or Chen notation"},
        {"criterion": "Cardinality accuracy", "max_score": 5, "description": "Accurate relationship cardinalities"},
        {"criterion": "Normalization", "max_score": 5, "description": "Proper 3NF normalization"},
        {"criterion": "Keys/constraints", "max_score": 5, "description": "Clear primary/foreign keys and constraints"}
    ]'::jsonb,
    16,
    '/tasks/practitioner/erd-saas'
FROM skills.skill_definitions WHERE slug = 'erd-database-design'
ON CONFLICT (task_key) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Advanced Level Tasks
-- -----------------------------------------------------------------------------

-- Task: Complete C4 Model
INSERT INTO skills.assessment_tasks (task_key, skill_id, name, description, difficulty, time_limit_minutes, assessment_type, artifacts_required, rubric, passing_score, instructions_url)
SELECT
    'task_drawio_advanced_001',
    id,
    'Complete C4 Model Documentation',
    'Create all 4 levels of C4 model (Context, Container, Component, Code) for a microservices-based banking application. Include at least 3 microservices.',
    'advanced',
    180,
    'practical',
    ARRAY['4 linked .drawio files', 'SVG/PDF exports', 'Architecture Decision Record', 'README.md'],
    '[
        {"criterion": "C4 completeness", "max_score": 5, "description": "All 4 levels present and complete"},
        {"criterion": "Consistency", "max_score": 5, "description": "Consistent naming and styling across levels"},
        {"criterion": "Technical accuracy", "max_score": 5, "description": "Realistic and implementable architecture"},
        {"criterion": "Audience clarity", "max_score": 5, "description": "Appropriate detail for each audience level"},
        {"criterion": "ADR quality", "max_score": 5, "description": "Well-documented decisions with rationale"}
    ]'::jsonb,
    22,
    '/tasks/advanced/c4-banking'
FROM skills.skill_definitions WHERE slug = 'c4-model-architecture'
ON CONFLICT (task_key) DO NOTHING;

-- Task: Multi-Region DR Architecture
INSERT INTO skills.assessment_tasks (task_key, skill_id, name, description, difficulty, time_limit_minutes, assessment_type, artifacts_required, rubric, passing_score, instructions_url)
SELECT
    'task_drawio_advanced_002',
    id,
    'Multi-Region Disaster Recovery Architecture',
    'Design a multi-region (3+ regions) disaster recovery architecture for a global e-commerce platform. Include RTO/RPO requirements, failover mechanisms, and cost considerations.',
    'advanced',
    120,
    'practical',
    ARRAY['.drawio XML file', 'Deployment guide', 'Cost analysis', 'Failover runbook'],
    '[
        {"criterion": "Regional replication", "max_score": 5, "description": "Proper data replication strategy across regions"},
        {"criterion": "Failover mechanism", "max_score": 5, "description": "Clear failover process with DNS/traffic management"},
        {"criterion": "Network design", "max_score": 5, "description": "Proper VPC peering and cross-region connectivity"},
        {"criterion": "Cost optimization", "max_score": 5, "description": "Cost-effective architecture with clear tradeoffs"},
        {"criterion": "Security", "max_score": 5, "description": "Security maintained across all regions"}
    ]'::jsonb,
    22,
    '/tasks/advanced/multi-region-dr'
FROM skills.skill_definitions WHERE slug = 'multi-cloud-architecture'
ON CONFLICT (task_key) DO NOTHING;

-- Task: Enterprise Template Library
INSERT INTO skills.assessment_tasks (task_key, skill_id, name, description, difficulty, time_limit_minutes, assessment_type, artifacts_required, rubric, passing_score, instructions_url)
SELECT
    'task_drawio_advanced_003',
    id,
    'Enterprise Diagram Template Library',
    'Create a reusable enterprise template library with 10+ custom shapes, 3 templates, and comprehensive style guide for organizational adoption.',
    'advanced',
    120,
    'practical',
    ARRAY['Custom shape library (.xml)', '3 template files', 'Style guide (PDF)', 'Training deck', 'README.md'],
    '[
        {"criterion": "Shape design quality", "max_score": 5, "description": "Professional, consistent custom shapes"},
        {"criterion": "Template reusability", "max_score": 5, "description": "Templates are versatile and parameterized"},
        {"criterion": "Style guide completeness", "max_score": 5, "description": "Comprehensive style guide with examples"},
        {"criterion": "Documentation clarity", "max_score": 5, "description": "Clear usage documentation"},
        {"criterion": "Training effectiveness", "max_score": 5, "description": "Training materials enable quick adoption"}
    ]'::jsonb,
    22,
    '/tasks/advanced/template-library'
FROM skills.skill_definitions WHERE slug = 'drawio-template-library'
ON CONFLICT (task_key) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Expert Level Tasks
-- -----------------------------------------------------------------------------

-- Task: Automated Infrastructure Diagramming
INSERT INTO skills.assessment_tasks (task_key, skill_id, name, description, difficulty, time_limit_minutes, assessment_type, artifacts_required, rubric, passing_score, instructions_url)
SELECT
    'task_drawio_expert_001',
    id,
    'Automated Infrastructure Diagram Generation',
    'Design a system that auto-generates draw.io diagrams from cloud API or IaC (Terraform/CloudFormation). Include data binding, auto-refresh, and CI/CD integration.',
    'expert',
    240,
    'practical',
    ARRAY['Automation scripts (Python/Node)', 'Template files', 'Data binding config', 'Live demo video', 'Documentation'],
    '[
        {"criterion": "Automation completeness", "max_score": 5, "description": "End-to-end automation from source to diagram"},
        {"criterion": "Real-time accuracy", "max_score": 5, "description": "Diagrams accurately reflect current infrastructure"},
        {"criterion": "Template flexibility", "max_score": 5, "description": "Templates handle diverse infrastructure patterns"},
        {"criterion": "System reliability", "max_score": 5, "description": "Robust error handling and retry logic"},
        {"criterion": "Documentation", "max_score": 5, "description": "Comprehensive setup and usage documentation"}
    ]'::jsonb,
    23,
    '/tasks/expert/auto-diagramming'
FROM skills.skill_definitions WHERE slug = 'drawio-dynamic-data'
ON CONFLICT (task_key) DO NOTHING;

-- Task: Enterprise Governance Framework
INSERT INTO skills.assessment_tasks (task_key, skill_id, name, description, difficulty, time_limit_minutes, assessment_type, artifacts_required, rubric, passing_score, instructions_url)
SELECT
    'task_drawio_expert_002',
    id,
    'Enterprise Architecture Governance Framework',
    'Design a complete architecture governance framework with diagram standards, review processes, templates (25+ shapes), and compliance checklists.',
    'expert',
    180,
    'practical',
    ARRAY['Standards document', 'Template library (25+ shapes)', 'Review process diagrams', 'Compliance checklists', 'Training program'],
    '[
        {"criterion": "Standards completeness", "max_score": 5, "description": "Comprehensive standards covering all diagram types"},
        {"criterion": "Template coverage", "max_score": 5, "description": "Templates for all common architecture patterns"},
        {"criterion": "Process efficiency", "max_score": 5, "description": "Review process is streamlined and effective"},
        {"criterion": "Scalability", "max_score": 5, "description": "Framework scales to large organizations"},
        {"criterion": "Adoption enablement", "max_score": 5, "description": "Clear path to organizational adoption"}
    ]'::jsonb,
    23,
    '/tasks/expert/governance-framework'
FROM skills.skill_definitions WHERE slug = 'archimate-enterprise'
ON CONFLICT (task_key) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Instructor Level Tasks
-- -----------------------------------------------------------------------------

-- Task: Design & Deliver Course
INSERT INTO skills.assessment_tasks (task_key, skill_id, name, description, difficulty, time_limit_minutes, assessment_type, artifacts_required, rubric, passing_score, instructions_url)
SELECT
    'task_drawio_instructor_001',
    id,
    'Design & Deliver Draw.io Training Course',
    'Create and deliver a complete Draw.io training curriculum. Train at least 10 students through the beginner and practitioner levels.',
    'instructor',
    NULL,  -- No time limit for instructor tasks
    'portfolio',
    ARRAY['Curriculum (50+ pages)', '10 lesson plans', 'Exercise materials', 'Assessment rubrics', 'Student feedback analysis', 'Completion certificates'],
    '[
        {"criterion": "Curriculum completeness", "max_score": 5, "description": "Covers all foundational and intermediate topics"},
        {"criterion": "Lesson quality", "max_score": 5, "description": "Engaging, well-structured lesson plans"},
        {"criterion": "Exercise effectiveness", "max_score": 5, "description": "Hands-on exercises reinforce learning"},
        {"criterion": "Student outcomes", "max_score": 5, "description": "Students achieve learning objectives (avg score)"},
        {"criterion": "Production quality", "max_score": 5, "description": "Professional-quality materials"}
    ]'::jsonb,
    24,
    '/tasks/instructor/training-course'
FROM skills.skill_definitions WHERE slug = 'drawio-collaboration'
ON CONFLICT (task_key) DO NOTHING;

-- Task: Certification Administration
INSERT INTO skills.assessment_tasks (task_key, skill_id, name, description, difficulty, time_limit_minutes, assessment_type, artifacts_required, rubric, passing_score, instructions_url)
SELECT
    'task_drawio_instructor_002',
    id,
    'Administer Certification Program',
    'Administer and evaluate certifications for 5+ candidates at practitioner level or above. Provide detailed feedback and improvement recommendations.',
    'instructor',
    NULL,
    'portfolio',
    ARRAY['5+ candidate portfolios', 'Detailed feedback reports', 'Applied assessment rubrics', 'Program documentation', 'Improvement recommendations'],
    '[
        {"criterion": "Assessment fairness", "max_score": 5, "description": "Consistent, unbiased evaluation across candidates"},
        {"criterion": "Feedback quality", "max_score": 5, "description": "Actionable, constructive feedback"},
        {"criterion": "Grading accuracy", "max_score": 5, "description": "Accurate scoring verified by cross-review"},
        {"criterion": "Documentation", "max_score": 5, "description": "Complete documentation of all assessments"}
    ]'::jsonb,
    18,
    '/tasks/instructor/cert-admin'
FROM skills.skill_definitions WHERE slug = 'drawio-collaboration'
ON CONFLICT (task_key) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Verification
-- -----------------------------------------------------------------------------

-- Verify assessment tasks
SELECT
    at.task_key,
    sd.slug AS skill_slug,
    at.difficulty,
    at.time_limit_minutes,
    at.passing_score,
    jsonb_array_length(at.rubric) AS criteria_count
FROM skills.assessment_tasks at
JOIN skills.skill_definitions sd ON at.skill_id = sd.id
ORDER BY
    CASE at.difficulty
        WHEN 'beginner' THEN 1
        WHEN 'intermediate' THEN 2
        WHEN 'advanced' THEN 3
        WHEN 'expert' THEN 4
        WHEN 'instructor' THEN 5
    END,
    at.task_key;
