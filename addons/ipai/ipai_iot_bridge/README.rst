===============
IPAI IoT Bridge
===============

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta

.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

|badge1| |badge2|

IoT device integration for IPAI CE+OCA stack without Enterprise IoT dependencies.

**Table of contents**

.. contents::
   :local:

Features
========

* Direct device communication via MQTT, HTTP/REST
* Device registry and lifecycle management
* Real-time data collection and storage
* Alert and notification system
* No Enterprise IoT box required

Supported Protocols
===================

* **MQTT**: For real-time sensor data
* **HTTP/REST**: For web-enabled devices
* **Modbus**: For industrial equipment
* **OPC UA**: For industrial automation
* **WebSocket**: For real-time bidirectional communication
* **Serial**: For legacy devices

Configuration
=============

1. Navigate to **Settings > Technical > IoT Bridge > Devices**
2. Register your devices with connection details
3. Configure alert rules for monitoring

Device Types
------------

Pre-configured device types include:

* Temperature Sensor
* Humidity Sensor
* Barcode Scanner
* Label Printer
* Scale
* POS Display

Usage
=====

Creating Readings Programmatically
----------------------------------

::

    reading = env['ipai.iot.reading'].create_reading(
        device_code='TEMP001',
        reading_type='temperature',
        value=25.5,
        unit='°C'
    )

Setting Up Alerts
-----------------

Configure alert rules to monitor device readings and notify users
when thresholds are exceeded.

Known Issues / Roadmap
======================

* Add MQTT broker integration
* Implement device auto-discovery
* Add dashboard widgets for monitoring

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
