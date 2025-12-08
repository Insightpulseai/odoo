# Retail & Scout Integration – InsightPulseAI Edition

**Module:** `point_of_sale`, `product`, `stock`, Scout Data Pipeline
**Domain:** Retail Analytics (Scout/SariCoach)
**Owner Engine:** Retail-Intel Engine
**Last Updated:** 2025-12-07

---

## 1. Overview & Purpose

The Retail & Scout workspace bridges Odoo 18 CE Point of Sale with the InsightPulseAI analytics platform. This integration handles:

- **POS transaction capture** from retail stores
- **Medallion data architecture** (Bronze → Silver → Gold → Platinum)
- **Retail analytics** via Scout pipeline
- **AI-powered insights** via SariCoach agents
- **Store performance dashboards** in Superset

### Key Differentiators from Stock Odoo

| Feature | Stock Odoo CE | InsightPulseAI Stack |
|---------|---------------|----------------------|
| POS Analytics | Basic reports | Medallion architecture in Supabase |
| Store Insights | Manual analysis | AI-generated via SariCoach |
| Real-time Data | Session-based | Streaming via n8n |
| Multi-tenant | Single company | RLS with tenant_id |
| Dashboards | Basic charts | Superset with drill-down |
| Forecasting | Not available | E3 Intelligence Engine |

---

## 2. Related Domain Engine(s)

| Engine | Role |
|--------|------|
| **Retail-Intel** | Primary owner - Scout analytics, SariCoach |
| **E1 Data Intake** | POS transaction ingestion |
| **E3 Intelligence** | Aggregation, insights generation |
| **E4 Creative** | AI coaching content |

---

## 3. Data Models

### 3.1 Core Odoo Models

| Model | Description | Key Fields |
|-------|-------------|------------|
| `pos.config` | POS configuration (per store) | `name`, `warehouse_id`, `pricelist_id` |
| `pos.session` | POS session (shift) | `config_id`, `user_id`, `start_at`, `stop_at`, `state` |
| `pos.order` | POS transactions | `session_id`, `partner_id`, `amount_total`, `date_order` |
| `pos.order.line` | Transaction line items | `order_id`, `product_id`, `qty`, `price_subtotal` |
| `pos.payment` | Payment records | `pos_order_id`, `payment_method_id`, `amount` |
| `product.product` | Products | `name`, `default_code`, `categ_id`, `list_price` |
| `product.category` | Product categories | `name`, `parent_id` |
| `res.partner` | Customers/Stores | `name`, `type`, `is_company` |

