<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">

        <record id="cron_check_overdue_bookings" model="ir.cron">
            <field name="name">IPAI Equipment: Check Overdue Bookings</field>
            <field name="model_id" ref="model_ipai_equipment_booking"/>
            <field name="state">code</field>
            <field name="code">model._cron_check_overdue_bookings()</field>
            <field name="interval_number">1</field>
            <field name="interval_type">days</field>
            <field name="active" eval="True"/>
            <field name="priority">10</field>
            <field name="user_id" ref="base.user_root"/>
        </record>

    </data>
</odoo>