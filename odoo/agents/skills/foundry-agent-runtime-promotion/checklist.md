# Checklist — foundry-agent-runtime-promotion

- [ ] Model selection evidence present (from model governor)
- [ ] Model safety assessment included
- [ ] Model cost assessment included
- [ ] Tool catalog approval present (from tool governor)
- [ ] Tool auth mode validated per tool
- [ ] Tool trust boundary documented per tool
- [ ] Auth configuration verified for every attached tool
- [ ] Eval quality score >= 0.98
- [ ] Eval safety score >= 0.99
- [ ] Eval policy adherence score >= 0.99
- [ ] Rollback/fallback strategy defined
- [ ] Rollback strategy tested or test plan documented
- [ ] No Preview features promoted as canonical without explicit approval
- [ ] Missing evidence list produced (even if empty)
- [ ] Release evidence package compiled
- [ ] Promotion verdict issued: PROMOTE or BLOCK
- [ ] Evidence captured in `docs/evidence/{stamp}/foundry/runtime-promotion/`
