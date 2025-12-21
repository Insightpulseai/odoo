-- Finance Seed Data
-- Expense categories, approval rules, budgets, and sample tasks

-- ============================================================================
-- EXPENSE CATEGORIES
-- ============================================================================
INSERT INTO finance_expense_categories (id, name, code, description, gl_account, requires_receipt, max_amount, requires_preapproval_above) VALUES
    -- Travel
    ('fc100000-0000-0000-0000-000000000001', 'Airfare', 'TRAVEL-AIR', 'Commercial airline tickets', '6100-10', true, 5000, 2000),
    ('fc100000-0000-0000-0000-000000000002', 'Lodging', 'TRAVEL-HOTEL', 'Hotel and accommodation', '6100-20', true, 500, NULL),
    ('fc100000-0000-0000-0000-000000000003', 'Ground Transportation', 'TRAVEL-GROUND', 'Taxi, Uber, Lyft, rental car', '6100-30', true, 200, NULL),
    ('fc100000-0000-0000-0000-000000000004', 'Parking & Tolls', 'TRAVEL-PARK', 'Parking fees and road tolls', '6100-40', true, 100, NULL),
    ('fc100000-0000-0000-0000-000000000005', 'Mileage Reimbursement', 'TRAVEL-MILE', 'Personal vehicle mileage', '6100-50', false, NULL, NULL),
    -- Meals
    ('fc100000-0000-0000-0000-000000000010', 'Meals - Client', 'MEALS-CLIENT', 'Client entertainment meals', '6200-10', true, 200, NULL),
    ('fc100000-0000-0000-0000-000000000011', 'Meals - Team', 'MEALS-TEAM', 'Team meals and events', '6200-20', true, 150, NULL),
    ('fc100000-0000-0000-0000-000000000012', 'Meals - Individual', 'MEALS-INDIV', 'Individual meal while traveling', '6200-30', true, 75, NULL),
    -- Office & Supplies
    ('fc100000-0000-0000-0000-000000000020', 'Office Supplies', 'OFFICE-SUPPLY', 'Stationery, printer supplies', '6300-10', true, 100, NULL),
    ('fc100000-0000-0000-0000-000000000021', 'Computer Equipment', 'OFFICE-COMP', 'Hardware, peripherals', '6300-20', true, 1000, 500),
    ('fc100000-0000-0000-0000-000000000022', 'Software & Subscriptions', 'OFFICE-SW', 'Software licenses, SaaS', '6300-30', true, 500, 200),
    ('fc100000-0000-0000-0000-000000000023', 'Books & Materials', 'OFFICE-BOOKS', 'Reference materials, books', '6300-40', true, 100, NULL),
    -- Professional Development
    ('fc100000-0000-0000-0000-000000000030', 'Training & Courses', 'TRAIN-COURSE', 'Training programs, certifications', '6400-10', true, 2000, 1000),
    ('fc100000-0000-0000-0000-000000000031', 'Conferences', 'TRAIN-CONF', 'Conference registration fees', '6400-20', true, 1500, 500),
    ('fc100000-0000-0000-0000-000000000032', 'Professional Memberships', 'TRAIN-MEMBER', 'Industry association dues', '6400-30', true, 500, NULL),
    -- Communications
    ('fc100000-0000-0000-0000-000000000040', 'Phone & Internet', 'COMM-PHONE', 'Mobile phone, home internet (WFH)', '6500-10', true, 150, NULL),
    ('fc100000-0000-0000-0000-000000000041', 'Shipping & Postage', 'COMM-SHIP', 'Package shipping, mail', '6500-20', true, 100, NULL),
    -- Other
    ('fc100000-0000-0000-0000-000000000050', 'Other Business Expense', 'OTHER', 'Miscellaneous business expenses', '6900-00', true, 250, 100);

