-- =============================================================================
-- DRAW.IO SKILLS CERTIFICATION SEEDS
-- =============================================================================
-- Complete Draw.io diagramming skill certification system
-- Integrates with skills.* schema for professional credentials
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Draw.io Skill Definitions (15+ Skills)
-- -----------------------------------------------------------------------------

-- Core Diagramming Fundamentals
INSERT INTO skills.skill_definitions (slug, title, description, category, level, spec_url, design_system_token)
VALUES
    (
        'drawio-fundamentals',
        'Draw.io Fundamentals',
        'Foundational competency in creating diagrams using draw.io interface, tools, and basic shapes.',
        'diagramming',
        'foundation',
        'https://www.drawio.com/blog',
        NULL
    ),
    (
        'drawio-shapes-connectors',
        'Shapes & Connectors Mastery',
        'Expert usage of shape libraries, custom shapes, connector routing, and layout optimization.',
        'diagramming',
        'associate',
        'https://www.drawio.com/doc/faq/connectors',
        NULL
    ),
    (
        'drawio-styling-themes',
        'Styling & Theme Design',
        'Create professional visual themes, color schemes, and branded diagram templates.',
        'design-system',
        'associate',
        'https://www.drawio.com/doc/faq/format-panel',
        NULL
    )
ON CONFLICT (slug) DO NOTHING;

-- Diagram Type Skills
INSERT INTO skills.skill_definitions (slug, title, description, category, level, spec_url, design_system_token)
VALUES
    (
        'flowchart-iso5807',
        'Flowchart Design (ISO 5807)',
        'Create flowcharts following ISO 5807 standards for process documentation and decision trees.',
        'process-modeling',
        'associate',
        'https://www.drawio.com/blog/flowchart-shapes',
        NULL
    ),
    (
        'uml-diagram-design',
        'UML Diagram Design',
        'Create UML diagrams (class, sequence, state, activity, component, deployment) following OMG standards.',
        'software-architecture',
        'professional',
        'https://www.drawio.com/blog/uml-class-diagrams',
        NULL
    ),
    (
        'bpmn-process-modeling',
        'BPMN 2.0 Process Modeling',
        'Create BPMN 2.0 diagrams for formal business process documentation with gateways, events, and subprocess flows.',
        'process-modeling',
        'professional',
        'https://www.drawio.com/blog/bpmn-2-0',
        NULL
    ),
    (
        'erd-database-design',
        'ERD & Database Design',
        'Design relational database schemas using Chen and Crow''s Foot notations with normalization and cardinality.',
        'data-modeling',
        'professional',
        'https://www.drawio.com/blog/entity-relationship-tables',
        NULL
    ),
    (
        'network-topology-design',
        'Network Topology Design',
        'Design network topologies, security group diagrams, and infrastructure layouts following Cisco standards.',
        'infrastructure',
        'professional',
        'https://www.drawio.com/blog/network-diagrams',
        NULL
    )
ON CONFLICT (slug) DO NOTHING;

-- Cloud Architecture Skills
INSERT INTO skills.skill_definitions (slug, title, description, category, level, spec_url, design_system_token)
VALUES
    (
        'aws-architecture-diagramming',
        'AWS Architecture Diagramming',
        'Design AWS cloud architectures with proper VPC, security groups, and AWS icon conventions.',
        'cloud-architecture',
        'professional',
        'https://www.drawio.com/blog/aws-architecture-diagrams',
        NULL
    ),
    (
        'azure-architecture-diagramming',
        'Azure Architecture Diagramming',
        'Design Microsoft Azure architectures with proper resource groups and Azure icons.',
        'cloud-architecture',
        'professional',
        'https://www.drawio.com/blog/azure-diagrams',
        NULL
    ),
    (
        'gcp-architecture-diagramming',
        'GCP Architecture Diagramming',
        'Design Google Cloud Platform architectures with proper project structures and GCP icons.',
        'cloud-architecture',
        'professional',
        'https://www.drawio.com/blog/gcp-diagrams',
        NULL
    ),
    (
        'multi-cloud-architecture',
        'Multi-Cloud Architecture Design',
        'Design hybrid and multi-cloud architectures spanning AWS, Azure, GCP with DR and cost optimization.',
        'cloud-architecture',
        'expert',
        'https://www.drawio.com/blog/cloud-architecture',
        NULL
    )
