<!-- loio405806439e3e4cbc8b34c49d1d15d91a -->

<link rel="stylesheet" type="text/css" href="../css/sap-icons.css"/>

# How to Create an API Instance and Service Key for API Integration Scenarios

Create an API instance and service key for API integration scenarios for SAP Advanced Financial Closing.



## Context

For some API integration scenarios, as the first step the integration scenario with SAP Advanced Financial Closing, you need to create an API instance and a service key. This step is required only for the following integration scenarios:

-   [SCIM API for User Access Management](scim-api-for-user-access-management-3f44fda.md)
-   [SAP Task Center Integration for SAP Advanced Financial Closing](sap-task-center-integration-for-sap-advanced-financial-closing-625bfc3.md)

> ### Note:  
> The API instance and service key you create apply to all API integration scenarios you want to use for SAP Advanced Financial Closing. This means that you don't need to repeat these steps for additional API integration scenarios you implement.



## Procedure

1.  Create an API instance:

    1.  Go to the SAP BTP cockpit.

    2.  Go to the subaccount that contains the entitlement to SAP Advanced Financial Closing.

    3.  Ensure that you have enabled the *standard* service plan entitlement for SAP Advanced Financial Closing.

        For more information, see [Configure Entitlements and Quotas for Subaccounts](https://help.sap.com/docs/btp/sap-business-technology-platform/configure-entitlements-and-quotas-for-subaccounts).

    4.  From the side panel, choose *Service Marketplace*.

    5.  In the service marketplace, search for `advanced financial closing`.

    6.  Choose the *SAP Advanced Financial Closing* tile to open the details.

    7.  Go to the *Service Plans* tab.

        > ### Note:  
        > If you don't see the tab, check that you have performed the previous step to enabled the *standard* service plan entitlement for your subaccount.

    8.  In the table, look for an entry called *API - standard*.

    9.  Open the additional options for this entry using the *More* icon <span class="SAP-icons-V5"></span>.

    10. Choose *Create*.

    11. In the *New Instance or Subscription* dialog, provide the following information:


        <table>
        <tr>
        <th valign="top">

        Field
        
        </th>
        <th valign="top">

        Entry
        
        </th>
        </tr>
        <tr>
        <td valign="top">
        
        *Service*
        
        </td>
        <td valign="top">
        
        Keep the default value.
        
        </td>
        </tr>
        <tr>
        <td valign="top">
        
        *Plan*
        
        </td>
        <td valign="top">
        
        Keep the default value.
        
        </td>
        </tr>
        <tr>
        <td valign="top">
        
        *Runtime Environment*
        
        </td>
        <td valign="top">
        
        Enter `Cloud Foundry`.
        
        </td>
        </tr>
        <tr>
        <td valign="top">
        
        *Space*
        
        </td>
        <td valign="top">
        
        Keep the default value.
        
        </td>
        </tr>
        <tr>
        <td valign="top">
        
        *Instance Name*
        
        </td>
        <td valign="top">
        
        Enter a name for this instance.
        
        </td>
        </tr>
        </table>
        

2.  Get the service key:

    > ### Tip:  
    > You can also get the service key using a command line tool. For more information about this, see [Access SAP Authorization and Trust Management Service APIs](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/ebc9113a520e495ea5fb759b9a7929f2.html).

    1.  From the side panel, choose *Instances* and find the API instance.

    2.  From the search result list, open the instance details.

    3.  In the *Service Keys* section, choose *Create*.

    4.  Open the service key credentials by clicking on the service key name.

        > ### Recommendation:  
        > Service keys hold sensitive data, such as the *clientid* and *clientsecret* elements.
        > 
        > You may want to pay attention to the security considerations described under [Data Used for API Integrations](../Security/data-used-for-api-integrations-62f0a49.md).

        You can use this information for the following cases:

        -   Use the API through your preferred command line tool as described under [Access SAP Authorization and Trust Management Service APIs](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/ebc9113a520e495ea5fb759b9a7929f2.html).

        -   Use the API through your identity management, such as the Identity Provisioning service. Maintain the API information as described below.






<a name="loio405806439e3e4cbc8b34c49d1d15d91a__result_edz_tfr_pzb"/>

## Results

You've now created an API instance and service key for API integration scenarios for SAP Advanced Financial Closing.

