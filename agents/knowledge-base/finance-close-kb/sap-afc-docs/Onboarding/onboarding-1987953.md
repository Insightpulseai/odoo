<!-- loio1987953b694f4f80a63fab2d4e31f19d -->

# Onboarding

Add SAP Advanced Financial Closing to your global account and subscribe to the product.



<a name="loio1987953b694f4f80a63fab2d4e31f19d__prereq_rxp_5qb_l4b"/>

## Prerequisites

-   You have already received the email from SAP Business Technology Platform with the technical information regarding your global account for SAP Advanced Financial Closing.


> ### Remember:  
> For a production tenant, you can also use the booster to benefit from an automated setup. For more information, see [Automated Setup for Production Tenant](../Automated-Setup/automated-setup-for-production-tenant-08b5486.md#loio08b54863254c43fda04b0726814e5506).

> ### Tip:  
> Some of the following steps are collapsed by default. To see the substeps, click on the first line of an affected step and it will expand.



## Procedure

1.  Follow the link in the email to get to the SAP BTP cockpit.

    > ### Note:  
    > Initially, only the receiver or receivers of the email have the required authorization to perform these steps. The receiver or receivers of the email are maintained under *Parties Involved* \> *Contact Person IT*.

2.  Choose the global account for which you received the email.

    > ### Note:  
    > If your organization has multiple global accounts, be sure to choose the global account that contains the entitlement to SAP Advanced Financial Closing. This account is mentioned in the email you've received.

3.  Add users to your global account. Go to *Security* \> *Users* and add the relevant users in the dialog box. Choose the ID format according to the identity provider \(IdP\) you use.

4.  Go to *Account Explorer* and choose *Create* \> *Subaccount*:

    Create the relevant subaccounts in your global account. On global account level, the number of subscriptions for this application is limited. Specifically, you can subscribe only once to SAP Advanced Financial Closing in your global account.

5.  Provide the following information for each subaccount you create and choose *Create*:

    1.  *Display Name*

    2.  *Description*

    3.  *Region*:

        The combination of provider and region represents the data center you are using.

        > ### Note:  
        > For SAP Advanced Financial Closing, the subaccount needs to be in the same region as the application. Currently `Europe (Frankfurt) (cf-eu10)` and `US (Virginia) (cf-us10)` are available as standard regions. If you have an EU access contract for SAP Advanced Financial Closing, the region `Europe (Frankfurt) (cf-eu11)` is shown.

    4.  *Subdomain*:

        The subdomain name must be unique for each data center. Therefore, we strongly recommend including a **customer-specific prefix** in the name of the subdomain. Please note that this subdomain is later part of your URL with which you access the application in the browser and also part of the API URL that you provide to your external trading platform.

    5.  *Advanced*:

        -   If SAP Advanced Financial Closing should be used productively, select the *Used for production* checkbox.
        -   For SAP Advanced Financial Closing beta features don't need to be enabled.


    > ### Example:  
    > Your subaccount details could look something like this:
    > 
    > -   Display Name: `AFC Prod`
    > 
    > -   Description: `Subscribed to SAP Advanced Financial Closing - Prod`
    > 
    > -   Region: `Europe (Frankfurt) (cf-eu10)`
    > 
    > -   Subdomain: `[CustomerNameAbbreviation]-afc-prod`

6.  Enable **Cloud Foundry** in your subaccount and provide a name for the organization. We recommend that you use the same name that you used for the subdomain, for example \[CustomerNameAbbreviation\]-afc-prod.

7.  Configure the entitlements of your subaccount:

    1.  Go to *Entitlements*.

        > ### Note:  
        > Make sure that you are in the correct subaccount. You can see the path of the account and subaccount on the top of your screen.

    2.  Choose *Edit*.

    3.  Choose *Add Service Plans*.

    4.  Under *Services*, search for **`advanced financial closing`** and choose **SAP Advanced Financial Closing** for a production tenant or **SAP Advanced Financial Closing \(test\)** for a test tenant.

        > ### Note:  
        > If the correct entry doesn't show, make sure you select *All Solutions* as a filter option under *Services*.

    5.  Select *Standard \(Application\)* and add the service plan.

        **Result:** **SAP Advanced Financial Closing** is now shown in the list of your subaccount's entitlements.


8.  Subscribe to the application:

    1.  Go to *Services* \> *Instances and Subscriptions*.

    2.  Choose *Create*.

    3.  Provide the following information:

        -   *Service*: `SAP Advanced Financial Closing` for a production tenant or `SAP Advanced Financial Closing (test)` for a test tenant

        -   *Plan*: `Subscriptions - standard`


    4.  Choose *Create*.

        **Result:** **SAP Advanced Financial Closing** is now shown in the list of your subaccount's instances and subscriptions, and the status is *Subscribed*.


9.  **Recommended:** Add SAP Advanced Financial Closing to your Cloud system notification subscriptions as described under [How to Sign Up for Update Notifications](../Monitoring-and-Troubleshooting/how-to-sign-up-for-update-notifications-77c4077.md).


-   **[Accessing SAP Advanced Financial Closing](accessing-sap-advanced-financial-closing-92e81ed.md#loio92e81ed38757493ca89484bd99e21ab0 "Access SAP Advanced
                                                  Financial Closing under one of
		two domains.")**  
Access SAP Advanced Financial Closing under one of two domains.

**Related Information**  


[Log On to Your Global Account \(SAP BTP documentation\)](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/77be28886328492086ab07c003cb8d37.html)

[Subscribe to Multitenant Applications Using the Cockpit \(SAP BTP documentation\)](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/7a3e39622be14413b2a4df7c02ca1170.html)

[Creating Service Instances in Cloud Foundry \(SAP Service Manager documentation\)](https://help.sap.com/docs/SERVICEMANAGEMENT/09cc82baadc542a688176dce601398de/6d6846def3c443aa9f83d127353147ce.html)