ON CONFLICT (slug) DO NOTHING;

-- Advanced Modeling Skills
INSERT INTO skills.skill_definitions (slug, title, description, category, level, spec_url, design_system_token)
VALUES
    (
        'c4-model-architecture',
        'C4 Model Architecture Diagramming',
        'Document software architecture using C4 model (Context, Container, Component, Code) following Simon Brown''s standard.',
        'software-architecture',
        'expert',
        'https://www.drawio.com/blog/c4-modelling',
        NULL
    ),
    (
        'api-integration-flows',
        'API & Integration Flow Diagramming',
        'Document API flows, webhooks, message queues, and data pipelines with request/response cycles.',
        'software-architecture',
        'professional',
        'https://www.drawio.com/blog/sequence-diagrams',
        NULL
    ),
    (
        'archimate-enterprise',
        'ArchiMate Enterprise Architecture',
        'Create ArchiMate 3.x diagrams for enterprise architecture documentation.',
        'enterprise-architecture',
        'expert',
        'https://www.drawio.com/blog/archimate-diagrams',
        NULL
    )
ON CONFLICT (slug) DO NOTHING;

-- Enterprise & Collaboration Skills
INSERT INTO skills.skill_definitions (slug, title, description, category, level, spec_url, design_system_token)
VALUES
    (
        'drawio-collaboration',
        'Collaborative Diagram Design',
        'Use draw.io real-time collaboration, version control, comments, and review workflows.',
        'collaboration',
        'associate',
        'https://www.drawio.com/blog/collaborative-editing',
        NULL
    ),
    (
        'drawio-atlassian-integration',
        'Atlassian Integration (Jira/Confluence)',
        'Embed and manage diagrams in Jira and Confluence using draw.io Atlassian apps.',
        'integration',
        'associate',
        'https://www.drawio.com/blog/confluence-cloud',
        NULL
    ),
    (
        'drawio-template-library',
        'Template & Library Creation',
        'Create reusable diagram templates and custom shape libraries for organizational standards.',
        'design-system',
        'professional',
        'https://www.drawio.com/blog/custom-libraries',
        NULL
    ),
    (
        'drawio-dynamic-data',
        'Dynamic Data & Automation',
        'Link diagrams to live data sources and create dynamic, auto-updating diagrams.',
        'automation',
        'expert',
        'https://www.drawio.com/blog/data-driven-diagrams',
        NULL
    ),
    (
        'drawio-export-import',
        'Export, Import & Format Conversion',
        'Import from external sources (Visio, Lucidchart) and export to multiple formats (SVG, PDF, PNG, XML).',
        'integration',
        'foundation',
        'https://www.drawio.com/blog/export-diagram',
        NULL
    ),
    (
        'drawio-accessibility',
        'Accessible Diagram Design',
        'Create diagrams accessible to people with disabilities following WCAG guidelines.',
        'accessibility',
        'associate',
        'https://www.drawio.com/blog/accessibility',
        NULL
    )
ON CONFLICT (slug) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Skill Criteria for Core Skills
-- -----------------------------------------------------------------------------

-- Criteria for drawio-fundamentals
WITH skill AS (
    SELECT id FROM skills.skill_definitions WHERE slug = 'drawio-fundamentals'
)
INSERT INTO skills.skill_criteria (skill_id, code, description, weight, required)
SELECT
    skill.id,
    x.code,
    x.description,
    x.weight,
    x.required
FROM skill,
    (VALUES
        ('INTERFACE_NAV', 'Navigate draw.io interface and understand panel layout.', 1.5, true),
        ('SHAPE_INSERT', 'Insert and style shapes from standard libraries.', 1.5, true),
        ('CONNECTOR_BASIC', 'Create connectors with labels and basic routing.', 1.5, true),
        ('EXPORT_FORMATS', 'Export diagrams to PNG, PDF, and SVG formats.', 1.0, true),
        ('DIAGRAM_TYPES', 'Identify appropriate diagram type for use case.', 1.0, false)
    ) AS x(code, description, weight, required)
