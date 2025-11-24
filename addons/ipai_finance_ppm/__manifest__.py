<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- Approval chain -->
    <record id="ipai_finance_person_ckvc" model="ipai.finance.person">
        <field name="code">CKVC</field>
        <field name="name">Khalil Veracruz</field>
        <field name="role">director</field>
        <field name="responsibility">Final approval / authorization</field>
    </record>
    <record id="ipai_finance_person_rim" model="ipai.finance.person">
        <field name="code">RIM</field>
        <field name="name">Rey Meran</field>
        <field name="role">manager</field>
        <field name="responsibility">Review / validation</field>
    </record>
    <record id="ipai_finance_person_bom" model="ipai.finance.person">
        <field name="code">BOM</field>
        <field name="name">Beng Manalo</field>
        <field name="role">supervisor</field>
        <field name="responsibility">Preparation / filing initiator</field>
    </record>

    <!-- Task executors -->
    <record id="ipai_finance_person_jpal" model="ipai.finance.person">
        <field name="code">JPAL</field>
        <field name="name">Jinky Paladin</field>
        <field name="email">jinky.paladin@omc.com</field>
        <field name="role">staff</field>
        <field name="responsibility">VAT &amp; monthly tax reporting owner (1601C/1601E/2550Q)</field>
    </record>
    <record id="ipai_finance_person_jpl" model="ipai.finance.person">
        <field name="code">JPL</field>
        <field name="name">Jerald Loterte</field>
        <field name="email">jerald.loterte@omc.com</field>
        <field name="role">staff</field>
        <field name="responsibility">WIP / revenue / job reconciliation coordinator</field>
    </record>
    <record id="ipai_finance_person_ji" model="ipai.finance.person">
        <field name="code">JI</field>
        <field name="name">Jasmin Ignacio</field>
        <field name="email">jasmin.ignacio@omc.com</field>
        <field name="role">staff</field>
        <field name="responsibility">Accruals &amp; cost allocation processor</field>
    </record>
    <record id="ipai_finance_person_jo" model="ipai.finance.person">
        <field name="code">JO</field>
        <field name="name">Jhoee Oliva</field>
        <field name="email">jhoee.oliva@omc.com</field>
        <field name="role">staff</field>
        <field name="responsibility">AP liquidation &amp; cash advance handler</field>
    </record>
    <record id="ipai_finance_person_jm" model="ipai.finance.person">
        <field name="code">JM</field>
        <field name="name">Joana Maravillas</field>
        <field name="email">joana.maravillas@omc.com</field>
        <field name="role">staff</field>
        <field name="responsibility">Asset &amp; lease entries / depreciation tracking</field>
    </record>
    <record id="ipai_finance_person_rmqb" model="ipai.finance.person">
        <field name="code">RMQB</field>
        <field name="name">Sally Brillantes</field>
        <field name="email">sally.brillantes@omc.com</field>
        <field name="role">staff</field>
        <field name="responsibility">Expense corrections &amp; reclassification processor</field>
    </record>
    <record id="ipai_finance_person_jap" model="ipai.finance.person">
        <field name="code">JAP</field>
        <field name="name">JAP</field>
        <field name="role">staff</field>
        <field name="responsibility">Billing adjustment / revenue recognition analyst</field>
    </record>
    <record id="ipai_finance_person_jrmo" model="ipai.finance.person">
        <field name="code">JRMO</field>
        <field name="name">JRMO</field>
        <field name="role">staff</field>
        <field name="responsibility">Accruals &amp; WIP schedule assistant</field>
    </record>
</odoo>