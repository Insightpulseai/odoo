<!-- loioc329991377c448baa4cadb8ea2605352 -->

# How to Set Up the SAP Build Work Zone Integration for SAP Advanced Financial Closing

Set up an integration between SAP Build Work Zone and SAP Advanced Financial Closing.



<a name="loioc329991377c448baa4cadb8ea2605352__prereq_e15_tqv_2dc"/>

## Prerequisites

-   Your entitlements for SAP Advanced Financial Closing and SAP Build Work Zone are part of the same SAP BTP subaccount.
-   Your SAP Build Work Zone tenant has to use the same domain as the default URL of your SAP Advanced Financial Closing tenant.

    For information about the default URL of your SAP Advanced Financial Closing tenant, see [Accessing SAP Advanced Financial Closing](../Onboarding/accessing-sap-advanced-financial-closing-92e81ed.md#loio92e81ed38757493ca89484bd99e21ab0).

    For more information specifically about domain handling in SAP Build Work Zone, see [Using the Common Super Domain](https://help.sap.com/docs/build-work-zone-standard-edition/sap-build-work-zone-standard-edition/using-super-common-domain?locale=en-US) in the SAP Build Work Zone documentation.

-   For the steps to be performed with regard to or in SAP Build Work Zone, you need to have the required authorization.



## Context

SAP Build Work Zone allows you to establish a unified point of access to SAP \(such as SAP S/4HANA Cloud Public Edition, SAP S/4HANA Cloud Private Edition, or SAP S/4HANA\), custom-built, and third-party applications and extensions. Following an integration with SAP Build Work Zone, you can set up one single launchpad page grouping all the relevant apps of the different solutions you have integrated, such as SAP Advanced Financial Closing. You can use this launchpad as a single point of entry and access the apps of the different solutions directly from there.



## Procedure

1.  For more information about setting up SAP Build Work Zone for access to SAP Advanced Financial Closing, see under [Federation of SAP BTP Content Providers](https://help.sap.com/docs/build-work-zone-standard-edition/sap-build-work-zone-standard-edition/federation-of-sap-btp-content-providers) \(SAP Build Work Zone, standard edition documentation\). Please follow the steps described under [Launchpad Modules Content Providers](https://help.sap.com/docs/build-work-zone-standard-edition/sap-build-work-zone-standard-edition/launchpad-modules-content-providers), since this is the process used for solutions provided by SAP, such as SAP Advanced Financial Closing.

2.  If the default URL for your SAP Advanced Financial Closing tenant uses the domain **afc.cloud.sap**, you need to maintain the SAP Build Work Zone common super domain as a trusted domain as described under [Configure Trusted Domains for Multi-Environment Subaccounts](https://help.sap.com/docs/btp/sap-business-technology-platform/c5e997235f724ec686dc5dc101a1ccfb.html).




<a name="loioc329991377c448baa4cadb8ea2605352__result_ltb_211_fdc"/>

## Results

You have now finished setting up an integration between SAP Advanced Financial Closing and SAP Build Work Zone.

