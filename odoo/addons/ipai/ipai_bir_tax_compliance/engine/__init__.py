"""
BIR Tax Compliance Rules Engine - JSONLogic evaluation with formula computation
Ported from TaxPulse-PH-Pack into the ipai_bir_tax_compliance Odoo module.
"""

from .evaluator import RulesEvaluator
from .formula import FormulaEngine
from .loader import RulesLoader

__all__ = ["RulesEvaluator", "FormulaEngine", "RulesLoader"]
