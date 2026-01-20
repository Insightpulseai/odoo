# Stack Relationships

> **Purpose**: Explicit entity relationships for LLM understanding.
> **Format**: Subject → Predicate → Object triples

---

## Core Infrastructure Triples

### Deployment Relationships
```
repo.odoo-ce DEPLOYS_TO droplet.odoo-erp-prod
repo.odoo-ce USES_DB cluster.odoo-db-sgp1
repo.odoo-ce INTEGRATES_WITH supabase.spdtwktxdalcfigzeqrz
vercel_project.shelf-nu DEPLOYS_FROM repo.odoo-ce
vercel_project.shelf-nu USES_DB supabase.spdtwktxdalcfigzeqrz
```

### Data Flow Relationships
```
odoo.public MIRRORS_TO supabase.odoo_shadow
supabase.kb STORES_DOCS_FOR rag.semantic_search
supabase.kg STORES_GRAPH_FOR agent.navigation
supabase.agent_mem STORES_MEMORY_FOR mcp.agents
```

### Module Relationships
```
module.ipai_enterprise_bridge PROVIDES_BASE_FOR module.ipai_scout_bundle
module.ipai_enterprise_bridge PROVIDES_BASE_FOR module.ipai_ces_bundle
module.ipai_scout_bundle INCLUDES module.sale_management
module.ipai_scout_bundle INCLUDES module.point_of_sale
module.ipai_ces_bundle INCLUDES module.project
module.ipai_ces_bundle INCLUDES module.hr_timesheet
```

---

## Service Dependencies

### Odoo Production
```
service.odoo-core RUNS_ON droplet.odoo-erp-prod
service.odoo-core CONNECTS_TO cluster.odoo-db-sgp1
service.odoo-core EXPOSES_API endpoint.erp.insightpulseai.net
service.odoo-core USES_SMTP provider.mailgun
```

### Supabase
```
service.supabase HOSTS_PROJECT spdtwktxdalcfigzeqrz
service.supabase PROVIDES schema.public
service.supabase PROVIDES schema.kb
service.supabase PROVIDES schema.kg
service.supabase PROVIDES schema.agent_mem
service.supabase PROVIDES extension.pgvector
```

### Vercel
```
platform.vercel HOSTS_PROJECT shelf-nu
platform.vercel HOSTS_PROJECT scout-dashboard
platform.vercel HOSTS_PROJECT tbwa-agency-dash
platform.vercel INTEGRATES_WITH supabase.spdtwktxdalcfigzeqrz
```

---

## Schema Relationships

### Knowledge Base Schema (`kb`)
```
kb.spaces CONTAINS kb.artifacts
kb.artifacts HAS_VERSIONS kb.versions
kb.artifacts TAGGED_WITH kb.blocks
kb.blocks CITES kb.citations
kb.catalog_sources ORGANIZES kb.catalog_nodes
kb.catalog_nodes TRACKS kb.harvest_state
```

### Knowledge Graph Schema (`kg`)
```
kg.nodes CONNECTED_BY kg.edges
kg.edges EVIDENCED_BY kg.evidence
kg.nodes EMBEDDED_IN kg.node_embeddings
kg.semantic_search QUERIES kg.node_embeddings
kg.neighborhood TRAVERSES kg.edges
```

### Agent Memory Schema (`agent_mem`)
```
agent_mem.sessions CONTAINS agent_mem.events
agent_mem.skills BOUND_TO agent_mem.agent_skill_bindings
agent_mem.events EMBEDDED_IN agent_mem.events.embedding
```

---

## Authentication Relationships

```
auth.users AUTHENTICATED_BY supabase.auth
auth.users AUTHORIZED_BY rls.policies
auth.users ASSIGNED_TO auth.roles
api.rest PROTECTED_BY auth.jwt
api.graphql PROTECTED_BY auth.jwt
```

---

## Monitoring Relationships

```
ops_advisor.recommendations TRACKS service.health
ops_advisor.scores MEASURES service.performance
ops_advisor.activity_log AUDITS service.changes
```

---

## How to Use These Relationships

### Finding Upstream Dependencies
"What does X depend on?" → Follow edges where X is the subject.

### Finding Downstream Dependents
"What depends on X?" → Follow edges where X is the object.

### Path Finding
"How does A connect to B?" → Traverse edges between A and B.

### Impact Analysis
"What breaks if X fails?" → Find all dependents of X recursively.

---

## Graph Query Examples

```sql
-- Find all things that depend on Odoo
SELECT e.*, n.label as dependent
FROM kg.edges e
JOIN kg.nodes n ON e.from_node = n.id
WHERE e.to_node = (SELECT id FROM kg.nodes WHERE slug = 'odoo-erp-prod');

-- Find the path from Vercel to Odoo DB
SELECT * FROM kg.neighborhood(
  (SELECT id FROM kg.nodes WHERE slug = 'shelf-nu'),
  3
);
```
