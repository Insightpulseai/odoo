# Checklist — azd-environment-bootstrap

## Project initialization

- [ ] azd template selected and validated
- [ ] azd init completed successfully
- [ ] azure.yaml present and valid
- [ ] All services declared in azure.yaml
- [ ] Hosting targets match platform (ACA, Functions)

## Environment configuration

- [ ] Environment created with azd env new
- [ ] Subscription ID set correctly
- [ ] Region set to platform convention (southeastasia)
- [ ] Resource group follows rg-ipai-{env} naming
- [ ] Environment variables configured via azd env set
- [ ] No secret values in environment variables (use Key Vault references)

## CI/CD integration

- [ ] azd pipeline config executed
- [ ] Pipeline uses federated credentials (not stored secrets)
- [ ] Workflow file generated and reviewed
- [ ] Pipeline targets correct environments

## Verification

- [ ] azd env get-values shows correct configuration
- [ ] azure.yaml validates with azd validate (if available)
- [ ] CI/CD workflow file passes lint