-- ============================================================================
-- APPROVAL RULES
-- ============================================================================
INSERT INTO finance_approval_rules (id, name, rule_type, min_amount, max_amount, approval_level, approver_type, auto_approve, priority) VALUES
    -- Auto-approve small expenses
    ('ar100000-0000-0000-0000-000000000001', 'Auto-approve under $50', 'expense', 0, 50, 1, 'manager', true, 10),
    -- Manager approval
    ('ar100000-0000-0000-0000-000000000002', 'Manager approval $50-$500', 'expense', 50, 500, 1, 'manager', false, 20),
    -- Department head for medium expenses
    ('ar100000-0000-0000-0000-000000000003', 'Dept head approval $500-$2000', 'expense', 500, 2000, 1, 'manager', false, 30),
    ('ar100000-0000-0000-0000-000000000004', 'Dept head approval $500-$2000 L2', 'expense', 500, 2000, 2, 'department_head', false, 31),
    -- Finance approval for large expenses
    ('ar100000-0000-0000-0000-000000000005', 'Finance approval $2000-$5000', 'expense', 2000, 5000, 1, 'manager', false, 40),
    ('ar100000-0000-0000-0000-000000000006', 'Finance approval $2000-$5000 L2', 'expense', 2000, 5000, 2, 'department_head', false, 41),
    ('ar100000-0000-0000-0000-000000000007', 'Finance approval $2000-$5000 L3', 'expense', 2000, 5000, 3, 'finance', false, 42),
    -- Executive approval for very large
    ('ar100000-0000-0000-0000-000000000008', 'Executive approval $5000+', 'expense', 5000, NULL, 1, 'manager', false, 50),
    ('ar100000-0000-0000-0000-000000000009', 'Executive approval $5000+ L2', 'expense', 5000, NULL, 2, 'department_head', false, 51),
    ('ar100000-0000-0000-0000-000000000010', 'Executive approval $5000+ L3', 'expense', 5000, NULL, 3, 'finance', false, 52),
    ('ar100000-0000-0000-0000-000000000011', 'Executive approval $5000+ L4', 'expense', 5000, NULL, 4, 'executive', false, 53);

-- ============================================================================
-- BUDGETS (Current Fiscal Year)
-- ============================================================================
INSERT INTO finance_budgets (id, name, fiscal_year, fiscal_quarter, department_id, cost_center, allocated_amount, status, warning_threshold_pct, critical_threshold_pct) VALUES
    -- Executive
    ('fb100000-0000-0000-0000-000000000001', 'Executive Budget Q1', 2024, 'Q1', 'd1000000-0000-0000-0000-000000000001', 'CC-EXEC', 500000, 'active', 80, 95),
    -- Finance
    ('fb100000-0000-0000-0000-000000000010', 'Finance Budget Q1', 2024, 'Q1', 'd1000000-0000-0000-0000-000000000002', 'CC-FIN', 150000, 'active', 80, 95),
    ('fb100000-0000-0000-0000-000000000011', 'Finance Budget Q2', 2024, 'Q2', 'd1000000-0000-0000-0000-000000000002', 'CC-FIN', 150000, 'active', 80, 95),
    -- HR
    ('fb100000-0000-0000-0000-000000000020', 'HR Budget Q1', 2024, 'Q1', 'd1000000-0000-0000-0000-000000000003', 'CC-HR', 120000, 'active', 80, 95),
    ('fb100000-0000-0000-0000-000000000021', 'HR Budget Q2', 2024, 'Q2', 'd1000000-0000-0000-0000-000000000003', 'CC-HR', 120000, 'active', 80, 95),
    -- Engineering
    ('fb100000-0000-0000-0000-000000000030', 'Engineering Budget Q1', 2024, 'Q1', 'd1000000-0000-0000-0000-000000000004', 'CC-ENG', 400000, 'active', 80, 95),
    ('fb100000-0000-0000-0000-000000000031', 'Engineering Budget Q2', 2024, 'Q2', 'd1000000-0000-0000-0000-000000000004', 'CC-ENG', 400000, 'active', 80, 95),
    -- Sales
    ('fb100000-0000-0000-0000-000000000040', 'Sales Budget Q1', 2024, 'Q1', 'd1000000-0000-0000-0000-000000000006', 'CC-SALES', 300000, 'active', 80, 95),
    ('fb100000-0000-0000-0000-000000000041', 'Sales Budget Q2', 2024, 'Q2', 'd1000000-0000-0000-0000-000000000006', 'CC-SALES', 350000, 'active', 80, 95),
    -- Product
    ('fb100000-0000-0000-0000-000000000050', 'Product Budget Q1', 2024, 'Q1', 'd1000000-0000-0000-0000-000000000008', 'CC-PROD', 200000, 'active', 80, 95);

