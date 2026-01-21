=====================
IPAI Enterprise Bridge
=====================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta

.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

.. |badge3| image:: https://img.shields.io/badge/github-InsightPulseAI%2Fodoo--ce-lightgray.png?logo=github
    :target: https://github.com/jgtolentino/odoo-ce/tree/main/addons/ipai/ipai_enterprise_bridge
    :alt: InsightPulseAI/odoo-ce

|badge1| |badge2| |badge3|

Provides Enterprise-compatible interfaces without Enterprise/IAP dependencies
for the IPAI CE+OCA stack.

**Table of contents**

.. contents::
   :local:

Features
========

* Enterprise feature stubs for compatibility
* IAP bypass configurations
* OCA-based alternatives routing
* Graceful degradation for EE-only features

This module ensures IPAI modules can reference Enterprise-style APIs while
running purely on CE+OCA stack.

Configuration
=============

Navigate to **Settings > Technical > Enterprise Bridge > Bridge Configuration**
to configure how Enterprise features are handled:

* **Stub**: No-op implementation (safe fallback)
* **OCA**: Routes to configured OCA alternative
* **Custom**: Uses custom IPAI implementation
* **Disabled**: Feature is completely unavailable

Usage
=====

The module provides:

1. **EnterpriseBridgeConfig** model for configuring feature bridges
2. **IAPBridgeMixin** for models needing IAP bypass functionality

Example usage in other modules::

    class MyModel(models.Model):
        _name = "my.model"
        _inherit = ["ipai.iap.bridge.mixin"]

        def some_method(self):
            if not self._check_iap_service("sms"):
                # Use alternative implementation
                alternative = self._get_iap_alternative("sms")
                ...

Known Issues / Roadmap
======================

* Add more Enterprise feature bridges
* Implement automatic OCA alternative detection
* Add migration tools for EE-to-CE transitions

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/jgtolentino/odoo-ce/issues>`_.

Credits
=======

Authors
~~~~~~~

* InsightPulse AI

Maintainers
~~~~~~~~~~~

This module is maintained by InsightPulse AI.
