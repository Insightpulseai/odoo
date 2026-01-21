======================
IPAI Mail Integration
======================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta

.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

|badge1| |badge2|

Direct email integration for IPAI CE+OCA stack without IAP dependencies.

**Table of contents**

.. contents::
   :local:

Features
========

* Direct SMTP gateway integration
* Mailgun API support
* SendGrid API support
* Amazon SES support
* OAuth2 authentication for SMTP
* Email tracking (opens and clicks)
* Comprehensive mail logging

Configuration
=============

1. Navigate to **Settings > Technical > Mail Integration > Gateways**
2. Create a new gateway configuration
3. Set up your SMTP or API credentials
4. Mark one gateway as default

Gateway Types
-------------

* **SMTP**: Direct SMTP server connection
* **Mailgun**: Mailgun API integration
* **SendGrid**: SendGrid API integration
* **Amazon SES**: AWS Simple Email Service

Usage
=====

Once configured, the module automatically routes outgoing emails
through the configured gateway. Email tracking data is logged
and accessible through **Settings > Mail Integration > Mail Log**.

Known Issues / Roadmap
======================

* Add webhook support for delivery notifications
* Implement bulk sending optimization
* Add email template management

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