ON CONFLICT (skill_id, code) DO NOTHING;

-- Criteria for uml-diagram-design
WITH skill AS (
    SELECT id FROM skills.skill_definitions WHERE slug = 'uml-diagram-design'
)
INSERT INTO skills.skill_criteria (skill_id, code, description, weight, required)
SELECT
    skill.id,
    x.code,
    x.description,
    x.weight,
    x.required
FROM skill,
    (VALUES
        ('UML_NOTATION', 'Correct UML notation for all diagram types.', 2.0, true),
        ('CLASS_DIAGRAMS', 'Create class diagrams with inheritance, composition, aggregation.', 2.0, true),
        ('SEQUENCE_DIAGRAMS', 'Create sequence diagrams with lifelines and message flows.', 2.0, true),
        ('STATE_MACHINES', 'Model state machines with transitions and guards.', 1.5, true),
        ('DESIGN_PATTERNS', 'Apply GoF design patterns in diagrams.', 1.0, false)
    ) AS x(code, description, weight, required)
ON CONFLICT (skill_id, code) DO NOTHING;

-- Criteria for c4-model-architecture
WITH skill AS (
    SELECT id FROM skills.skill_definitions WHERE slug = 'c4-model-architecture'
)
INSERT INTO skills.skill_criteria (skill_id, code, description, weight, required)
SELECT
    skill.id,
    x.code,
    x.description,
    x.weight,
    x.required
FROM skill,
    (VALUES
        ('C4_CONTEXT', 'Create System Context diagram (Level 1) with actors and systems.', 2.0, true),
        ('C4_CONTAINER', 'Create Container diagram (Level 2) with applications and data stores.', 2.0, true),
        ('C4_COMPONENT', 'Create Component diagram (Level 3) with internal architecture.', 2.0, true),
        ('C4_CODE', 'Create Code diagram (Level 4) for detailed implementation.', 1.5, false),
        ('C4_CONSISTENCY', 'Maintain consistency across all 4 levels.', 1.5, true),
        ('ADR_QUALITY', 'Document architecture decisions with rationale.', 1.0, false)
    ) AS x(code, description, weight, required)
ON CONFLICT (skill_id, code) DO NOTHING;

-- Criteria for aws-architecture-diagramming
WITH skill AS (
    SELECT id FROM skills.skill_definitions WHERE slug = 'aws-architecture-diagramming'
)
INSERT INTO skills.skill_criteria (skill_id, code, description, weight, required)
SELECT
    skill.id,
    x.code,
    x.description,
    x.weight,
    x.required
FROM skill,
    (VALUES
        ('AWS_SYMBOLS', 'Use correct AWS architecture icons and placement.', 2.0, true),
        ('VPC_DESIGN', 'Design VPCs with subnets, routing, and security groups.', 2.0, true),
        ('SECURITY_ARCH', 'Reflect security best practices (IAM, encryption, firewalls).', 1.5, true),
        ('SCALABILITY', 'Show auto-scaling, load balancing, and elasticity.', 1.5, true),
        ('COST_AWARENESS', 'Consider cost implications in architecture decisions.', 1.0, false)
    ) AS x(code, description, weight, required)
ON CONFLICT (skill_id, code) DO NOTHING;

-- Criteria for bpmn-process-modeling
WITH skill AS (
    SELECT id FROM skills.skill_definitions WHERE slug = 'bpmn-process-modeling'
)
INSERT INTO skills.skill_criteria (skill_id, code, description, weight, required)
SELECT
    skill.id,
    x.code,
    x.description,
    x.weight,
    x.required
FROM skill,
    (VALUES
        ('BPMN_COMPLIANCE', 'BPMN 2.0 specification compliance.', 2.0, true),
        ('GATEWAY_LOGIC', 'Correct exclusive, parallel, and inclusive gateway usage.', 2.0, true),
        ('SUBPROCESS', 'Model subprocesses and call activities.', 1.5, true),
        ('EVENTS', 'Use start, intermediate, and end events correctly.', 1.5, true),
        ('EXECUTION_READY', 'Diagrams are executable or simulation-ready.', 1.0, false)
    ) AS x(code, description, weight, required)
