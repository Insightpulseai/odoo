# Constitution — Azure Assessment Harness

## Purpose

This bundle defines an internal assessment harness that prepares InsightPulseAI for official Microsoft Assessments by making the internal review process disciplined, repeatable, role-aware, and testable.

It exists so that:
- assessment evidence is gathered systematically from repo, SSOT, IaC, and runtime artifacts,
- draft answers are produced by role-based personas grounded in real Microsoft certification boundaries,
- scores are challenged by skeptical judges who distinguish present vs governed vs proven,
- internal scores can be compared against official Microsoft Assessment results after the portal is run,
- the gap between self-assessment and external benchmark is measurable and closeable.

## What this is

An internal **preparation, challenge, and calibration layer** for Microsoft Assessments.

## What this is NOT

This harness does **not** replace the official Microsoft Assessments platform at `learn.microsoft.com/assessments/`. The official platform remains the external authority for:
- normalized benchmark scoring comparable across customers,
- curated per-pillar recommendations linked to Microsoft Learn,
- exportable CSV results and shareable results pages,
- registration-required questionnaire with branching logic.

## Governing principles

### 1. Evidence-first, not opinion-first
Every answer must cite a specific artifact: file path, command output, Resource Graph query, or screenshot. Answers without evidence are flagged as "ungrounded."

### 2. Present vs Governed vs Proven
A control that exists is not the same as one that is source-controlled, and neither is the same as one that has been operationally validated. Scoring must distinguish all three levels.

### 3. Role-based personas, not generic reviewers
Personas map to real Microsoft role boundaries (AZ-305, AZ-500, AZ-400, AI-102, DP-600, AZ-120, AZ-104). This produces answers that think like Microsoft's own role families instead of one blended "cloud architect" voice.

### 4. Skeptical judges, not rubber stamps
Judges challenge optimistic answers, downgrade where evidence is only "present" but not "governed" or "proven," and flag answer-risky postures before the official assessment is taken.

### 5. Calibration, not replacement
After running the official Microsoft assessment, the internal harness compares its own scores against the official results and updates its calibration model. The gap between internal and official is a measurable metric.

### 6. Covers more than WAF
The harness simulates multiple Microsoft assessment families: WAF, DevOps Capability, FinOps, Platform Engineering, Go-Live, GenAIOps, and SaaS Journey.

## Organizational scope

- agents (personas, judges, skills)
- ssot/assessment (mapping, rubric, role map)
- docs/evidence/assessments (runbook, results, comparison)
- spec/azure-assessment-harness (this bundle)

## Delivery model

This is an internal tooling target, not a customer-facing product. Azure Boards projection is optional.

## Non-goals

- Replacing the official Microsoft Assessments portal
- Producing scores that claim Microsoft endorsement
- Building a hosted assessment questionnaire UI
- Automating the official portal submission
