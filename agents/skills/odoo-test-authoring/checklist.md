# Checklist — odoo-test-authoring

- [ ] `tests/__init__.py` exists and imports all test modules
- [ ] Test file named `test_<module>.py` or `test_<feature>.py`
- [ ] Appropriate base class used (TransactionCase, HttpCase, SavepointCase)
- [ ] `@tagged` decorator used for test categorization
- [ ] Test data created in `setUp` or `setUpClass` (not relying on prod data)
- [ ] Each test method tests one specific behavior
- [ ] Assertions use `self.assertEqual`, `self.assertTrue`, `self.assertRaises`, etc.
- [ ] Tests run on disposable `test_<module>` database (never prod/dev/staging)
- [ ] Every failure classified (passes locally / init only / env issue / migration gap / real defect)
- [ ] No claims of "all tests pass" without evidence log citation
- [ ] No silently skipped failures
- [ ] No `cr.commit()` calls in tests
- [ ] TransactionCase used for ORM tests (auto-rollback)
- [ ] Evidence saved to `docs/evidence/{stamp}/odoo-dev/odoo-test-authoring/`
