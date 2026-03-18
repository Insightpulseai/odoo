# Examples — odoo-test-authoring

## Example 1: TransactionCase for business logic

**Input**: Test margin computation on `ipai.finance.report`

**Output**:
```python
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestFinanceReport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.report = cls.env['ipai.finance.report'].create({
            'name': 'Test Report',
            'budget_amount': 10000.0,
        })

    def test_margin_computation_positive(self):
        """Margin is positive when actual cost is below budget."""
        self.report.actual_cost = 7000.0
        self.assertEqual(self.report.margin_pct, 30.0)
        self.assertFalse(self.report.is_over_budget)

    def test_margin_computation_over_budget(self):
        """Over-budget flag is set when actual cost exceeds budget."""
        self.report.actual_cost = 12000.0
        self.assertTrue(self.report.is_over_budget)

    def test_margin_zero_budget(self):
        """Zero budget yields zero margin, no division error."""
        self.report.budget_amount = 0.0
        self.assertEqual(self.report.margin_pct, 0.0)
```

- Test count: 3
- Results: 3/3 PASS
- Classification: passes locally
- Evidence: `docs/evidence/20260317-1400/odoo-dev/odoo-test-authoring/test.log`

## Example 2: Failure classified as env issue

**Input**: Test fails because `--no-http` flag prevents controller test

**Output**:
- Test: `test_api_endpoint` — FAIL
- Classification: **env issue** (HttpCase requires HTTP server; `--no-http` flag blocks it)
- Action: Re-run without `--no-http` or document limitation

## Example 3: Rejected — test uses production database

**Input**: Run tests on `odoo_dev` database

**Output**:
- Validation: FAIL (BLOCKER)
- Reason: Tests must use disposable `test_<module>` database, never `odoo_dev`
- Recommendation: Use `odoo-bin -d test_ipai_finance_ppm -i ipai_finance_ppm --test-enable`