-- ============================================================================
-- SAMPLE EXPENSE CLAIMS
-- ============================================================================
INSERT INTO finance_expense_claims (id, claim_number, employee_id, department_id, title, description, claim_date, total_amount, status, cost_center) VALUES
    ('ec100000-0000-0000-0000-000000000001', 'EXP-202401-00001', 'e1000000-0000-0000-0000-000000000032', 'd1000000-0000-0000-0000-000000000004', 'AWS Summit Conference', 'Travel and registration for AWS Summit 2024', '2024-01-15', 1850.00, 'approved', 'CC-ENG'),
    ('ec100000-0000-0000-0000-000000000002', 'EXP-202401-00002', 'e1000000-0000-0000-0000-000000000042', 'd1000000-0000-0000-0000-000000000006', 'Client Dinner - Acme Corp', 'Dinner meeting with Acme Corp executives', '2024-01-18', 325.50, 'pending_approval', 'CC-SALES'),
    ('ec100000-0000-0000-0000-000000000003', 'EXP-202401-00003', 'e1000000-0000-0000-0000-000000000012', 'd1000000-0000-0000-0000-000000000002', 'Office Supplies Restock', 'Monthly office supplies purchase', '2024-01-20', 89.99, 'paid', 'CC-FIN'),
    ('ec100000-0000-0000-0000-000000000004', 'EXP-202401-00004', 'e1000000-0000-0000-0000-000000000034', 'd1000000-0000-0000-0000-000000000004', 'DevOps Certification', 'AWS DevOps Professional certification exam', '2024-01-22', 300.00, 'submitted', 'CC-ENG'),
    ('ec100000-0000-0000-0000-000000000005', 'EXP-202401-00005', 'e1000000-0000-0000-0000-000000000051', 'd1000000-0000-0000-0000-000000000008', 'User Research Tools', 'Annual subscription for UserTesting.com', '2024-01-25', 4800.00, 'pending_approval', 'CC-PROD');

-- ============================================================================
-- SAMPLE EXPENSE LINES
-- ============================================================================
INSERT INTO finance_expense_lines (id, claim_id, category_id, description, expense_date, amount, currency, amount_local, has_receipt, receipt_url) VALUES
    -- AWS Summit Conference
    ('el100000-0000-0000-0000-000000000001', 'ec100000-0000-0000-0000-000000000001', 'fc100000-0000-0000-0000-000000000001', 'Round-trip flight SFO-LAS', '2024-01-10', 450.00, 'USD', 450.00, true, '/receipts/exp001-flight.pdf'),
    ('el100000-0000-0000-0000-000000000002', 'ec100000-0000-0000-0000-000000000001', 'fc100000-0000-0000-0000-000000000002', 'Hotel - 2 nights Venetian', '2024-01-10', 600.00, 'USD', 600.00, true, '/receipts/exp001-hotel.pdf'),
    ('el100000-0000-0000-0000-000000000003', 'ec100000-0000-0000-0000-000000000001', 'fc100000-0000-0000-0000-000000000031', 'AWS Summit registration', '2024-01-08', 750.00, 'USD', 750.00, true, '/receipts/exp001-conf.pdf'),
    ('el100000-0000-0000-0000-000000000004', 'ec100000-0000-0000-0000-000000000001', 'fc100000-0000-0000-0000-000000000012', 'Meals during conference', '2024-01-11', 50.00, 'USD', 50.00, true, '/receipts/exp001-meals.pdf'),
    -- Client Dinner
    ('el100000-0000-0000-0000-000000000010', 'ec100000-0000-0000-0000-000000000002', 'fc100000-0000-0000-0000-000000000010', 'Dinner at Nobu - 4 guests', '2024-01-18', 325.50, 'USD', 325.50, true, '/receipts/exp002-dinner.pdf'),
    -- Office Supplies
    ('el100000-0000-0000-0000-000000000020', 'ec100000-0000-0000-0000-000000000003', 'fc100000-0000-0000-0000-000000000020', 'Printer paper, pens, post-its', '2024-01-20', 89.99, 'USD', 89.99, true, '/receipts/exp003-supplies.pdf'),
    -- Certification
    ('el100000-0000-0000-0000-000000000030', 'ec100000-0000-0000-0000-000000000004', 'fc100000-0000-0000-0000-000000000030', 'AWS DevOps Professional exam fee', '2024-01-22', 300.00, 'USD', 300.00, true, '/receipts/exp004-exam.pdf'),
    -- User Research Tools
    ('el100000-0000-0000-0000-000000000040', 'ec100000-0000-0000-0000-000000000005', 'fc100000-0000-0000-0000-000000000022', 'UserTesting.com annual subscription', '2024-01-25', 4800.00, 'USD', 4800.00, true, '/receipts/exp005-usertesting.pdf');

