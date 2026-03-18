# Public Seed Data Registry for Odoo Enterprise Platform

> Research date: 2026-03-17
> Purpose: Identify real, publicly available datasets to seed an Odoo-centered enterprise platform
> Platform context: Odoo CE 19.0 + OCA, operating in the Philippines (PH)

---

## Table of Contents

1. [Retail / Commerce](#1-retail--commerce)
2. [Marketing](#2-marketing)
3. [Finance / FinOps](#3-finance--finops)
4. [ERP / CRM / HR](#4-erp--crm--hr)
5. [Media / Entertainment](#5-media--entertainment)
6. [Agent / Workflow](#6-agent--workflow)
7. [Philippines / SEA Specific](#7-philippines--sea-specific)
8. [Odoo Built-in Demo Data](#8-odoo-built-in-demo-data)
9. [Synthetic Data Generators](#9-synthetic-data-generators)
10. [Platform Sample Datasets](#10-platform-sample-datasets-databricks-dbt-fivetran)
11. [Government Open Data](#11-government-open-data)
12. [Gap Analysis & Recommendations](#12-gap-analysis--recommendations)

---

## 1. Retail / Commerce

### 1.1 Brazilian E-Commerce (Olist) -- TOP PICK

| Field | Value |
|-------|-------|
| **Name** | Brazilian E-Commerce Public Dataset by Olist |
| **URL** | https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce |
| **License** | CC BY-NC-SA 4.0 |
| **Size** | ~100K orders, 8 CSV files, ~45 MB |
| **Schema** | `olist_orders_dataset.csv` (order_id, customer_id, order_status, timestamps), `olist_order_items_dataset.csv` (order_id, product_id, seller_id, price, freight), `olist_products_dataset.csv` (product_id, category, dimensions, weight), `olist_customers_dataset.csv` (customer_id, zip, city, state), `olist_order_payments_dataset.csv` (payment_type, installments, value), `olist_order_reviews_dataset.csv` (review_score, comment), `olist_sellers_dataset.csv`, `olist_geolocation_dataset.csv` |
| **Odoo fit** | Excellent. Maps directly to: `sale.order`, `sale.order.line`, `product.template`, `res.partner` (customers + sellers), `account.payment`, `stock.picking`. Multi-table relational structure mirrors ERP data model. |
| **Gaps** | Brazilian locale (needs PH adaptation). No inventory/stock levels. No chart of accounts. |

### 1.2 UCI Online Retail II

| Field | Value |
|-------|-------|
| **Name** | Online Retail II |
| **URL** | https://archive.ics.uci.edu/dataset/502/online+retail+ii |
| **Alt URL** | https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci |
| **License** | CC BY 4.0 |
| **Size** | ~1M transactions, ~43.5 MB |
| **Schema** | Invoice, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country |
| **Odoo fit** | Good. Maps to `account.move` (invoices), `product.product` (StockCode), `sale.order.line`. Includes cancellations (prefix 'C'). UK-based gift retailer. |
| **Gaps** | Flat single-table. No customer names/addresses. No payment details. |

### 1.3 Instacart Market Basket Analysis

| Field | Value |
|-------|-------|
| **Name** | Instacart Online Grocery Shopping Dataset 2017 |
| **URL** | https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis |
| **Alt URL** | https://www.instacart.com/datasets/grocery-shopping-2017 |
| **License** | Non-commercial use only |
| **Size** | 3M+ orders, 200K+ users, 50K products |
| **Schema** | orders (order_id, user_id, order_dow, order_hour), products (product_id, product_name, aisle_id, department_id), order_products (order_id, product_id, add_to_cart_order, reordered), aisles, departments |
| **Odoo fit** | Good for `product.category` hierarchy (departments > aisles > products) and `sale.order` / `sale.order.line`. Large volume for stress testing. |
| **Gaps** | No pricing data. No customer demographics. Grocery-specific categories. |

### 1.4 Tableau Superstore

| Field | Value |
|-------|-------|
| **Name** | Sample Superstore Dataset |
| **URL** | https://www.kaggle.com/datasets/vivek468/superstore-dataset-final |
| **Alt URL** | https://www.kaggle.com/datasets/truongdai/tableau-sample-superstore |
| **License** | Public domain / Tableau sample |
| **Size** | ~10K rows |
| **Schema** | Row ID, Order ID, Order Date, Ship Date, Ship Mode, Customer ID, Customer Name, Segment, Country, City, State, Postal Code, Region, Product ID, Category, Sub-Category, Product Name, Sales, Quantity, Discount, Profit |
| **Odoo fit** | Compact but comprehensive. Maps to `sale.order`, `product.template`, `res.partner`, `product.category`. Includes profit margins and shipping. Good for demos. |
| **Gaps** | US-only geography. Small dataset. No inventory or payment data. |

### 1.5 Amazon Products Dataset (1.4M)

| Field | Value |
|-------|-------|
| **Name** | Amazon Products Dataset 2023 (1.4M Products) |
| **URL** | https://www.kaggle.com/datasets/asaniczka/amazon-products-dataset-2023-1-4m-products |
| **License** | CC0 (Public Domain) |
| **Size** | 1.4M products |
| **Schema** | Product name, category, sub-category, price, rating, number of reviews, ASIN |
| **Odoo fit** | Massive product catalog for `product.template` and `product.category` seeding. |
| **Gaps** | No transaction/order data. No customer data. Amazon-specific categories. |

### 1.6 Retail Sales Dataset (Sample Transactions)

| Field | Value |
|-------|-------|
| **Name** | Retail Sales Dataset - Sample Transactions |
| **URL** | https://www.kaggle.com/datasets/bekkarmerwan/retail-sales-dataset-sample-transactions |
| **License** | Public |
| **Size** | ~1K rows |
| **Schema** | Transaction ID, Date, Customer ID, Gender, Age, Product Category, Quantity, Price per Unit, Total Amount |
| **Odoo fit** | Simple, clean. Good for quick `sale.order` prototyping with customer demographics. |
| **Gaps** | Very small. No product details. No payment/shipping info. |

---

## 2. Marketing

### 2.1 Marketing Campaign Performance

| Field | Value |
|-------|-------|
| **Name** | Marketing Campaign Performance Dataset |
| **URL** | https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset |
| **License** | Public |
| **Size** | ~200K rows |
| **Schema** | Campaign_ID, Company, Campaign_Type (Email/Social Media/Influencer/Display/Search), Target_Audience, Duration, Channel_Used, Conversion_Rate, Acquisition_Cost, ROI, Location, Language, Clicks, Impressions, Engagement_Score, Customer_Segment, Date |
| **Odoo fit** | Maps to `utm.campaign`, `utm.source`, `utm.medium`. Conversion and ROI data useful for marketing analytics dashboards in Superset. |
| **Gaps** | No individual lead/contact records. Aggregate metrics only. |

### 2.2 Email Campaign Management for SME

| Field | Value |
|-------|-------|
| **Name** | Email Campaign Management for SME |
| **URL** | https://www.kaggle.com/datasets/loveall/email-campaign-management-for-sme |
| **License** | CC BY-NC-SA 4.0 |
| **Size** | ~2.5K rows |
| **Schema** | Email_ID, Email_Type, Subject_Hotness_Score, Source, Customer_Location, Time_Email_sent_Category, Word_Count, Total_Links, Total_Images, Email_Status (opened/clicked/ignored) |
| **Odoo fit** | Maps to Odoo mass mailing (`mailing.mailing`, `mailing.trace`). Email open/click tracking. |
| **Gaps** | Small dataset. No actual email content. No customer identity fields. |

### 2.3 Digital Marketing Conversion Prediction

| Field | Value |
|-------|-------|
| **Name** | Predict Conversion in Digital Marketing Dataset |
| **URL** | https://www.kaggle.com/datasets/rabieelkharoua/predict-conversion-in-digital-marketing-dataset |
| **License** | Public |
| **Size** | ~8.8K rows |
| **Schema** | Age, Gender, Income, CampaignChannel (Email/PPC/Referral/SEO/Social), CampaignType, AdSpend, ClickThroughRate, ConversionRate, WebsiteVisits, PagesPerVisit, TimeOnSite, SocialShares, EmailOpens, EmailClicks, PreviousPurchases, LoyaltyPoints, AdvertisingPlatform, AdvertisingTool, Conversion |
| **Odoo fit** | Rich behavioral data. Maps to `crm.lead` scoring and marketing attribution. Good for AI/ML model training. |
| **Gaps** | Synthetic data. No temporal dimension. No individual campaign IDs. |

### 2.4 Superstore Marketing Campaign

| Field | Value |
|-------|-------|
| **Name** | Superstore Marketing Campaign Dataset |
| **URL** | https://www.kaggle.com/datasets/ahsan81/superstore-marketing-campaign-dataset |
| **License** | Public |
| **Size** | ~2.2K rows |
| **Schema** | ID, Year_Birth, Education, Marital_Status, Income, Kidhome, Teenhome, Dt_Customer, Recency, MntWines, MntFruits, MntMeatProducts, MntFishProducts, MntSweetProducts, MntGoldProds, NumDealsPurchases, NumWebPurchases, NumCatalogPurchases, NumStorePurchases, NumWebVisitsMonth, AcceptedCmp1-5, Response, Complain |
| **Odoo fit** | Customer segmentation (RFM-like). Maps to `res.partner` demographics + purchase behavior. Campaign response tracking. |
| **Gaps** | No campaign details. No product-level transactions. |

---

## 3. Finance / FinOps

### 3.1 SEC EDGAR Financial Statement Extracts -- TOP PICK

| Field | Value |
|-------|-------|
| **Name** | SEC EDGAR Financial Statements & Notes Dataset |
| **URL** | https://www.sec.gov/about/developer-resources |
| **Bulk URL** | https://www.sec.gov/dera/data/financial-statement-data-sets |
| **API** | https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json |
| **License** | Public domain (US Government) |
| **Size** | Thousands of companies, quarterly dumps since 2009 |
| **Schema** | XBRL tags (Assets, Liabilities, Revenue, NetIncome, etc.), CIK, company name, filing date, fiscal period, value, units |
| **Odoo fit** | Chart of accounts reference data. Maps to `account.account` taxonomy. Financial statement structures for `account.financial.report`. |
| **Gaps** | US GAAP only (not Philippine PFRS). XBRL format needs parsing. No transaction-level data. |

### 3.2 Financial Transactions Dataset

| Field | Value |
|-------|-------|
| **Name** | Financial Transactions Dataset |
| **URL** | https://www.kaggle.com/datasets/cankatsrc/financial-transactions-dataset |
| **License** | Public |
| **Size** | ~100K rows |
| **Schema** | Transaction_ID, Customer_Name, Date, Amount, Transaction_Type (Debit/Credit), Account_Type, Balance, Currency |
| **Odoo fit** | Maps to `account.move.line` (journal entries). Debit/Credit structure matches double-entry bookkeeping. |
| **Gaps** | No journal/account hierarchy. Single currency per row. No invoice linkage. |

### 3.3 Invoices Dataset

| Field | Value |
|-------|-------|
| **Name** | Invoices Dataset |
| **URL** | https://www.kaggle.com/datasets/cankatsrc/invoices |
| **License** | Public |
| **Size** | ~10K rows |
| **Schema** | Invoice_No, Date, Customer, Product, Quantity, Unit_Price, Total, Payment_Status, Payment_Date |
| **Odoo fit** | Direct map to `account.move` (type=out_invoice). Includes payment status for `account.payment` reconciliation. |
| **Gaps** | No tax calculations. No multi-line invoices. No vendor invoices (AP side). |

### 3.4 Customer Invoice Dataset (Payment Prediction)

| Field | Value |
|-------|-------|
| **Name** | Payment Date Prediction for Invoices Dataset |
| **URL** | https://www.kaggle.com/datasets/pradumn203/payment-date-prediction-for-invoices-dataset |
| **License** | Public |
| **Size** | ~50K rows |
| **Schema** | Invoice details with payment terms, actual payment dates, customer info, amounts |
| **Odoo fit** | Maps to `account.move` + `account.payment.term`. Excellent for testing AR aging and payment prediction models. |
| **Gaps** | No line items. No product linkage. |

### 3.5 Financial Statements of Major Companies

| Field | Value |
|-------|-------|
| **Name** | Financial Statements of Major Companies (2009-2023) |
| **URL** | https://www.kaggle.com/datasets/rish59/financial-statements-of-major-companies2009-2023 |
| **License** | Public |
| **Size** | Multi-year, multiple companies |
| **Schema** | Balance sheet, income statement, cash flow statement line items |
| **Odoo fit** | Reference for `account.financial.report` templates. Validates MIS Builder report structures. |
| **Gaps** | Summary-level only. No journal entries. US companies only. |

### 3.6 Philippine Government Chart of Accounts

| Field | Value |
|-------|-------|
| **Name** | Revised Chart of Accounts (UACS) |
| **URL** | https://uacs.gov.ph/resources/uacs/object-code/chart-of-accounts |
| **Alt URL** | https://www.coa.gov.ph/download/4944/cy-2015/66003/coa_c2015-010_annexa.pdf |
| **License** | Public (Philippine Government) |
| **Size** | ~500 account codes |
| **Schema** | Account code (hierarchical), account name, account type (Asset/Liability/Equity/Revenue/Expense) |
| **Odoo fit** | Reference for building PH-compliant `account.account` chart. Needed for BIR compliance. PDF format requires parsing. |
| **Gaps** | Government-focused (not private sector). PDF not CSV. Needs manual mapping to Odoo account types. |

### 3.7 BIR Chart of Accounts Reference

| Field | Value |
|-------|-------|
| **Name** | BIR Chart of Accounts |
| **URL** | https://www.scribd.com/document/340086752/BIR-Chart-of-Accounts |
| **License** | Public reference (BIR guidance) |
| **Schema** | Account codes for Philippine private-sector bookkeeping aligned with BIR requirements |
| **Odoo fit** | Direct reference for `l10n_ph` chart of accounts in Odoo. Essential for tax-compliant PH deployment. |
| **Gaps** | Scribd access may require account. Not machine-readable. |

---

## 4. ERP / CRM / HR

### 4.1 Customer Relationship Management Dataset

| Field | Value |
|-------|-------|
| **Name** | Customer Relationship Management Dataset |
| **URL** | https://www.kaggle.com/datasets/gaurobsaha/customer-relationship-management-dataset |
| **License** | Public |
| **Size** | ~5K rows |
| **Schema** | Customer demographics, purchase history, interaction channels, satisfaction scores, churn indicators |
| **Odoo fit** | Maps to `res.partner` + `crm.lead`. Customer lifecycle data for CRM pipeline seeding. |
| **Gaps** | No opportunity/deal stages. No activity log. |

### 4.2 Customer Support Ticket Dataset

| Field | Value |
|-------|-------|
| **Name** | Customer Support Ticket Dataset |
| **URL** | https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset |
| **License** | Public |
| **Size** | ~50K tickets |
| **Schema** | Ticket_ID, Customer_Name, Customer_Email, Customer_Age, Customer_Gender, Product_Purchased, Date_of_Purchase, Ticket_Type (Technical/Billing/General), Ticket_Subject, Ticket_Description, Ticket_Status, Resolution, Ticket_Priority, Ticket_Channel, First_Response_Time, Time_to_Resolution, Customer_Satisfaction_Rating |
| **Odoo fit** | Excellent for `helpdesk.ticket` (OCA helpdesk or custom). Maps to support workflow with SLA metrics. |
| **Gaps** | No internal assignment/team data. No knowledge base linkage. |

### 4.3 Multilingual Customer Support Tickets

| Field | Value |
|-------|-------|
| **Name** | Multilingual Customer Support Tickets |
| **URL** | https://www.kaggle.com/datasets/tobiasbueck/multilingual-customer-support-tickets |
| **Alt URL** | https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets |
| **License** | Public |
| **Size** | Multi-language (EN, FR, ES, PT) |
| **Schema** | Ticket text, language, category, priority |
| **Odoo fit** | Multi-language support testing. NLP/AI agent training data for ticket classification. |
| **Gaps** | No structured CRM fields. Text-heavy. |

### 4.4 IBM HR Analytics (Employee Attrition) -- TOP PICK

| Field | Value |
|-------|-------|
| **Name** | IBM HR Analytics Employee Attrition & Performance |
| **URL** | https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset |
| **License** | Public (IBM sample) |
| **Size** | 1,470 employees, 35 fields |
| **Schema** | Age, Attrition, BusinessTravel, DailyRate, Department, DistanceFromHome, Education, EducationField, EnvironmentSatisfaction, Gender, HourlyRate, JobInvolvement, JobLevel, JobRole, JobSatisfaction, MaritalStatus, MonthlyIncome, MonthlyRate, NumCompaniesWorked, OverTime, PercentSalaryHike, PerformanceRating, RelationshipSatisfaction, StockOptionLevel, TotalWorkingYears, TrainingTimesLastYear, WorkLifeBalance, YearsAtCompany, YearsInCurrentRole, YearsSinceLastPromotion, YearsWithCurrManager |
| **Odoo fit** | Maps to `hr.employee`, `hr.department`, `hr.job`. Rich demographic + compensation data for HR module seeding. |
| **Gaps** | No leave/attendance data. No payroll transactions. No recruitment pipeline. US-centric job roles. |

### 4.5 Human Resources Data Set

| Field | Value |
|-------|-------|
| **Name** | Human Resources Data Set |
| **URL** | https://www.kaggle.com/datasets/rhuebner/human-resources-data-set |
| **License** | CC BY-SA 4.0 |
| **Size** | ~300 employees |
| **Schema** | Employee_Name, EmpID, MarriedID, MaritalStatusID, GenderID, EmpStatusID, DeptID, PerfScoreID, FromDiversityJobFairID, Salary, Termd, PositionID, Position, State, Zip, DOB, Sex, MaritalDesc, CitizenDesc, HispanicLatino, RaceDesc, DateofHire, DateofTermination, TermReason, EmploymentStatus, Department, ManagerName, ManagerID, RecruitmentSource, PerformanceScore, EngagementSurvey, EmpSatisfaction, SpecialProjectsCount, LastPerformanceReview_Date, DaysLateLast30, Absences |
| **Odoo fit** | More complete than IBM for `hr.employee` + `hr.department` + manager hierarchy. Includes termination reasons and recruitment source. |
| **Gaps** | Small dataset. US-specific. No payroll/leave transactions. |

### 4.6 Support Ticket Priority Dataset (50K)

| Field | Value |
|-------|-------|
| **Name** | Support Ticket Priority Dataset (50K) |
| **URL** | https://www.kaggle.com/datasets/albertobircoci/support-ticket-priority-dataset-50k |
| **License** | Public |
| **Size** | 50K tickets |
| **Schema** | Ticket priority levels, categories, descriptions |
| **Odoo fit** | Volume testing for helpdesk/support modules. Priority classification training data. |
| **Gaps** | Limited structured fields. |

---

## 5. Media / Entertainment

### 5.1 MovieLens -- TOP PICK

| Field | Value |
|-------|-------|
| **Name** | MovieLens Latest Dataset |
| **URL** | https://grouplens.org/datasets/movielens/ |
| **Kaggle** | https://www.kaggle.com/datasets/grouplens/movielens-20m-dataset |
| **License** | Free for research/education |
| **Size** | Multiple versions: 100K, 1M, 10M, 20M, 32M ratings |
| **Schema** | `movies.csv` (movieId, title, genres), `ratings.csv` (userId, movieId, rating, timestamp), `tags.csv` (userId, movieId, tag, timestamp), `links.csv` (movieId, imdbId, tmdbId) |
| **Odoo fit** | Content catalog model for media companies. Maps to custom product catalog with ratings/reviews. Useful for recommendation engine testing. |
| **Gaps** | Movies only. No revenue/financial data. No content production metadata. |

### 5.2 Entertainment (Movies, TV Shows) Database

| Field | Value |
|-------|-------|
| **Name** | Entertainment (Movies, TV Shows) Dataset |
| **URL** | https://www.kaggle.com/datasets/priyanshuganwani09/entertainment-movies-tv-shows-database |
| **License** | Public |
| **Schema** | Title, type (movie/TV), genre, release date, runtime, rating, description |
| **Odoo fit** | Content catalog seeding. Maps to `product.template` with custom fields for media attributes. |
| **Gaps** | No audience metrics. No engagement data. No financial data. |

### 5.3 Streaming Activity Dataset

| Field | Value |
|-------|-------|
| **Name** | Streaming Activity Dataset |
| **URL** | https://www.kaggle.com/datasets/thedevastator/streaming-activity-dataset |
| **License** | Public |
| **Schema** | User activity, streaming duration, content consumed |
| **Odoo fit** | Engagement analytics. Could feed Superset dashboards for media clients. |
| **Gaps** | No content metadata. No revenue data. |

### 5.4 Social Media Engagement Metrics

| Field | Value |
|-------|-------|
| **Name** | Social Media Viral Content & Engagement Metrics |
| **URL** | https://www.kaggle.com/datasets/aliiihussain/social-media-viral-content-and-engagement-metrics |
| **License** | Public |
| **Schema** | Content type, platform, likes, shares, comments, engagement rate, viral score |
| **Odoo fit** | Social media analytics. Feeds marketing dashboards. Content performance benchmarking. |
| **Gaps** | No content catalog linkage. No customer/contact mapping. |

---

## 6. Agent / Workflow

### 6.1 Agentic AI Performance Dataset 2025

| Field | Value |
|-------|-------|
| **Name** | Agentic AI Performance and Capabilities Dataset |
| **URL** | https://www.kaggle.com/datasets/bismasajjad/agentic-ai-performance-and-capabilities-dataset |
| **License** | Public |
| **Schema** | Agent performance metrics, task types, completion rates, capabilities |
| **Odoo fit** | Benchmarking agent workflows. Testing agent orchestration in MCP coordinator. |
| **Gaps** | Synthetic/survey data. Not transaction-level. |

### 6.2 AI Workforce & Automation Dataset

| Field | Value |
|-------|-------|
| **Name** | AI Workforce and Automation Dataset (2015-2025) |
| **URL** | https://www.kaggle.com/datasets/emirhanakku/ai-workforce-and-automation-dataset-20152025 |
| **License** | Public |
| **Schema** | Industry, automation level, workforce impact, technology adoption metrics |
| **Odoo fit** | Reference data for automation planning. Useful for ops dashboards. |
| **Gaps** | Aggregate industry data. No task-level workflow data. |

### 6.3 dbt Jaffle Shop (Workflow Simulation) -- TOP PICK

| Field | Value |
|-------|-------|
| **Name** | Jaffle Shop Data |
| **URL** | https://github.com/dbt-labs/jaffle-shop-data |
| **Classic** | https://github.com/dbt-labs/jaffle-shop-classic |
| **License** | Apache 2.0 |
| **Size** | ~1 year of generated data (scalable via jafgen) |
| **Schema** | `raw_customers.csv` (id, first_name, last_name), `raw_orders.csv` (id, user_id, order_date, status), `raw_payments.csv` (id, order_id, payment_method, amount) |
| **Odoo fit** | Clean relational data for testing ERP data pipelines (Bronze > Silver > Gold). Scalable generation. Perfect for Databricks lakehouse testing. |
| **Gaps** | Minimal schema. No products. No inventory. Fictional data. |

---

## 7. Philippines / SEA Specific

### 7.1 PSA OpenStat (Philippine Statistics Authority)

| Field | Value |
|-------|-------|
| **Name** | PSA OpenStat Database |
| **URL** | https://openstat.psa.gov.ph/ |
| **Database** | https://openstat.psa.gov.ph/Database |
| **License** | Public (Philippine Government) |
| **Schema** | Demographic statistics, economic indicators, trade data, price indices, employment data |
| **Odoo fit** | Philippine market reference data. Consumer Price Index for pricing models. Trade statistics for import/export module seeding. |
| **Gaps** | Aggregate statistics, not transactional. Requires manual extraction. |

### 7.2 Open Data Philippines Portal

| Field | Value |
|-------|-------|
| **Name** | Open Data Philippines (ODPH) |
| **URL** | https://data.gov.ph/ |
| **License** | Philippine Open Data License |
| **Schema** | Government datasets across agencies: procurement, budget, geographic, demographic |
| **Odoo fit** | Government procurement data for `purchase.order` seeding. Philippine geographic data for `res.country.state` and `res.city`. |
| **Gaps** | Inconsistent data quality. Many datasets are outdated. |

### 7.3 TMO Group SEA E-Commerce Data Packs

| Field | Value |
|-------|-------|
| **Name** | SEA E-Commerce Sales Data (Philippines - Shopee & Lazada) |
| **URL** | https://www.tmogroup.asia/insights/southeast-asia-ecommerce-data-monthly-updates/ |
| **PH Download** | https://www.tmogroup.asia/downloads/the-philippine-ecommerce-sales-estimates-april-2024/ |
| **License** | Free download (TMO Group research) |
| **Schema** | SKU counts, sales volumes, revenue by category, price range distribution, top products by revenue |
| **Odoo fit** | Philippine e-commerce market benchmarks. Product category and pricing reference for PH market. |
| **Gaps** | Aggregate estimates, not transactional. Monthly snapshots only. |

### 7.4 Shopee Product Matching (Kaggle Competition)

| Field | Value |
|-------|-------|
| **Name** | Shopee - Price Match Guarantee |
| **URL** | https://www.kaggle.com/c/shopee-product-matching/data |
| **License** | Competition rules (non-commercial) |
| **Size** | 34K+ product postings with images |
| **Schema** | posting_id, image, image_phash, title, label_group |
| **Odoo fit** | Product matching / deduplication testing. SEA product titles and images. |
| **Gaps** | No pricing. No transaction data. Image-focused. Competition data access restrictions. |

### 7.5 Shopee Sales Data Sample

| Field | Value |
|-------|-------|
| **Name** | Shopee Sales Data Apr-May 2023 |
| **URL** | https://www.kaggle.com/datasets/yoongsin/shopee-sample-data |
| **License** | Public |
| **Schema** | Product sales data from Shopee platform |
| **Odoo fit** | SEA marketplace reference data. |
| **Gaps** | Small sample. Limited timeframe. |

---

## 8. Odoo Built-in Demo Data

When creating an Odoo database with demo data enabled (`--demo=all` or checkbox during DB creation), modules automatically load sample records.

### What Odoo Demo Data Provides

| Module | Demo Records Created |
|--------|---------------------|
| `base` | ~10 res.company, ~50 res.partner (contacts), res.country/state (all countries), res.currency |
| `sale` | Sample quotations and sales orders, demo products |
| `purchase` | Sample RFQs and purchase orders |
| `account` | Chart of accounts (locale-dependent), sample journal entries, demo invoices |
| `stock` | Warehouse configuration, sample stock moves, demo products with stock levels |
| `crm` | Sample leads and opportunities at various stages, demo sales teams |
| `hr` | Sample employees, departments, job positions |
| `project` | Sample projects and tasks |
| `mrp` | Bills of materials, manufacturing orders |
| `website` | Sample website pages, themes, and product listings |
| `mail` | Sample messages and channels |

### How to Load Demo Data

```bash
# Load all demo data during DB creation
odoo-bin -d odoo_dev_demo -i base,sale,purchase,account,stock,crm,hr,project --demo=all --stop-after-init

# Demo data files are in each module's demo/ directory
# Example: vendor/odoo/addons/sale/demo/sale_demo.xml
```

### Limitations of Built-in Demo Data

- Very small volume (~50-100 records per module)
- Generic/fictional data (not industry-specific)
- No PH-specific locale data (no BIR chart of accounts)
- No realistic transaction volumes for performance testing
- Demo partners use placeholder addresses

---

## 9. Synthetic Data Generators

### 9.1 Python Faker

| Field | Value |
|-------|-------|
| **Name** | Faker |
| **URL** | https://github.com/joke2k/faker |
| **PyPI** | https://pypi.org/project/Faker/ |
| **License** | MIT |
| **Capabilities** | Names, addresses, emails, phone numbers, companies, dates, text, credit cards, SSNs (fake), localized data (PH locale: `faker.providers.address.fil_PH`) |
| **Odoo fit** | Generate `res.partner` records with Filipino names/addresses. Seed `hr.employee` with PH-localized data. Scale to any volume. |
| **Usage** | `pip install faker` then `from faker import Faker; fake = Faker('fil_PH')` |

### 9.2 PyDataFaker (ERP-specific)

| Field | Value |
|-------|-------|
| **Name** | PyDataFaker |
| **URL** | https://github.com/SamEdwardes/pydatafaker |
| **License** | MIT |
| **Capabilities** | Generates related ERP tables: invoices, vendors, purchase orders, employees, products with referential integrity |
| **Odoo fit** | Purpose-built for ERP seeding. Generates tables that map directly to Odoo models with proper foreign keys. |

---

## 10. Platform Sample Datasets (Databricks, dbt, Fivetran)

### 10.1 Databricks Built-in Samples

| Field | Value |
|-------|-------|
| **Name** | Databricks Sample Datasets |
| **URL** | https://docs.databricks.com/aws/en/discover/databricks-datasets |
| **Azure docs** | https://learn.microsoft.com/en-us/azure/databricks/discover/databricks-datasets |
| **Available in** | Unity Catalog `samples` schema |
| **Datasets** | `samples.nyctaxi.trips` (NYC taxi rides), `samples.tpch.*` (TPC-H benchmark: orders, customers, lineitem, part, supplier, nation, region), `samples.tpcds_sf1.*` (TPC-DS benchmark) |
| **Odoo fit** | TPC-H is excellent for testing lakehouse pipelines. `lineitem` + `orders` + `customer` + `supplier` mirror Odoo sale/purchase flows. Pre-loaded in workspace. |

### 10.2 Databricks Retail Org Sample

| Field | Value |
|-------|-------|
| **Name** | Databricks Retail Organization Sample Data |
| **Path** | `/databricks-datasets/retail-org/` (in workspace) |
| **GitHub** | https://github.com/databricks/Spark-The-Definitive-Guide/blob/master/data/retail-data/all/online-retail-dataset.csv |
| **Schema** | Sales orders (JSON), customer data (CSV), US-based customers, finished products |
| **Odoo fit** | Ready-to-use in Databricks workspace for lakehouse pipeline testing. |

### 10.3 Fivetran dbt Packages (Schema References)

| Package | URL | Schema |
|---------|-----|--------|
| Salesforce Source | https://github.com/fivetran/dbt_salesforce_source | Account, Contact, Lead, Opportunity, User |
| Stripe | https://github.com/fivetran/dbt_stripe | Payment, Charge, Customer, Invoice, Subscription |
| QuickBooks | https://github.com/fivetran/dbt_quickbooks | Account, Bill, Invoice, Payment, Vendor, Customer |

These packages define the **schema contracts** for common business data models. Useful as reference for mapping Odoo data to analytics-ready tables, even without Fivetran.

---

## 11. Government Open Data

### 11.1 Data.gov (US)

| Field | Value |
|-------|-------|
| **Name** | Data.gov Catalog |
| **URL** | https://catalog.data.gov/ |
| **Commerce** | https://data.commerce.gov/ |
| **License** | Public domain (US Government) |
| **Relevant datasets** | Business formation statistics, trade data, economic indicators, consumer spending |
| **Odoo fit** | Reference data for US market operations. Import/export trade data. |

### 11.2 Bureau of Economic Analysis (BEA)

| Field | Value |
|-------|-------|
| **Name** | BEA Open Data |
| **URL** | https://www.bea.gov/open-data |
| **License** | Public domain |
| **Schema** | GDP, personal income, international transactions, industry accounts |
| **Odoo fit** | Economic reference data for financial planning modules. |

---

## 12. Gap Analysis & Recommendations

### Coverage Matrix

| Domain | Dataset Coverage | Top Pick | Critical Gaps |
|--------|-----------------|----------|---------------|
| **Retail/Commerce** | Excellent | Olist (Brazilian) | No PH-specific retail transactions |
| **Marketing** | Good | Campaign Performance | No Odoo mass mailing format data |
| **Finance** | Moderate | SEC EDGAR + Invoices | No PH chart of accounts in CSV. No VAT/BIR tax data |
| **CRM** | Moderate | CRM Dataset + Support Tickets | No sales pipeline with stages matching Odoo CRM |
| **HR** | Good | IBM HR + Human Resources Set | No PH-specific employment data. No payroll |
| **Media** | Good | MovieLens | No revenue/business data for media companies |
| **Agents/Workflow** | Weak | Jaffle Shop (indirect) | No task orchestration datasets. No MCP test data |
| **PH/SEA** | Weak | PSA OpenStat + TMO | No transactional PH retail data. Government data is aggregate |

### Recommended Seed Strategy

**Phase 1 -- Immediate (public datasets)**:
1. Load Odoo demo data for base module structure
2. Import Olist dataset for sale/purchase/product/partner seeding (adapt locale)
3. Import IBM HR dataset for employee seeding
4. Import UCI Online Retail II for high-volume invoice testing
5. Import Jaffle Shop for lakehouse pipeline validation

**Phase 2 -- Generated (Faker + PyDataFaker)**:
1. Generate 10K Filipino `res.partner` records using `Faker('fil_PH')`
2. Generate PH-localized invoices, purchase orders, and products
3. Generate HR employee records with PH departments and positions
4. Build BIR-compliant chart of accounts from COA/UACS reference

**Phase 3 -- Enrichment (API + scraping where permitted)**:
1. Pull PSA OpenStat economic indicators for reference tables
2. Extract SEC EDGAR chart of accounts taxonomy as `account.account` template
3. Build PH product category tree from TMO Group data packs
4. Create CRM pipeline demo from CRM dataset + support tickets

### Key Gaps That Require Custom Generation

| Gap | Why It Matters | Recommended Approach |
|-----|---------------|---------------------|
| PH Chart of Accounts (BIR-compliant) | Tax compliance | Manual build from BIR/COA references + Odoo `l10n_ph` |
| PH Product Categories | Local market relevance | Derive from TMO/PSA data + Shopee/Lazada categories |
| Sales Pipeline with Odoo Stages | CRM module testing | Generate using Faker with Odoo stage names |
| Payroll Transactions | HR module testing | Generate using PyDataFaker with PH tax brackets |
| MCP Agent Task Data | Agent orchestration testing | Build custom dataset from n8n workflow logs |
| Multi-company Data | Multi-entity testing | Generate using Faker with multiple PH company profiles |

---

## File Format Notes for Odoo Import

All external datasets should be transformed to Odoo-compatible CSV format:

```
# res.partner import format
id,name,email,phone,street,city,state_id/id,country_id/id,company_type
__import__.partner_001,Juan dela Cruz,juan@example.ph,+639171234567,123 Rizal St,Makati,base.state_ph_00,base.ph,person

# product.template import format
id,name,type,categ_id/id,list_price,standard_price,sale_ok,purchase_ok
__import__.product_001,Widget A,consu,product.product_category_all,100.00,60.00,True,True

# account.move import format (invoices)
id,partner_id/id,move_type,invoice_date,invoice_line_ids/product_id/id,invoice_line_ids/quantity,invoice_line_ids/price_unit
```

---

*Registry maintained at: `/docs/research/seed-data-registry.md`*
*Next action: Execute Phase 1 imports with transformation scripts*
