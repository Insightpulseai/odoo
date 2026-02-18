========
Invoices
========

.. _pos_invoices/invoices:

Point of Sale allows you to issue and print invoices for :ref:`registered customers
<pos/use/customers>` upon payment and retrieve all past invoiced orders.

.. note::
   An invoice created in a POS creates an entry into the corresponding :ref:`accounting journal
   <cheat_sheet/journals>` :ref:`configured in the POS settings
   <pos_invoices/invoice_configuration>`.

.. _pos_invoices/invoice_configuration:

Configuration
=============

To define the default journals for a specific POS, go to the :ref:`POS' settings
<pos/use/settings>`, scroll down to the :guilabel:`Accounting` section, and select the appropriate
journals for :guilabel:`Orders` and :guilabel:`Invoices` under :guilabel:`Default Journals`.

.. image:: pos_invoices/invoice-config.png
   :alt: accounting section in the POS settings
   :scale: 70 %

.. note::
   Specific journals can also be defined for each :doc:`payment method <../payment_methods>`.

Invoice a customer
==================

To invoice a customer, first make sure a :ref:`customer is set <pos/use/customers>` for the order.
Then, upon :ref:`processing the payment <pos/use/sell>`, click :guilabel:`Invoice` underneath the
customer's name to issue an invoice for that order.

Select the payment method and click :guilabel:`Validate`. The invoice is automatically issued
and ready to be downloaded and/or printed.

Retrieve invoices
=================

To retrieve the invoice of a POS order, follow these steps:

#. Go to :menuselection:`Point of Sale --> Orders --> Orders`.
#. Click the relevant invoiced order in the list.
#. On the order form, click the :guilabel:`Invoice` smart button.

.. tip::
   - Invoiced orders have the :guilabel:`Fully Invoiced` :guilabel:`Invoice Status`.
   - You can filter the list of orders to only display invoiced orders in the list: click the search
     bar and select the :guilabel:`Invoiced` filter.

QR codes to generate invoices
=============================

Customers can also request an invoice by scanning the QR code printed on their receipt. Upon
scanning, they must fill in a form with their billing information and click :guilabel:`Get my
invoice`. The invoice is then generated and available for download and the order's status is
updated to :guilabel:`Fully invoiced`.

To use this feature, enable QR codes on receipts by going to :menuselection:`Point of Sale -->
Configuration --> Settings`. Then, select the POS in the :guilabel:`Point of Sale` field, scroll
down to the :guilabel:`Bills & Receipts` section, and enable :guilabel:`Use QR code on ticket`.
