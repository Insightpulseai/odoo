-- Clear existing directory data
DELETE FROM ipai_finance_person;

-- Insert correct directory with real names and functional roles
INSERT INTO ipai_finance_person (code, name, email, role, create_uid, write_uid, create_date, write_date) VALUES
('CKVC', 'Khalil Veracruz', 'khalil.veracruz@omc.com', 'Finance Director', 1, 1, NOW(), NOW()),
('RIM', 'Rey Meran', 'rey.meran@omc.com', 'Senior Finance Manager', 1, 1, NOW(), NOW()),
('BOM', 'Beng Manalo', 'beng.manalo@omc.com', 'Finance Supervisor', 1, 1, NOW(), NOW()),
('JPAL', 'Jinky Paladin', 'jinky.paladin@omc.com', 'Tax Filing & BIR Forms Owner', 1, 1, NOW(), NOW()),
('JPL', 'Jerald Loterte', 'jerald.loterte@omc.com', 'WIP & Revenue Reconciliation', 1, 1, NOW(), NOW()),
('JI', 'Jasmin Ignacio', 'jasmin.ignacio@omc.com', 'Accruals & Expense Matching', 1, 1, NOW(), NOW()),
('JO', 'Jhoee Oliva', 'jhoee.oliva@omc.com', 'Cash Advances & Employee Claims', 1, 1, NOW(), NOW()),
('JM', 'Joana Maravillas', 'joana.maravillas@omc.com', 'Asset Management & Depreciation', 1, 1, NOW(), NOW()),
('RMQB', 'Sally Brillantes', 'sally.brillantes@omc.com', 'Expense Adjustments & Reclassifications', 1, 1, NOW(), NOW()),
('JAP', 'Jan Pierre', 'jan.pierre@omc.com', 'Billing Adjustments & Job Transfers', 1, 1, NOW(), NOW()),
('JRMO', 'Junior Staff', 'junior.staff@omc.com', 'WIP Schedule Support', 1, 1, NOW(), NOW());
