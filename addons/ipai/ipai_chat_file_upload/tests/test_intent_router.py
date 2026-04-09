# -*- coding: utf-8 -*-
"""Tests for attachment-aware intent routing (FR-10).

These tests verify that the intent router correctly classifies user
intent and document type, and that the system instruction builder
produces task-specific prompts that prevent generic clarification.
"""
from odoo.tests.common import TransactionCase, tagged

from ..models.intent_router import (
    INTENT_EXTRACT,
    INTENT_GENERAL,
    INTENT_REVIEW,
    INTENT_SUMMARIZE,
    INTENT_VALIDATE,
    build_system_instruction,
    classify_document_type,
    classify_intent,
)


@tagged('post_install', '-at_install')
class TestIntentClassification(TransactionCase):
    """Test intent classification from user messages."""

    # ------------------------------------------------------------------
    # Extract intent
    # ------------------------------------------------------------------
    def test_extract_first(self):
        self.assertEqual(classify_intent('extract first'), INTENT_EXTRACT)

    def test_extract_the_fields(self):
        self.assertEqual(
            classify_intent('extract the fields from this document'),
            INTENT_EXTRACT,
        )

    def test_parse_this(self):
        self.assertEqual(classify_intent('parse this'), INTENT_EXTRACT)

    def test_what_does_it_say(self):
        self.assertEqual(
            classify_intent('what does it say'),
            INTENT_EXTRACT,
        )

    # ------------------------------------------------------------------
    # Validate intent
    # ------------------------------------------------------------------
    def test_assess_tax_computation(self):
        self.assertEqual(
            classify_intent(
                'assess if the tax computation and total amount billed is correct'
            ),
            INTENT_VALIDATE,
        )

    def test_check_totals(self):
        self.assertEqual(classify_intent('check totals'), INTENT_VALIDATE)

    def test_verify_amounts(self):
        self.assertEqual(
            classify_intent('verify if the amounts are correct'),
            INTENT_VALIDATE,
        )

    def test_is_total_correct(self):
        self.assertEqual(
            classify_intent('is the total correct?'),
            INTENT_VALIDATE,
        )

    def test_check_discrepancy(self):
        self.assertEqual(
            classify_intent('check for discrepancies'),
            INTENT_VALIDATE,
        )

    def test_validate_compliance(self):
        self.assertEqual(
            classify_intent('validate compliance'),
            INTENT_VALIDATE,
        )

    # ------------------------------------------------------------------
    # Review intent
    # ------------------------------------------------------------------
    def test_review(self):
        self.assertEqual(classify_intent('review this'), INTENT_REVIEW)

    def test_analyze(self):
        self.assertEqual(
            classify_intent('analyze the document'),
            INTENT_REVIEW,
        )

    def test_inspect(self):
        self.assertEqual(classify_intent('inspect this file'), INTENT_REVIEW)

    # ------------------------------------------------------------------
    # Summarize intent
    # ------------------------------------------------------------------
    def test_summarize_this(self):
        self.assertEqual(classify_intent('summarize this'), INTENT_SUMMARIZE)

    def test_give_overview(self):
        self.assertEqual(
            classify_intent('give me an overview'),
            INTENT_SUMMARIZE,
        )

    def test_key_points(self):
        self.assertEqual(
            classify_intent('what are the key points?'),
            INTENT_SUMMARIZE,
        )

    def test_whats_this(self):
        self.assertEqual(
            classify_intent("what's this document about?"),
            INTENT_SUMMARIZE,
        )

    # ------------------------------------------------------------------
    # General intent
    # ------------------------------------------------------------------
    def test_general_question(self):
        self.assertEqual(
            classify_intent('how do I set up a vendor?'),
            INTENT_GENERAL,
        )

    def test_empty_message(self):
        self.assertEqual(classify_intent(''), INTENT_GENERAL)

    def test_none_message(self):
        self.assertEqual(classify_intent(None), INTENT_GENERAL)


