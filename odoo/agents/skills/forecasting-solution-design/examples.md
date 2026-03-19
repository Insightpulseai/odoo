# forecasting-solution-design — Examples

## Example 1: Retail SKU-Level Demand Forecast

**Input**: Grocery retailer, 5,000 SKUs across 200 stores. Need weekly demand forecast for inventory reorder. 3 years of POS data available. Promotions calendar available.

**Output**:

Scenario: SKU-store weekly demand forecasting for inventory optimization.

Data assessment:
- 3 years history: sufficient for seasonal patterns
- 5,000 SKUs x 200 stores = 1M time series: ML approach justified at this scale
- External signals: promotions (strong), holidays (moderate), weather (weak for grocery)

Feature engineering:
- Lags: sales_lag_1w, sales_lag_4w, sales_lag_52w
- Rolling: rolling_mean_4w, rolling_std_8w, rolling_max_4w
- Calendar: week_of_year, is_holiday_week, days_to_next_holiday
- Promotion: is_promo, promo_type, promo_discount_pct, days_since_last_promo
- Hierarchy: category_sales_4w, store_sales_4w

Model: LightGBM with global model (all SKU-stores as features, not separate models). Justified by scale (1M series) and shared promotional patterns.

Evaluation:
- Primary: WAPE < 25% at SKU-store-week level
- Bias: forecast bias within +/- 3% (no systematic over/under-ordering)
- Backtest: 4 holdout periods (4 consecutive weeks each)
- Business: stockout rate < 2%, overstock waste < 5%

Action integration: Weekly forecast export to ERP reorder module. Dashboard for planners with anomaly flags. Alert when any SKU forecast exceeds 3x historical average.

---

## Example 2: Restaurant Staffing Forecast

**Input**: Fast-casual restaurant chain, 50 locations. Need daily staffing forecast (covers needed per shift). 18 months of transaction data.

**Output**:

Scenario: Daily shift-level demand forecasting for staffing optimization.

Data assessment:
- 18 months: borderline for annual seasonality (prefer 2+ years)
- 50 locations x 3 shifts = 150 time series: statistical methods appropriate
- External signals: weather (strong for restaurants), local events (moderate)

Model: Prophet per location-shift combination. Justified by small series count and strong calendar effects. Prophet handles holidays and trend changes well at this scale.

Evaluation:
- Primary: MAPE < 15% at location-shift-day level
- Business: understaffing incidents < 5%, overstaffing cost < 8% of labor budget
- Backtest: 3 holdout periods (2 weeks each)

Action integration: Daily staffing recommendation pushed to scheduling system. Manager override capability for known local events. Weekly accuracy report for continuous improvement.