### 3.2 Supabase Medallion Schema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MEDALLION DATA ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────┐│
│  │   BRONZE    │────▶│   SILVER    │────▶│    GOLD     │────▶│PLATINUM ││
│  │  (Raw Data) │     │  (Cleaned)  │     │(Aggregated) │     │(Insights││
│  └─────────────┘     └─────────────┘     └─────────────┘     └─────────┘│
│                                                                         │
│  • pos_sessions      • transactions     • daily_sales     • ai_insights│
│  • transactions      • products         • store_kpis      • coaching   │
│  • line_items        • stores           • product_perf    • alerts     │
│  • payments          • customers        • trends          • forecasts  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Bronze Schema (Raw Data)

```sql
-- Raw POS sessions
CREATE TABLE scout_bronze.pos_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    odoo_id INTEGER NOT NULL,
    config_id INTEGER,
    store_name VARCHAR(255),
    user_id INTEGER,
    cashier_name VARCHAR(255),
    start_at TIMESTAMPTZ,
    stop_at TIMESTAMPTZ,
    state VARCHAR(20),
    cash_register_balance_start DECIMAL(15,2),
    cash_register_balance_end DECIMAL(15,2),
    raw_payload JSONB,
    ingested_at TIMESTAMPTZ DEFAULT now()
);

-- Raw transactions
CREATE TABLE scout_bronze.transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    odoo_id INTEGER NOT NULL,
    session_id UUID REFERENCES scout_bronze.pos_sessions(id),
    order_date TIMESTAMPTZ,
    partner_id INTEGER,
    customer_name VARCHAR(255),
    amount_total DECIMAL(15,2),
    amount_tax DECIMAL(15,2),
    amount_paid DECIMAL(15,2),
    state VARCHAR(20),
    raw_payload JSONB,
    ingested_at TIMESTAMPTZ DEFAULT now()
);

-- Raw line items
CREATE TABLE scout_bronze.line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    odoo_id INTEGER NOT NULL,
    transaction_id UUID REFERENCES scout_bronze.transactions(id),
    product_id INTEGER,
    product_name VARCHAR(255),
    qty DECIMAL(10,2),
    price_unit DECIMAL(15,2),
    discount DECIMAL(5,2),
    price_subtotal DECIMAL(15,2),
    price_subtotal_incl DECIMAL(15,2),
    raw_payload JSONB,
    ingested_at TIMESTAMPTZ DEFAULT now()
);
```

### 3.4 Silver Schema (Cleaned Data)

```sql
-- Cleaned transactions with foreign keys
CREATE TABLE scout_silver.transactions (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_time TIME NOT NULL,
    store_id UUID REFERENCES scout_dim.stores(id),
    customer_id UUID REFERENCES scout_dim.customers(id),
    cashier_id UUID,
    gross_amount DECIMAL(15,2) NOT NULL,
    tax_amount DECIMAL(15,2),
    discount_amount DECIMAL(15,2),
    net_amount DECIMAL(15,2) NOT NULL,
    item_count INTEGER,
    payment_method VARCHAR(50),
    is_valid BOOLEAN DEFAULT true,
    cleaned_at TIMESTAMPTZ DEFAULT now()
);

-- Cleaned line items with dimensions
CREATE TABLE scout_silver.line_items (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    transaction_id UUID REFERENCES scout_silver.transactions(id),
    product_id UUID REFERENCES scout_dim.products(id),
    category_id UUID REFERENCES scout_dim.categories(id),
    quantity DECIMAL(10,2) NOT NULL,
    unit_price DECIMAL(15,2) NOT NULL,
    discount_pct DECIMAL(5,2),
    line_total DECIMAL(15,2) NOT NULL,
    is_valid BOOLEAN DEFAULT true
);
```

### 3.5 Dimension Tables

```sql
-- Store dimension
CREATE TABLE scout_dim.stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    odoo_config_id INTEGER,
    store_code VARCHAR(50) NOT NULL,
    store_name VARCHAR(255) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    region VARCHAR(100),
    store_type VARCHAR(50),
    size_sqm DECIMAL(10,2),
    opening_date DATE,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB
);

-- Product dimension
CREATE TABLE scout_dim.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    odoo_id INTEGER,
    sku VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category_id UUID REFERENCES scout_dim.categories(id),
    brand VARCHAR(100),
    unit_price DECIMAL(15,2),
    cost_price DECIMAL(15,2),
    is_active BOOLEAN DEFAULT true
);

-- Category dimension
CREATE TABLE scout_dim.categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    odoo_id INTEGER,
    name VARCHAR(255) NOT NULL,
    parent_id UUID REFERENCES scout_dim.categories(id),
    level INTEGER,
    path VARCHAR(500)
);

-- Customer dimension
CREATE TABLE scout_dim.customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    odoo_id INTEGER,
    customer_code VARCHAR(50),
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    customer_type VARCHAR(50),
    loyalty_tier VARCHAR(50),
    first_purchase_date DATE,
    total_purchases DECIMAL(15,2),
    is_active BOOLEAN DEFAULT true
);
```

### 3.6 Gold Schema (Aggregated Data)

```sql
-- Daily store sales
CREATE TABLE scout_gold.daily_store_sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    store_id UUID REFERENCES scout_dim.stores(id),
    sale_date DATE NOT NULL,
    transaction_count INTEGER,
    gross_sales DECIMAL(15,2),
    net_sales DECIMAL(15,2),
    tax_collected DECIMAL(15,2),
    discounts_given DECIMAL(15,2),
    avg_basket_size DECIMAL(15,2),
    items_sold INTEGER,
    unique_customers INTEGER,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (tenant_id, store_id, sale_date)
);

-- Product performance
CREATE TABLE scout_gold.product_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    product_id UUID REFERENCES scout_dim.products(id),
    period_type VARCHAR(20), -- 'daily', 'weekly', 'monthly'
    period_start DATE,
    period_end DATE,
    units_sold DECIMAL(10,2),
    revenue DECIMAL(15,2),
    gross_margin DECIMAL(15,2),
    store_count INTEGER,
    avg_price DECIMAL(15,2),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Store KPIs
CREATE TABLE scout_gold.store_kpis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    store_id UUID REFERENCES scout_dim.stores(id),
    kpi_date DATE NOT NULL,
    -- Sales KPIs
    sales_target DECIMAL(15,2),
    sales_actual DECIMAL(15,2),
    sales_achievement_pct DECIMAL(5,2),
    -- Traffic KPIs
    foot_traffic INTEGER,
    conversion_rate DECIMAL(5,2),
    -- Product KPIs
    top_product_id UUID,
    top_category_id UUID,
    -- Trend indicators
    sales_vs_prev_day DECIMAL(5,2),
    sales_vs_prev_week DECIMAL(5,2),
    sales_vs_prev_month DECIMAL(5,2)
);

-- Category trends
CREATE TABLE scout_gold.category_trends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    category_id UUID REFERENCES scout_dim.categories(id),
    trend_date DATE NOT NULL,
    trend_period VARCHAR(20),
    sales_amount DECIMAL(15,2),
    units_sold INTEGER,
    market_share_pct DECIMAL(5,2),
    growth_rate DECIMAL(5,2),
    trend_direction VARCHAR(20) -- 'up', 'down', 'stable'
);
```

### 3.7 Platinum Schema (AI Insights)

```sql
-- AI-generated insights
CREATE TABLE platinum.retail_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    insight_type VARCHAR(50), -- 'opportunity', 'risk', 'trend', 'recommendation'
    entity_type VARCHAR(50), -- 'store', 'product', 'category', 'customer'
    entity_id UUID,
    insight_date DATE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20), -- 'high', 'medium', 'low'
    confidence_score DECIMAL(3,2),
    data_points JSONB,
    action_items JSONB,
    generated_by VARCHAR(100),
    is_acknowledged BOOLEAN DEFAULT false,
    acknowledged_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- SariCoach coaching messages
CREATE TABLE saricoach.coaching_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    store_id UUID REFERENCES scout_dim.stores(id),
    owner_id UUID,
    message_date DATE NOT NULL,
    message_type VARCHAR(50), -- 'daily_brief', 'alert', 'tip', 'celebration'
    title VARCHAR(255),
    content TEXT NOT NULL,
    metrics JSONB,
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Forecasts
CREATE TABLE platinum.sales_forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    store_id UUID REFERENCES scout_dim.stores(id),
    forecast_date DATE NOT NULL,
    forecast_horizon INTEGER, -- days ahead
    predicted_sales DECIMAL(15,2),
    lower_bound DECIMAL(15,2),
    upper_bound DECIMAL(15,2),
    model_version VARCHAR(50),
    confidence_interval DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT now()
);
```

---

## 4. User Roles & Permissions

| Role | Odoo Group | Supabase Role | Permissions |
|------|------------|---------------|-------------|
| Retail Admin | `point_of_sale.group_pos_manager` | `retail_admin` | Full retail access |
| Store Owner | `point_of_sale.group_pos_user` | `sari_store_owner` | Own store data only |
| Brand Sponsor | - | `brand_sponsor` | Brand aggregate view |
| Analyst | - | `scout_viewer` | Read-only analytics |
| Cashier | `point_of_sale.group_pos_user` | - | POS operations only |

---

## 5. Key Workflows

### 5.1 Data Ingestion Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      SCOUT DATA PIPELINE                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ODOO POS          n8n INGESTION        SUPABASE                       │
│  ┌─────────┐      ┌─────────────┐      ┌──────────────────────────────┐│
│  │ Session │─────▶│ wf_scout_   │─────▶│  scout_bronze.pos_sessions   ││
│  │  Close  │      │  ingest     │      │  scout_bronze.transactions   ││
│  └─────────┘      └─────────────┘      │  scout_bronze.line_items     ││
│                                        └──────────────────────────────┘│
│                                                    │                    │
│                                                    ▼                    │
│                   ┌─────────────┐      ┌──────────────────────────────┐│
│                   │ wf_scout_   │─────▶│  scout_silver.transactions   ││
│                   │  transform  │      │  scout_silver.line_items     ││
│                   └─────────────┘      │  scout_dim.*                 ││
│                                        └──────────────────────────────┘│
│                                                    │                    │
│                                                    ▼                    │
│                   ┌─────────────┐      ┌──────────────────────────────┐│
│                   │ wf_scout_   │─────▶│  scout_gold.daily_store_sales││
│                   │  aggregate  │      │  scout_gold.product_perf     ││
│                   └─────────────┘      │  scout_gold.store_kpis       ││
│                                        └──────────────────────────────┘│
│                                                    │                    │
│                                                    ▼                    │
│                   ┌─────────────┐      ┌──────────────────────────────┐│
│                   │ wf_saricoach│─────▶│  platinum.retail_insights    ││
│                   │  _generate  │      │  saricoach.coaching_messages ││
│                   └─────────────┘      └──────────────────────────────┘│
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Pipeline Stages:**

1. **Bronze Ingestion** (Real-time)
   - Trigger: POS session close in Odoo
   - n8n fetches session, orders, lines, payments
   - Store raw JSON in bronze tables
   - **Workflow:** `wf_scout_ingest`

2. **Silver Transformation** (Every 15 min)
   - Clean and validate bronze data
   - Resolve foreign keys to dimensions
   - Apply business rules
   - **Workflow:** `wf_scout_transform`

3. **Gold Aggregation** (Hourly/Daily)
   - Calculate daily aggregates
   - Compute KPIs and trends
   - Update performance metrics
   - **Workflow:** `wf_scout_aggregate`

4. **Platinum AI Generation** (Daily)
   - Generate AI insights
   - Create coaching messages
   - Calculate forecasts
   - **Workflow:** `wf_saricoach_generate`

### 5.2 POS Session Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. Open    │────▶│  2. Process │────▶│  3. Close   │────▶│  4. Sync    │
│   Session   │     │   Sales     │     │   Session   │     │   to Scout  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
    Opening          In Progress          Closing            Synced
```

**Step-by-Step:**

1. **Open Session** (Odoo POS)
   - Cashier opens POS session
   - Enter opening balance
   - Session state: `opening_control`

2. **Process Sales** (Odoo POS)
   - Ring up transactions
   - Accept payments (cash, card, e-wallet)
   - Session state: `opened`

3. **Close Session** (Odoo POS)
   - Close session at end of shift
   - Enter closing balance
   - Session state: `closing_control` → `closed`
   - **Triggers:** `wf_pos_session_close`

4. **Sync to Scout** (n8n)
   - n8n webhook captures close event
   - Fetch session data via Odoo API
   - Insert to bronze tables
   - **Triggers:** `wf_scout_ingest`

### 5.3 SariCoach Daily Brief

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SARICOACH DAILY BRIEF                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Good morning, Store Owner! Here's your daily brief for Store #123:    │
│                                                                         │
│  📊 Yesterday's Performance                                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Sales: ₱45,230 (+12% vs target)  ✅                            │   │
│  │  Transactions: 87 (+5% vs avg)                                  │   │
│  │  Avg Basket: ₱520 (+8% vs avg)                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  🏆 Top Performers                                                     │
│  1. Rice (25kg) - 45 units sold                                        │
│  2. Cooking Oil - 38 units sold                                        │
│  3. Canned Sardines - 72 units sold                                    │
│                                                                         │
│  💡 Today's Tips                                                       │
│  • Stock up on Rice - running low based on current sales velocity      │
│  • Consider promoting Cooking Oil combo with Rice                      │
│  • Payday weekend coming - prepare for higher traffic                  │
│                                                                         │
│  ⚠️ Alerts                                                             │
│  • Sugar inventory below safety stock (15 units remaining)             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Generation Process:**

1. **Daily Aggregation** (5 AM)
   - Calculate previous day metrics
   - Compare to targets and averages
   - Identify anomalies

2. **AI Analysis** (5:30 AM)
   - Generate insights from data patterns
   - Create personalized tips
   - Flag alerts and opportunities

3. **Message Delivery** (6 AM)
   - Store in `saricoach.coaching_messages`
   - Push notification via Mattermost
   - Mobile app notification (if available)

---

## 6. Integrations

### 6.1 Supabase Tables/Views

| Supabase Schema | Description | RLS |
|-----------------|-------------|-----|
| `scout_bronze.*` | Raw ingested data | tenant_id |
| `scout_silver.*` | Cleaned transactions | tenant_id |
| `scout_dim.*` | Dimension tables | tenant_id |
| `scout_gold.*` | Aggregated metrics | tenant_id |
| `scout_fact.*` | Fact tables | tenant_id |
| `saricoach.*` | Coaching content | tenant_id + store_id |
| `platinum.*` | AI insights | tenant_id |
| `analytics.*` | Custom analytics | tenant_id |

### 6.2 n8n Workflows

| Workflow ID | Trigger | Action | Target |
|-------------|---------|--------|--------|
| `wf_pos_session_close` | Session closed | Capture event | n8n webhook |
| `wf_scout_ingest` | Session close event | Fetch & store raw | `scout_bronze.*` |
| `wf_scout_transform` | Every 15 min | Clean data | `scout_silver.*` |
| `wf_scout_aggregate` | Hourly | Aggregate metrics | `scout_gold.*` |
| `wf_saricoach_generate` | Daily 5:30 AM | Generate coaching | `saricoach.*` |
| `wf_product_sync` | Product change | Sync dimension | `scout_dim.products` |
| `wf_store_sync` | POS config change | Sync dimension | `scout_dim.stores` |
| `wf_inventory_alert` | Below safety stock | Alert store owner | Mattermost |

### 6.3 AI Agents/Tools

| Agent | Capability | Use Case |
|-------|------------|----------|
| **SariCoach** | Daily coaching for store owners | "How's my store doing?" |
| **Retail Analyst** | Deep-dive analytics | "Why did sales drop last week?" |
| **Demand Forecaster** | Sales predictions | "What should I stock for next week?" |
| **Inventory Optimizer** | Stock recommendations | "When should I reorder Rice?" |
| **Promo Advisor** | Promotion suggestions | "What promotions will work best?" |

---

## 7. Configuration Guide

### 7.1 POS Configuration

| Setting | Value | Notes |
|---------|-------|-------|
| Point of Sale Name | Store-specific | e.g., "SM Makati Branch" |
| Receipt Header | Company info | Logo, address, TIN |
| Payment Methods | Cash, GCash, Maya, Card | Configure per store |
| Price List | Standard/Promo | Can vary by location |
| Stock Location | Store warehouse | Link to stock location |

### 7.2 Product Setup

```
Product Categories:
├── Food & Beverages
│   ├── Rice & Grains
│   ├── Canned Goods
│   ├── Beverages
│   └── Snacks
├── Personal Care
│   ├── Soap & Shampoo
│   └── Toiletries
├── Household
│   ├── Cleaning Supplies
│   └── Laundry
└── Others
    ├── Tobacco
    └── Miscellaneous
```

### 7.3 Scout Pipeline Configuration

```yaml
# scout_config.yaml
ingestion:
  batch_size: 1000
  retry_attempts: 3
  retry_delay_ms: 5000

transformation:
  dedup_window_hours: 24
  validation_rules:
    - amount_positive
    - valid_product_ref
    - valid_store_ref

aggregation:
  daily_run_time: "00:30"
  weekly_run_day: "monday"
  monthly_run_day: 1

ai:
  model: "claude-3-sonnet"
  max_tokens: 1500
  temperature: 0.7
  coaching_style: "friendly_filipino"
```

---

## 8. Reports & Analytics

### 8.1 Superset Dashboards

| Dashboard | Location | Key Metrics |
|-----------|----------|-------------|
| Store Overview | `/superset/dashboard/scout-store` | Sales, traffic, conversion |
| Product Performance | `/superset/dashboard/scout-products` | Units, revenue, margin |
| Category Analysis | `/superset/dashboard/scout-categories` | Share, trends, growth |
| Regional View | `/superset/dashboard/scout-regional` | Region comparisons |
| SariCoach Insights | `/superset/dashboard/saricoach` | AI insights, alerts |

### 8.2 Standard Reports

- Daily Sales Summary
- Weekly Performance Report
- Monthly Category Trends
- Store Comparison Report
- Product Movement Report
- Inventory Velocity Report

---

## 9. Delta from Official Odoo Docs

| Topic | Official Odoo Docs | InsightPulseAI Differences |
|-------|-------------------|---------------------------|
| POS Reports | Basic session reports | Full medallion analytics in Supabase |
| Multi-store | Single company | Multi-tenant with RLS |
| Real-time Data | Session-based | Streaming via n8n webhooks |
| AI Insights | Not available | SariCoach AI coaching |
| Mobile | Basic Odoo mobile | Custom mobile dashboard planned |
| Forecasting | Not available | E3 Intelligence predictions |
| Loyalty | Basic | Customer dimension with tiers |

---

## 10. Known Limitations & Phase 2+ Items

### Current Limitations

- **No offline POS**: Requires internet connection
- **No real-time sync**: Near real-time (15-min batches)
- **Limited mobile app**: Web dashboards only

### Phase 2 Roadmap

- [ ] Offline POS with sync-on-connect
- [ ] Real-time streaming with Supabase Realtime
- [ ] Mobile SariCoach app (Flutter)
- [ ] Automated reorder suggestions
- [ ] Customer loyalty program integration
- [ ] Competitor price monitoring

---

> **InsightPulseAI Integration:**
> - **Data flows to:** `scout_bronze.*` → `scout_silver.*` → `scout_gold.*` → `platinum.*`
> - **Used by engines:** Retail-Intel, E1 Data Intake, E3 Intelligence, E4 Creative
> - **Triggered automations:** `wf_scout_ingest`, `wf_scout_transform`, `wf_saricoach_generate`
> - **AI agents:** SariCoach, Retail Analyst, Demand Forecaster, Inventory Optimizer

---

## References

- [Odoo 18 POS Documentation](https://www.odoo.com/documentation/18.0/applications/sales/point_of_sale.html)
- [OCA pos modules](https://github.com/OCA/pos)
- [InsightPulseAI Technical Architecture](../architecture/INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md)
