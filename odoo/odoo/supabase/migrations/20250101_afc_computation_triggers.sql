-- AFC Close Manager Computation Triggers
-- Replaces GENERATED ALWAYS AS columns with trigger-based computation

-- 1. Trigger for closing_task.is_overdue
CREATE OR REPLACE FUNCTION afc.update_task_overdue_status()
RETURNS TRIGGER AS $$
BEGIN
    NEW.is_overdue := (
        NEW.status NOT IN ('completed') AND NEW.due_date < CURRENT_DATE
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_task_overdue
    BEFORE INSERT OR UPDATE ON afc.closing_task
    FOR EACH ROW
    EXECUTE FUNCTION afc.update_task_overdue_status();

-- 2. Trigger for bir_form_1700.tax_payable and penalties_applicable
CREATE OR REPLACE FUNCTION afc.update_bir_1700_computed()
RETURNS TRIGGER AS $$
BEGIN
    NEW.tax_payable := COALESCE(NEW.computed_tax, 0) - COALESCE(NEW.tax_withheld, 0);
    NEW.penalties_applicable := (NEW.filing_deadline < CURRENT_DATE AND NEW.filed_at IS NULL);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_bir_1700
    BEFORE INSERT OR UPDATE ON afc.bir_form_1700
    FOR EACH ROW
    EXECUTE FUNCTION afc.update_bir_1700_computed();

-- 3. Trigger for bir_form_1601c.filing_deadline
CREATE OR REPLACE FUNCTION afc.update_bir_1601c_deadline()
RETURNS TRIGGER AS $$
BEGIN
    NEW.filing_deadline := (DATE_TRUNC('month', NEW.tax_period) + INTERVAL '1 month' + INTERVAL '19 days')::DATE;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_bir_1601c_deadline
    BEFORE INSERT OR UPDATE ON afc.bir_form_1601c
    FOR EACH ROW
    EXECUTE FUNCTION afc.update_bir_1601c_deadline();

-- 4. Trigger for bir_form_2550q VAT calculations
CREATE OR REPLACE FUNCTION afc.update_bir_2550q_vat()
RETURNS TRIGGER AS $$
BEGIN
    NEW.output_vat := NEW.vatable_sales * 0.12;
    NEW.vat_payable := GREATEST(NEW.output_vat - COALESCE(NEW.input_vat, 0), 0);
    NEW.excess_input_vat := GREATEST(COALESCE(NEW.input_vat, 0) - NEW.output_vat, 0);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_bir_2550q_vat
    BEFORE INSERT OR UPDATE ON afc.bir_form_2550q
    FOR EACH ROW
    EXECUTE FUNCTION afc.update_bir_2550q_vat();

\echo 'Computation triggers created successfully ✅'
