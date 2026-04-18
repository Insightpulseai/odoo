---
name: prismalab-prisma-compliance
description: Validate systematic reviews against PRISMA 2020 checklist and generate compliance reports. Covers all 27 checklist items and abstract checklist.
---

# PrismaLab PRISMA 2020 Compliance Skill

## When to Use
- User needs to check a manuscript against PRISMA 2020
- User needs to generate a PRISMA checklist for submission
- User asks about reporting requirements for systematic reviews
- User needs PRISMA-S (search reporting), PRISMA-P (protocol), or PRISMA-ScR (scoping reviews)

## PRISMA 2020 Checklist (27 Items)

### Title
1. Identify the report as a systematic review

### Abstract
2. Structured summary (PRISMA abstract checklist: 12 items)

### Introduction
3. Rationale for the review
4. Objectives with PICO elements

### Methods
5. Eligibility criteria
6. Information sources (databases, registers, other sources)
7. Search strategy (full strategy for at least one database)
8. Selection process
9. Data collection process
10. Data items (outcomes, other variables)
11. Study risk of bias assessment
12. Effect measures
13. Synthesis methods
14. Reporting bias assessment
15. Certainty assessment (GRADE)

### Results
16. Study selection (PRISMA flow diagram)
17. Study characteristics
18. Risk of bias in studies
19. Results of individual studies
20. Results of syntheses
21. Reporting biases
22. Certainty of evidence

### Discussion
23. Discussion of results in context
24. Limitations
25. Conclusions and implications

### Other Information
26. Registration and protocol
27. Support and funding

## Compliance Check Workflow

### Input
Provide the manuscript text (paste or upload PDF).

### Processing
```python
# Use GPT-4.1 to assess each checklist item
compliance_prompt = """
Assess this systematic review manuscript against the PRISMA 2020 checklist.
For each of the 27 items, provide:
- Item number and name
- Status: PRESENT / PARTIAL / ABSENT
- Location: page/section where found (if present)
- Comment: what's missing or could be improved

Also check:
- Is the PRISMA flow diagram present and complete?
- Is the search strategy reproducible?
- Are effect measures clearly defined?
- Is heterogeneity assessed and reported?
- Is the GRADE assessment present?
- Is AI assistance declared in methods?
"""
```

### Output Format
```markdown
## PRISMA 2020 Compliance Report

**Overall Score: X/27 items fully reported**

| # | Item | Status | Location | Comment |
|---|------|--------|----------|---------|
| 1 | Title | PRESENT | p.1 | Identified as systematic review |
| 2 | Abstract | PARTIAL | p.1 | Missing registration number |
| ... | ... | ... | ... | ... |

### Critical Gaps
- [ ] Item X: [description of what's missing]
- [ ] Item Y: [description of what's missing]

### Recommendations
1. [Specific recommendation to address gap]
2. [Specific recommendation to address gap]
```

## PRISMA Extensions Supported

| Extension | Use Case |
|-----------|----------|
| PRISMA-P | Protocol reporting (pre-registration) |
| PRISMA-S | Search strategy reporting |
| PRISMA-ScR | Scoping review reporting |
| PRISMA-DTA | Diagnostic test accuracy reviews |
| PRISMA-IPD | Individual participant data meta-analyses |
| PRISMA-NMA | Network meta-analyses |

## Integration with Other PrismaLab Skills
- After compliance check → `prismalab-systematic-review` to fix gaps
- After identifying missing synthesis → `prismalab-meta-analysis` to compute
- After identifying missing data → `prismalab-evidence-extraction` to extract

## Quality Standards
- Compliance check is advisory, not authoritative
- Final compliance determination is the author's responsibility
- Some items require subjective judgment (e.g., "adequate" rationale)
- Journal-specific requirements may differ from PRISMA 2020
