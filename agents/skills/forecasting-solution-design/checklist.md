# forecasting-solution-design — Checklist

## Scenario Classification
- [ ] Forecasting type identified (demand, inventory, staffing, revenue)
- [ ] Granularity defined (SKU/store/region, daily/weekly/monthly)
- [ ] Action requirements documented (what decisions does the forecast drive?)
- [ ] Success criteria defined in business terms

## Data Assessment
- [ ] History depth evaluated (2+ years for seasonal patterns)
- [ ] Granularity match confirmed between data and forecast requirement
- [ ] External signals identified and assessed for relevance
- [ ] Data quality issues documented (missing values, outliers, regime changes)
- [ ] Series count determined (drives model selection)

## Feature Engineering
- [ ] Lag features specified with appropriate windows
- [ ] Rolling aggregates defined (mean, std, min, max)
- [ ] Calendar features included (day, week, month, holiday, promotion)
- [ ] External signals integrated where relevant
- [ ] Hierarchy features included for multi-level forecasts

## Model Selection
- [ ] Statistical methods considered first (ARIMA, ETS, Prophet)
- [ ] ML methods justified by scale or complexity (if used)
- [ ] Model complexity matches problem complexity
- [ ] Ensemble or hierarchical reconciliation considered where appropriate
- [ ] Baseline model defined for comparison

## Evaluation
- [ ] Primary metric selected (MAPE, WAPE, RMSE)
- [ ] Forecast bias measured (systematic over/under-prediction)
- [ ] Backtesting performed on 3+ holdout periods
- [ ] Business metric defined (stockout rate, waste, service level)
- [ ] Acceptance criteria documented

## Action Integration
- [ ] Forecast output feeds into a business system (ERP, scheduler, dashboard)
- [ ] Alert thresholds defined for anomalous forecasts
- [ ] Human-in-the-loop process defined for high-stakes decisions
- [ ] Feedback loop established (actual vs. forecast for continuous improvement)
