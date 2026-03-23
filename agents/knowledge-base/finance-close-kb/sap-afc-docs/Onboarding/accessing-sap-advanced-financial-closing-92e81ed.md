<!-- loio92e81ed38757493ca89484bd99e21ab0 -->

<link rel="stylesheet" type="text/css" href="../css/sap-icons.css"/>

# Accessing SAP Advanced Financial Closing

Access SAP Advanced Financial Closing under one of two domains.



<a name="loio92e81ed38757493ca89484bd99e21ab0__section_ygf_pdj_kbc"/>

## Context

You can access SAP Advanced Financial Closing under two different domains. The **default URL** for accessing the SAP Advanced Financial Closing launchpad is determined during the subscription of your tenant. Depending on when your tenant was subscribed, your default URL follows one of the following patterns:

-   For subscriptions as of June 23, 2024, the domain pattern is as follows:

    `<subdomain>.production.<region>.afc.cloud.sap`

-   For subscriptions prior to June 23, 2024, the domain pattern is as follows:

    `<subdomain>.production-afc-sap.cfapps.<region>.hana.ondemand.com`


Independent of your default URL, the SAP Advanced Financial Closing launchpad is always accessible with either pattern.

Emails sent from SAP Advanced Financial Closing use the default URL. In most cases, the secondary URL isn't relevant for you.



<a name="loio92e81ed38757493ca89484bd99e21ab0__section_y2c_2hj_kbc"/>

## Relevance of the Domain Distinction

The distinction between the `afc.cloud.sap` domain and the `hana.ondemand.com` domain can become relevant in **certain integration scenarios**. Due to the upcoming deprecation of third-party cookie support by browser vendors, the navigation flow between integrated applications may be interrupted if the domains used by the two products differ.

> ### Example:  
> If you've set up integration with SAP Build Work Zone, you need to ensure that your default URL for SAP Advanced Financial Closing uses the same domain as your SAP Build Work Zone instance.



### Integration with SAP Build Work Zone

From the example above, you've already learned that there are certain URL requirements for the integration with SAP Build Work Zone. In detail, this means that if you've subscribed to SAP Advanced Financial Closing on June 23, 2024 or later, you can use the integration with SAP Build Work Zone only if your SAP Build Work Zone instance uses the domain `workzone.cloud.sap`.

For more information specifically about domain handling in SAP Build Work Zone, see [Using the Common Super Domain](https://help.sap.com/docs/build-work-zone-standard-edition/sap-build-work-zone-standard-edition/using-super-common-domain?locale=en-US) in the SAP Build Work Zone documentation.

<a name="loio26bf9ffa15114bfeb698ef8c35cd78a6"/>

<!-- loio26bf9ffa15114bfeb698ef8c35cd78a6 -->

## How to Verify the Default URL

Check the default URL of your SAP Advanced Financial Closing launchpad.



## Context

You can check the default URL of your SAP Advanced Financial Closing launchpad. This may be necessary to ensure that certain integration scenarios work.



## Procedure

1.  Go to the SAP BTP cockpit.

2.  Go to the subaccount that has the subscription for SAP Advanced Financial Closing.

3.  In the table in the *Subscriptions* section, find the entry for SAP Advanced Financial Closing and choose the *Go to Application* button \(<span class="SAP-icons-V5"></span>\).

4.  In the browser tab that opens, you can see the default URL of your SAP Advanced Financial Closing launchpad.

    > ### Remember:  
    > The default URL follows one of the following patterns:
    > 
    > -   `<subdomain>.production.<region>.afc.cloud.sap`
    > 
    > -   `<subdomain>.production-afc-sap.cfapps.<region>.hana.ondemand.com`




<a name="loio26bf9ffa15114bfeb698ef8c35cd78a6__result_ocs_ykp_kbc"/>

## Results

You have now verified the default URL of your SAP Advanced Financial Closing launchpad.

<a name="loio92783ff283164575afcf1da037d185b9"/>

<!-- loio92783ff283164575afcf1da037d185b9 -->

## How to Change the Default URL

Change the default URL of your SAP Advanced Financial Closing launchpad.



## Context

You can request a change of the default URL for your SAP Advanced Financial Closing launchpad. This may be necessary if an integration scenario requires both integration components or systems to have the same domain.

> ### Remember:  
> Even after changing the default URL, SAP Advanced Financial Closing can still be accessed using both the default and secondary URL, that is, both URLs using either the `afc.cloud.sap` domain or the `hana.ondemand.com` domain respectively.



## Procedure

To request a change of your default URL, open a support ticket under the component `FIN-FIO-FCC`.

> ### Note:  
> Changing the default URL has the following effects:
> 
> -   The subscription URL in the SAP BTP cockpit changes accordingly.
> -   The URLs in emails sent from SAP Advanced Financial Closing change.



<a name="loio92783ff283164575afcf1da037d185b9__result_ldd_lmj_kbc"/>

## Results

Once you get the confirmation, the default URL for your SAP Advanced Financial Closing launchpad has been changed.

