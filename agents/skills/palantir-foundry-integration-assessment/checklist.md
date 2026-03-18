# Checklist — palantir-foundry-integration-assessment

- [ ] Confirmed whether a real Palantir Foundry workload exists in the organization
- [ ] Naming disambiguation performed (Microsoft Foundry vs Palantir Foundry)
- [ ] All stakeholders informed of the naming distinction
- [ ] If no Palantir workload: recommendation is REJECT or DEFER — do not proceed
- [ ] If Palantir workload exists: use cases documented
- [ ] SDK selection made (Foundry Platform SDK vs Ontology SDK)
- [ ] Ontology SDK preferred for ontology-based work (per Palantir guidance)
- [ ] Integration scope boundary defined
- [ ] Data flow direction documented (unidirectional preferred)
- [ ] SSOT boundary implications assessed
- [ ] No bidirectional data flows created without explicit SSOT documentation
- [ ] Palantir integration not treated as prerequisite for other platform capabilities
- [ ] Recommendation produced: proceed / defer / reject with justification
- [ ] Evidence captured in `docs/evidence/{stamp}/palantir-foundry/assessment/`
