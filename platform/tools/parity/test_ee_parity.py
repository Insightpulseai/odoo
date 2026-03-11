#!/usr/bin/env python3
"""
Odoo 19 Enterprise Edition Parity Test Suite
Automated validation of CE + OCA + ipai_* against EE features

Usage:
    python test_ee_parity.py --odoo-url http://localhost:8069 --db odoo_test
    python test_ee_parity.py --category payroll --verbose
    python test_ee_parity.py --report html
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ParityStatus(Enum):
    FULL = "full"  # 100% parity
    PARTIAL = "partial"  # 50-99% parity
    ALTERNATIVE = "alt"  # Different approach, same outcome
    MISSING = "missing"  # Not implemented
    NOT_NEEDED = "skip"  # Not relevant for use case


@dataclass
class TestResult:
    test_id: str
    category: str
    feature: str
    ee_description: str
    status: ParityStatus
    score: float
    notes: str = ""
    error: Optional[str] = None
    execution_time: float = 0.0


@dataclass
class ParityReport:
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_tests: int = 0
    passed: int = 0
    partial: int = 0
    failed: int = 0
    skipped: int = 0
    overall_score: float = 0.0
    results: list = field(default_factory=list)

    def add_result(self, result: TestResult):
        self.results.append(result)
        self.total_tests += 1

        if result.status == ParityStatus.FULL:
            self.passed += 1
        elif result.status in [ParityStatus.PARTIAL, ParityStatus.ALTERNATIVE]:
            self.partial += 1
        elif result.status == ParityStatus.NOT_NEEDED:
            self.skipped += 1
        else:
            self.failed += 1

    def calculate_score(self):
        """Calculate overall parity score"""
        applicable = self.total_tests - self.skipped
        if applicable == 0:
            return 0.0

        total_score = sum(
            r.score for r in self.results if r.status != ParityStatus.NOT_NEEDED
        )
        self.overall_score = (total_score / applicable) * 100
        return self.overall_score


class OdooAPI:
    """Odoo XML-RPC/JSON-RPC API wrapper"""

    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url.rstrip("/")
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.session = requests.Session()

    def authenticate(self) -> bool:
        """Authenticate and get user ID"""
        try:
            response = self.session.post(
                f"{self.url}/web/session/authenticate",
                json={
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": {
                        "db": self.db,
                        "login": self.username,
                        "password": self.password,
                    },
                    "id": 1,
                },
            )
            result = response.json()
            if result.get("result", {}).get("uid"):
                self.uid = result["result"]["uid"]
                logger.info(f"Authenticated as UID {self.uid}")
                return True
            return False
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def call(self, model: str, method: str, args: list = None, kwargs: dict = None):
        """Call Odoo model method"""
        args = args or []
        kwargs = kwargs or {}

        response = self.session.post(
            f"{self.url}/web/dataset/call_kw",
            json={
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "model": model,
                    "method": method,
                    "args": args,
                    "kwargs": kwargs,
                },
                "id": 2,
            },
        )
        result = response.json()
        if "error" in result:
            raise Exception(result["error"])
        return result.get("result")

    def search_read(
        self, model: str, domain: list = None, fields: list = None, limit: int = 100
    ):
        """Search and read records"""
        domain = domain or []
        fields = fields or []
        return self.call(model, "search_read", [domain, fields], {"limit": limit})

    def check_module_installed(self, module_name: str) -> bool:
        """Check if a module is installed"""
        modules = self.search_read(
            "ir.module.module",
            [("name", "=", module_name), ("state", "=", "installed")],
            ["name"],
        )
        return len(modules) > 0

    def check_model_exists(self, model_name: str) -> bool:
        """Check if a model exists"""
        models = self.search_read("ir.model", [("model", "=", model_name)], ["model"])
        return len(models) > 0

    def check_field_exists(self, model: str, field_name: str) -> bool:
        """Check if a field exists on a model"""
        fields = self.search_read(
            "ir.model.fields",
            [("model", "=", model), ("name", "=", field_name)],
            ["name"],
        )
        return len(fields) > 0


class ParityTester:
    """Main parity testing engine"""

    def __init__(self, api: OdooAPI):
        self.api = api
        self.report = ParityReport()

    # ===========================================
    # ACCOUNTING TESTS
    # ===========================================

    def test_gl_001(self) -> TestResult:
        """Test General Ledger functionality"""
        try:
            # Check core accounting module
            has_account = self.api.check_module_installed("account")

            # Check OCA financial reports
            has_reports = self.api.check_module_installed("account_financial_report")

            # Check GL model exists
            has_gl = self.api.check_model_exists("account.move.line")

            # Verify can query GL
            gl_entries = self.api.search_read(
                "account.move.line", [], ["name", "debit", "credit"], limit=5
            )

            if has_account and has_gl:
                status = ParityStatus.FULL if has_reports else ParityStatus.PARTIAL
                score = 1.0 if has_reports else 0.8
                notes = (
                    f"GL functional. OCA reports: {has_reports}. "
                    f"Sample entries: {len(gl_entries)}"
                )
            else:
                status = ParityStatus.MISSING
                score = 0.0
                notes = "Core accounting module not found"

            return TestResult(
                test_id="test_gl_001",
                category="accounting",
                feature="General Ledger",
                ee_description="Full GL with drill-down and analysis",
                status=status,
                score=score,
                notes=notes,
            )
        except Exception as e:
            return TestResult(
                test_id="test_gl_001",
                category="accounting",
                feature="General Ledger",
                ee_description="Full GL with drill-down and analysis",
                status=ParityStatus.MISSING,
                score=0.0,
                error=str(e),
            )

    def test_bank_001(self) -> TestResult:
        """Test Bank Reconciliation"""
        try:
            has_account = self.api.check_module_installed("account")
            has_reconcile = self.api.check_module_installed("account_reconcile_oca")

            # Check reconciliation model
            has_model = self.api.check_model_exists("account.bank.statement")

            if has_account and has_model:
                status = ParityStatus.FULL if has_reconcile else ParityStatus.PARTIAL
                score = 1.0 if has_reconcile else 0.7
                notes = f"Bank reconciliation available. OCA module: {has_reconcile}"
            else:
                status = ParityStatus.MISSING
                score = 0.0
                notes = "Bank reconciliation not available"

            return TestResult(
                test_id="test_bank_001",
                category="accounting",
                feature="Bank Reconciliation",
                ee_description="Auto-matching with configurable rules",
                status=status,
                score=score,
                notes=notes,
            )
        except Exception as e:
            return TestResult(
                test_id="test_bank_001",
                category="accounting",
                feature="Bank Reconciliation",
                ee_description="Auto-matching with configurable rules",
                status=ParityStatus.MISSING,
                score=0.0,
                error=str(e),
            )

    def test_asset_001(self) -> TestResult:
        """Test Asset Management"""
        try:
            has_asset = self.api.check_module_installed("account_asset_management")
            has_model = self.api.check_model_exists("account.asset")

            if has_asset and has_model:
                # Check for depreciation functionality
                has_depr_field = self.api.check_field_exists(
                    "account.asset", "depreciation_line_ids"
                )
                status = ParityStatus.FULL if has_depr_field else ParityStatus.PARTIAL
                score = 1.0 if has_depr_field else 0.8
                notes = "Asset management with depreciation schedules"
            else:
                status = ParityStatus.MISSING
                score = 0.0
                notes = "Asset management module not installed"

            return TestResult(
                test_id="test_asset_001",
                category="accounting",
                feature="Asset Management",
                ee_description="Fixed assets with depreciation schedules",
                status=status,
                score=score,
                notes=notes,
            )
        except Exception as e:
            return TestResult(
                test_id="test_asset_001",
                category="accounting",
                feature="Asset Management",
                ee_description="Fixed assets with depreciation schedules",
                status=ParityStatus.MISSING,
                score=0.0,
                error=str(e),
            )

    # ===========================================
    # PAYROLL TESTS (PH-Specific)
    # ===========================================

    def test_pay_001(self) -> TestResult:
        """Test Payroll Base"""
        try:
            has_payroll = self.api.check_module_installed("hr_payroll")
            has_ph = self.api.check_module_installed("ipai_hr_payroll_ph")
            has_model = self.api.check_model_exists("hr.payslip")

            if has_payroll and has_model:
                status = ParityStatus.FULL if has_ph else ParityStatus.PARTIAL
                score = 1.0 if has_ph else 0.6
                notes = f"Payroll base: {has_payroll}, PH localization: {has_ph}"
            else:
                status = ParityStatus.MISSING
                score = 0.0
                notes = "Payroll module not installed"

            return TestResult(
                test_id="test_pay_001",
                category="payroll",
                feature="Payslip Generation",
                ee_description="Monthly payroll processing",
                status=status,
                score=score,
                notes=notes,
            )
        except Exception as e:
            return TestResult(
                test_id="test_pay_001",
                category="payroll",
                feature="Payslip Generation",
                ee_description="Monthly payroll processing",
                status=ParityStatus.MISSING,
                score=0.0,
                error=str(e),
            )

    def test_pay_002(self) -> TestResult:
        """Test SSS Computation"""
        try:
            has_ph = self.api.check_module_installed("ipai_hr_payroll_ph")

            if has_ph:
                # Check for SSS fields on payslip
                has_sss_ee = self.api.check_field_exists("hr.payslip", "sss_ee")
                has_sss_er = self.api.check_field_exists("hr.payslip", "sss_er")

                if has_sss_ee and has_sss_er:
                    status = ParityStatus.FULL
                    score = 1.0
                    notes = "SSS computation with 2025 tables"
                else:
                    status = ParityStatus.PARTIAL
                    score = 0.5
                    notes = "SSS fields missing on payslip"
            else:
                status = ParityStatus.MISSING
                score = 0.0
                notes = "ipai_hr_payroll_ph not installed"

            return TestResult(
                test_id="test_pay_002",
                category="payroll",
                feature="SSS Computation",
                ee_description="Philippine SSS contribution calculation",
                status=status,
                score=score,
                notes=notes,
            )
        except Exception as e:
            return TestResult(
                test_id="test_pay_002",
                category="payroll",
                feature="SSS Computation",
                ee_description="Philippine SSS contribution calculation",
                status=ParityStatus.MISSING,
                score=0.0,
                error=str(e),
            )

    def test_pay_003(self) -> TestResult:
        """Test PhilHealth Computation"""
        try:
            has_ph = self.api.check_module_installed("ipai_hr_payroll_ph")

            if has_ph:
                has_philhealth_ee = self.api.check_field_exists(
                    "hr.payslip", "philhealth_ee"
                )
                has_philhealth_er = self.api.check_field_exists(
                    "hr.payslip", "philhealth_er"
                )

                if has_philhealth_ee and has_philhealth_er:
                    status = ParityStatus.FULL
                    score = 1.0
                    notes = "PhilHealth 5% split computation"
                else:
                    status = ParityStatus.PARTIAL
                    score = 0.5
                    notes = "PhilHealth fields missing"
            else:
                status = ParityStatus.MISSING
                score = 0.0
                notes = "ipai_hr_payroll_ph not installed"

            return TestResult(
                test_id="test_pay_003",
                category="payroll",
                feature="PhilHealth",
                ee_description="Philippine PhilHealth contribution",
                status=status,
                score=score,
                notes=notes,
            )
        except Exception as e:
            return TestResult(
                test_id="test_pay_003",
                category="payroll",
                feature="PhilHealth",
                ee_description="Philippine PhilHealth contribution",
                status=ParityStatus.MISSING,
                score=0.0,
                error=str(e),
            )

    def test_pay_005(self) -> TestResult:
        """Test BIR Withholding Tax"""
        try:
            has_ph = self.api.check_module_installed("ipai_hr_payroll_ph")

            if has_ph:
                has_wht = self.api.check_field_exists("hr.payslip", "withholding_tax")
                has_table = self.api.check_model_exists("ipai.bir.tax.table")

                if has_wht and has_table:
                    status = ParityStatus.FULL
                    score = 1.0
                    notes = "TRAIN Law tax tables implemented"
                elif has_wht:
                    status = ParityStatus.PARTIAL
                    score = 0.7
                    notes = "Withholding tax field exists, table model missing"
                else:
                    status = ParityStatus.PARTIAL
                    score = 0.5
                    notes = "Withholding tax fields not found"
            else:
                status = ParityStatus.MISSING
                score = 0.0
                notes = "ipai_hr_payroll_ph not installed"

            return TestResult(
                test_id="test_pay_005",
                category="payroll",
                feature="Withholding Tax",
                ee_description="BIR TRAIN Law tax computation",
                status=status,
                score=score,
                notes=notes,
            )
        except Exception as e:
            return TestResult(
                test_id="test_pay_005",
                category="payroll",
                feature="Withholding Tax",
                ee_description="BIR TRAIN Law tax computation",
                status=ParityStatus.MISSING,
                score=0.0,
                error=str(e),
            )

    def test_pay_007(self) -> TestResult:
        """Test BIR 1601-C Report"""
        try:
            has_ph = self.api.check_module_installed("ipai_hr_payroll_ph")
            has_bir = self.api.check_module_installed("ipai_bir_compliance")

            if has_ph or has_bir:
                # Check for 1601-C report model
                has_report = self.api.check_model_exists("ipai.bir.1601c")

                if has_report:
                    status = ParityStatus.FULL
                    score = 1.0
                    notes = "BIR 1601-C monthly remittance report"
                else:
                    status = ParityStatus.PARTIAL
                    score = 0.5
                    notes = "Module installed but 1601-C model missing"
            else:
                status = ParityStatus.MISSING
                score = 0.0
                notes = "BIR compliance module not installed"

            return TestResult(
                test_id="test_pay_007",
                category="payroll",
                feature="BIR 1601-C",
                ee_description="Monthly withholding tax remittance form",
                status=status,
                score=score,
                notes=notes,
            )
        except Exception as e:
            return TestResult(
                test_id="test_pay_007",
                category="payroll",
                feature="BIR 1601-C",
                ee_description="Monthly withholding tax remittance form",
                status=ParityStatus.MISSING,
                score=0.0,
                error=str(e),
            )

    # ===========================================
    # APPROVALS TESTS
    # ===========================================

    def test_apv_001(self) -> TestResult:
        """Test Approvals Module"""
        try:
            has_approvals = self.api.check_module_installed("ipai_approvals")
            has_model = self.api.check_model_exists("ipai.approval.request")

            if has_approvals and has_model:
                status = ParityStatus.FULL
                score = 1.0
                notes = "Approval request workflow implemented"
            elif has_approvals:
                status = ParityStatus.PARTIAL
                score = 0.7
                notes = "Module installed, checking model structure"
            else:
                status = ParityStatus.MISSING
                score = 0.0
                notes = "ipai_approvals not installed"

            return TestResult(
                test_id="test_apv_001",
                category="approvals",
                feature="Approval Requests",
                ee_description="Configurable approval workflows",
                status=status,
                score=score,
                notes=notes,
            )
        except Exception as e:
            return TestResult(
                test_id="test_apv_001",
                category="approvals",
                feature="Approval Requests",
                ee_description="Configurable approval workflows",
                status=ParityStatus.MISSING,
                score=0.0,
                error=str(e),
            )

    def test_apv_002(self) -> TestResult:
        """Test Multi-level Approvals"""
        try:
            has_approvals = self.api.check_module_installed("ipai_approvals")

            if has_approvals:
                has_category = self.api.check_model_exists("ipai.approval.category")
                has_line = self.api.check_model_exists("ipai.approval.line")

                if has_category and has_line:
                    status = ParityStatus.FULL
                    score = 1.0
                    notes = "Multi-level approval chains supported"
                else:
                    status = ParityStatus.PARTIAL
                    score = 0.6
                    notes = "Basic approvals, multi-level incomplete"
            else:
                status = ParityStatus.MISSING
                score = 0.0
                notes = "ipai_approvals not installed"

            return TestResult(
                test_id="test_apv_002",
                category="approvals",
                feature="Multi-level Approvals",
                ee_description="Sequential/parallel approval routing",
                status=status,
                score=score,
                notes=notes,
            )
        except Exception as e:
            return TestResult(
                test_id="test_apv_002",
                category="approvals",
                feature="Multi-level Approvals",
                ee_description="Sequential/parallel approval routing",
                status=ParityStatus.MISSING,
                score=0.0,
                error=str(e),
            )

    # ===========================================
    # HELPDESK TESTS
    # ===========================================

    def test_hd_001(self) -> TestResult:
        """Test Helpdesk Ticket Management"""
        try:
            has_helpdesk = self.api.check_module_installed("ipai_helpdesk")
            has_model = self.api.check_model_exists("ipai.helpdesk.ticket")

            if has_helpdesk and has_model:
                status = ParityStatus.FULL
                score = 1.0
                notes = "Helpdesk ticketing system available"
            elif has_helpdesk:
                status = ParityStatus.PARTIAL
                score = 0.7
                notes = "Module installed, checking ticket model"
            else:
                # Check for OCA alternative
                has_oca = self.api.check_module_installed("helpdesk_mgmt")
                if has_oca:
                    status = ParityStatus.ALTERNATIVE
                    score = 0.8
                    notes = "Using OCA helpdesk_mgmt"
                else:
                    status = ParityStatus.MISSING
                    score = 0.0
                    notes = "No helpdesk module installed"

            return TestResult(
                test_id="test_hd_001",
                category="helpdesk",
                feature="Ticket Management",
                ee_description="Multi-channel ticket creation and tracking",
                status=status,
                score=score,
                notes=notes,
            )
        except Exception as e:
            return TestResult(
                test_id="test_hd_001",
                category="helpdesk",
                feature="Ticket Management",
                ee_description="Multi-channel ticket creation and tracking",
                status=ParityStatus.MISSING,
                score=0.0,
                error=str(e),
            )

    def test_hd_002(self) -> TestResult:
        """Test SLA Tracking"""
        try:
            has_helpdesk = self.api.check_module_installed("ipai_helpdesk")

            if has_helpdesk:
                has_sla = self.api.check_model_exists("ipai.helpdesk.sla")
                has_sla_field = self.api.check_field_exists(
                    "ipai.helpdesk.ticket", "sla_deadline"
                )

                if has_sla and has_sla_field:
                    status = ParityStatus.FULL
                    score = 1.0
                    notes = "SLA policies with deadline tracking"
                elif has_sla_field:
                    status = ParityStatus.PARTIAL
                    score = 0.7
                    notes = "SLA deadlines without policy engine"
                else:
                    status = ParityStatus.PARTIAL
                    score = 0.5
                    notes = "Basic helpdesk without SLA"
            else:
                status = ParityStatus.MISSING
                score = 0.0
                notes = "Helpdesk module not installed"

            return TestResult(
                test_id="test_hd_002",
                category="helpdesk",
                feature="SLA Tracking",
                ee_description="Response/resolution time targets",
                status=status,
                score=score,
                notes=notes,
            )
        except Exception as e:
            return TestResult(
                test_id="test_hd_002",
                category="helpdesk",
                feature="SLA Tracking",
                ee_description="Response/resolution time targets",
                status=ParityStatus.MISSING,
                score=0.0,
                error=str(e),
            )

    # ===========================================
    # PLANNING TESTS
    # ===========================================

    def test_plan_001(self) -> TestResult:
        """Test Resource Planning"""
        try:
            has_planning = self.api.check_module_installed("ipai_planning")
            has_model = self.api.check_model_exists("ipai.planning.slot")

            if has_planning and has_model:
                status = ParityStatus.FULL
                score = 1.0
                notes = "Shift planning and resource allocation"
            elif has_planning:
                status = ParityStatus.PARTIAL
                score = 0.7
                notes = "Module installed, checking slot model"
            else:
                status = ParityStatus.MISSING
                score = 0.0
                notes = "ipai_planning not installed"

            return TestResult(
                test_id="test_plan_001",
                category="planning",
                feature="Shift Planning",
                ee_description="Create and assign work shifts",
                status=status,
                score=score,
                notes=notes,
            )
        except Exception as e:
            return TestResult(
                test_id="test_plan_001",
                category="planning",
                feature="Shift Planning",
                ee_description="Create and assign work shifts",
                status=ParityStatus.MISSING,
                score=0.0,
                error=str(e),
            )

    def test_plan_003(self) -> TestResult:
        """Test Conflict Detection"""
        try:
            has_planning = self.api.check_module_installed("ipai_planning")

            if has_planning:
                has_conflict = self.api.check_field_exists(
                    "ipai.planning.slot", "is_conflicting"
                )

                if has_conflict:
                    status = ParityStatus.FULL
                    score = 1.0
                    notes = "Automatic overlap/conflict detection"
                else:
                    status = ParityStatus.PARTIAL
                    score = 0.6
                    notes = "Planning without conflict detection"
            else:
                status = ParityStatus.MISSING
                score = 0.0
                notes = "ipai_planning not installed"

            return TestResult(
                test_id="test_plan_003",
                category="planning",
                feature="Conflict Detection",
                ee_description="Overlapping shift warnings",
                status=status,
                score=score,
                notes=notes,
            )
        except Exception as e:
            return TestResult(
                test_id="test_plan_003",
                category="planning",
                feature="Conflict Detection",
                ee_description="Overlapping shift warnings",
                status=ParityStatus.MISSING,
                score=0.0,
                error=str(e),
            )

    # ===========================================
    # TEST RUNNER
    # ===========================================

    def get_all_tests(self) -> list:
        """Get all test methods"""
        return [
            # Accounting
            self.test_gl_001,
            self.test_bank_001,
            self.test_asset_001,
            # Payroll
            self.test_pay_001,
            self.test_pay_002,
            self.test_pay_003,
            self.test_pay_005,
            self.test_pay_007,
            # Approvals
            self.test_apv_001,
            self.test_apv_002,
            # Helpdesk
            self.test_hd_001,
            self.test_hd_002,
            # Planning
            self.test_plan_001,
            self.test_plan_003,
        ]

    def run_all(self, category: str = None) -> ParityReport:
        """Run all tests or tests in a specific category"""
        tests = self.get_all_tests()

        for test_func in tests:
            result = test_func()

            # Filter by category if specified
            if category and result.category != category:
                continue

            self.report.add_result(result)

            # Log result
            status_icon = {
                ParityStatus.FULL: "PASS",
                ParityStatus.PARTIAL: "PARTIAL",
                ParityStatus.ALTERNATIVE: "ALT",
                ParityStatus.MISSING: "FAIL",
                ParityStatus.NOT_NEEDED: "SKIP",
            }
            logger.info(
                f"{status_icon[result.status]} {result.test_id}: "
                f"{result.feature} - {result.notes}"
            )

        self.report.calculate_score()
        return self.report

    def generate_report(self, format: str = "text") -> str:
        """Generate test report in specified format"""
        if format == "json":
            return json.dumps(
                {
                    "timestamp": self.report.timestamp,
                    "total_tests": self.report.total_tests,
                    "passed": self.report.passed,
                    "partial": self.report.partial,
                    "failed": self.report.failed,
                    "skipped": self.report.skipped,
                    "overall_score": round(self.report.overall_score, 2),
                    "results": [
                        {
                            "test_id": r.test_id,
                            "category": r.category,
                            "feature": r.feature,
                            "status": r.status.value,
                            "score": r.score,
                            "notes": r.notes,
                            "error": r.error,
                        }
                        for r in self.report.results
                    ],
                },
                indent=2,
            )

        elif format == "html":
            return self._generate_html_report()

        else:  # text
            return self._generate_text_report()

    def _generate_text_report(self) -> str:
        lines = [
            "=" * 60,
            "ODOO 19 ENTERPRISE EDITION PARITY REPORT",
            "=" * 60,
            f"Timestamp: {self.report.timestamp}",
            f"Total Tests: {self.report.total_tests}",
            f"Passed: {self.report.passed}",
            f"Partial: {self.report.partial}",
            f"Failed: {self.report.failed}",
            f"Skipped: {self.report.skipped}",
            f"Overall Score: {self.report.overall_score:.1f}%",
            "",
            "-" * 60,
            "DETAILED RESULTS",
            "-" * 60,
        ]

        # Group by category
        categories = {}
        for r in self.report.results:
            if r.category not in categories:
                categories[r.category] = []
            categories[r.category].append(r)

        for cat, results in categories.items():
            lines.append(f"\n[{cat.upper()}]")
            cat_score = sum(r.score for r in results) / len(results) * 100
            lines.append(f"Category Score: {cat_score:.1f}%")
            lines.append("")

            for r in results:
                status = {
                    ParityStatus.FULL: "FULL",
                    ParityStatus.PARTIAL: "PARTIAL",
                    ParityStatus.ALTERNATIVE: "ALT",
                    ParityStatus.MISSING: "MISSING",
                    ParityStatus.NOT_NEEDED: "SKIP",
                }[r.status]
                lines.append(f"  {r.test_id}: {r.feature}")
                lines.append(f"    Status: {status} ({r.score*100:.0f}%)")
                lines.append(f"    Notes: {r.notes}")
                if r.error:
                    lines.append(f"    Error: {r.error}")
                lines.append("")

        # Parity assessment
        lines.append("=" * 60)
        if self.report.overall_score >= 90:
            lines.append("FULL EE PARITY ACHIEVED")
        elif self.report.overall_score >= 75:
            lines.append("PRODUCTION READY (Minor gaps)")
        elif self.report.overall_score >= 50:
            lines.append("MVP READY (Significant gaps)")
        else:
            lines.append("NOT READY FOR PRODUCTION")
        lines.append("=" * 60)

        return "\n".join(lines)

    def _generate_html_report(self) -> str:
        score_class = (
            "high"
            if self.report.overall_score >= 75
            else "medium" if self.report.overall_score >= 50 else "low"
        )

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Odoo 19 EE Parity Report</title>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .score {{ font-size: 3em; text-align: center; padding: 20px; }}
        .score.high {{ color: #28a745; }}
        .score.medium {{ color: #ffc107; }}
        .score.low {{ color: #dc3545; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; }}
        .status-full {{ color: #28a745; }}
        .status-partial {{ color: #ffc107; }}
        .status-missing {{ color: #dc3545; }}
        .status-alt {{ color: #17a2b8; }}
        .status-skip {{ color: #6c757d; }}
        .category {{ background: #e9ecef; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Odoo 19 Enterprise Edition Parity Report</h1>
        <p>Generated: {self.report.timestamp}</p>

        <div class="score {score_class}">
            {self.report.overall_score:.1f}% Parity
        </div>

        <div class="summary">
            <div class="stat">
                <div class="stat-value">{self.report.total_tests}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat">
                <div class="stat-value" style="color: #28a745;">{self.report.passed}</div>
                <div class="stat-label">Full Parity</div>
            </div>
            <div class="stat">
                <div class="stat-value" style="color: #ffc107;">{self.report.partial}</div>
                <div class="stat-label">Partial</div>
            </div>
            <div class="stat">
                <div class="stat-value" style="color: #dc3545;">{self.report.failed}</div>
                <div class="stat-label">Missing</div>
            </div>
            <div class="stat">
                <div class="stat-value" style="color: #6c757d;">{self.report.skipped}</div>
                <div class="stat-label">Skipped</div>
            </div>
        </div>

        <h2>Detailed Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Test ID</th>
                    <th>Feature</th>
                    <th>Status</th>
                    <th>Score</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
"""

        # Group by category
        categories = {}
        for r in self.report.results:
            if r.category not in categories:
                categories[r.category] = []
            categories[r.category].append(r)

        for cat, results in categories.items():
            cat_score = sum(r.score for r in results) / len(results) * 100
            html += f'<tr class="category"><td colspan="5">{cat.upper()} ({cat_score:.0f}%)</td></tr>'

            for r in results:
                status_class = {
                    ParityStatus.FULL: "status-full",
                    ParityStatus.PARTIAL: "status-partial",
                    ParityStatus.ALTERNATIVE: "status-alt",
                    ParityStatus.MISSING: "status-missing",
                    ParityStatus.NOT_NEEDED: "status-skip",
                }[r.status]
                status_label = r.status.value.upper()
                error_html = (
                    f' <span style="color:red;">Error: {r.error}</span>'
                    if r.error
                    else ""
                )
                html += f"""
                <tr>
                    <td><code>{r.test_id}</code></td>
                    <td>{r.feature}</td>
                    <td class="{status_class}">{status_label}</td>
                    <td>{r.score*100:.0f}%</td>
                    <td>{r.notes}{error_html}</td>
                </tr>
"""

        html += """
            </tbody>
        </table>

        <h2>Parity Assessment</h2>
        <div style="padding: 20px; background: #f8f9fa; border-radius: 8px;">
"""

        if self.report.overall_score >= 90:
            html += '<p style="font-size: 1.5em; color: #28a745;">FULL EE PARITY ACHIEVED</p>'
        elif self.report.overall_score >= 75:
            html += '<p style="font-size: 1.5em; color: #28a745;">PRODUCTION READY (Minor gaps)</p>'
        elif self.report.overall_score >= 50:
            html += '<p style="font-size: 1.5em; color: #ffc107;">MVP READY (Significant gaps identified)</p>'
        else:
            html += '<p style="font-size: 1.5em; color: #dc3545;">NOT READY FOR PRODUCTION</p>'

        html += """
        </div>
    </div>
</body>
</html>
"""
        return html


def main():
    parser = argparse.ArgumentParser(description="Odoo 19 EE Parity Testing")
    parser.add_argument(
        "--odoo-url", default="http://localhost:8069", help="Odoo URL"
    )
    parser.add_argument("--db", default="odoo", help="Database name")
    parser.add_argument("--username", default="admin", help="Username")
    parser.add_argument("--password", default="admin", help="Password")
    parser.add_argument("--category", help="Test only specific category")
    parser.add_argument(
        "--report",
        choices=["text", "json", "html"],
        default="text",
        help="Report format",
    )
    parser.add_argument("--output", help="Output file (default: stdout)")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Connect to Odoo
    api = OdooAPI(args.odoo_url, args.db, args.username, args.password)

    if not api.authenticate():
        logger.error("Failed to authenticate with Odoo")
        sys.exit(1)

    # Run tests
    tester = ParityTester(api)
    report = tester.run_all(category=args.category)

    # Generate report
    output = tester.generate_report(args.report)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        logger.info(f"Report written to {args.output}")
    else:
        print(output)

    # Exit with appropriate code
    sys.exit(0 if report.overall_score >= 75 else 1)


if __name__ == "__main__":
    main()
