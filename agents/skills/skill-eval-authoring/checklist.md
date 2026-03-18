# Skill Eval Authoring — Checklist

- [ ] Eval type selected (single-turn / multi-turn / agent)
- [ ] Grading method selected (code / model / human)
- [ ] >=3 positive test cases written
- [ ] >=2 negative test cases written
- [ ] Each test has: prompt, expected output, grading criteria
- [ ] Partial credit defined for multi-component outputs
- [ ] Pass criteria defined (pass@k or pass^k with threshold)
- [ ] LLM grader calibrated against human judgment (if model-based)
- [ ] Capability → regression graduation plan documented