-- ============================================================================
-- SAMPLE FINANCE TASKS
-- ============================================================================
INSERT INTO finance_tasks (id, task_number, title, description, task_type, priority, status, assigned_to, due_date, sla_hours, related_entity_type, related_entity_id) VALUES
    ('ft100000-0000-0000-0000-000000000001', 'FIN-20240125-0001', 'Review expense claim EXP-202401-00002', 'Client dinner expense requires manager approval', 'expense_approval', 'medium', 'pending', 'e1000000-0000-0000-0000-000000000041', '2024-01-28', 48, 'expense_claim', 'ec100000-0000-0000-0000-000000000002'),
    ('ft100000-0000-0000-0000-000000000002', 'FIN-20240125-0002', 'Review expense claim EXP-202401-00005', 'High-value subscription requires finance approval', 'expense_approval', 'high', 'pending', 'e1000000-0000-0000-0000-000000000011', '2024-01-27', 24, 'expense_claim', 'ec100000-0000-0000-0000-000000000005'),
    ('ft100000-0000-0000-0000-000000000003', 'FIN-20240125-0003', 'Process payment for EXP-202401-00001', 'Approved expense ready for payment', 'payment_processing', 'medium', 'pending', 'e1000000-0000-0000-0000-000000000014', '2024-01-30', 72, 'expense_claim', 'ec100000-0000-0000-0000-000000000001'),
    ('ft100000-0000-0000-0000-000000000004', 'FIN-20240126-0001', 'January month-end close preparation', 'Prepare for January month-end close', 'month_end_close', 'high', 'in_progress', 'e1000000-0000-0000-0000-000000000012', '2024-02-05', 240, NULL, NULL),
    ('ft100000-0000-0000-0000-000000000005', 'FIN-20240126-0002', 'Q1 budget review - Engineering', 'Review engineering Q1 budget utilization', 'budget_review', 'medium', 'pending', 'e1000000-0000-0000-0000-000000000011', '2024-02-10', 120, 'budget', 'fb100000-0000-0000-0000-000000000030'),
    ('ft100000-0000-0000-0000-000000000006', 'FIN-20240126-0003', 'Vendor invoice reconciliation', 'Reconcile January vendor invoices with POs', 'reconciliation', 'medium', 'pending', 'e1000000-0000-0000-0000-000000000013', '2024-02-07', 96, NULL, NULL);

-- ============================================================================
-- SAMPLE APPROVAL HISTORY
-- ============================================================================
INSERT INTO finance_approval_history (id, entity_type, entity_id, approval_level, approver_id, action, comments, requested_at, actioned_at) VALUES
    ('ah100000-0000-0000-0000-000000000001', 'expense_claim', 'ec100000-0000-0000-0000-000000000001', 1, 'e1000000-0000-0000-0000-000000000031', 'approved', 'Approved - valid business expense', '2024-01-15 10:00:00', '2024-01-15 14:30:00'),
    ('ah100000-0000-0000-0000-000000000002', 'expense_claim', 'ec100000-0000-0000-0000-000000000001', 2, 'e1000000-0000-0000-0000-000000000030', 'approved', 'Approved for payment', '2024-01-15 14:30:00', '2024-01-16 09:15:00'),
    ('ah100000-0000-0000-0000-000000000003', 'expense_claim', 'ec100000-0000-0000-0000-000000000003', 1, 'e1000000-0000-0000-0000-000000000011', 'auto_approved', 'Auto-approved: Amount under $100 threshold', '2024-01-20 11:00:00', '2024-01-20 11:00:01');

COMMIT;
