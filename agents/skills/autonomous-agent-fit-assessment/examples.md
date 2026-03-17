# Autonomous Agent Fit Assessment — Examples

## Example 1: Production Incident Debug — JUSTIFIED

```
Assessment: agent_justified
Open-ended: yes — root cause unknown, investigation path unpredictable
Feedback-dependent: yes — each diagnostic step's results determine next action
Adaptive: yes — hypothesis shifts as evidence accumulates
Cost-justified: yes — production incident cost >> agent cost
Guardrails: sandbox (read-only prod access), 30-min timeout, log all actions, human approval for any remediation
```

## Example 2: Weekly Report Generation — NOT JUSTIFIED

```
Assessment: workflow_sufficient
Open-ended: no — same sections every week
Feedback-dependent: no — data sources are known
Adaptive: no — same process each time
Alternative: Sequential workflow (query → compute → format → deliver)
```

## Example 3: Research Question — JUSTIFIED

```
Assessment: agent_justified
Open-ended: yes — research paths depend on what's found
Feedback-dependent: yes — each source shapes next query
Adaptive: yes — must follow promising leads, abandon dead ends
Cost-justified: yes — comprehensive research requires exploration
Guardrails: web-only sandbox, 100 tool calls max, 15-min timeout, summary checkpoint at 50% budget
```