ON CONFLICT (skill_id, code) DO NOTHING;

-- Criteria for erd-database-design
WITH skill AS (
    SELECT id FROM skills.skill_definitions WHERE slug = 'erd-database-design'
)
INSERT INTO skills.skill_criteria (skill_id, code, description, weight, required)
SELECT
    skill.id,
    x.code,
    x.description,
    x.weight,
    x.required
FROM skill,
    (VALUES
        ('NOTATION', 'Correct Chen or Crow''s Foot notation usage.', 2.0, true),
        ('CARDINALITY', 'Accurate cardinality and optionality markers.', 2.0, true),
        ('NORMALIZATION', 'Schema reflects proper normalization (3NF minimum).', 1.5, true),
        ('KEYS', 'Primary and foreign keys clearly indicated.', 1.5, true),
        ('INDEXES', 'Performance considerations with index suggestions.', 1.0, false)
    ) AS x(code, description, weight, required)
ON CONFLICT (skill_id, code) DO NOTHING;

-- Criteria for drawio-template-library
WITH skill AS (
    SELECT id FROM skills.skill_definitions WHERE slug = 'drawio-template-library'
)
INSERT INTO skills.skill_criteria (skill_id, code, description, weight, required)
SELECT
    skill.id,
    x.code,
    x.description,
    x.weight,
    x.required
FROM skill,
    (VALUES
        ('SHAPE_DESIGN', 'Custom shapes are well-designed and reusable.', 2.0, true),
        ('LIBRARY_ORG', 'Library organized with clear categories.', 1.5, true),
        ('STYLE_GUIDE', 'Documented style guide for usage.', 1.5, true),
        ('TEMPLATE_VARS', 'Templates use variables for customization.', 1.0, false),
        ('TRAINING_MAT', 'Training materials for library adoption.', 1.0, false)
    ) AS x(code, description, weight, required)
ON CONFLICT (skill_id, code) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Draw.io Agent Holders
-- -----------------------------------------------------------------------------

INSERT INTO skills.skill_holders (holder_type, holder_slug, display_name, meta)
VALUES
    (
        'agent',
        'Pulser.Architect',
        'Architect – Systems Design Intelligence',
        '{"stack":["c4","archimate","uml"],"specialty":"architecture-diagramming"}'::jsonb
    ),
    (
        'agent',
        'Pulser.Blueprint',
        'Blueprint – Infrastructure Visualization',
        '{"stack":["aws","azure","gcp","network"],"specialty":"cloud-architecture"}'::jsonb
    ),
    (
        'agent',
        'Pulser.Flow',
        'Flow – Process Modeling Intelligence',
        '{"stack":["bpmn","flowchart","n8n"],"specialty":"process-automation"}'::jsonb
    ),
    (
        'agent',
        'Pulser.Schema',
        'Schema – Data Model Intelligence',
        '{"stack":["erd","postgresql","supabase"],"specialty":"database-design"}'::jsonb
    ),
    (
        'agent',
        'Pulser.Canvas',
        'Canvas – Visual Design Intelligence',
        '{"stack":["drawio","figma","mermaid"],"specialty":"diagram-creation"}'::jsonb
    )
ON CONFLICT (holder_type, holder_slug) DO UPDATE
    SET display_name = EXCLUDED.display_name,
        meta = EXCLUDED.meta;

-- -----------------------------------------------------------------------------
-- Knowledge Sources for Draw.io
-- -----------------------------------------------------------------------------

