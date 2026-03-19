# Checklist — sample-to-contract-extraction

## Sample review

- [ ] Sample URL and version recorded
- [ ] Sample structure reviewed (IaC, app code, config)
- [ ] Core pattern identified (architecture, auth, data flow)
- [ ] Language/runtime noted

## Security audit

- [ ] Managed identity: present or absent
- [ ] VNet integration: present or absent
- [ ] Keyless access: present or absent
- [ ] Private endpoints: present or absent
- [ ] No hardcoded secrets in sample code

## Pattern abstraction

- [ ] Language-specific code stripped
- [ ] Architecture-neutral description written
- [ ] Multiple language implementations noted (if available)
- [ ] Core dependencies identified

## Platform alignment

- [ ] Deviations from canonical stack documented
- [ ] Required adaptations listed
- [ ] Incompatible elements identified
- [ ] Cost implications noted

## Contract drafting

- [ ] Contract document created in docs/contracts/
- [ ] Pattern description is clear and actionable
- [ ] Guardrails defined
- [ ] Examples provided
- [ ] Provenance recorded (URL, date, version)
- [ ] Registered in platform contracts index
