# -*- coding: utf-8 -*-
"""
Post-installation hooks for ipai_finance_ppm_tdi module.
Loads seed data programmatically to work around Odoo 18 noupdate="1" issue.
"""
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """
    Load seed data after module installation.
    This hook is called after all XML files have been processed.

    Workaround for Odoo 18.0 issue where XML data files with noupdate="1"
    cause silent installation failure during first-time module install.
    """
    _logger.info("=== Finance PPM TDI Post-Init Hook: Loading Seed Data ===")

    env = api.Environment(cr, SUPERUSER_ID, {})

    # Force load XML data files
    # Odoo's load_data() method bypasses the noupdate issue
    from odoo.modules import module
    module_name = 'ipai_finance_ppm_tdi'

    # List of data files to force-load (order matters for dependencies)
    data_files = [
        'data/finance_team_seed.xml',
        'data/month_end_tasks_seed.xml',
        'data/bir_calendar_seed.xml',
        'data/logframe_kpi_seed.xml',
        'data/ph_holiday_calendar_seed.xml',
    ]

    for data_file in data_files:
        try:
            _logger.info(f"Loading {data_file}...")
            # Use Odoo's internal XML loading mechanism
            module.load_data(cr, module_name, data_file, idref={}, mode='init', noupdate=True)
            _logger.info(f"✅ Successfully loaded {data_file}")
        except Exception as e:
            _logger.error(f"❌ Failed to load {data_file}: {str(e)}")
            # Continue loading other files even if one fails
            continue

    # Verify record counts
    bir_count = env['finance.ppm.bir.calendar'].search_count([])
    logframe_count = env['finance.ppm.logframe'].search_count([])
    holiday_count = env['finance.ppm.ph.holiday'].search_count([])

    _logger.info(f"=== Seed Data Load Complete ===")
    _logger.info(f"BIR Calendar Records: {bir_count}")
    _logger.info(f"LogFrame Records: {logframe_count}")
    _logger.info(f"PH Holiday Records: {holiday_count}")
    _logger.info(f"Expected: 52 BIR, 27 LogFrame, 38 PH Holidays")

    if bir_count == 52 and logframe_count == 27 and holiday_count == 38:
        _logger.info("✅ All seed data loaded successfully!")
    else:
        _logger.warning(f"⚠️ Seed data counts don't match expected values")
