#!/usr/bin/env python3
"""Verify Phase 3 seed data loaded successfully."""

import xmlrpc.client

# Connection settings
url = 'http://localhost:8069'
db = 'odoo'
username = 'admin'
password = 'admin'

try:
    # Authenticate
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})

    if not uid:
        print("❌ Authentication failed")
        exit(1)

    # Connect to models
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Check new models exist and count records
    print("=" * 60)
    print("PHASE 3 VERIFICATION - Finance PPM TDI Seed Data")
    print("=" * 60)

    try:
        bir_count = models.execute_kw(db, uid, password,
            'finance.ppm.bir.calendar', 'search_count', [[]])
        print(f"✅ BIR Calendar Records: {bir_count} (expected: 52)")

        logframe_count = models.execute_kw(db, uid, password,
            'finance.ppm.logframe', 'search_count', [[]])
        print(f"✅ LogFrame KPI Records: {logframe_count} (expected: 27)")

        holiday_count = models.execute_kw(db, uid, password,
            'finance.ppm.ph.holiday', 'search_count', [[]])
        print(f"✅ PH Holiday Records: {holiday_count} (expected: 38)")

        print("-" * 60)
        total = bir_count + logframe_count + holiday_count
        print(f"🎯 Total New Model Records: {total}")
        print(f"🎯 Expected Total: 117 (52+27+38)")
        print("=" * 60)

        if bir_count == 52 and logframe_count == 27 and holiday_count == 38:
            print("\n✅✅✅ PHASE 3 SMOKE TEST PASSED!")
            print("All 3 new models loaded successfully with correct record counts.")
            exit(0)
        else:
            print("\n❌ Phase 3 FAILED: Model data incomplete")
            exit(1)

    except Exception as e:
        print(f"❌ Model not found in registry or query failed: {e}")
        exit(1)

except Exception as e:
    print(f"❌ Connection or authentication error: {e}")
    exit(1)
