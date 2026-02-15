# Odoo 19 Agent Architecture

## System Overview

The following diagram illustrates how the `Skill Registry`, `Skill Map`, and `Knowledge Base` interact to empower the Odoo Agent.

![Antigravity Architecture](assets/antigravity_architecture.drawio)
_Note: This diagram is rendered by your local Draw.io extension._

```mermaid
graph TD
    User[User Request] --> Agent[Odoo Agent]

    subgraph "Registry System"
        Agent --> Registry[odoo_skills.yaml]
        Registry --> Mapper[odoo_developer_skill_map.yaml]
    end

    subgraph "Capabilities"
        Mapper -->|Loads| KSkills[Knowledge Skills]
        Mapper -->|Loads| PSkills[Procedural Skills]

        KSkills -->|Retrieves| KB[Knowledge Base /kb/odoo19]
        PSkills -->|Executes| Scripts[Automated Workflows]
    end

    subgraph "Knowledge Base"
        KB --> Dev[Developer Docs]
        KB --> Admin[Admin Docs]
        KB --> Svc[Services Docs]
    end

    subgraph "Procedural Execution"
        Scripts --> OdooSH[Odoo.sh Workflow]
        OdooSH -->|Input| Git[Git Repo]
        OdooSH -->|Output| Evidence[Evidence Artifacts]
    end
```

## Workflow: Odoo.sh CI/CD via Procedural Skill

Visualization of the deterministic `odoo.sh.workflow` skill.

```mermaid
sequenceDiagram
    participant Agent
    participant Skill as odoo.sh.workflow
    participant Repo as Git Repository
    participant Env as Odoo.sh / Local
    participant Log as Evidence Log

    Agent->>Skill: Invoke (repo, target, ref)

    rect rgb(240, 248, 255)
    note right of Agent: Phase 1: Preparation
    Skill->>Repo: Validate Invariants (conf, db filters)
    Skill->>Repo: Compute Diff & Run Plan
    Skill->>Log: Write plan.json
    end

    rect rgb(255, 250, 240)
    note right of Agent: Phase 2: Execution
    Skill->>Env: Build & Run Unit Tests
    Skill->>Env: Apply Migrations (if needed)
    Skill->>Log: Write run.log
    end

    rect rgb(240, 255, 240)
    note right of Agent: Phase 3: Verification
    Skill->>Env: Health Check / Smoke Test
    Env-->>Skill: Status OK
    Skill->>Log: Write health.json
    end

    Skill->>Agent: Return Evidence Package
```
