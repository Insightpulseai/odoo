# forecasting-solution-design — Evaluation Criteria

## Accuracy (target: 0.90)
- Model selection matches problem scale and complexity
- Feature engineering is appropriate for the data and domain
- Evaluation methodology uses correct metrics for the scenario

## Completeness (target: 0.90)
- All six areas covered: scenario classification, data assessment, feature engineering, model selection, evaluation, action integration
- External signals considered (not necessarily used, but assessed)
- Business success criteria defined alongside technical metrics

## Safety (target: 0.99)
- No deployment recommendation without backtesting
- No forecast pipeline without action integration
- No over-engineering (deep learning for 50 time series)
- Statistical methods considered before ML methods

## Policy Adherence (target: 0.99)
- Scenario archetype guardrail respected (does not influence platform architecture)
- Simplest-first model selection principle followed
- Evaluation includes business metrics, not just statistical metrics
- Action integration is mandatory

## Failure Modes
| Mode | Detection | Mitigation |
|------|-----------|------------|
| Over-engineering | Complex model for simple problem | Require baseline comparison |
| No evaluation | Deployed without backtesting | Block deployment without holdout results |
| Forecast without action | No integration plan | Require action plan in design |
| Data insufficiency | Less than 2 years for seasonal | Document limitation, adjust expectations |
| Scope creep | Design becomes platform architecture | Enforce scenario archetype guardrail |
