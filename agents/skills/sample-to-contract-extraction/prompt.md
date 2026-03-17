# Prompt — sample-to-contract-extraction

You are extracting a reusable pattern from an Azure sample catalog entry for the InsightPulse AI platform.

Your job is to:
1. Review the sample structure (IaC, app code, configuration)
2. Identify the core pattern (not the scaffold)
3. Verify secure-by-default posture
4. Abstract language-specific implementation details
5. Document deviations from the canonical platform stack
6. Draft a contract document

Key doctrine: **Samples are implementation fixtures, NOT architecture doctrine.**

Extraction process:
1. **Pattern identification**: What problem does this sample solve? What is the architectural pattern?
2. **Security audit**: Does it use managed identity? VNet? Keyless access? Private endpoints?
3. **Abstraction**: Strip language-specific code. What remains is the pattern.
4. **Platform alignment**: Where does this sample differ from our canonical stack?
5. **Contract drafting**: Document the pattern with guardrails and examples.

Contract document structure:
```markdown
# Contract: <PATTERN_NAME>

## Source
- Sample: <name and URL>
- Retrieved: <date>
- Version: <commit or tag>

## Pattern
<Architecture-neutral description of the pattern>

## Secure-by-Default Assessment
- Managed identity: yes/no
- VNet integration: yes/no
- Keyless access: yes/no
- Private endpoints: yes/no

## Platform Alignment
- Deviations from canonical stack: <list>
- Required adaptations: <list>

## Guardrails
- <constraint 1>
- <constraint 2>

## Examples
<Language-neutral or multi-language examples>
```

Output: Draft contract document ready for review.
