<!-- loio08b54863254c43fda04b0726814e5506 -->

# Automated Setup for Production Tenant

Booster in SAP BTP cockpit for automated setup of a production tenant for SAP Advanced Financial Closing



<a name="loio08b54863254c43fda04b0726814e5506__section_v51_vqj_pdc"/>

## Context

For SAP Advanced Financial Closing, a booster is available in the SAP BTP cockpit. This booster supports you with your initial system setup by automating several of the setup steps. The following steps can be covered by the booster:

> ### Note:  
> The booster supports the automated setup for your production tenant only. If you want to setup a test tenant as well, you need to set it up manually as described under [Onboarding](../Onboarding/onboarding-1987953.md).
> 
> For more information about a system landscape involving both a production and a test tenant, see [System Landscape](../System-Landscape/system-landscape-3b9f341.md).

-   Create or select the SAP BTP subaccount that you want to use for SAP Advanced Financial Closing.
-   Initial role template assignments for users, such as administrators, developers, and business users.
-   Create formations for communication systems of type SAP S/4HANA Cloud Public Edition.

    > ### Note:  
    > An automated formation setup is currently possible for systems of type SAP S/4HANA Cloud Public Edition only.
    > 
    > The system needs to have been registered under *System Landscape* \> *Systems* in your subaccount before you can use the booster. The communication scenario group needs to be set as either *All Communication Scenarios* or *Integration with SAP Advanced Financial Closing*. The registration happened either automatically or it had to be done manually. For more information, see [Registering an SAP System \(SAP BTP documentation\)](https://help.sap.com/docs/btp/sap-business-technology-platform/2ffdaff0f1454acdb046876045321c91.html).




<a name="loio08b54863254c43fda04b0726814e5506__section_vrc_54k_pdc"/>

## Components Included in the Booster

The following components are included in the booster and will be configured when you use the booster for the initial set up of SAP Advanced Financial Closing:

-   *AFC Public API* \(Standard plan\)
-   Subscription to **SAP Advanced Financial Closing** for your production tenant
-   Subscription to **SAP Audit Log service** for SAP BTP

**Related Information**  


[Boosters \(SAP BTP documentation\)](https://help.sap.com/docs/btp/sap-business-technology-platform/fb1b56148f834749a2bf51127421610b.html)

[System Landscape](../System-Landscape/system-landscape-3b9f341.md "Understand the system landscape of SAP Advanced Financial Closing.")

[Onboarding](../Onboarding/onboarding-1987953.md "Add SAP Advanced Financial Closing to your global account and subscribe to the product.")

[User Management](../User-Management/user-management-ae7fa30.md "Understand how you can manage users and their authorizations in SAP Advanced Financial Closing.")

[Connectivity](../Connectivity/connectivity-200deae.md "Connect your financial cloud or on-premise systems to SAP Advanced Financial Closing.")

<a name="loiobc3d834ea2bc4a8fa0bf33cba6cedb1e"/>

<!-- loiobc3d834ea2bc4a8fa0bf33cba6cedb1e -->

## How to Automate Setting Up SAP Advanced Financial Closing Using a Booster

Use a booster to automate setting up your initial system.



<a name="loiobc3d834ea2bc4a8fa0bf33cba6cedb1e__prereq_t5b_nxj_pdc"/>

## Prerequisites

-   You have a global SAP BTP account with an entitlement for SAP Advanced Financial Closing.
-   You're a global account manager for this account.
-   You have an SAP Cloud Identity Services identity provider that you can use for SAP Advanced Financial Closing.

    For more information, see [SAP Cloud Identity Services - Identity Authentication](https://help.sap.com/docs/IDENTITY_AUTHENTICATION/6d6d63354d1242d185ab4830fc04feb1/d17a116432d24470930ebea41977a888.html).

-   You’re setting up SAP Advanced Financial Closing in the plan *afc-production – standard*.

    > ### Remember:  
    > The booster supports the automated setup for your production tenant only. If you want to setup a test tenant as well, you need to set it up manually as described under [Onboarding](../Onboarding/onboarding-1987953.md).
    > 
    > For more information about a system landscape involving both a production and a test tenant, see [System Landscape](../System-Landscape/system-landscape-3b9f341.md).




## Procedure

1.  Go to the SAP BTP cockpit.

2.  Go to the global account that has the entitlement for SAP Advanced Financial Closing.

3.  Go to *Boosters* and search for `SAP Advanced Financial Closing`.

4.  Find the *Set Up SAP Advanced Financial Closing* booster and choose *Start*.

    > ### Tip:  
    > If you don't choose *Start* right away and choose the tile instead, you can find more information about the booster:
    > 
    > -   On the *Overview* tab, you can find an overview of what the booster does and how to set up SAP Advanced Financial Closing.
    > -   Go to the *Components* tab to check which components will be configured when you use the booster. The booster covers the following components:
    >     -   *AFC Public API* \(Standard plan\)
    >     -   Subscription to **SAP Advanced Financial Closing** for your production tenant
    >     -   Subscription to **SAP Audit Log service** for SAP BTP
    > 
    > -   Go to the *Additional Resources* tab to find links to more information about SAP Advanced Financial Closing.

5.  Choose *Start* in the booster header.

6.  *Check Prerequisites* screen:

    First, the system checks whether you're the global account manager and whether you meet all other the requirements to use this booster. This check covers authorization and entitlement requirements as well as establishing whether an identity provider exists.

7.  *Select Scenario* screen:

    Decide whether you want to create a new subaccount or select an existing subaccount to be used for the configuration:

    1.  *Create Subaccount*:

        1.  On the next screen, you find more information about the entitlements required for this configuration.
        2.  Under *Subaccount Name*, you can enter a name for your new subaccount.
        3.  Under *Provider*, you select the infrastructure provider for your new subaccount. For a subaccount for SAP Advanced Financial Closing, you need to select *Amazon Web Services \(AWS\)*.
        4.  Under *Region*, you select the region in which your subaccount will be created. For a subaccount for SAP Advanced Financial Closing, the following regions are available:
            -   `Europe (Frankfurt) (cf-eu10)`
            -   `US (Virginia) (cf-us10)`
            -   `Europe (Frankfurt) (cf-eu11)` \(for EU access contracts\)

        5.  Under *Subdomain*, you enter a subdomain for your new subaccount.

        > ### Note:  
        > For more information about subaccounts in the SAP BTP cockpit, see [Managing Subaccounts Using the Cockpit \(SAP BTP documentation\)](https://help.sap.com/docs/btp/sap-business-technology-platform/55d0b6d8b96846b8ae93b85194df0944.html).

    2.  *Select Subaccount*:

        Select an existing subaccount with the relevant entitlements from the list.


8.  *Add User* screen:

    Grant authorizations to users right away. You can, of course, also grant user authorizations later on.

    1.  Under *Custom Identity Provider for Applications*, select your identity provider.

    2.  Under *Administrators*, you can add users that should have system administrator authorizations.

        > ### Note:  
        > The user of the person currently using the booster is added automatically.

    3.  Under *Developers*, you can add users that should have authorizations to view the subaccount.

        > ### Note:  
        > The user of the person currently using the booster is added automatically.

    4.  Under *Business Users*, you can add users that should have authorizations to manage, process, and approve task lists and tasks, and to manage configuration, reporting, and user management in SAP Advanced Financial Closing.


    > ### Note:  
    > For more information about role templates in SAP Advanced Financial Closing, see [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).

9.  *Set Up Integrations* screen:

    1.  In the *Create Formation* section, under *Formation Name*, keep or change the suggested name for the formation to be created.

        > ### Note:  
        > For more information about formations, see [Including Systems in a Formation \(SAP BTP documentation\)](https://help.sap.com/docs/btp/sap-business-technology-platform/including-sap-systems-in-formation).

    2.  In the *Include Systems* section, under *SAP S/4HANA Cloud System*, select the communication system you already want to connect to SAP Advanced Financial Closing.

        > ### Remember:  
        > The system needs to have been registered under *System Landscape* \> *Systems* in your subaccount before you can use the booster. The communication scenario group needs to be set as either *All Communication Scenarios* or *Integration with SAP Advanced Financial Closing*. The registration happened either automatically or it had to be done manually. For more information, see [Registering an SAP System \(SAP BTP documentation\)](https://help.sap.com/docs/btp/sap-business-technology-platform/2ffdaff0f1454acdb046876045321c91.html).

        > ### Note:  
        > You can also manually connect your communication system later, but the way as described here should be the preferred one. However, to connect your communication system manually later, simply leave the selection for *SAP S/4HANA Cloud System* empty. For more information about establishing a connection manually, see [Connectivity](../Connectivity/connectivity-200deae.md).


10. *Review* screen:

    1.  Review the information you have provided.

    2.  To start the setup, choose *Finish*.

        > ### Note:  
        > The setup may take several minutes.





<a name="loiobc3d834ea2bc4a8fa0bf33cba6cedb1e__result_ach_vxp_pdc"/>

## Results

You have now configured your SAP BTP subaccount for SAP Advanced Financial Closing. You can check the results in your SAP BTP global account and subaccount:

-   **Global Account:**

    Under *System Landscape*, you can check for systems and formations that have been added.

-   **Subaccount:**
    -   In the *Overview* section on the *Entitlements* tab, you can check for the new entitlements relating to SAP Advanced Financial Closing.
    -   Under *Services* \> *Instances and Subscriptions*, you can check for the subscriptions to SAP Advanced Financial Closing and to the SAP Audit Log service for SAP BTP. Additionally, you can see that the *AFC Public API* has been configured as an instance.
    -   Under *Connectivity* \> *Destinations*, you can check for the destination that has been created to connect your communication system.
    -   Under *Security* \> *Users*, you can check for the users that you have added during the configurations.
    -   Under *Security* \> *Role Collections*, you can check for the roles that exist for SAP Advanced Financial Closing.
    -   Under *Security* \> *Trust Configuration*, you can check for the identity provider used for SAP Advanced Financial Closing.

-   When working with SAP Cloud Identity Services, you can find the corresponding source and target system information under *Identity Provisioning*.
-   In **SAP Advanced Financial Closing**, a communication system has been created if a system of type SAP S/4HANA Cloud Public Edition was included in the setup.

    -   A connection check for the system has been done.
    -   A master data sync between your SAP S/4HANA Cloud Public Edition communication system and SAP Advanced Financial Closing has been started.

    > ### Note:  
    > During daily synchronization between the communication system and SAP Advanced Financial Closing, your business configuration data and master data are synchronized. For more information about the synchronization and validation of data, see [Synchronization of Communication Systems](../Connectivity/synchronization-of-communication-systems-a86348d.md).




<a name="loiobc3d834ea2bc4a8fa0bf33cba6cedb1e__postreq_stw_vxp_pdc"/>

## Next Steps

-   Grant authorizations to business users as described under [User Management](../User-Management/user-management-ae7fa30.md).
-   You or other users can perform business settings as described under [Business Configuration](../Business-Configuration/business-configuration-9719d0a.md).
-   More information about administrative settings, such as system settings, security, archiving, and about integration capabilities of SAP Advanced Financial Closing can be found in the [Administration Guide](../Document-History/document-history-5e2c27a.md).
-   Once authorized, business users can start using SAP Advanced Financial Closing as described in the [User Guide](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/239ab375e0334c149082cc6851644e8b.html "Provides details about the changes made in each version of this document.") :arrow_upper_right:.

**Related Information**  


[Managing Subaccounts Using the Cockpit \(SAP BTP documentation\)](https://help.sap.com/docs/btp/sap-business-technology-platform/55d0b6d8b96846b8ae93b85194df0944.html)

[Including Systems in a Formation \(SAP BTP documentation\)](https://help.sap.com/docs/btp/sap-business-technology-platform/including-sap-systems-in-formation)

[Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md "Static roles enable users to see the affected apps on their SAP Fiori launchpad.")

[Automating Integrations with SAP Advanced Financial Closing \(SAP BTP documentation\)](https://help.sap.com/docs/btp/sap-business-technology-platform/automating-integrations-with-sap-advanced-financial-closing)

[Log On to Your Global Account \(SAP BTP documentation\)](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/77be28886328492086ab07c003cb8d37.html)

[Subscribe to Multitenant Applications Using the Cockpit \(SAP BTP documentation\)](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/7a3e39622be14413b2a4df7c02ca1170.html)

[Creating Service Instances in Cloud Foundry \(SAP Service Manager documentation\)](https://help.sap.com/docs/SERVICEMANAGEMENT/09cc82baadc542a688176dce601398de/6d6846def3c443aa9f83d127353147ce.html)

