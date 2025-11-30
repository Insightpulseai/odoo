-- Import Directory data
INSERT INTO ipai_finance_person (code, name, email, role, create_uid, write_uid, create_date, write_date) VALUES
('CKVC', 'CKVC', 'ckvc@insightpulseai.net', 'Finance Supervisor', 1, 1, NOW(), NOW()),
('RIM', 'RIM', 'rim@insightpulseai.net', 'Senior Finance Manager', 1, 1, NOW(), NOW()),
('BOM', 'BOM', 'bom@insightpulseai.net', 'Finance Manager', 1, 1, NOW(), NOW()),
('JPAL', 'JPAL', 'jpal@insightpulseai.net', 'Tax Specialist', 1, 1, NOW(), NOW()),
('LAS', 'LAS', 'las@insightpulseai.net', 'Accounting Manager', 1, 1, NOW(), NOW()),
('RMQB', 'RMQB', 'rmqb@insightpulseai.net', 'Financial Analyst', 1, 1, NOW(), NOW()),
('JAP', 'JAP', 'jap@insightpulseai.net', 'Compliance Officer', 1, 1, NOW(), NOW()),
('JRMO', 'JRMO', 'jrmo@insightpulseai.net', 'Finance Assistant', 1, 1, NOW(), NOW());

-- Import Monthly Tasks data
INSERT INTO ipai_finance_task_template (employee_code_id, category, name, prep_duration, review_duration, approval_duration, create_uid, write_uid, create_date, write_date)
SELECT 
    id,
    'Foundation & Corp',
    'Review corporate financial statements',
    2.0, 1.0, 1.0,
    1, 1, NOW(), NOW()
FROM ipai_finance_person WHERE code = 'CKVC';

INSERT INTO ipai_finance_task_template (employee_code_id, category, name, prep_duration, review_duration, approval_duration, create_uid, write_uid, create_date, write_date)
SELECT 
    id,
    'Foundation & Corp',
    'Approve month-end journal entries',
    1.0, 0.5, 0.5,
    1, 1, NOW(), NOW()
FROM ipai_finance_person WHERE code = 'CKVC';

INSERT INTO ipai_finance_task_template (employee_code_id, category, name, prep_duration, review_duration, approval_duration, create_uid, write_uid, create_date, write_date)
SELECT 
    id,
    'Revenue/WIP',
    'Review revenue recognition schedules',
    3.0, 2.0, 1.0,
    1, 1, NOW(), NOW()
FROM ipai_finance_person WHERE code = 'RIM';

INSERT INTO ipai_finance_task_template (employee_code_id, category, name, prep_duration, review_duration, approval_duration, create_uid, write_uid, create_date, write_date)
SELECT 
    id,
    'Revenue/WIP',
    'Validate WIP calculations',
    2.0, 1.0, 1.0,
    1, 1, NOW(), NOW()
FROM ipai_finance_person WHERE code = 'RIM';

INSERT INTO ipai_finance_task_template (employee_code_id, category, name, prep_duration, review_duration, approval_duration, create_uid, write_uid, create_date, write_date)
SELECT 
    id,
    'VAT & Tax Reporting',
    'Prepare VAT returns',
    2.0, 1.0, 1.0,
    1, 1, NOW(), NOW()
FROM ipai_finance_person WHERE code = 'BOM';

INSERT INTO ipai_finance_task_template (employee_code_id, category, name, prep_duration, review_duration, approval_duration, create_uid, write_uid, create_date, write_date)
SELECT 
    id,
    'VAT & Tax Reporting',
    'Review tax provisions',
    1.0, 1.0, 0.5,
    1, 1, NOW(), NOW()
FROM ipai_finance_person WHERE code = 'BOM';

INSERT INTO ipai_finance_task_template (employee_code_id, category, name, prep_duration, review_duration, approval_duration, create_uid, write_uid, create_date, write_date)
SELECT 
    id,
    'VAT & Tax Reporting',
    'File BIR forms 1601-C/1601-EQ',
    1.0, 0.5, 0.5,
    1, 1, NOW(), NOW()
FROM ipai_finance_person WHERE code = 'JPAL';

INSERT INTO ipai_finance_task_template (employee_code_id, category, name, prep_duration, review_duration, approval_duration, create_uid, write_uid, create_date, write_date)
SELECT 
    id,
    'Working Capital',
    'Review AR aging reports',
    2.0, 1.0, 1.0,
    1, 1, NOW(), NOW()
FROM ipai_finance_person WHERE code = 'LAS';

INSERT INTO ipai_finance_task_template (employee_code_id, category, name, prep_duration, review_duration, approval_duration, create_uid, write_uid, create_date, write_date)
SELECT 
    id,
    'Working Capital',
    'Monitor cash flow projections',
    1.0, 0.5, 0.5,
    1, 1, NOW(), NOW()
FROM ipai_finance_person WHERE code = 'LAS';

INSERT INTO ipai_finance_task_template (employee_code_id, category, name, prep_duration, review_duration, approval_duration, create_uid, write_uid, create_date, write_date)
SELECT 
    id,
    'Working Capital',
    'Analyze inventory levels',
    1.0, 0.5, 0.5,
    1, 1, NOW(), NOW()
FROM ipai_finance_person WHERE code = 'RMQB';

INSERT INTO ipai_finance_task_template (employee_code_id, category, name, prep_duration, review_duration, approval_duration, create_uid, write_uid, create_date, write_date)
SELECT 
    id,
    'Compliance',
    'Review regulatory compliance',
    1.0, 0.5, 0.5,
    1, 1, NOW(), NOW()
FROM ipai_finance_person WHERE code = 'JAP';

INSERT INTO ipai_finance_task_template (employee_code_id, category, name, prep_duration, review_duration, approval_duration, create_uid, write_uid, create_date, write_date)
SELECT 
    id,
    'Administrative',
    'Prepare meeting minutes',
    0.5, 0.5, 0.5,
    1, 1, NOW(), NOW()
FROM ipai_finance_person WHERE code = 'JRMO';