@tagged('post_install', '-at_install')
class TestDocumentTypeClassification(TransactionCase):
    """Test document type classification from text content."""

    def test_invoice_from_text(self):
        text = 'INVOICE\nTotal Due: PHP 95,408.16\nVAT: 12%\nTIN: 123-456-789'
        self.assertEqual(classify_document_type(text), 'invoice')

    def test_invoice_from_filename(self):
        self.assertEqual(
            classify_document_type('', 'march (2).pdf'),
            'general',  # filename alone doesn't say invoice
        )

    def test_invoice_from_billing_keyword(self):
        text = 'Billing Statement\nSubtotal: 50,000\nEWT: 2,500'
        self.assertEqual(classify_document_type(text), 'invoice')

    def test_contract_from_text(self):
        text = (
            'SERVICE AGREEMENT\nThis contract is entered into by '
            'the parties hereinafter referred to as...'
        )
        self.assertEqual(classify_document_type(text), 'contract')

    def test_financial_statement(self):
        text = 'Balance Sheet as of March 31, 2026\nTotal Equity: 1,200,000'
        self.assertEqual(classify_document_type(text), 'financial_statement')

    def test_general_document(self):
        text = 'Meeting notes from today. Discussion about next steps.'
        self.assertEqual(classify_document_type(text), 'general')


@tagged('post_install', '-at_install')
class TestSystemInstruction(TransactionCase):
    """Test that system instructions prevent generic clarification."""

    def test_extract_instruction_no_clarification(self):
        instr = build_system_instruction(INTENT_EXTRACT, 'general', 1)
        self.assertIn('Extract all fields', instr)
        self.assertIn('Do not ask clarification', instr)

    def test_validate_invoice_instruction(self):
        instr = build_system_instruction(INTENT_VALIDATE, 'invoice', 1)
        self.assertIn('tax computation', instr)
        self.assertIn('Recompute', instr)
        self.assertIn('Do not ask for invoice numbers', instr)

    def test_validate_general_instruction(self):
        instr = build_system_instruction(INTENT_VALIDATE, 'general', 1)
        self.assertIn('validated', instr)
        self.assertIn('Do not ask clarification', instr)

    def test_review_instruction(self):
        instr = build_system_instruction(INTENT_REVIEW, 'general', 1)
        self.assertIn('review', instr)
        self.assertIn('Do not ask clarification', instr)

    def test_summarize_instruction(self):
        instr = build_system_instruction(INTENT_SUMMARIZE, 'general', 1)
        self.assertIn('summary', instr)
        self.assertIn('Do not ask clarification', instr)

    def test_general_with_sources_instruction(self):
        instr = build_system_instruction(INTENT_GENERAL, 'general', 1)
        self.assertIn('do not ask the user to provide', instr)

    def test_general_without_sources_returns_none(self):
        instr = build_system_instruction(INTENT_GENERAL, 'general', 0)
        self.assertIsNone(instr)


@tagged('post_install', '-at_install')
class TestAntiRegressionGenericClarification(TransactionCase):
    """Anti-regression: system instructions must never produce
    generic clarification prompts when attachment + intent are present.

    These tests encode the exact failure modes from the original bug report.
    """

    # Banned phrases that indicate the system is ignoring attachments
    BANNED_PHRASES = [
        'what type of analysis',
        'what record/module',
        'please provide more details about the transaction',
        'what kind of review',
        'which module',
        'can you specify',
    ]

    def _assert_no_banned_phrases(self, instruction):
        """Verify that the instruction doesn't contain banned phrases."""
        lower = instruction.lower()
        for phrase in self.BANNED_PHRASES:
            self.assertNotIn(
                phrase,
                lower,
                f'System instruction contains banned generic phrase: "{phrase}"',
            )

    def test_extract_first_no_generic_questions(self):
        """'extract first' + attachment must not ask generic questions."""
        instr = build_system_instruction(INTENT_EXTRACT, 'general', 1)
        self._assert_no_banned_phrases(instr)

    def test_assess_tax_no_generic_questions(self):
        """'assess tax computation' + invoice must not ask generic questions."""
        instr = build_system_instruction(INTENT_VALIDATE, 'invoice', 1)
        self._assert_no_banned_phrases(instr)

    def test_summarize_no_generic_questions(self):
        """'summarize this' + attachment must not ask generic questions."""
        instr = build_system_instruction(INTENT_SUMMARIZE, 'general', 1)
        self._assert_no_banned_phrases(instr)

    def test_review_no_generic_questions(self):
        """'review' + attachment must not ask generic questions."""
        instr = build_system_instruction(INTENT_REVIEW, 'general', 1)
        self._assert_no_banned_phrases(instr)

    def test_validate_general_no_generic_questions(self):
        """'validate' + non-invoice attachment must not ask generic questions."""
        instr = build_system_instruction(INTENT_VALIDATE, 'general', 1)
        self._assert_no_banned_phrases(instr)

    def test_general_with_sources_no_generic_questions(self):
        """General question + attachment must not ask generic questions."""
        instr = build_system_instruction(INTENT_GENERAL, 'general', 1)
        self._assert_no_banned_phrases(instr)
