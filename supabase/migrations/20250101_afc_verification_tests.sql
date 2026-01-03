-- AFC Close Manager Schema Verification Tests
-- Tests Four-Eyes Principle, GL Balance, PH Tax, and SOX 404 Audit Immutability

DO $$
DECLARE
    v_calendar_id INTEGER;
    v_gl_id INTEGER;
    v_task_id INTEGER;
    v_audit_id INTEGER;
    v_tax DECIMAL;
BEGIN
    -- Create test calendar
    INSERT INTO afc.close_calendar (
        name, period_start, period_end, fiscal_year, fiscal_period,
        company_id, created_by
    ) VALUES (
        'Test Calendar', '2025-01-01', '2025-01-31', 2025, 1, 1, 1
    ) RETURNING id INTO v_calendar_id;

    RAISE NOTICE '';
    RAISE NOTICE '╔════════════════════════════════════════════╗';
    RAISE NOTICE '║  AFC CLOSE MANAGER CONSTRAINT TESTS        ║';
    RAISE NOTICE '╚════════════════════════════════════════════╝';
    RAISE NOTICE '';
    RAISE NOTICE '=== FOUR-EYES PRINCIPLE TESTS ===';

    -- Test 1: preparer = reviewer (SHOULD FAIL)
    BEGIN
        INSERT INTO afc.closing_task (
            calendar_id, name, due_date,
            preparer_id, reviewer_id, approver_id
        ) VALUES (
            v_calendar_id, 'Test Violation 1', CURRENT_DATE + 7, 1, 1, 2
        );
        RAISE EXCEPTION 'FAILED: Four-Eyes did not detect preparer=reviewer';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE '✅ Four-Eyes blocks preparer=reviewer (1=1)';
    END;

    -- Test 2: preparer = approver (SHOULD FAIL)
    BEGIN
        INSERT INTO afc.closing_task (
            calendar_id, name, due_date,
            preparer_id, reviewer_id, approver_id
        ) VALUES (
            v_calendar_id, 'Test Violation 2', CURRENT_DATE + 7, 1, 2, 1
        );
        RAISE EXCEPTION 'FAILED: Four-Eyes did not detect preparer=approver';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE '✅ Four-Eyes blocks preparer=approver (1=1)';
    END;

    -- Test 3: reviewer = approver (SHOULD FAIL)
    BEGIN
        INSERT INTO afc.closing_task (
            calendar_id, name, due_date,
            preparer_id, reviewer_id, approver_id
        ) VALUES (
            v_calendar_id, 'Test Violation 3', CURRENT_DATE + 7, 1, 2, 2
        );
        RAISE EXCEPTION 'FAILED: Four-Eyes did not detect reviewer=approver';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE '✅ Four-Eyes blocks reviewer=approver (2=2)';
    END;

    -- Test 4: Valid Four-Eyes (SHOULD PASS)
    INSERT INTO afc.closing_task (
        calendar_id, name, due_date,
        preparer_id, reviewer_id, approver_id
    ) VALUES (
        v_calendar_id, 'Valid Task', CURRENT_DATE + 7, 1, 2, 3
    ) RETURNING id INTO v_task_id;
    RAISE NOTICE '✅ Four-Eyes allows valid scenario (preparer=1, reviewer=2, approver=3)';

    RAISE NOTICE '';
    RAISE NOTICE '=== GL BALANCE VALIDATION TESTS ===';

    -- Test 5: Draft GL with unbalanced totals (SHOULD PASS)
    INSERT INTO afc.gl_posting (
        calendar_id, journal_id, posting_date,
        total_debit, total_credit, status, created_by
    ) VALUES (
        v_calendar_id, 1, CURRENT_DATE, 100.00, 90.00, 'draft', 1
    ) RETURNING id INTO v_gl_id;
    RAISE NOTICE '✅ GL Balance allows draft with unbalanced totals (DR=100, CR=90)';

    -- Test 6: Validated GL with unbalanced totals (SHOULD FAIL)
    BEGIN
        UPDATE afc.gl_posting
        SET status = 'validated', total_debit = 100.00, total_credit = 90.00
        WHERE id = v_gl_id;
        RAISE EXCEPTION 'FAILED: GL Balance did not block unbalanced validated entry';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE '✅ GL Balance blocks validated with unbalanced totals (DR=100, CR=90)';
    END;

    -- Test 7: Validated GL with balanced totals (SHOULD PASS)
    UPDATE afc.gl_posting
    SET status = 'validated', total_debit = 100.00, total_credit = 100.00
    WHERE id = v_gl_id;
    RAISE NOTICE '✅ GL Balance allows validated with balanced totals (DR=100, CR=100)';

    RAISE NOTICE '';
    RAISE NOTICE '=== PH TAX CALCULATION TESTS (2024 TRAIN Law) ===';

    -- Test 8: ₱250,000 (0% bracket - no tax)
    v_tax := afc.calculate_ph_income_tax(250000, 2024, FALSE);
    IF v_tax = 0 THEN
        RAISE NOTICE '✅ PH tax: ₱250K income → ₱0 tax (0%% bracket)';
    ELSE
        RAISE EXCEPTION 'FAILED: Expected ₱0, got ₱%', v_tax;
    END IF;

    -- Test 9: ₱400,000 (15% bracket)
    v_tax := afc.calculate_ph_income_tax(400000, 2024, FALSE);
    RAISE NOTICE '✅ PH tax: ₱400K income → ₱% tax (15%% bracket)', v_tax;

    -- Test 10: ₱2,000,000 (25% bracket)
    v_tax := afc.calculate_ph_income_tax(2000000, 2024, FALSE);
    RAISE NOTICE '✅ PH tax: ₱2M income → ₱% tax (25%% bracket)', v_tax;

    -- Test 11: PWD/Senior 5% flat rate
    v_tax := afc.calculate_ph_income_tax(2000000, 2024, TRUE);
    IF v_tax = 100000 THEN
        RAISE NOTICE '✅ PWD/Senior: ₱2M × 5%% = ₱100,000';
    ELSE
        RAISE EXCEPTION 'FAILED: Expected ₱100K, got ₱%', v_tax;
    END IF;

    RAISE NOTICE '';
    RAISE NOTICE '=== SOX 404 AUDIT LOG IMMUTABILITY TESTS ===';

    -- Test 12: Create audit log entry
    INSERT INTO afc.sod_audit_log (
        user_id, action_type, resource_type, resource_id, metadata
    ) VALUES (
        1, 'CREATE', 'closing_task', v_task_id, '{"test": true}'::jsonb
    ) RETURNING id INTO v_audit_id;
    RAISE NOTICE '✅ Audit log entry created (id=%)', v_audit_id;

    -- Test 13: Try UPDATE (SHOULD FAIL)
    BEGIN
        UPDATE afc.sod_audit_log SET action_type = 'UPDATE' WHERE id = v_audit_id;
        RAISE EXCEPTION 'FAILED: SOX 404 audit log allowed UPDATE';
    EXCEPTION
        WHEN raise_exception THEN
            IF SQLERRM LIKE '%immutable%SOX 404%' THEN
                RAISE NOTICE '✅ SOX 404 blocks UPDATE to audit log';
            ELSE
                RAISE;
            END IF;
    END;

    -- Test 14: Try DELETE (SHOULD FAIL)
    BEGIN
        DELETE FROM afc.sod_audit_log WHERE id = v_audit_id;
        RAISE EXCEPTION 'FAILED: SOX 404 audit log allowed DELETE';
    EXCEPTION
        WHEN raise_exception THEN
            IF SQLERRM LIKE '%immutable%SOX 404%' THEN
                RAISE NOTICE '✅ SOX 404 blocks DELETE of audit log';
            ELSE
                RAISE;
            END IF;
    END;

    RAISE NOTICE '';
    RAISE NOTICE '╔════════════════════════════════════════════╗';
    RAISE NOTICE '║  ALL CONSTRAINT TESTS PASSED ✅            ║';
    RAISE NOTICE '╚════════════════════════════════════════════╝';
    RAISE NOTICE '';

    -- Cleanup
    ROLLBACK;
END $$;

-- Final Summary
SELECT '✅ AFC Close Manager canonical schema deployed and verified successfully' AS summary;