INSERT INTO knowledge.sources (slug, kind, base_url, meta)
VALUES
    ('drawio-blog', 'docs', 'https://www.drawio.com/blog', '{"priority": 1, "crawl_status": "pending"}'::jsonb),
    ('drawio-docs', 'docs', 'https://www.drawio.com/doc', '{"priority": 1, "crawl_status": "pending"}'::jsonb),
    ('drawio-github', 'repo', 'https://github.com/jgraph/drawio', '{"priority": 2}'::jsonb),
    ('c4-model-docs', 'docs', 'https://c4model.com/', '{"priority": 2}'::jsonb),
    ('archimate-spec', 'spec', 'https://pubs.opengroup.org/architecture/archimate3-doc/', '{"priority": 3}'::jsonb),
    ('bpmn-spec', 'spec', 'https://www.omg.org/spec/BPMN/2.0/', '{"priority": 3}'::jsonb),
    ('uml-spec', 'spec', 'https://www.omg.org/spec/UML/', '{"priority": 3}'::jsonb),
    ('aws-architecture-icons', 'docs', 'https://aws.amazon.com/architecture/icons/', '{"priority": 2}'::jsonb),
    ('azure-architecture-icons', 'docs', 'https://docs.microsoft.com/en-us/azure/architecture/icons/', '{"priority": 2}'::jsonb)
ON CONFLICT (slug) DO UPDATE
    SET kind = EXCLUDED.kind,
        base_url = EXCLUDED.base_url,
        meta = EXCLUDED.meta,
        updated_at = NOW();

-- -----------------------------------------------------------------------------
-- Sample Telemetry Runs for Draw.io Skills
-- -----------------------------------------------------------------------------

INSERT INTO telemetry.runs (run_id, agent_slug, context, status, metadata)
VALUES
    ('drawio-skill-eval-001', 'Pulser.Architect', 'c4-diagram-assessment', 'passed', '{"skill_slug": "c4-model-architecture", "score": 23}'::jsonb),
    ('drawio-skill-eval-002', 'Pulser.Blueprint', 'aws-arch-assessment', 'passed', '{"skill_slug": "aws-architecture-diagramming", "score": 21}'::jsonb),
    ('drawio-skill-eval-003', 'Pulser.Flow', 'bpmn-assessment', 'passed', '{"skill_slug": "bpmn-process-modeling", "score": 22}'::jsonb),
    ('drawio-skill-eval-004', 'Pulser.Schema', 'erd-assessment', 'running', '{"skill_slug": "erd-database-design"}'::jsonb),
    ('drawio-skill-eval-005', 'Pulser.Canvas', 'fundamentals-assessment', 'passed', '{"skill_slug": "drawio-fundamentals", "score": 19}'::jsonb)
ON CONFLICT (run_id) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Verification Queries
-- -----------------------------------------------------------------------------

-- Verify Draw.io skill definitions
SELECT slug, title, category, level
FROM skills.skill_definitions
WHERE category IN ('diagramming', 'software-architecture', 'cloud-architecture', 'process-modeling', 'data-modeling', 'enterprise-architecture', 'integration', 'design-system', 'collaboration', 'automation', 'accessibility', 'infrastructure')
ORDER BY category, level DESC;

-- Verify criteria counts per skill
SELECT
    sd.slug,
    sd.category,
    COUNT(sc.id) AS criteria_count,
    SUM(CASE WHEN sc.required THEN 1 ELSE 0 END) AS required_count
FROM skills.skill_definitions sd
LEFT JOIN skills.skill_criteria sc ON sc.skill_id = sd.id
WHERE sd.slug LIKE 'drawio-%' OR sd.slug LIKE '%architecture%' OR sd.slug LIKE 'uml-%' OR sd.slug LIKE 'bpmn-%' OR sd.slug LIKE 'erd-%' OR sd.slug LIKE 'flowchart-%' OR sd.slug LIKE 'c4-%'
GROUP BY sd.slug, sd.category
ORDER BY sd.category, sd.slug;

-- Verify Draw.io agent holders
SELECT holder_type, holder_slug, display_name, meta->>'specialty' AS specialty
FROM skills.skill_holders
WHERE holder_slug LIKE 'Pulser.%' AND (meta->>'specialty' LIKE '%diagram%' OR meta->>'specialty' LIKE '%architecture%' OR meta->>'specialty' LIKE '%design%')
ORDER BY holder_slug;

-- Verify Draw.io knowledge sources
SELECT slug, kind, base_url
FROM knowledge.sources
WHERE slug LIKE 'drawio-%' OR slug LIKE '%architecture%' OR slug LIKE '%spec'
ORDER BY slug;
